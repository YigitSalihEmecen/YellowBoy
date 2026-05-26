#pragma once
#include <stdint.h>

// ─── Pins ───────────────────────────────────────────────────────────────────
#define TFT_PIN_BL     21
#define SCREEN_W       320
#define SCREEN_H       240

#define PCF_SDA_PIN    22
#define PCF_SCL_PIN    27
#define PCF_I2C_ADDR   0x20

#define SD_PIN_CS 5
#define SD_PIN_MOSI 23
#define SD_PIN_MISO 19
#define SD_PIN_SCK 18

#define LED_R_PIN 4
#define LED_G_PIN 16
#define LED_B_PIN 17

// ─── GameBoy ────────────────────────────────────────────────────────────────
#define GB_SCREEN_W 160
#define GB_SCREEN_H 144

// Max scale keeping 10:9 ratio on 320x240 display -> 266x240
#define GAME_W 266
#define GAME_H 240
#define OFFSET_X ((SCREEN_W - GAME_W) / 2)
#define OFFSET_Y ((SCREEN_H - GAME_H) / 2)
