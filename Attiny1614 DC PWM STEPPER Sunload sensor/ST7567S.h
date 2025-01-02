/*
 * ST7567S.h
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

#ifndef ST7567S_H_
#define ST7567S_H_

#define ST7567S_ADD 0x3f
#define ST7567S_SCREEN_WIDTH 128    // Ekrano plotis pikseliais
#define ST7567S_SCREEN_HEIGHT 64    // Ekrano aukðtis pikseliais (64 pikseliai = 8 puslapiø)
#define ST7567S_PAGE_COUNT (ST7567S_SCREEN_HEIGHT / 8) // Puslapiø skaièius
#define ST7567S_CONTRAST 0x20 //0x00-0x3f


#endif /* ST7567S_H_ */