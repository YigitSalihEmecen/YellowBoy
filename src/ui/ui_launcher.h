#pragma once
#include "sd_manager.h"

int launcher_show(RomEntry* roms, int count);
int launcher_ingame_menu();   // 0=resume 1=save 2=load 3=quit 4=calibrate 5=settings
void launcher_settings_menu(); // palette, frameskip, brightness
void launcher_mapping_screen();

// Color Palette Macros
#define GB_BG_COLOR    0x9DC2    // Lightest Green/Yellow (#9bbc0f)
#define GB_LIGHT_COLOR 0x8D62    // Light Green (#8bac0f)
#define GB_DARK_COLOR  0x3306    // Dark Green (#306230)
#define GB_TEXT_COLOR  0x11C2    // Darkest Green (#0f380f)
