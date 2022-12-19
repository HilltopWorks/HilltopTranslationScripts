.psx
.erroronwarning on
;#################         Defining Globals               ####################
.definelabel SJIS_START_HI,	   0x1FC6
.definelabel SJIS_START_LO,    0x5FE2
.definelabel SJIS_GLYPH_SIZE,       30

;Change DRAW_GLYPH to use our 8px by 12px font
HEIGHT equ 12
WIDTH_IN_PIXELS equ 8
WIDTH_IN_VRAM_BYTES equ 2
GLYPH_LENGTH equ HEIGHT * WIDTH_IN_PIXELS / 8


; ################         Defining BB_300.EXE            ####################
.open "EXTRACT\BASE\BB_300.EXE", 0x8003F800
BASE_ADDRESS equ 0x8003F800

;Remove the font clearing call
.org BASE_ADDRESS + 0x38920
	nop
;Increase max glyphs per text line to 32 (Main Dialogue)
.org BASE_ADDRESS + 0xbf80
	slti 	v0, v0, 0x20
;Increase max glyphs per text line to 32 (Menu Text)
.org BASE_ADDRESS + 0xD9F0
	slti 	v1, v1, 0x20
;Reduce glyph width to 8 when drawing to frame (Main dialogue)
.org BASE_ADDRESS + 0x1C + 0xde28
	add 	v0, r0, v1
;Reduce glyph width to 8 when drawing to frame (Menu Text)
.org BASE_ADDRESS + 0x1C + 0xdf48
	add 	v0, r0, v1
;Implement 1 byte text (main dialogue)
.org BASE_ADDRESS - 0x20 + 0xbf90
	addiu   v0,v0, 1
;Implement 1 byte text (menu text)
.org BASE_ADDRESS + 0xd9ec
	addiu   v0,v0, 1

.definelabel Krom2RawAdd,	BASE_ADDRESS + 0x1e274
.definelabel CHARS_ON_LINE,	0x800AB018
.definelabel GLYPH_DATA,    0x800C11b0
.definelabel LOAD_IMAGE,    BASE_ADDRESS + 0xe4d0
.definelabel DRAW_GLYPH,	BASE_ADDRESS + 0xb730
.definelabel DRAW_GLYPH_END, DRAW_GLYPH + 0x204 ;0x8004BFCC
.definelabel FONT_START,	BASE_ADDRESS + 0xf0 + 0x69834

; TOAST text

.definelabel TOAST_1_BYTE,     BASE_ADDRESS + 0xdfe4
.definelabel DRAW_TOAST_GLYPH, BASE_ADDRESS + 0xe380




;<<<<<<<<<<<<<<<<<<<<<<<<<<<<         START OF FUNCTIONS         >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


;Load in our font
.org FONT_START
.import "IMAGE/font.bin"

.org DRAW_GLYPH 
.area DRAW_GLYPH_END-.
	;Housekeeping
	addiu 	sp, sp, -0x38   ;Push stack
	sw 		s3, 0x24(sp)
	move 	s3,a1 			;
	sra 	v0,s3,0x3
	la 		v1,CHARS_ON_LINE		;create CHARS_ON_LINE address
	andi 	v0,v0,0x6
	addu 	v0,v0,v1
	sw		s2,0x20(sp)     ;Store pass-through values
	move	s2,a2
	sw		s1,0x1c(sp)
	move	s1,a3
	sw		ra,0x30(sp)
	sw		s5,0x2c(sp)
	sw		s4,0x28(sp)
	sw		s0,0x18(sp)
	
	sh 		a2,0x0(v0)		;store num_chars in CHARS_ON_LINE
	;Set glyph destination pointer
	move 	s0,v0
	la 		t6,GLYPH_DATA
	;lui 	v0,GLYPH_DATA_HI
	;addiu	t6,v0,GLYPH_DATA_LO	;t6 = GLYPH_ptr
	clear 	t7					;t7 = glyph_cursor = 0
	;Get font offset
	lbu  	v0, 0x0(a0)			;v0 = next second kanji byte
	li 		v1, 0xc 			;size of glyph in bytes
	subiu   v0, v0,0x80			;Adjust to text offset
	mult    v0, v1
	la      t2, FONT_START	;t2 = Font start
	mflo	t4                	;t4 = glyph offset
	addu    t4,t4,t2		  	;t4 = glyph address

H_LINE_START: 	
	lbu		v0,0x0(t4)		;v0 = next H line byte of glyph
	nop
	addiu   t4,t4,1			;increment font cursor
	li 		t2,3			;t2 = GLYPH_X (in vram pixels)
NEXT_H_LINE:
	andi 	t0,v0,0x80      ;next_byte & 0x80=>t0
	beq 	t0,r0,IF_FIRST_BIT_NOT_SET
	 clear 	v1				;VRAM_WORD = v1 = 0
	li 		v1,0x0f			;VRAM_WORD = 0xF
IF_FIRST_BIT_NOT_SET:
	andi	t0,v0,0x40		;next_byte & 0x40=>t0
	beq		t0,r0,IF_SECOND_BIT_NOT_SET
	 nop
	ori		v1,v1,0xf0			;VRAM_WORD &= 0xf0
IF_SECOND_BIT_NOT_SET:
	sb 		v1,0x0(t6)		;Write glyph byte
	addiu 	t6,t6,0x1		;INC glyph ptr
	addiu   t2,t2,-0x1		;DEC glyph X counter
	bgez	t2,NEXT_H_LINE	;while glyph x > -1
	 sll	v0,v0,2			;
	addiu	t7,t7,1			;INC glyph_cursor
	slti	v1,t7,HEIGHT	   ;Repeat if cursor not
	bne 	v1,r0,H_LINE_START ;at full HEIGHT
FINISHED_WRITING:	
	li		a1,HEIGHT			;Set height
	addiu   a0,sp,0x10
	sll 	v1,a2,0x10
	sra		v1,v1,0x10
	addiu	v1,v1,-1
	sll		v0,v1,1
	addiu	v0,v0,0x140
	andi	v1,s3,0x3f
	sra 	v1,v1,0x4
	sh		v0,0x10(sp)		;rect X
	sll		v0,v1,0x1
	addu	v0,v0,v1
	sll		v0,v0,0x2
	addiu	v0,v0,0x1d0
	sh		v0,0x12(sp)		;rect Y
	li		v0,2				;set width
	sh		a1,0x16(sp)		;char_height
	la 		a1, GLYPH_DATA

	jal		LOAD_IMAGE
	 sh		v0,0x14(sp)		;char width
	
	;End housekeeping
	lw 		ra,0x30(sp)
	lw		s5,0x2c(sp)
	lw		s4,0x28(sp)
	lw		s3,0x24(sp)
	lw		s2,0x20(sp)
	lw		s1,0x1c(sp)
	lw		s0,0x18(sp)
	addiu	sp,sp,0x38
	jr		ra					;ret
	 nop
.endarea


.org TOAST_1_BYTE
	addiu  s0, s0, 1

.org DRAW_TOAST_GLYPH
	addiu  sp, sp, -0x20
	sw     ra, 0x18(sp)
	lbu    a0, 0(a0)
	li 	   v0, SJIS_GLYPH_SIZE
	mult   v0, a0
	lui    a3, SJIS_START_HI
	addiu  a3, a3, SJIS_START_LO	;a3 = glyph base
	mflo   a0		     			;a0 = glyph offset
	addu   a3, a3, a0    			;a3 = GLYPH address
	nop


.close