/*
 * I2c.c
 *
 * Created: 2024-08-15 22:42:43
 *  Author: Saulius
 */ 
#include "Settings.h"

void I2C_init(){
	TWI0.CTRLA = TWI_SDAHOLD_OFF_gc
	| TWI_SDASETUP_4CYC_gc;
	TWI0.MBAUD = (uint8_t)TWI0_BAUD(1000000, 0.3); //Baud ~1M
	TWI0.MCTRLA = TWI_ENABLE_bm //Enable TWI
	| TWI_FMPEN_bm
	| TWI_SMEN_bm
	| TWI_QCEN_bm; //Quick command enable
	TWI0.MSTATUS = TWI_BUSSTATE_IDLE_gc; //Turn bus to idle
}

uint8_t TranssmitAdd(uint8_t Add, uint8_t Read){
	uint8_t address = (Add << 1) + Read; //for faster data sendig calculate final address value before data sending
 for (uint8_t i = 0; i< 3; i++){
 TWI0.MADDR = (address);
 // Laukiame, kol bus baigta.
 while (!(TWI0.MSTATUS & TWI_WIF_bm));
  if(!(TWI0.MSTATUS & TWI_RXACK_bm)) //if receive ACK
   return 0;
 }
 I2C.Fault = 1; //NACK error
 TWI0.MCTRLB = TWI_MCMD_STOP_gc; // sending stop
 return 1; //if after 3 times attempt to sending Add get NACK
}
uint8_t Stop(){
while(!(TWI0.MSTATUS & TWI_CLKHOLD_bm));
 TWI0.MCTRLB |= TWI_MCMD_STOP_gc; // sending stop to sda
 if(TWI0.MSTATUS & TWI_RXACK_bm) //if receive nack from slave
  return 1;// exit with error 
 return 0; // or if all ok send 0
}

void WriteToReg(uint8_t Add, uint8_t Reg, uint8_t Data){ //single byte write
	TranssmitAdd(Add, W);// write Add and W
		TWI0.MDATA = Reg; // Siunèiame valdymo baità (A0=1, kad nurodytø, jog siunèiame duomenis).
		while (!(TWI0.MSTATUS & TWI_WIF_bm));

		TWI0.MDATA = Data; // Siunèiame duomenis.
		while (!(TWI0.MSTATUS & TWI_WIF_bm));
		TWI0.MCTRLB = TWI_MCMD_STOP_gc;
}