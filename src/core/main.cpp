#include <Arduino.h>
#include "config.h"
#include "display.h"
#include "pcf_input.h"
#include "sd_manager.h"
#include "ui_launcher.h"
#include "emulator_bridge.h"
#include <driver/dac.h>

static RomEntry roms[64];
static int rcnt = 0;
static char cur_path[80] = {0};
static TaskHandle_t ttask = nullptr;
static TaskHandle_t audiotask = nullptr;
static volatile bool emu_on = false, menu_req = false;

void pcf_task(void* p) {
    (void)p;
    for(;;) {
        pcf_update();
        if (emu_on) {
            uint16_t b = pcf_get_buttons();
            if (b & GB_BTN_MENU) menu_req = true;
            emu_set_joypad(b & 0xFF);
        }
        vTaskDelay(pdMS_TO_TICKS(12));
    }
}

void audio_task(void* p) {
    (void)p;
    for(;;) {
        if (emu_on && !menu_req) {
            emu_audio_task_step();
        } else {
            vTaskDelay(pdMS_TO_TICKS(10));
        }
    }
}

static void tt_start() {
    if(!ttask) xTaskCreatePinnedToCore(pcf_task,"t",4096,0,2,&ttask,0);
    else vTaskResume(ttask);
    if(!audiotask) xTaskCreatePinnedToCore(audio_task,"a",4096,0,2,&audiotask,0);
    else vTaskResume(audiotask);
}
static void tt_stop() { 
    if(ttask) vTaskSuspend(ttask); 
    if(audiotask) vTaskSuspend(audiotask);
}

static void save_ram() {
    if(!cur_path[0]) return;
    uint32_t sz=0; uint8_t* r=emu_get_cart_ram(&sz);
    if(sz>0) { sd_save_state(cur_path,r,sz); Serial.printf("[SAVE] %u bytes\n",sz); }
}
static void load_ram() {
    if(!cur_path[0]) return;
    uint32_t sz=0; emu_get_cart_ram(&sz);
    if(sz>0) { uint8_t* t=(uint8_t*)malloc(sz);
        if(t){if(sd_load_state(cur_path,t,sz))emu_set_cart_ram(t,sz);free(t);} }
}

// ─── Emulation loop ─────────────────────────────────────────────────────────
void run_emu() {
    emu_on = true; menu_req = false;
    tt_start();
    display_wait_idle();
    display_clear(TFT_BLACK);

    uint32_t ft=0;
    while(emu_on) {
        emu_run_frame();

        if (menu_req) {
            menu_req = false;
            tt_stop();
            display_wait_idle();

            int c = launcher_ingame_menu();
            switch(c) {
                case 0: break;  // resume
                case 1:  // save
                    save_ram();
                    display_wait_idle();
                    tft.fillRect(80,80,160,40,GB_BG_COLOR);
                    tft.drawRect(80,80,160,40,GB_TEXT_COLOR);
                    tft.setTextDatum(MC_DATUM); tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR);
                    tft.drawString("SAVED!",160,100,4);
                    delay(700);
                    break;
                case 2:  // load
                    load_ram(); emu_reset(); load_ram();
                    tft.fillRect(80,80,160,40,GB_BG_COLOR);
                    tft.drawRect(80,80,160,40,GB_TEXT_COLOR);
                    tft.setTextDatum(MC_DATUM); tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR);
                    tft.drawString("LOADED!",160,100,4);
                    delay(700);
                    break;
                case 3:  // quit
                    emu_on=false; save_ram(); tt_stop(); return;
                case 4:  // settings
                    launcher_settings_menu(); break;
            }
            display_clear(TFT_BLACK);
            dac_output_enable(DAC_CHANNEL_2);
            tt_start();
        }

        // FPS log
        uint32_t n=millis();
        if(n-ft>3000){ft=n;Serial.printf("[G] FPS:%u btn:0x%02X\n",emu_get_fps(),pcf_get_buttons());}
        taskYIELD();
    }
}

// ─── Setup ──────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200); delay(200);
    Serial.println("\n=== CYD-GB ===");
    pinMode(LED_R_PIN,OUTPUT); pinMode(LED_G_PIN,OUTPUT); pinMode(LED_B_PIN,OUTPUT);
    digitalWrite(LED_R_PIN,HIGH); digitalWrite(LED_G_PIN,HIGH); digitalWrite(LED_B_PIN,HIGH);

    // Explicitly ground the speaker pin to kill any static/hiss before UI or emulator starts
    pinMode(26, OUTPUT);
    digitalWrite(26, LOW);

    display_init();
    pcf_init();

    if(!sd_init()) {
        tft.fillScreen(GB_BG_COLOR); tft.setTextDatum(MC_DATUM);
        tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); 
        tft.drawString("SD Card Error!",160,100,4);
        tft.setTextColor(GB_DARK_COLOR, GB_BG_COLOR); 
        tft.drawString("Insert FAT32 SD & reset",160,140,2);
        while(true) delay(1000);
    }

    // Splash
    tft.fillScreen(GB_BG_COLOR); tft.setTextDatum(MC_DATUM);
    
    tft.fillRect(0, 0, 320, 16, GB_TEXT_COLOR);
    tft.fillRect(0, 224, 320, 16, GB_TEXT_COLOR);
    
    tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); 
    tft.setTextSize(2);
    tft.drawString("YellowBoy", 160, 100, 2);
    tft.setTextSize(1);
    tft.drawString("-by yigit-", 160, 130, 2);
    
    delay(1200);

    // Load saved settings from NVS
    uint8_t s_pal, s_fs, s_bl, s_vol;
    if (pcf_load_settings(&s_pal, &s_fs, &s_bl, &s_vol)) {
        emu_set_palette(s_pal);
        emu_set_frame_skip(s_fs);
        display_set_backlight(s_bl);
        emu_audio_volume = s_vol;
        Serial.printf("[INIT] Loaded settings: pal=%d fs=%d bl=%d vol=%d\n", s_pal, s_fs, s_bl, s_vol);
    } else {
        // Force button mapping on first boot
        launcher_mapping_screen();
        // Save initial defaults
        pcf_save_settings(0, 0, 255, 10);
    }

    Serial.printf("[INIT] Heap: %u\n",ESP.getFreeHeap());
}

// ─── Loop ───────────────────────────────────────────────────────────────────
void loop() {
    rcnt = sd_scan_roms(roms, 64);
    int sel = launcher_show(roms, rcnt);
    if(sel<0||sel>=rcnt) return;

    strncpy(cur_path,roms[sel].full_path,79);

    // Loading screen
    display_wait_idle();
    tft.fillScreen(GB_BG_COLOR); tft.setTextDatum(MC_DATUM);
    
    tft.fillRect(0, 0, 320, 16, GB_TEXT_COLOR);
    tft.fillRect(0, 224, 320, 16, GB_TEXT_COLOR);
    
    tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); 
    tft.setTextSize(2);
    tft.drawString("Loading...",160,100,2);
    tft.setTextSize(1);
    
    char nm[30]; strncpy(nm,roms[sel].filename,28); nm[28]=0;
    char* d=strrchr(nm,'.'); if(d)*d=0;
    
    tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); 
    tft.drawString(nm,160,140,2);

    if(!emu_open_rom(cur_path)){
        tft.setTextColor(TFT_RED); tft.drawString("Open failed!",160,170,2); delay(2000); return;
    }
    if(!emu_init(0,0)){
        tft.setTextColor(TFT_RED); tft.drawString("Init failed!",160,170,2); delay(2000); emu_close_rom(); return;
    }

    load_ram();
    emu_set_frame_skip(0);
    digitalWrite(LED_G_PIN,LOW);
    run_emu();
    digitalWrite(LED_G_PIN,HIGH);
    emu_close_rom();
}
