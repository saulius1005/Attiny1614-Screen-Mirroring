/*
 * USART.c
 *
 * Created: 2024-10-01 15:51:21
 *  Author: Saulius
 */ 
 #include "Settings.h"

 void USART0_init(){
	 USART0.BAUD = (uint16_t)USART0_BAUD_RATE(1280000);// Set baud rate
	 USART0.CTRLB = USART_RXEN_bm | USART_TXEN_bm | USART_RXMODE_CLK2X_gc; //TX, TX on, 2x speed
	 USART0.CTRLC = USART_CMODE_ASYNCHRONOUS_gc | USART_CHSIZE_8BIT_gc | USART_PMODE_DISABLED_gc | USART_SBMODE_1BIT_gc;
 }

 void USART0_sendChar(char c){
	 while (!(USART0.STATUS & USART_DREIF_bm));
	 USART0.TXDATAL = c;
 }

 int USART0_printChar(char c, FILE *stream){
	 USART0_sendChar(c);
	 return 0;
 }

 void USART0_sendString(char *str){
	 for(size_t i = 0; i < strlen(str); i++){
		 USART0_sendChar(str[i]);
	 }
 }

 char USART0_readChar(){
	 USART0.STATUS = USART_RXCIF_bm;// clear buffer before reading
	 while (!(USART0.STATUS & USART_RXCIF_bm));
	 return USART0.RXDATAL;
 }

void DataReading(uint8_t *data) {
	uint16_t received_bytes = 0;
	// Priimame visà 1536 baitø masyvà vienu metu
	while (received_bytes < 1024) {
		data[received_bytes++] = USART0_readChar();  // Skaitymas per UART
	}

}