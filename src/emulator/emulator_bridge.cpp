#include "emulator_bridge.h"
#include <SPI.h>
#include <driver/dac.h>
#include "display.h"
#include "hw_config.h"
#include <stdlib.h>

extern "C" {
#include "minigb_apu.h"
}

#define AUDIO_BUF_SIZE 8192 // must be power of 2
#define AUDIO_SAMPLE_RATE_HZ 32768
#define AUDIO_PWM_FREQ_HZ 200000
static uint8_t audio_ring[AUDIO_BUF_SIZE];
static volatile uint32_t audio_head = 0;
static volatile uint32_t audio_tail = 0;
static hw_timer_t * audio_timer = NULL;
static struct minigb_apu_ctx apu_ctx;
static SemaphoreHandle_t audio_sync_sem = NULL;

void IRAM_ATTR audio_isr() {
    if (audio_head != audio_tail) {
        uint8_t sample = audio_ring[audio_tail & (AUDIO_BUF_SIZE - 1)];
        dac_output_voltage(DAC_CHANNEL_2, sample);
        audio_tail++;
    } else {
        dac_output_voltage(DAC_CHANNEL_2, 128);
    }
}

uint8_t audio_read(const uint16_t addr) {
    return minigb_apu_audio_read(&apu_ctx, addr);
}

void audio_write(const uint16_t addr, const uint8_t val) {
    minigb_apu_audio_write(&apu_ctx, addr, val);
}

static void audio_init_hw() {
    // We use the ESP32's True Analog DAC instead of PWM!
    // CYD Speaker is on GPIO 26, which is explicitly DAC2.
    // This eliminates the 200kHz PWM carrier noise.
    dac_output_enable(DAC_CHANNEL_2);
    
    if (!audio_timer) {
        audio_timer = timerBegin(0, 80, true);
        timerAttachInterrupt(audio_timer, &audio_isr, true);
        // 80 MHz / 80 = 1 MHz timer tick => period = 1e6 / sample_rate.
        timerAlarmWrite(audio_timer, 1000000 / AUDIO_SAMPLE_RATE_HZ, true);
        timerAlarmEnable(audio_timer);
    }
}

uint8_t emu_audio_volume = 10;

#include "peanut_gb.h"
#include <Arduino.h>
#include <string.h>
#include <SD.h>
#include <esp_partition.h>

#define ENABLE_LCD 1

#define PEANUT_GB_HIGH_LCD_ACCURACY 0
#include "peanut_gb.h"

// ─── ROM Mmap ─────────────────────────────────────────────────────────────
static const esp_partition_t* rom_part = nullptr;
static spi_flash_mmap_handle_t rom_mmap_handle;
static const uint8_t* mapped_rom = nullptr;
static uint32_t romlen = 0;

// ─── State ──────────────────────────────────────────────────────────────────
static struct gb_s* gb = nullptr;
#define MAXRAM (32*1024)
static uint8_t* cram = nullptr;
static uint16_t lbuf[GB_SCREEN_W];
static uint8_t fskip = 0, fcnt = 0;
static uint32_t fpsc = 0, fpst = 0, cfps = 0;
static uint8_t jpad = 0;

// ─── 20 Palettes (byte-swapped for pushImage) ──────────────────────────────
#define SW(c) (uint16_t)(((c)>>8)|((c)<<8))

static const uint16_t pals[NUM_PALETTES][4] = {
    {SW(0x9FE5),SW(0x4F64),SW(0x2542),SW(0x0261)}, //  0 Classic Green
    {SW(0xFFFF),SW(0xAD55),SW(0x52AA),SW(0x0000)}, //  1 Original DMG
    {SW(0xFFFF),SW(0xB596),SW(0x6B4D),SW(0x0000)}, //  2 Pocket Gray
    {SW(0xFFDF),SW(0xD68F),SW(0x7A4B),SW(0x1082)}, //  3 Warm Sepia
    {SW(0xBF5F),SW(0x6CDF),SW(0x339F),SW(0x0019)}, //  4 Cool Blue
    {SW(0xFFF0),SW(0xFC00),SW(0x8800),SW(0x2000)}, //  5 Autumn
    {SW(0xE71C),SW(0x9CD3),SW(0x4228),SW(0x0000)}, //  6 Grayscale
    {SW(0xFFFF),SW(0xFE20),SW(0xC800),SW(0x4000)}, //  7 Lava
    {SW(0xAFFF),SW(0x5F5F),SW(0x2D1F),SW(0x0019)}, //  8 Ocean
    {SW(0xFFF0),SW(0xBDE0),SW(0x5AE0),SW(0x0120)}, //  9 Forest
    {SW(0xFFFF),SW(0xFD20),SW(0xAB00),SW(0x4000)}, // 10 Sunset
    {SW(0xFFDF),SW(0xF71C),SW(0xAA13),SW(0x3808)}, // 11 Cherry
    {SW(0xCFFF),SW(0x867F),SW(0x433F),SW(0x0019)}, // 12 Ice
    {SW(0xFFB6),SW(0xD52A),SW(0x8A08),SW(0x3000)}, // 13 Chocolate
    {SW(0xFFFF),SW(0xBF5F),SW(0x5F1F),SW(0x0019)}, // 14 Mint
    {SW(0xFFF8),SW(0xFCC0),SW(0xC880),SW(0x6000)}, // 15 Peach
    {SW(0xEF3C),SW(0x867F),SW(0x4179),SW(0x0000)}, // 16 Lavender
    {SW(0xFFFF),SW(0x07FF),SW(0x001F),SW(0x0000)}, // 17 Neon
    {SW(0x0000),SW(0x4228),SW(0xAD55),SW(0xFFFF)}, // 18 Inverted
    {SW(0xFE60),SW(0xAB00),SW(0x5000),SW(0x0000)}, // 19 Gold
};
static const char* palnames[NUM_PALETTES] = {
    "Classic Green","Original DMG","Pocket Gray","Warm Sepia","Cool Blue",
    "Autumn","Grayscale","Lava","Ocean","Forest",
    "Sunset","Cherry","Ice","Chocolate","Mint",
    "Peach","Lavender","Neon","Inverted","Gold"
};
static uint8_t curpal = 0;

void emu_set_palette(uint8_t i) { 
    if (i<NUM_PALETTES) curpal=i; 
    display_set_palette(pals[curpal]);
}
uint8_t emu_get_palette() { return curpal; }
const char* emu_get_palette_name(uint8_t i) { return (i<NUM_PALETTES)?palnames[i]:"?"; }

// ─── Callbacks ──────────────────────────────────────────────────────────────
static uint8_t IRAM_ATTR gb_rom_read(struct gb_s* g, const uint_fast32_t a) {
    (void)g; if(a>=romlen) return 0xFF; return mapped_rom[a];
}
static uint8_t IRAM_ATTR gb_cram_r(struct gb_s* g, const uint_fast32_t a) {
    (void)g; return (a<MAXRAM)?cram[a]:0xFF;
}
static void IRAM_ATTR gb_cram_w(struct gb_s* g, const uint_fast32_t a, const uint8_t v) {
    (void)g; if(a<MAXRAM) cram[a]=v;
}
static void gb_err(struct gb_s* g, const enum gb_error_e e, const uint16_t a) {
    (void)g; Serial.printf("[EMU] Err %d @0x%04X\n",(int)e,a);
}
static void IRAM_ATTR lcd_line(struct gb_s* g, const uint8_t px[160], const uint_fast8_t ln) {
    (void)g;
    if (fskip>0 && (fcnt%(fskip+1))!=0) return;
    display_push_gb_line(ln, (uint8_t*)px);
}

// ─── API ────────────────────────────────────────────────────────────────────
bool emu_open_rom(const char* path) {
    File sf = SD.open(path, FILE_READ); 
    if(!sf) return false;
    uint32_t sz = sf.size();
    
    rom_part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_FAT, "rom");
    if (!rom_part) {
        Serial.println("[EMU] rom part not found");
        sf.close(); return false;
    }

    bool need_copy = true;
    if (sz <= rom_part->size) {
        uint8_t f_hdr[256];
        uint8_t p_hdr[256];
        sf.seek(0); sf.read(f_hdr, 256);
        esp_partition_read(rom_part, 0, p_hdr, 256);
        sf.seek(0);
        if (memcmp(f_hdr, p_hdr, 256) == 0) {
            need_copy = false;
            Serial.println("[EMU] ROM already in flash");
        }
    }

    if (need_copy) {
        if (sz > rom_part->size) {
            Serial.println("[EMU] ROM too large");
            sf.close(); return false;
        }
        Serial.printf("[EMU] Copying %u bytes to flash...\n", sz);
        esp_partition_erase_range(rom_part, 0, (sz + SPI_FLASH_SEC_SIZE - 1) & ~(SPI_FLASH_SEC_SIZE - 1));
        uint8_t buf[4096];
        uint32_t tot = 0;
        while (sf.available()) {
            size_t r = sf.read(buf, 4096);
            esp_partition_write(rom_part, tot, buf, r);
            tot += r;
        }
        Serial.println("[EMU] Copy done");
    }
    
    romlen = sz;
    sf.close();
    
    const void* map_ptr;
    esp_err_t err = esp_partition_mmap(rom_part, 0, rom_part->size, SPI_FLASH_MMAP_DATA, &map_ptr, &rom_mmap_handle);
    if (err != ESP_OK) {
        Serial.printf("[EMU] mmap failed: %d\n", err);
        return false;
    }
    mapped_rom = (const uint8_t*)map_ptr;
    
    return true;
}

void emu_close_rom() {
    if (mapped_rom) {
        spi_flash_munmap(rom_mmap_handle);
        mapped_rom = nullptr;
    }
    dac_output_disable(DAC_CHANNEL_2);
    pinMode(26, OUTPUT);
    digitalWrite(26, LOW);
    romlen=0;
}

bool emu_init(uint8_t*,uint32_t) {
    if(!mapped_rom||!romlen) return false;
    if(!cram) cram=(uint8_t*)malloc(MAXRAM); if(!cram) return false;
    memset(cram,0xFF,MAXRAM);
    if(!gb) gb=(struct gb_s*)malloc(sizeof(struct gb_s)); if(!gb) return false;
    memset(gb,0,sizeof(struct gb_s));
    enum gb_init_error_e r=gb_init(gb,gb_rom_read,gb_cram_r,gb_cram_w,gb_err,nullptr);
    if(r!=GB_INIT_NO_ERROR){Serial.printf("[EMU] init fail %d\n",(int)r);return false;}
    gb_init_lcd(gb,lcd_line);
    minigb_apu_audio_init(&apu_ctx);
    audio_init_hw();
    audio_head = audio_tail = 0;
    if(!audio_sync_sem) audio_sync_sem = xSemaphoreCreateCounting(2, 0);
    xSemaphoreTake(audio_sync_sem, 0); // clear
    fcnt=fpsc=cfps=0; fpst=millis();
    char t[17]={0}; for(int i=0;i<16;i++){char c=(char)mapped_rom[0x134+i];t[i]=(c>=32&&c<127)?c:0;}
    Serial.printf("[EMU] '%s' %uKB heap:%u\n",t,romlen/1024,ESP.getFreeHeap());
    return true;
}

void emu_run_frame() {
    gb->direct.joypad_bits.a=!(jpad&0x10); gb->direct.joypad_bits.b=!(jpad&0x20);
    gb->direct.joypad_bits.select=!(jpad&0x40); gb->direct.joypad_bits.start=!(jpad&0x80);
    gb->direct.joypad_bits.right=!(jpad&0x01); gb->direct.joypad_bits.left=!(jpad&0x02);
    gb->direct.joypad_bits.up=!(jpad&0x04); gb->direct.joypad_bits.down=!(jpad&0x08);
    gb_run_frame(gb); 
    display_end_frame();

    xSemaphoreTake(audio_sync_sem, portMAX_DELAY);

    fcnt++; fpsc++;
    uint32_t n=millis(); if(n-fpst>=1000){cfps=fpsc;fpsc=0;fpst=n;}
}

void emu_audio_task_step() {
    audio_sample_t audio_buffer[AUDIO_SAMPLES_TOTAL];
    minigb_apu_audio_callback(&apu_ctx, audio_buffer);
    
    while ((uint16_t)(audio_head - audio_tail) > AUDIO_BUF_SIZE - (AUDIO_SAMPLES_TOTAL / 2)) {
        vTaskDelay(1);
    }

    static int32_t prev_x = 0;
    static int32_t prev_y = 0;
    static int32_t lpf_y = 0;

    for (int i = 0; i < AUDIO_SAMPLES_TOTAL; i += 2) {
        int32_t x0 = (audio_buffer[i] + audio_buffer[i+1]) / 2;
        
        // Aggressive High-Pass Filter (restored to 100 to eliminate bass frequencies and prevent physical speaker distortion)
        int32_t y = (100 * (prev_y + x0 - prev_x)) / 256;
        prev_x = x0;
        prev_y = y;

        // Low-Pass Filter (removes harsh 32kHz DAC stair-step ringing / hiss)
        lpf_y = (lpf_y + y) / 2;

        // Scale to 8-bit. We use 1024 to compensate for the volume lost by the aggressive high-pass filter.
        int32_t mix = (lpf_y * emu_audio_volume) / 1024;

        // Digital noise gate: clamp micro-fluctuations to pure zero
        if (mix > -2 && mix < 2) mix = 0;

        int32_t out = mix + 128;
        if (out < 0) out = 0;
        if (out > 255) out = 255;
        
        audio_ring[audio_head & (AUDIO_BUF_SIZE - 1)] = (uint8_t)out;
        audio_head++;
    }
    xSemaphoreGive(audio_sync_sem);
}

void emu_set_joypad(uint8_t b){jpad=b;}
uint8_t* emu_get_cart_ram(uint32_t* s){uint_fast32_t r=0;gb_get_save_size_s(gb,&r);if(s)*s=(uint32_t)r;return cram;}
void emu_set_cart_ram(const uint8_t* d,uint32_t s){if(s>MAXRAM)s=MAXRAM;memcpy(cram,d,s);}
void emu_set_frame_skip(uint8_t s){fskip=s;}
uint8_t emu_get_frame_skip(){return fskip;}
uint32_t emu_get_fps(){return cfps;}
uint16_t* emu_get_line_buffer(){return lbuf;}
void emu_reset(){gb_reset(gb);fcnt=0;}
