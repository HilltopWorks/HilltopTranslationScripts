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


; ################         Defining BB_001.EXE            ####################
.open "EXTRACT\BASE\BB_001.EXE", 0x8003B800
BASE_ADDRESS equ 0x8003B800

;Remove the font clearing call
.org BASE_ADDRESS + 0x3C040
	nop
;Increase max glyphs per text line to 32 (Main Dialogue)
.org 0x800456d0               ; THIS IS CORRECT
	slti 	v1, v1, 0x20
;Increase max glyphs per text line to 32 (Menu Text)
.org 0x80046FD0
	slti 	v1, v1, 0x20
.org 0x800459ac
	slti	v1, v1, 0x20

;Reduce glyph width to 8 when drawing to frame (Main dialogue)
.org BASE_ADDRESS + 0x1C + 0xbb8c
	add 	v0, r0, v1
;Reduce glyph width to 8 when drawing to frame (Menu Text)
.org BASE_ADDRESS + 0x1C + 0xbcc4
	add 	v0, r0, v1
;Implement 1 byte text (main dialogue)
.org 0x800456cc               ; THIS IS CORRECT
	addiu   v0,a0, 1          ; THIS IS CORRECT
.org 0x800456e0
	lbu		v0, 0x1(a0)
.org 0x800456ec
	addiu	v0, a0, 0x2       ; THIS IS CORRECT
	

;Implement 1 byte text (menu text)
.org 0x800459a8
	addiu   v0,a0, 1
.org 0x800459bc
	lbu		v0, 0x1(a0)
.org 0x800459c8
	addiu	v0, a0, 0x2

.definelabel Krom2RawAdd,	BASE_ADDRESS + 0x2283C
.definelabel CHARS_ON_LINE,	0x80090fd8   ;THIS IS CORRECT
.definelabel GLYPH_DATA,    0x80093918
.definelabel LOAD_IMAGE,    0x8005f698   ;THIS IS CORRECT
.definelabel DRAW_GLYPH,	0x800452a4
.definelabel DRAW_GLYPH_END,0x80045498   ;
.definelabel FONT_START,	BASE_ADDRESS + 0xf0 + 0x53a08

; TOAST text

.definelabel TOAST_1_BYTE,     0x80047570   ;THIS IS CORRECT
.definelabel DRAW_TOAST_GLYPH, 0x800476c8   ;THIS IS CORRECT




;<<<<<<<<<<<<<<<<<<<<<<<<<<<<         START OF FUNCTIONS         >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


;Load in our font
.org FONT_START
.import "IMAGE/font.bin"

.org DRAW_GLYPH 
.area DRAW_GLYPH_END-.
	;Housekeeping
	addiu 	sp, sp, -0x28   ;Push stack
	sw		ra, 0x24(sp)    ;Store pass-through values
	sw		s2, 0x20(sp)
	sw		s1, 0x1c(sp)
	sw		s0, 0x18(sp)

	;Load Parameters
	lw		a1, 0x478(gp)   ;text_ptr+1 
	lhu		a2, 0x470(gp)   ;num_chars

	move 	s3,a1 			;
	sra 	v0,s3,0x3
	la 		v1,CHARS_ON_LINE		;create CHARS_ON_LINE address
	andi 	v0,v0,0x6
	addu 	v0,v0,v1

	
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
	lw 		ra,0x24(sp)
	lw		s2,0x20(sp)
	lw		s1,0x1c(sp)
	lw		s0,0x18(sp)
	addiu	sp,sp,0x28
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
	lui    t0, SJIS_START_HI
	addiu  t0, t0, SJIS_START_LO	;a3 = glyph base
	mflo   a0		     			;a0 = glyph offset
	addu   t0, t0, a0    			;a3 = GLYPH address
	nop


.close