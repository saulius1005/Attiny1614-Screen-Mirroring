/*
 * Attiny1614 DC PWM STEPPER Sunload sensor.c
 *
 * Created: 2024-08-15 21:40:53
 * Author : Saulius
 */ 
#include "Settings.h"
#include "images.h"

int main(void)
{
	GPIO_init();
	I2C_init();
	USART0_init();
	    
screen_init(0);
screen_init(1);

screen_clear(0);	
screen_clear(1);

screen_write_text(0, "Text test on 0 line",0,0);
screen_write_text(1, "Text test on 0 line",0,0);

screen_write_text(0, "OLED screen",1,0);
screen_write_text(1, "LCD screen",1,0);

screen_write_text(0, "and after text",2,0);
screen_write_text(1, "and after text",2,0);

screen_write_text(0, "Stationary image",3,0);
screen_write_text(1, "Stationary image",3,0);

screen_write_text(0, "from a flash memory",4,0);
screen_write_text(1, "from a flash memory",4,0);

screen_write_text(0, "using pgm",5,0);
screen_write_text(1, "using pgm",5,0);
_delay_ms(3000);

screen_draw_image(0, 0, test);
screen_draw_image(0, 1, test);
_delay_ms(3000);

screen_write_text(0, "Now will start",2,10);
screen_write_text(1, "Now will start",2,10);

screen_write_text(0, "screen mirroring",3,10);
screen_write_text(1, "screen mirroring",3,10);

screen_write_text(0, "from PC using UART",4,10);
screen_write_text(1, "from PC using UART",4,10);

screen_write_text(0, "on OLED screen",5,10);
screen_write_text(1, "on LCD screen",5,10);
_delay_ms(3000);

USART0_sendString("START\r\n");

    while (1) 
    {		
		uint8_t pack[1024]={0};
		DataReading(pack);
		screen_draw_image(1, 0, pack);
		USART0_sendString("OK\r\n");
		DataReading(pack);
		screen_draw_image(1, 1, pack);
		USART0_sendString("OK\r\n");		
    }
}

