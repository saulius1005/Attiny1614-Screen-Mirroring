/*
 * Screen.c
 *
 * Created: 2024-10-01 10:17:37
 *  Author: Saulius
 *
 *
 * 2024-10-09: Fixed screen_draw_image function
 *
 *
 *
 *
 */ 
#include "Settings.h"
#include "font.h"

void screen_command(uint8_t add, uint8_t cmd) {
	WriteToReg(add, 0x00, cmd);
}

void screen_data(uint8_t add, uint8_t data) {
	WriteToReg(add, 0x40, data);
}

void screen_init(uint8_t driver){ //0-SSD1306 1-ST7567S //default SSD1306
	if(driver == 1){ //ST767S
		for (uint8_t i=0; i<10; i++){
				screen_command(ST7567S_ADD, st7567sCommands[i]);
		}		
	}
	else //SSD1306
	{
		for (uint8_t i=0; i<25; i++){
			screen_command(SSD1306_ADD, ssd1306Commands[i]);
		}
	}
}

void screen_draw_image(uint8_t mode, uint8_t driver, const uint8_t *image_data) {
    uint8_t page_count, screen_width, add;

    // Pasirinkite valdiklio tipus
    if(driver == 1){
        page_count = ST7567S_PAGE_COUNT;
        screen_width = ST7567S_SCREEN_WIDTH;
        add = ST7567S_ADD;
    } else {
        page_count = SSD1306_PAGE_COUNT;
        screen_width = SSD1306_SCREEN_WIDTH;
        add = SSD1306_ADD;
    }

    // Paveikslëlio rodymas
    for (uint8_t page = 0; page <= page_count; page++) {
        screen_command(add, 0xB0 + page);  // Set page address
        screen_command(add, 0x00);  // Set lower column address
        screen_command(add, 0x10);  // Set higher column address
        uint16_t page_offset = 7-page;
        for (uint8_t col = 0; col < screen_width; col++) {
	        uint16_t index = col * 8 + page_offset;
	        uint8_t data=0;
	        if (mode == 0) {
		        data = pgm_read_byte(&image_data[index]);  // Skaityti ið pgm atminties
		        } else {
		        data = image_data[index];  // Skaityti tiesiogiai ið atminties
	        }
            screen_data(add, data);
        }
    }
}


void screen_draw_char(uint8_t add, char c) {
	if (c < 32 || c > 127) {
		c = 32; // Jei simbolis nëra palaikomas, naudokite tarpà
	}

	for (uint8_t i = 0; i < 5; i++) {
		uint8_t line = font[c - 32][i]; // Atitinkamas ðrifto duomenø baitas
		screen_data(add, line);
	}
	screen_data(add, 0x00); // Tarpas tarp simboliø
}

void screen_draw_text(uint8_t add, const char *text) {
	while (*text) {
		screen_draw_char(add, *text);
		text++;
	}
}

void screen_write_text(uint8_t driver, const char *text, uint8_t line, uint8_t start_pixel) {
	uint8_t add = SSD1306_ADD;
	if(driver == 1)
		add = ST7567S_ADD;
	screen_command(add, 0xB0 | line);
	screen_command(add, 0x10 | (start_pixel >> 4));
	screen_command(add, 0x00 | (start_pixel & 0x0F));
	screen_draw_text(add, text);
}

void screen_contrast(uint8_t contrast){// contrast for LCD only (ST767S)
	uint8_t add = ST7567S_ADD;
	if(contrast > 0x3f) //ST767S have 63 level of contrast
		contrast = 0x3f;
	screen_command(add, 0x81); //contrast register
	screen_command(add, contrast); //contrast value

}

void screen_clear(uint8_t driver) {
	uint8_t add = SSD1306_ADD;
	if(driver == 1){
		add = ST7567S_ADD;
	}
	for (int page = 0; page < 8; page++) { 
		screen_command(add, 0xB0 + page);
		screen_command(add, 0x00);
		screen_command(add, 0x10);
		
		for (int column = 0; column < 128; column++) {
			screen_data(add, 0x00);
		}
	}
	if(driver == 1){
		screen_contrast(ST7567S_CONTRAST);
	}
}