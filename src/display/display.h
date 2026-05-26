#pragma once
#include <TFT_eSPI.h>
extern TFT_eSPI tft;

void display_init();
void display_set_backlight(uint8_t level);
void display_set_palette(const uint16_t* pal);
void display_clear(uint16_t color = TFT_BLACK);
void display_push_gb_line(uint8_t line_y, uint8_t* buf160);
void display_end_frame();
void display_wait_idle();
