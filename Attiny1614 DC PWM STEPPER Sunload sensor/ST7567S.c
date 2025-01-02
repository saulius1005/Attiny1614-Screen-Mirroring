/*
 * ST7565.c
 *
 * Created: 2024-08-15 22:48:14
 *  Author: Saulius
 */ 
#include "Settings.h"
const uint8_t st7567sCommands[10]={
	0xe2,  // Software reset
	0x2f,  // Power control (rekomenduojama: Booster, Regulator ir Follower visi �jungti)
	0xa2,  // Bias voltage (1/9 bias)
	0xc8,  // Scan direction (C8 = nuo apa�ios � vir��)
	0xa0,  // Column address direction (A0 = �prasta, A1 = apversta)
	0x40,  // Start line address (40 = linija 0 prad�ioje)
	0x81,  // Kontrasto nustatymo komanda
	0x05,  // Kontrasto reik�m� (galite keisti pagal poreik� nuo 0x00 iki 0x3F)
	0xA6,  // Display normal (A6 = normalus vaizdas, A7 = apverstas vaizdas)
	0xaf   // Display ON (Ekranas �jungiamas)
};