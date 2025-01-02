/*
 * SSD1306.h
 *
 * Created: 2024-08-17 00:14:20
 *  Author: Saulius
 *
 *
 * 2024-10-09: Fixed Screen size
 *
 *
 *
 */ 

#ifndef SSD1306_H_
#define SSD1306_H_

#define SSD1306_ADD 0x3c
#define SSD1306_SCREEN_WIDTH 128    // Ekrano plotis pikseliais
#define SSD1306_SCREEN_HEIGHT 64    // Ekrano aukðtis pikseliais (64 pikseliai = 8 puslapiø)
#define SSD1306_PAGE_COUNT (SSD1306_SCREEN_HEIGHT / 8) // Puslapiø skaièius

#endif /* SSD1306_H_ */