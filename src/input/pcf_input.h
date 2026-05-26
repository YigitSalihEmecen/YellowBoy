#pragma once
#include <stdint.h>
#include <stdbool.h>

#define GB_BTN_RIGHT   0x01
#define GB_BTN_LEFT    0x02
#define GB_BTN_UP      0x04
#define GB_BTN_DOWN    0x08
#define GB_BTN_A       0x10
#define GB_BTN_B       0x20
#define GB_BTN_SELECT  0x40
#define GB_BTN_START   0x80
#define GB_BTN_MENU    0x100

void pcf_init();
void pcf_update();
uint16_t pcf_get_buttons();
bool pcf_is_pressed(uint16_t btn_mask);
uint8_t pcf_get_raw_state();
extern uint8_t pcf_btn_map[8];

// Settings persistence (NVS)
void pcf_save_settings(uint8_t palette, uint8_t fskip, uint8_t brightness, uint8_t vol);
void pcf_save_mapping();
bool pcf_load_settings(uint8_t* palette, uint8_t* fskip, uint8_t* brightness, uint8_t* vol);
