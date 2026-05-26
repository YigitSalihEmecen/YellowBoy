#include "pcf_input.h"
#include "config.h"
#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>

static Preferences prefs;
static uint16_t cur_btns = 0;
static uint32_t last_ms = 0;
uint8_t pcf_btn_map[8] = {7, 5, 6, 4, 0, 2, 1, 3};

void pcf_init() {
    Wire.begin(PCF_SDA_PIN, PCF_SCL_PIN);
    Serial.printf("[PCF] Init I2C SDA=%d SCL=%d Addr=0x%02X\n", PCF_SDA_PIN, PCF_SCL_PIN, PCF_I2C_ADDR);
}

void pcf_update() {
    uint32_t now = millis();
    if (now - last_ms < 14) return;
    last_ms = now;

    Wire.requestFrom((uint16_t)PCF_I2C_ADDR, (uint8_t)1, true);
    if (Wire.available()) {
        uint8_t val = Wire.read();
        uint16_t b = 0;
        
        // Active low: bit is 0 when button is pressed
        if (!(val & (1 << pcf_btn_map[0]))) b |= GB_BTN_UP;
        if (!(val & (1 << pcf_btn_map[1]))) b |= GB_BTN_DOWN;
        if (!(val & (1 << pcf_btn_map[2]))) b |= GB_BTN_LEFT;
        if (!(val & (1 << pcf_btn_map[3]))) b |= GB_BTN_RIGHT;
        if (!(val & (1 << pcf_btn_map[4]))) b |= GB_BTN_A;
        if (!(val & (1 << pcf_btn_map[5]))) b |= GB_BTN_B;
        if (!(val & (1 << pcf_btn_map[6]))) b |= GB_BTN_START;
        if (!(val & (1 << pcf_btn_map[7]))) b |= GB_BTN_SELECT;

        // Combo for MENU (Start + Select)
        if ((b & GB_BTN_START) && (b & GB_BTN_SELECT)) {
            b |= GB_BTN_MENU;
        }

        cur_btns = b;
    }
}

uint8_t pcf_get_raw_state() {
    Wire.requestFrom((uint16_t)PCF_I2C_ADDR, (uint8_t)1, true);
    if (Wire.available()) return Wire.read();
    return 0xFF;
}

uint16_t pcf_get_buttons() {
    return cur_btns;
}

bool pcf_is_pressed(uint16_t btn_mask) {
    return (cur_btns & btn_mask) != 0;
}

// ─── Settings NVS ───────────────────────────────────────────────────────────
void pcf_save_settings(uint8_t palette, uint8_t fskip, uint8_t brightness, uint8_t vol) {
    Preferences prefs;
    prefs.begin("cydgb", false);
    prefs.putUChar("pal", palette);
    prefs.putUChar("fs", fskip);
    prefs.putUChar("bl", brightness);
    prefs.putUChar("vol", vol);
    prefs.putBytes("bmap", pcf_btn_map, 8);
    prefs.end();
}

void pcf_save_mapping() {
    Preferences prefs;
    prefs.begin("cydgb", false);
    prefs.putBytes("bmap", pcf_btn_map, 8);
    prefs.end();
}

bool pcf_load_settings(uint8_t* palette, uint8_t* fskip, uint8_t* brightness, uint8_t* vol) {
    Preferences prefs;
    prefs.begin("cydgb", true);
    if (!prefs.isKey("pal")) {
        prefs.end();
        return false;
    }
    *palette = prefs.getUChar("pal", 0);
    *fskip = prefs.getUChar("fs", 0);
    *brightness = prefs.getUChar("bl", 255);
    *vol = prefs.getUChar("vol", 10);
    
    if (prefs.isKey("bmap")) {
        prefs.getBytes("bmap", pcf_btn_map, 8);
    } else {
        prefs.end();
        return false;
    }
    prefs.end();
    return true;
}
