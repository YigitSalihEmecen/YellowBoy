#include "ui_launcher.h"
#include "display.h"
#include "pcf_input.h"
#include "emulator_bridge.h"
#include "config.h"
#include <Arduino.h>

#define ITEMS_PP 5
#define ITEM_H   34
#define ITEM_Y0  44
#define ITEM_X   8

// Color Palette Macros
#define GB_BG_COLOR    0x9DC2    // Lightest Green/Yellow (#9bbc0f)
#define GB_LIGHT_COLOR 0x8D62    // Light Green (#8bac0f)
#define GB_DARK_COLOR  0x3306    // Dark Green (#306230)
#define GB_TEXT_COLOR  0x11C2    // Darkest Green (#0f380f)

// ─── Helpers ────────────────────────────────────────────────────────────────
#include <driver/dac.h>

static void ui_beep(int freq, int duration) {
    dac_output_disable(DAC_CHANNEL_2);
    pinMode(26, OUTPUT);
    
    // Use a software loop to generate the tone! 
    // This entirely avoids LEDC timers, fixing the bug where the screen backlight dimmed!
    uint32_t period = 1000000 / freq;
    uint32_t end_time = millis() + duration;
    
    while (millis() < end_time) {
        digitalWrite(26, HIGH);
        delayMicroseconds(10); // 10us HIGH pulse is very short (extremely low volume)
        digitalWrite(26, LOW);
        delayMicroseconds(period - 10);
    }
}

static void wait_release() { 
    while(pcf_get_buttons() != 0) {
        pcf_update();
        delay(10);
    } 
    delay(100); 
}

static void draw_header(const char* t) {
    tft.fillRect(0,0,320,36,GB_TEXT_COLOR);
    tft.fillRect(0,36,320,2,GB_DARK_COLOR);
    
    tft.setTextColor(GB_BG_COLOR, GB_TEXT_COLOR); 
    tft.setTextDatum(ML_DATUM);
    tft.drawString("YellowBoy -by yigit-",10,18,2);
    
    tft.setTextDatum(MR_DATUM); 
    tft.setTextColor(GB_LIGHT_COLOR, GB_TEXT_COLOR);
    tft.drawString(t,310,18,1);
}

// ─── ROM List ───────────────────────────────────────────────────────────────
static void draw_list(RomEntry* r, int cnt, int pg, int sel) {
    int s = pg*ITEMS_PP, e = min(s+ITEMS_PP, cnt);
    tft.fillRect(0,38,320,202,GB_BG_COLOR);

    for (int i=s; i<e; i++) {
        int y = ITEM_Y0 + (i-s)*ITEM_H;
        bool is_sel = (i==sel);
        uint16_t bg = is_sel ? GB_TEXT_COLOR : GB_BG_COLOR;
        uint16_t fg = is_sel ? GB_BG_COLOR : GB_TEXT_COLOR;
        
        tft.fillRect(ITEM_X,y,304,ITEM_H-4,bg);
        tft.drawRect(ITEM_X,y,304,ITEM_H-4,GB_TEXT_COLOR);

        if (is_sel) {
            tft.fillRect(ITEM_X-6,y+6,6,18,GB_TEXT_COLOR);
        }

        // Badge
        uint16_t bc = r[i].is_gbc ? GB_TEXT_COLOR : GB_LIGHT_COLOR;
        uint16_t btxt = r[i].is_gbc ? GB_BG_COLOR : GB_TEXT_COLOR;
        const char* bt = r[i].is_gbc ? "C" : "G";
        tft.fillRect(ITEM_X+3,y+5,16,18,bc);
        tft.drawRect(ITEM_X+3,y+5,16,18,GB_TEXT_COLOR);
        
        tft.setTextColor(btxt,bc); tft.setTextDatum(MC_DATUM);
        tft.drawString(bt,ITEM_X+11,y+14,2);

        // Name (truncated, readable)
        char nm[30]; strncpy(nm,r[i].filename,28); nm[28]=0;
        char* dot=strrchr(nm,'.'); if(dot)*dot=0;
        tft.setTextColor(fg,bg); tft.setTextDatum(ML_DATUM);
        tft.drawString(nm,ITEM_X+26,y+ITEM_H/2-2,2);

        // Size
        char sz[12]; snprintf(sz,12,"%uK",r[i].size/1024);
        tft.setTextColor(is_sel ? GB_LIGHT_COLOR : GB_DARK_COLOR,bg); tft.setTextDatum(MR_DATUM);
        tft.drawString(sz,308,y+ITEM_H/2-2,1);
    }

    // Nav bar
    tft.fillRect(0,SCREEN_H-22,320,2,GB_DARK_COLOR);
    tft.fillRect(0,SCREEN_H-20,320,20,GB_TEXT_COLOR);
    int tp = (cnt+ITEMS_PP-1)/ITEMS_PP;
    if (tp>1) {
        tft.setTextColor(GB_BG_COLOR,GB_TEXT_COLOR); tft.setTextDatum(MC_DATUM);
        char ps[16]; snprintf(ps,16,"< %d/%d >",pg+1,tp);
        tft.drawString(ps,160,SCREEN_H-10,2);
    }
}

int launcher_show(RomEntry* roms, int cnt) {
    int pg=0, sel=0;
    tft.fillScreen(GB_BG_COLOR);
    draw_header("ROM LIST");

    if (cnt==0) {
        tft.setTextDatum(MC_DATUM);
        tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); tft.drawString("No ROMs found!",160,80,2);
        tft.setTextColor(GB_DARK_COLOR, GB_BG_COLOR); tft.drawString("Put .gb files in /roms/gb/",160,120,2);
        tft.drawString("on your SD card",160,140,2);
        while(true) delay(1000);
    }

    draw_list(roms,cnt,pg,sel);
    wait_release();

    while (true) {
        pcf_update();
        uint16_t b = pcf_get_buttons();
        if (b != 0) {
            if (b & GB_BTN_DOWN) {
                if (sel < cnt - 1) {
                    ui_beep(880, 20); // A5 (Cursor move)
                    sel++;
                    if (sel >= (pg + 1) * ITEMS_PP) { pg++; }
                    draw_list(roms,cnt,pg,sel);
                }
            } else if (b & GB_BTN_UP) {
                if (sel > 0) {
                    ui_beep(880, 20); // A5
                    sel--;
                    if (sel < pg * ITEMS_PP) { pg--; }
                    draw_list(roms,cnt,pg,sel);
                }
            } else if (b & GB_BTN_RIGHT) {
                int tp = (cnt+ITEMS_PP-1)/ITEMS_PP;
                if (pg < tp - 1) {
                    ui_beep(1046, 30); // C6 (Page flip)
                    pg++; sel = pg * ITEMS_PP;
                    draw_list(roms,cnt,pg,sel);
                }
            } else if (b & GB_BTN_LEFT) {
                if (pg > 0) {
                    ui_beep(1046, 30); // C6
                    pg--; sel = pg * ITEMS_PP;
                    draw_list(roms,cnt,pg,sel);
                }
            } else if (b & GB_BTN_A) {
                ui_beep(1760, 60); // A6 (Select / Confirm)
                wait_release();
                return sel;
            } else if (b & GB_BTN_B) {
                ui_beep(440, 60); // A4 (Back / Cancel)
                // Do nothing for ROM list
            }
            wait_release(); // basic debounce
        }
        delay(20);
    }
}

// ─── In-game menu ───────────────────────────────────────────────────────────
static void mbtn(int y, const char* t, bool hl) {
    uint16_t bg = hl ? GB_TEXT_COLOR : GB_BG_COLOR;
    uint16_t fg = hl ? GB_BG_COLOR : GB_TEXT_COLOR;
    tft.fillRect(65,y,190,26,bg);
    tft.drawRect(65,y,190,26,GB_TEXT_COLOR);
    if (hl) {
        tft.fillRect(59,y+4,6,18,GB_TEXT_COLOR);
    }
    tft.setTextColor(fg,bg); tft.setTextDatum(MC_DATUM);
    tft.drawString(t,160,y+13,2);
}

int launcher_ingame_menu() {
    tft.fillRect(45,10,230,220,GB_BG_COLOR);
    tft.drawRect(45,10,230,220,GB_TEXT_COLOR);
    tft.drawRect(46,11,228,218,GB_TEXT_COLOR); // thick border
    
    tft.setTextColor(GB_TEXT_COLOR,GB_BG_COLOR); tft.setTextDatum(MC_DATUM);
    tft.drawString("PAUSED",160,28,4);

    #define MI 5
    int yp[MI]={48,78,108,138,168};
    const char* lb[MI]={"Resume","Save Game","Load Save","Settings","Quit"};
    
    int hl = 0;
    for(int i=0;i<MI;i++) mbtn(yp[i],lb[i],(i==hl));
    wait_release();

    while(true) {
        pcf_update();
        uint16_t b = pcf_get_buttons();
        if (b != 0) {
            if (b & GB_BTN_DOWN) {
                ui_beep(880, 20);
                mbtn(yp[hl],lb[hl],false);
                tft.fillRect(59,yp[hl]+4,6,18,GB_BG_COLOR); // erase
                hl = (hl + 1) % MI;
                mbtn(yp[hl],lb[hl],true);
            } else if (b & GB_BTN_UP) {
                ui_beep(880, 20);
                mbtn(yp[hl],lb[hl],false);
                tft.fillRect(59,yp[hl]+4,6,18,GB_BG_COLOR); // erase
                hl = (hl + MI - 1) % MI;
                mbtn(yp[hl],lb[hl],true);
            } else if (b & GB_BTN_A) {
                ui_beep(1760, 60);
                wait_release();
                // 0=resume 1=save 2=load 3=settings 4=quit
                switch(hl){case 0:return 0;case 1:return 1;case 2:return 2;case 3:return 4;case 4:return 3;}
            } else if (b & GB_BTN_B) {
                ui_beep(440, 60);
                wait_release();
                return 0; // resume
            }
            wait_release();
        }
        delay(15);
    }
}

// ─── Settings menu ──────────────────────────────────────────────────────────
void launcher_settings_menu() {
    uint8_t pal = emu_get_palette();
    uint8_t fs = emu_get_frame_skip();
    uint8_t bl = 255; // brightness
    uint8_t vol = emu_audio_volume; // volume
    
    int hl = 0; // 0=pal, 1=fs, 2=bl, 3=vol, 4=done

    auto draw_settings = [&]() {
        tft.fillScreen(GB_BG_COLOR);
        tft.setTextDatum(MC_DATUM);

        // Palette
        tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); tft.drawString("Color Palette:",160,16,2);
        uint16_t bg0 = hl==0 ? GB_TEXT_COLOR : GB_BG_COLOR;
        uint16_t fg0 = hl==0 ? GB_BG_COLOR : GB_TEXT_COLOR;
        tft.fillRect(40,26,240,24, bg0);
        tft.drawRect(40,26,240,24, GB_TEXT_COLOR);
        char palstr[40]; snprintf(palstr,40,"%d/%d %s",pal+1,NUM_PALETTES,emu_get_palette_name(pal));
        tft.setTextColor(fg0, bg0);
        tft.drawString(palstr,160,38,2);
        if(hl==0){ tft.fillRect(34,26+3,6,18,GB_TEXT_COLOR); }
        tft.setTextDatum(ML_DATUM); tft.drawString("<",48,38,2);
        tft.setTextDatum(MR_DATUM); tft.drawString(">",272,38,2);

        // Frame skip
        tft.setTextDatum(MC_DATUM);
        tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); tft.drawString("Frame Skip:",160,60,2);
        uint16_t bg1 = hl==1 ? GB_TEXT_COLOR : GB_BG_COLOR;
        uint16_t fg1 = hl==1 ? GB_BG_COLOR : GB_TEXT_COLOR;
        tft.fillRect(40,70,240,24, bg1);
        tft.drawRect(40,70,240,24, GB_TEXT_COLOR);
        char fss[16]; snprintf(fss,16,"%d (FPS ~%d)",fs, fs==0?60:60/(fs+1));
        tft.setTextColor(fg1, bg1); tft.drawString(fss,160,82,2);
        if(hl==1){ tft.fillRect(34,70+3,6,18,GB_TEXT_COLOR); }
        tft.setTextDatum(ML_DATUM); tft.drawString("<",50,82,2);
        tft.setTextDatum(MR_DATUM); tft.drawString(">",270,82,2);

        // Brightness
        tft.setTextDatum(MC_DATUM);
        tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); tft.drawString("Brightness:",160,104,2);
        uint16_t bg2 = hl==2 ? GB_TEXT_COLOR : GB_BG_COLOR;
        uint16_t fg2 = hl==2 ? GB_BG_COLOR : GB_TEXT_COLOR;
        tft.fillRect(40,114,240,24, bg2);
        tft.drawRect(40,114,240,24, GB_TEXT_COLOR);
        char bls[16]; snprintf(bls,16,"%d%%",bl*100/255);
        tft.setTextColor(fg2, bg2); tft.drawString(bls,160,126,2);
        if(hl==2){ tft.fillRect(34,114+3,6,18,GB_TEXT_COLOR); }
        tft.setTextDatum(ML_DATUM); tft.drawString("<",50,126,2);
        tft.setTextDatum(MR_DATUM); tft.drawString(">",270,126,2);

        // Volume
        tft.setTextDatum(MC_DATUM);
        tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); tft.drawString("Volume:",160,148,2);
        uint16_t bg3 = hl==3 ? GB_TEXT_COLOR : GB_BG_COLOR;
        uint16_t fg3 = hl==3 ? GB_BG_COLOR : GB_TEXT_COLOR;
        tft.fillRect(40,158,240,24, bg3);
        tft.drawRect(40,158,240,24, GB_TEXT_COLOR);
        char vols[16]; snprintf(vols,16,"%d",vol);
        tft.setTextColor(fg3, bg3); tft.drawString(vols,160,170,2);
        if(hl==3){ tft.fillRect(34,158+3,6,18,GB_TEXT_COLOR); }
        tft.setTextDatum(ML_DATUM); tft.drawString("<",50,170,2);
        tft.setTextDatum(MR_DATUM); tft.drawString(">",270,170,2);

        // Done button
        uint16_t bg4 = hl==4 ? GB_TEXT_COLOR : GB_BG_COLOR;
        uint16_t fg4 = hl==4 ? GB_BG_COLOR : GB_TEXT_COLOR;
        tft.fillRect(100,200,120,24, bg4);
        tft.drawRect(100,200,120,24, GB_TEXT_COLOR);
        if(hl==4){ tft.fillRect(94,200+3,6,18,GB_TEXT_COLOR); }
        tft.setTextColor(fg4, bg4); tft.setTextDatum(MC_DATUM);
        tft.drawString("DONE",160,212,2);
    };

    draw_settings();
    wait_release();

    while(true) {
        pcf_update();
        uint16_t b = pcf_get_buttons();
        if (b != 0) {
            bool changed = false;
            if (b & GB_BTN_DOWN) {
                ui_beep(880, 20);
                hl = (hl + 1) % 5;
                changed = true;
            } else if (b & GB_BTN_UP) {
                ui_beep(880, 20);
                hl = (hl + 4) % 5;
                changed = true;
            } else if (b & GB_BTN_LEFT) {
                if (hl == 0) { pal = (pal+NUM_PALETTES-1)%NUM_PALETTES; changed=true; ui_beep(1046, 20); }
                else if (hl == 1 && fs>0) { fs--; changed=true; ui_beep(1046, 20); }
                else if (hl == 2 && bl>30) { bl-=25; changed=true; ui_beep(1046, 20); }
                else if (hl == 3 && vol>0) { vol--; changed=true; ui_beep(1046, 20); }
            } else if (b & GB_BTN_RIGHT) {
                if (hl == 0) { pal = (pal+1)%NUM_PALETTES; changed=true; ui_beep(1318, 20); }
                else if (hl == 1 && fs<4) { fs++; changed=true; ui_beep(1318, 20); }
                else if (hl == 2 && bl<255) { bl=min(255,bl+25); changed=true; ui_beep(1318, 20); }
                else if (hl == 3 && vol<10) { vol++; changed=true; ui_beep(1318, 20); }
            } else if (b & GB_BTN_A) {
                if (hl == 4) {
                    ui_beep(1760, 60);
                    emu_set_palette(pal);
                    emu_set_frame_skip(fs);
                    display_set_backlight(bl);
                    emu_audio_volume = vol;
                    pcf_save_settings(pal, fs, bl, vol);
                    wait_release();
                    return;
                }
            } else if (b & GB_BTN_B) {
                ui_beep(440, 60);
                wait_release();
                return;
            }

            if (changed) {
                emu_set_palette(pal);
                emu_set_frame_skip(fs);
                display_set_backlight(bl);
                draw_settings();
            }
            wait_release();
        }
        delay(20);
    }
}

// ─── Mapping Screen ─────────────────────────────────────────────────────────
void launcher_mapping_screen() {
    tft.fillScreen(GB_BG_COLOR);
    tft.setTextDatum(MC_DATUM);
    tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR); 
    tft.drawString("Button Mapping", 160, 40, 4);

    const char* btn_names[8] = {"UP", "DOWN", "LEFT", "RIGHT", "A", "B", "START", "SELECT"};
    uint8_t new_map[8];

    while (pcf_get_raw_state() != 0xFF) delay(10);
    delay(200);

    for (int i = 0; i < 8; i++) {
        tft.fillRect(0, 100, 320, 100, GB_BG_COLOR);
        tft.setTextColor(GB_DARK_COLOR, GB_BG_COLOR);
        tft.drawString("Press button for:", 160, 120, 2);
        tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR);
        tft.drawString(btn_names[i], 160, 160, 4);

        int pressed_bit = -1;
        while (pressed_bit == -1) {
            uint8_t raw = pcf_get_raw_state();
            if (raw != 0xFF) {
                for (int b = 0; b < 8; b++) {
                    if (!(raw & (1 << b))) {
                        bool used = false;
                        for (int j = 0; j < i; j++) {
                            if (new_map[j] == b) used = true;
                        }
                        if (!used) {
                            pressed_bit = b;
                            break;
                        }
                    }
                }
            }
            delay(10);
        }

        new_map[i] = pressed_bit;

        while (pcf_get_raw_state() != 0xFF) delay(10);
        delay(100);
    }

    tft.fillRect(0, 100, 320, 100, GB_BG_COLOR);
    tft.setTextColor(GB_TEXT_COLOR, GB_BG_COLOR);
    tft.drawString("Mapping Saved!", 160, 140, 4);
    
    memcpy(pcf_btn_map, new_map, 8);
    pcf_save_mapping();
    
    delay(1000);
}
