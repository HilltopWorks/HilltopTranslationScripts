.psx
.open "EXTRACT\SYSTEM.BIN\SYSTEM.BIN.0012", 0x8009c1d8
.include "char.asm"
.org 0x8009e0c0
	 .area 0x50, 0x00 ;nops the code that checks if you press L1 or R1, not sure if adding a jump is better lmao
	 .endarea 
.org 0x8009c824
	  li  $v1, 3 ; sets the character type to 3 (latin alphabeth) when loading the menu

.org 0x8009eee8
	 .area 0x3ac, 0x00 ;removes the code needed to draw the character text
	 .endarea
	 
;THE FOLLOWING BLOCK IS FOR REMOVING THE FUNCTION CALLS NEEDED TO DRAW THE GREEN LINE FOR THE CHARACTER SELECTION
;-------------------------------
.org 0x8009f2e8 ;1st line
	 nop 
.org 0x8009f318 ;2nd line
	 nop
.org 0x8009f348	;3rd line
	 nop
;--------------------------------

.org 0x8009eaf0
	 li $v0, 176 ;letters Y position
.org 0x8009eb58	 
	 li $v0, 178 ;bold letters y position
.close