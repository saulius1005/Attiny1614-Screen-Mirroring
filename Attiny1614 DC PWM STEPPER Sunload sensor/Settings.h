/*
 * Settings.h
 *
 * Created: 2024-08-15 22:41:44
 *  Author: Saulius
 */ 

#ifndef SETTINGS_H_
#define SETTINGS_H_

#define F_CPU 20000000
#define TWI0_BAUD(F_SCL, T_RISE) ((((((float)F_CPU / (float)F_SCL)) - 10 - ((float)F_CPU * T_RISE / 1000000))) / 2) //I2C baud calculation
#define USART0_BAUD_RATE(BAUD_RATE) ((float)(F_CPU * 64 / (8 *(float)BAUD_RATE)) + 0.5) //USART baud calculation
#define W 0 //I2C write
#define R 1 //I2C read
#define NO_STOP 0 //for TranssmitByte() function
#define STOP 1 //for TranssmitByte() function

#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>
#include <string.h>
#include <avr/pgmspace.h>
#include "SSD1306.h"
#include "ST7567S.h"

extern const uint8_t font[96][5];
extern const uint8_t ssd1306Commands[25];
extern const uint8_t st7567sCommands[10];

struct Error{
	uint8_t Fault; //1-NACK ADD, 2-NACK Reading, 3-NACK Sending
}I2C;

void GPIO_init(); //Attiny1614 CPU speed and Pins settings

void USART0_init();
void USART0_sendChar(char c);
void USART0_sendString(char *str);
char USART0_readChar();

void DataReading();

void I2C_init(); //I2C settings
uint8_t TranssmitAdd(uint8_t Add, uint8_t Read);
void WriteToReg(uint8_t Add, uint8_t Reg, uint8_t Data);

void screen_init(uint8_t driver);
void screen_command(uint8_t add, uint8_t cmd);
void screen_data(uint8_t add, uint8_t cmd);
void screen_draw_image(uint8_t mode, uint8_t driver, const uint8_t *image_data);
void screen_draw_char(uint8_t add, char c);
void screen_draw_text(uint8_t add, const char *text);
void screen_write_text(uint8_t driver, const char *text, uint8_t line, uint8_t start_pixel);
void screen_clear(uint8_t driver);
void screen_contrast(uint8_t contrast);

#endif /* SETTINGS_H_ */