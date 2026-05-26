# YellowBoy

A high-performance Game Boy emulator built for the ESP32 Cheap Yellow Display (CYD) board, featuring a custom I2C physical controller, true analog audio, and a pixel-perfect retro aesthetic.

Mainly made for my hardware project "YellowBoy" which is a handheld game console. It will be released as an open source project on YouTube. Still work in progress like this emulator.

Designed to not need PSRAM.

## Hardware Specs
- **Board:** ESP32-2432S028R (Cheap Yellow Display / CYD)
- **Controller:** Custom physical controller wired via I2C utilizing a PCF8574 GPIO expander.
- **Audio:** Outputs True Analog Audio via the ESP32's DAC (GPIO 26) with a built-in digital high-pass filter.

## Features
- **Dynamic Button Mapping:** On the very first boot, the device will prompt you to press your physical controller buttons in order (Up, Down, Left, Right, A, B, Start, Select) to dynamically map them to the emulator and save the mapping to the internal flash memory.
- **SD Card ROM Loading:** Automatically parses and loads `.gb` and `.gbc` ROM files from a FAT32 formatted MicroSD card.
- **Persistent Settings:** Saves your Volume, Brightness, Frame Skip, and retro Color Palette preferences across reboots.

## Quick Setup
1. Open the project in PlatformIO.
2. Connect your CYD via USB and choose flash the device.
3. Insert your FAT32 SD card with ROMs and play!

## Tested Games
1. Super Mario Land 
2. Super Mario Land 2: 6 golden coins
3. Batman - The Animated Series
4. Castlevania Legends
5. Tetris 
6. Tetris 2
7. Donkey Kong Land 2 
8. Donkey Kong Land 3
9. Legend of Zelda: Link's Awakening
10. Final Fantasy Adventure
11. Metroid II: Return of Samus

## Credits
This project relies heavily on the incredible work of:
- [Peanut-GB](https://github.com/deltabeard/Peanut-GB) by deltabeard (Core Emulator Engine)
- [minigb_apu](https://github.com/deltabeard/minigb_apu) by deltabeard (Audio Processing Unit)
