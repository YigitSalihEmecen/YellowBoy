#include "display.h"
#include "hw_config.h"
#include <Arduino.h>
#include "emulator_bridge.h"

TFT_eSPI tft = TFT_eSPI();
#define MAX_BUFFER_LINES 16
static uint16_t* dma_buf[2];
static int dma_active = 0;
static uint8_t x_map[320];

struct gb_line_msg {
    uint8_t line_y;
    uint8_t data[GB_SCREEN_W];
};
static QueueHandle_t line_queue = NULL;
static SemaphoreHandle_t render_sem = NULL;

static uint16_t current_palette[4] = {0xFFFF, 0xAD55, 0x52AA, 0x0000}; // Default White-to-Black

void display_render_task(void* arg) {
    int local_buffered_lines = 0;
    int local_start_y = 0;

    while (true) {
        struct gb_line_msg msg;
        if (xQueueReceive(line_queue, &msg, portMAX_DELAY) == pdTRUE) {
            uint8_t* src_line = msg.data;
            int y = msg.line_y;

            if (y == 0) {
                tft.startWrite(); // Assert CS for the whole frame
            }

            int y0 = y * GAME_H / GB_SCREEN_H;
            int y1 = (y+1) * GAME_H / GB_SCREEN_H;
            if (y1 == y0) y1 = y0 + 1;

            for (int sy = y0; sy < y1 && sy < GAME_H; sy++) {
                uint16_t* dest_row = &dma_buf[dma_active][local_buffered_lines * GAME_W];
                for (int x = 0; x < GAME_W; x++) {
                    dest_row[x] = current_palette[src_line[x_map[x]] & 3];
                }
                local_buffered_lines++;

                if (local_buffered_lines == MAX_BUFFER_LINES || (y == GB_SCREEN_H - 1 && sy == y1 - 1)) {
                    tft.dmaWait(); // Wait for previous DMA to finish before sending next
                    tft.pushImageDMA(OFFSET_X, OFFSET_Y + local_start_y, GAME_W, local_buffered_lines, dma_buf[dma_active]);
                    
                    dma_active = 1 - dma_active;
                    local_start_y += local_buffered_lines;
                    local_buffered_lines = 0;
                }
            }
            if (y == GB_SCREEN_H - 1) {
                tft.dmaWait();
                tft.endWrite(); // Release CS at the end of the frame
                local_start_y = 0;
                xSemaphoreGive(render_sem);
            }
        }
    }
}

void display_init() {
    pinMode(TFT_PIN_BL, OUTPUT);
    digitalWrite(TFT_PIN_BL, HIGH);
    tft.init();
    tft.initDMA();
    tft.setRotation(1);
    tft.invertDisplay(true);
    tft.fillScreen(TFT_BLACK);
    ledcSetup(1, 5000, 8);
    ledcAttachPin(TFT_PIN_BL, 1);
    ledcWrite(1, 255);
    
    for (int i = 0; i < GAME_W; i++) {
        x_map[i] = i * GB_SCREEN_W / GAME_W;
    }
    
    dma_buf[0] = (uint16_t*)heap_caps_malloc(GAME_W * MAX_BUFFER_LINES * 2, MALLOC_CAP_DMA);
    dma_buf[1] = (uint16_t*)heap_caps_malloc(GAME_W * MAX_BUFFER_LINES * 2, MALLOC_CAP_DMA);
    
    line_queue = xQueueCreate(32, sizeof(struct gb_line_msg));
    render_sem = xSemaphoreCreateBinary();
    xTaskCreatePinnedToCore(display_render_task, "render", 4096, NULL, 3, NULL, 0); // Core 0

    Serial.printf("[TFT] %dx%d OK\n", tft.width(), tft.height());
}

void display_set_backlight(uint8_t level) {
    ledcWrite(1, level);
}

void display_set_palette(const uint16_t* pal) {
    memcpy(current_palette, pal, sizeof(current_palette));
}

void display_clear(uint16_t color) { tft.fillScreen(color); }

void display_push_gb_line(uint8_t y, uint8_t* buf) {
    if (y >= GB_SCREEN_H) return;
    struct gb_line_msg msg;
    msg.line_y = y;
    memcpy(msg.data, buf, GB_SCREEN_W);
    xQueueSend(line_queue, &msg, portMAX_DELAY);
}

void display_wait_idle() {
    if (line_queue) {
        while (uxQueueMessagesWaiting(line_queue) > 0) {
            delay(1);
        }
    }
    delay(5); // Give render task a moment to block on xQueueReceive
    tft.dmaWait(); // Ensure hardware DMA is finished
}

void display_end_frame() {
    // handled inside Core 0 task (giving semaphore)
}
