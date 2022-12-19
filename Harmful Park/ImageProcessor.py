from asyncio.windows_events import NULL
from logging import exception
from PIL import Image,ImageDraw, ImageFont
import re
import os
import numpy as np
import sys
from pathlib import Path
import json


FOUR_BIT_CLUT    = 0
EIGHT_BIT_CLUT   = 1
SIXTEEN_BIT_CLUT = 2
TWENTYFOUR_BIT_CLUT = 3
TIM_ID = 0x10
FOUR_BIT_MASK_1  = 0b0000000000001111
FOUR_BIT_MASK_2  = 0b0000000011110000
FOUR_BIT_MASK_3  = 0b0000111100000000
FOUR_BIT_MASK_4  = 0b1111000000000000

EIGHT_BIT_MASK_1 = 0b0000000011111111
EIGHT_BIT_MASK_2 = 0b1111111100000000

PXL_HEADER_SIZE = 0x14
PXL_ID = 0x11
CLT_ID = 0x12

OUTPUT_FOLDER = "OUTPUT"
ORIGINAL_FOLDER = "ORIGINAL"
LOG_FOLDER = "logs"

WORD_MODE = 'word'
LETTER_MODE = 'letter'

PUNCTUATION = ',.?!;:\'"@#—$%^&*()_-+={}[]\|<>~`…'
#SKIP_TOKEN = "[SKIP]"
FONT_DEF_STRING = '!FontDef'
IMG_DEF_STRING = '!ImgDef'
SEQUENCE_DEF_STRING = '<<<SEQUENCE '

#Per-project variables
DEFAULT_SCALING = 4096
DEFAULT_ROTATION = 0
DEFAULT_FLAG2_RESERVE = 0
#IMAGE_WHITESPACE = 1 #Buffer pixels before and after images
LETTER_WHITESPACE = 0 #Buffer pixels after every letter
SPACE_WIDTH = 4 #Size of space character in pixels
NEWLINE_DISTANCE = 16 #Y distance moved after a newline

#Per-game variables
SOURCE_FOLDER = "PS1_Base_Project/cd/working/"
GAME_NAME = "Harmful Park" #Checked for game specific sprite params

HAR_ORIGINAL_FOLDER = 'HAR Original'
HAR_EXE_PATH = 'HAR/HARMFUL.EXE'
MG1_PATH = 'HAR/MG1/MG.EXE'
ALPHA_COLOR = (0,0,0,0)


HAR_ANI_TABLE_OFFSETS = []


           #PXL File              #CLT file
IMAGES = [["SZSTAGE/ST0_PXL.PAC", "SZSTAGE/ST0.CLS"],
          ["SZSTAGE/ST1_PXL.PAC", "SZSTAGE/ST1.CLS"],
          ["SZSTAGE/ST2_PXL.PAC", "SZSTAGE/ST2.CLS"],
          ["SZSTAGE/ST3_PXL.PAC", "SZSTAGE/ST3.CLS"],
          ["SZSTAGE/ST4_PXL.PAC", "SZSTAGE/ST4.CLS"],
          ["SZSTAGE/ST5_PXL.PAC", "SZSTAGE/ST5.CLS"],
          ["SZSTAGE/ST6_PXL.PAC", "SZSTAGE/ST6.CLS"],
          ["SZSTAGE/ST7_PXL.PAC", "SZSTAGE/ST7.CLS"],
          ["SZSTAGE/ST8_PXL.PAC", "SZSTAGE/ST8.CLS"],
          ["SZSTAGE/ST9_PXL.PAC", "SZSTAGE/ST9.CLS"],

          ["ANM/BOX_PXL.PAC", "ANM/P00.CLS"],
          ["ANM/FAIL_PXL.PAC", "ANM/P00.CLS"],
          ["ANM/GUID_PXL.PAC", "ANM/P00.CLS"],
          ["ANM/PIX.PAC", "ANM/P00.CLS"],
          
          ["BG/OPEN_PXL.PAC", "BG/OPEN.CLS"],
          ["BG/PXL00.PAC", "BG/00.CLS"],
          ["BG/PXL01.PAC", "BG/01.CLS"],
          ["BG/PXL02.PAC", "BG/02.CLS"],
          
          ["SZGRP/OPT_PXL.PAC", "SZGRP/OPT.CLS"],
          ["SZGRP/SEL0_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZGRP/SEL1_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZGRP/TTL_PXL.PAC", "SZGRP/TTL.CLS"],

          ["SZINGAME/WAI0_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/WAI1_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/FEF0_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZINGAME/FEF1_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/FEF2_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/FEF3_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZINGAME/FEF4_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/FEM0_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZINGAME/FEM1_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/FEM2_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/FEM3_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZINGAME/FEM4_PXL.PAC", "SZINGAME/WAIT.CLS"],
          ["SZINGAME/STAT_PXL.PAC", "SZINGAME/WAIT.CLS"],

          ["SZSYSTEM/LOD0_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZSYSTEM/LOD1_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZSYSTEM/REC0_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZSYSTEM/REC1_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZSYSTEM/SAV0_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZSYSTEM/SAV1_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZSYSTEM/SYS0_PXL.PAC", "SZGRP/COMMON.CLS"],
          ["SZSYSTEM/SYS1_PXL.PAC", "SZGRP/COMMON.CLS"],

            ]

#ANM classes
class ANM:
    def __init__(self, ID, version, NCLUTS, TPF, sequences, spriteGroups, CLUTGrps, fileName, offset):
        self.fileName = fileName
        self.ID = ID
        self.version = version
        self.NCLUTS = NCLUTS
        self.TPF = TPF
        self.sequences = sequences
        self.spriteGroups = spriteGroups
        self.CLUTGrps = CLUTGrps
        self.offset = offset

class SEQUENCE:
    def __init__(self, spriteGrpNumber, time, attr, hotSpotX, hotSpotY):
        self.spriteGrpNumber = spriteGrpNumber
        self.time = time
        self.attr = attr 
        self.hotSpotX = hotSpotX
        self.hotSpotY = hotSpotY

class SPRGRP:
    def __init__(self, NSprite, sprites):
        self.NSprite = NSprite
        self.sprites = sprites

class SPRITE:
    def __init__(self, u,v, ofsX, ofsY, CLX, CLY, ABE, TexturePageNumber, ABR, TPFSprite, RSZ, ROT, THW, Width, Height, Rotation, Flag2Reserve, CSN, BNO, XScaling, YScaling):
        self.u = u
        self.v = v
        self.ofsX = ofsX 
        self.ofsY = ofsY
        self.CLX = CLX
        self.CLY = CLY
        self.ABE = ABE
        self.TexturePageNumber = TexturePageNumber
        self.ABR = ABR
        self.TPFSprite = TPFSprite
        self.RSZ = RSZ 
        self.ROT = ROT
        self.THW = THW
        self.Width = Width
        self.Height = Height
        self.Rotation = Rotation 
        self.Flag2Reserve = Flag2Reserve
        self.CSN = CSN
        self.BNO = BNO
        self.XScaling = XScaling
        self.YScaling = YScaling


class CLUTGRP:
    def __init__(self, bnum, DX, DY, W, H, CLUTS):
        self.bnum = bnum
        self.DX = DX
        self.DY = DY
        self.W = W
        self.H = H
        self.CLUTS = CLUTS

#PXL Classes
class PXL:# file OR ID, version, PMD, bnum, DX, DY, W, H, PXLData
    def __init__(self, *args):
        if len(args) == 1:
            self.ID = readByte(args[0])
            self.version = readByte(args[0])
            args[0].read(2)
            self.PMD = readInt(args[0]) & 0b1

            self.bnum = readInt(args[0])
            self.DX = readShort(args[0])
            self.DY = readShort(args[0])
            self.W = readShort(args[0])
            self.H = readShort(args[0])
            self.PXLData = readPXLEntries(args[0], self.PMD, self.bnum - 0xC)
            self.TPN = (self.DX//64) + (self.DY//256)*16
        
        elif len(args) == 9:
            self.ID = args[0]
            self.version = args[1]
            self.PMD = args[2]
            self.bnum = args[3]
            self.DX = args[4]
            self.DY = args[5]
            self.W = args[6]
            self.H = args[7]
            self.PXLData = args[8]
            self.TPN = (self.DX//64) + (self.DY//256)*16
        
        else:
            raise exception("PXL constructor arguments must be 1 file or 9 parameters!")

class TIM:
    def __init__(self, *args):
        if len(args) == 1:
            self.ID = readByte(args[0])
            self.version = readByte(args[0])
            args[0].read(2)
            Flag = readInt(args[0])
            self.PMD = Flag & 0b111
            self.CF = (Flag & 0b1000) >>3
            if self.CF == 0b1:
                self.CLUTbnum = readInt(args[0])
                self.CLUTDX = readShort(args[0])
                self.CLUTDY = readShort(args[0])
                self.CLUTW = readShort(args[0])
                self.CLUTH = readShort(args[0])
                self.CLUT = readCLTEntries(args[0], (self.CLUTbnum - 0xC)//2)

            self.bnum = readInt(args[0])
            self.DX = readShort(args[0])
            self.DY = readShort(args[0])
            self.W = readShort(args[0])
            self.H = readShort(args[0])
            self.PXLData = readPXLEntries(args[0], self.PMD, self.bnum - 0xC)

            self.TPN = (self.DX//64) + (self.DY//256)*16
        
        elif len(args) == 10:
            self.ID = args[0]
            self.version = args[1]
            self.PMD = args[2]
            self.CF = args[3]
            self.bnum = args[4]
            self.DX = args[5]
            self.DY = args[6]
            self.W = args[7]
            self.H = args[8]
            self.PXLData = args[9]
            self.TPN = (self.DX//64) + (self.DY//256)*16

        elif len(args) == 16:
            self.ID = args[0]
            self.version = args[1]
            self.PMD = args[2]
            self.CF = args[3]
            self.bnum = args[4]
            self.DX = args[5]
            self.DY = args[6]
            self.W = args[7]
            self.H = args[8]
            self.PXLData = args[9]
            self.CLUTbnum = args[10]
            self.CLUTDX = args[11]
            self.CLUTDY = args[12]
            self.CLUTW = args[13]
            self.CLUTH = args[14]
            self.CLUT = args[15]
            self.TPN = (self.DX//64) + (self.DY//256)*16
        
        else:
            raise exception("TIM constructor arguments must be 1 file or 10 parameters(no clut) or 16 parameters(clut)!")

class SUBCELL:
    def __init__(self, *args):
        if len(args) == 9:
            self.u = args[0]
            self.v = args[1]
            self.CLX = args[2]
            self.CLY = args[3]
            self.VLP = args[4]
            self.HLP = args[5]
            self.TPN = args[6]
            self.ABR = args[7]
            self.TPF = args[8]

class CEL:
    def __init__(self, *args):
        if len(args) == 1:
            self.ID = readByte(args[0])
            self.version = readByte(args[0])
            flag = readShort(args[0])
            self.ATT = flag & 0b1000000000000000 >> 15
            self.ATL = flag & 0b0100000000000000 >> 14
            self.NCELL = readShort(args[0])
            self.CELLWidth = readByte(args[0])
            self.CELLHeight = readByte(args[0])

            self.CELLS = []
            for cellNumber in range(self.NCELL):
                u = readByte(args[0])
                v = readByte(args[0])
                CBA = readShort(args[0])
                CLX = CBA & 0b000000000111111
                CLY = (CBA & 0b111111111000000) >> 6
                cellFlag = readShort(args[0])
                VLP = cellFlag & 0b01
                HLP = cellFlag & 0b10
                TSB = readShort(args[0])
                TPN = TSB & 0b000011111
                ABR = TSB & 0b001100000 >> 5
                TPF = TSB & 0b110000000 >> 7
                self.CELLS.append(SUBCELL(u,v,CLX,CLY,VLP,HLP,TPN,ABR,TPF))
            
            if self.ATT != 0:
                ATRsize = 8 + self.ATL * 8
                self.ATRs = []

                if ATRsize == 8:
                    for cellNumber in range(self.NCELL):
                        self.ATRs.append(readByte(args[0]))
                else:
                    for cellNumber in range(self.NCELL):
                        self.ATRs.append(readShort(args[0]))
                
class BGD:
    def __init__(self, *args):
        if len(args) == 1:
            self.ID = readByte(args[0])
            self.version = readByte(args[0])
            flag = readShort(args[0])
            self.ATT = flag & 0b1000000000000000 >> 15
            self.ATL = flag & 0b0100000000000000 >> 14
            self.MAPW = readByte(args[0])
            self.MAPH = readByte(args[0])
            self.CELLW = readByte(args[0])
            self.CELLH = readByte(args[0])
            self.MAP = []

            for y in range(self.MAPW):
                for x in range(self.MAPH):
                    self.MAP.append(readShort(args[0]))

            if self.ATT != 0:
                    ATRsize = 8 + self.ATL * 8
                    self.ATRs = []

                    if ATRsize == 8:
                        for cellNumber in range(self.MAPW * self.MAPH):
                            self.ATRs.append(readByte(args[0]))
                    else:
                        for cellNumber in range(self.MAPW * self.MAPH):
                            self.ATRs.append(readShort(args[0]))



#CLT Classes
class CLT:
    def __init__(self, *args):

        if len(args) == 1:
            self.ID = readByte(args[0])
            self.version = readByte(args[0])
            args[0].read(2)
            self.PMODE = readInt(args[0]) & 0b11
            self.bnum = readInt(args[0])
            self.DX = readShort(args[0])
            self.DY = readShort(args[0])
            self.W = readShort(args[0])
            self.H = readShort(args[0])

            self.CLUTs = readCLTEntries(args[0], (self.bnum - 0xC)//2)
        
        elif len(args) == 9:
            self.ID = args[0]
            self.version = args[1]
            self.PMODE = args[2]
            self.bnum = args[3]
            self.DX = args[4]
            self.DY = args[5]
            self.W = args[6]
            self.H = args[7]

            self.CLUTs = args[8]
        else:
            raise exception("CLT constructor arguments must be 1 file or 8 parameters!")

#Converts a TIM to a PXL + CLT
def extractTIM(TIMObj):
    PXLObj = PXL(PXL_ID, TIMObj.version, TIMObj.PMD, TIMObj.bnum, TIMObj.DX, TIMObj.DY, TIMObj.W, TIMObj.H, TIMObj.PXLData)
    CLTObj = CLT(CLT_ID, TIMObj.version, TIMObj.PMD, TIMObj.CLUTbnum, TIMObj.CLUTDX, TIMObj.CLUTDY, TIMObj.CLUTW, TIMObj.CLUTH, TIMObj.CLUT)

    return PXLObj,CLTObj

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val 

#Reads little endian int from file and advances cursor
def readInt(file):
    readInt = int.from_bytes(file.read(4), byteorder='little')
    return readInt

#Reads little endian short from file and advances cursor
def readShort(file):
    readShort = int.from_bytes(file.read(2), byteorder='little')
    return readShort

#Reads little endian byte from file and advances cursor
def readByte(file):
    readByte = int.from_bytes(file.read(1), byteorder='little')
    return readByte

#Returns a PXL file of given length as value array
def readPXLEntries(file, PMODE, fileLength):
    PXL_Entries = []
    for x in range(fileLength // 2):
        pixels = readShort(file)
        if PMODE == FOUR_BIT_CLUT:
            PXL_Entries +=  [pixels & FOUR_BIT_MASK_1]
            PXL_Entries += [(pixels & FOUR_BIT_MASK_2) >> 4]
            PXL_Entries += [(pixels & FOUR_BIT_MASK_3) >> 8]
            PXL_Entries += [(pixels & FOUR_BIT_MASK_4) >> 12]

        elif PMODE == EIGHT_BIT_CLUT:
            PXL_Entries += [pixels & EIGHT_BIT_MASK_1]
            PXL_Entries += [(pixels & EIGHT_BIT_MASK_2) >> 8]

        else:
            raise exception("UNRECOGNIZED PMODE")

    return PXL_Entries

#Returns a specific CLUT from a file as RGBA array
def getCLUT(clutFile, CLUTOffset, CLUTNumber, PMODE):

    CLTFile = clutFile
    CLTFile.read(CLUTOffset)

    CLT_ID    = readInt(CLTFile)
    CLT_PMODE = readInt(CLTFile)
    CLT_bnum  = readInt(CLTFile)
    CLT_DX    = readShort(CLTFile)
    CLT_DY    = readShort(CLTFile)
    CLT_W     = readShort(CLTFile)
    CLT_H     = readShort(CLTFile)

    if PMODE == FOUR_BIT_CLUT:
        CLUT_SIZE = 0x20
    elif PMODE == EIGHT_BIT_CLUT:
        CLUT_SIZE = 0x200
    
    CLUTStart = CLUT_SIZE * CLUTNumber

    CLTFile.read(CLUTStart)

    CLUT = readCLTEntries(CLTFile, CLUT_SIZE//2)
    
    return CLUT

#Returns X number of CLT entries as an RGBA array
def readCLTEntries(file, numEntries):
    CLT_Entries = []
    for x in range(numEntries):
        entry = readShort(file)

        red   = entry & 0b0000000000011111
        green = (entry & 0b0000001111100000) >> 5
        blue  = (entry & 0b0111110000000000) >>10
        alpha = (entry & 0b1000000000000000) >> 15

        CLT_Entries += [[red, green, blue, alpha]]


    return CLT_Entries

#Returns an ANM file as an ANM object
def readANM(file, offset):
    file.seek(offset)
    ANM_ID      = readByte(file)
    ANM_Version = readByte(file)
    ANM_Flag    = readShort(file)
    NSPRITEGp   = readShort(file)
    NSEQUENCE   = readShort(file)
    NCLUTS =   (ANM_Flag & 0b1111000000000000) >> 12
    TPF =     ANM_Flag & 0b11

    sequences = []
    
    for sequenceNumber in range(NSEQUENCE):
        spriteGrpCount = readShort(file)
        time = readByte(file)
        attr = readByte(file) >> 4 #Dev specified value
        hotSpotX = readShort(file)
        hotSpotY = readShort(file)
        sequences.append(SEQUENCE(spriteGrpCount, time, attr, hotSpotX, hotSpotY))

    spriteGroups = []
    for spriteGroupNumber in range(NSPRITEGp):
        NSprite = readInt(file)
        sprites = []
        for spriteNumber in range(NSprite):
            u = readByte(file) 
            v = readByte(file)
            ofsX = readByte(file)
            ofsY = readByte(file)
            CBA = readShort(file)
            CLX =  CBA &  0b111111
            CLY = (CBA &  0b111111111000000) >>6
            ABE = (CBA & 0b1000000000000000) >>15 #isSemiTransperencyProcessingOn
            
            FLAG1 = readShort(file)
            TexturePageNumber   = FLAG1 & 0b11111
            ABR              = (FLAG1 & 0b1100000) >> 5 #Semi transperency rate
            TPFSprite      = (FLAG1 & 0b110000000) >> 7 #Pixel Depth 00->4bit 01->8bit 10->16bit
            RSZ          = (FLAG1 & 0b10000000000) >> 10 #isScaled
            ROT         = (FLAG1 & 0b100000000000) >> 11 #isRotated
            THW     = (FLAG1 & 0b1111000000000000) >> 12 #Square dimensions, else 0 and use H/W
            
            if THW == 0:
                Width = readShort(file)
                Height = readShort(file)
            else:
                Width = -1
                Height = -1
            Rotation = readShort(file)
            spriteFlag2 = readShort(file)
            Flag2Reserve = (spriteFlag2 & 0b11111111)
            CSN = (spriteFlag2 &   0b11111100000000) >> 8 #Color set number (editor only)
            BNO = (spriteFlag2 & 0b1100000000000000) >> 14 #TIM Bank number
            XScaling = readShort(file) 
            YScaling = readShort(file)
            sprites.append(SPRITE(u, v, ofsX, ofsY, CLX, CLY, ABE, TexturePageNumber, ABR, TPFSprite, RSZ, ROT, THW, Width, Height, Rotation, Flag2Reserve, CSN, BNO, XScaling, YScaling))

        spriteGroups.append(SPRGRP(NSprite, sprites))


    CLUTGroups = []
    if NCLUTS > 0:
        for clutNumber in range(NCLUTS):
            bnum = readInt(file)
            DX = readShort(file)
            DY = readShort(file)
            clutWidth = readShort(file)
            clutHeight = readShort(file)

            CLUT = readCLTEntries(file, bnum - 0xC)
            CLUTGroups.append(CLUTGRP(bnum, DX, DY, clutWidth, clutHeight, CLUT))
    ANM_OBJ = ANM(ANM_ID, ANM_Version, NCLUTS, TPF, sequences,  spriteGroups, CLUTGroups, os.path.basename(file.name), offset)


    return ANM_OBJ

#Saves the sequences of an ANM object as a set of images
def animateANM(ANM, PXLs, CLUTs):
    nSequences = len(ANM.sequences)
    if not os.path.exists(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)

    logfile = open(os.path.join(LOG_FOLDER, ANM.fileName + '-' + str(ANM.offset) + '.log'), "w")
    for sequenceNumber in range(nSequences):

        logfile.write("-----\nSequence #" + str(sequenceNumber) + ":\n-----\n")

        sequence = ANM.sequences[sequenceNumber]

        #DEBUG
        if sequence.spriteGrpNumber >= len(ANM.spriteGroups):
             sequence.spriteGrpNumber = 0
             print("DEBUG failsafe triggered on " + ANM.fileName + ' offset ' + str(ANM.offset) +  ' sequence ' + str(sequenceNumber))

        spriteGroup = ANM.spriteGroups[sequence.spriteGrpNumber]

        numSprites = spriteGroup.NSprite
        logfile.write("Number of sprites: " + str(numSprites) + '\n\n')

        compositeWidth = 0
        compositeHeight = 0
        spriteImages = []
        runningImage = Image.new('RGBA', (compositeWidth, compositeHeight), (0,0,0,0))
        for spriteNumber in range(numSprites):
            #Check all CLUTs and pick based on CLX/CLY within CLUT bounds
            sprite = spriteGroup.sprites[spriteNumber]
            if sprite.THW ==  0:
                spriteHeight = sprite.Height
                spriteWidth  = sprite.Width
            else:
                spriteHeight = sprite.THW << 3
                spriteWidth  = sprite.THW << 3

            for searchCLUT in CLUTs:
                
                trueCLUTX = 0x10 *sprite.CLX - searchCLUT.DX
                trueCLUTY = sprite.CLY - searchCLUT.DY

                if trueCLUTX < searchCLUT.W and trueCLUTY < searchCLUT.H and trueCLUTX >= 0 and trueCLUTY >= 0:
                    #Correct CLUT found
                    break

            
            if sprite.TPFSprite == FOUR_BIT_CLUT:
                clutNumber = trueCLUTY + trueCLUTX
            elif sprite.TPFSprite == EIGHT_BIT_CLUT:
                clutNumber = trueCLUTY + 0x10 * trueCLUTX
            else:
                raise exception("INVALID CLUT ")

            #Check all PXls and pick based on sprite TPN matching PXL DX/DY
            PXLFound = False
            for pxl in PXLs:
                BANK_WIDTH = 64
                SHELF_WIDTH = 16
                SHELF_HEIGHT = 256
                pxlDX = pxl.DX
                pxlDY = pxl.DY

                shelfNumber = sprite.TexturePageNumber // SHELF_WIDTH

                if shelfNumber == 0:
                    spriteDY = 0
                elif shelfNumber == 1:
                    spriteDY = SHELF_HEIGHT

                spriteDX = (sprite.TexturePageNumber % SHELF_WIDTH) * BANK_WIDTH

                #DEBUGGING
                spriteIsInRangeX = spriteDX >= pxl.DX and spriteDX < (pxl.DX + pxl.W)
                spriteIsInRangeY = spriteDY >= pxl.DY and spriteDY < (pxl.DY + pxl.H)

                if spriteIsInRangeX and spriteIsInRangeY:
                    pxlMatch = pxl
                    PXLFound = True
                    break

            if not PXLFound:
                print("Could not find TPN match for " + ANM.fileName + ' sequence ' + str(sequenceNumber) + ' sprite number ' + str(spriteNumber))
                logfile.write("Sprite #: " + str(spriteNumber) + '\n')
                logfile.write("[ERROR] Sprite is MALFORMED, PXL match could not be found\n")
                logfile.write("Sprite TPN/BNO: " + str(sprite.TexturePageNumber) +  '/' + str(sprite.BNO) + '\n')
                logfile.write("Sprite TPF: " + str(sprite.TPFSprite) + '\n')
                logfile.write("Sprite CSN/CLUT Number: " + str(sprite.CSN) +  '/' + str(clutNumber) + '\n')
                logfile.write("Sprite CLX/CLY: " + str(sprite.CLX) + "/" + str(sprite.CLY) + '\n')
                logfile.write("Sprite ABR/ABE: " + str(sprite.ABR) + "/" + str(sprite.ABE) + '\n')
                logfile.write("Sprite width/height: " + str(spriteWidth) + '/' + str(spriteHeight) + '\n')
                logfile.write("Sprite u/v: " + str(sprite.u) + '/' + str(sprite.v) + '\n')
                logfile.write("Sprite offset X/Y: " + str(sprite.ofsX) + '/' + str(sprite.ofsY) + '\n')
                logfile.write("Sprite RSZ/ROT: " + str(sprite.RSZ) + '/' + str(sprite.ROT) + '\n')
                logfile.write("Sprite scaling X/Y: " + str(sprite.XScaling) + '/' + str(sprite.YScaling) + '\n')
                logfile.write("Sprite rotation: " + str(sprite.Rotation) + '\n')
                logfile.write("Sprite Flag2Reserve: " + str(sprite.Flag2Reserve) + '\n\n')
                continue
            else:
                logfile.write("Sprite #: " + str(spriteNumber) + '\n')
                logfile.write("Sprite TPN/BNO: " + str(sprite.TexturePageNumber) +  '/' + str(sprite.BNO) + '\n')
                logfile.write("Sprite TPF: " + str(sprite.TPFSprite) + '\n')
                logfile.write("Sprite CSN/CLUT Number: " + str(sprite.CSN) +  '/' + str(clutNumber) + '\n')
                logfile.write("Sprite CLX/CLY: " + str(sprite.CLX) + "/" + str(sprite.CLY) + '\n')
                logfile.write("Sprite ABR/ABE: " + str(sprite.ABR) + "/" + str(sprite.ABE) + '\n')
                logfile.write("Sprite width/height: " + str(spriteWidth) + '/' + str(spriteHeight) + '\n')
                logfile.write("Sprite u/v: " + str(sprite.u) + '/' + str(sprite.v) + '\n')
                logfile.write("Sprite offset X/Y: " + str(sprite.ofsX) + '/' + str(sprite.ofsY) + '\n')
                logfile.write("Sprite RSZ/ROT: " + str(sprite.RSZ) + '/' + str(sprite.ROT) + '\n')
                logfile.write("Sprite scaling X/Y: " + str(sprite.XScaling) + '/' + str(sprite.YScaling) + '\n')
                logfile.write("Sprite rotation: " + str(sprite.Rotation) + '\n')
                logfile.write("Sprite Flag2Reserve: " + str(sprite.Flag2Reserve) + '\n\n')

            totalImage = generatePNG(pxlMatch.PXLData, searchCLUT.CLUTs, pxlMatch.W, pxlMatch.H, clutNumber, sprite.TPFSprite) #sprite.CSN
            
            spriteImage = totalImage.crop((sprite.u, sprite.v, sprite.u + spriteWidth, sprite.v + spriteHeight))

            trueSpriteOffsetX = sprite.ofsX
            trueSpriteOffsetY = sprite.ofsY
            trueWidth = spriteWidth
            trueHeight = spriteHeight

            #Perform sprite scaling
            if sprite.RSZ != 0:
                #X scaling
                XScalingFixedPoint = sprite.XScaling
                beforeDecimalX = (XScalingFixedPoint & 0b1111000000000000) >> 12
                afterDecimalX =   XScalingFixedPoint & 0b0000111111111111

                if beforeDecimalX & 0b1000 != 0:
                    #scaling is negative
                    beforeDecimalX = -twos_comp(beforeDecimalX, 4)
                    spriteImage = spriteImage.transpose(method=Image.FLIP_LEFT_RIGHT)

                trueXScaling = beforeDecimalX + (afterDecimalX / (2**12))
                
                #Y scaling
                YScalingFixedPoint = sprite.YScaling
                beforeDecimalY = (YScalingFixedPoint & 0b1111000000000000) >> 12
                afterDecimalY =   YScalingFixedPoint & 0b0000111111111111
                
                if beforeDecimalY & 0b1000 != 0:
                    #scaling is negative
                    beforeDecimalY = -twos_comp(beforeDecimalY, 4)
                    spriteImage = spriteImage.transpose(method=Image.FLIP_TOP_BOTTOM)
                
                trueYScaling = beforeDecimalY + (afterDecimalY / (2**12))
                
                trueWidth = int(spriteWidth * trueXScaling)
                trueHeight = int(spriteHeight * trueYScaling)

                spriteImage = spriteImage.resize((trueWidth, trueHeight), Image.NEAREST)
                trueSpriteOffsetX = int(sprite.ofsX + (spriteWidth - trueWidth)/2)
                trueSpriteOffsetY = int(sprite.ofsY + (spriteHeight - trueHeight)/2)
                

            #Perform rotation
            if sprite.ROT != 0:
                rotationAngleInDegrees = -(sprite.Rotation / (2**12)) * 360
                spriteImage = spriteImage.rotate(rotationAngleInDegrees, expand=True)
                trueWidth = spriteImage.width
                trueHeight = spriteImage.height
                trueSpriteOffsetX = int(sprite.ofsX + (spriteWidth - trueWidth)/2)
                trueSpriteOffsetY = int(sprite.ofsY + (spriteHeight - trueHeight)/2)
            
            spriteImages.append([spriteImage, [trueSpriteOffsetX, trueSpriteOffsetY]])


            #Update bounds of parent image
            if trueWidth + trueSpriteOffsetX > compositeWidth:
                compositeWidth = trueWidth + trueSpriteOffsetX
                runningImage = add_margin(runningImage, 0,  trueWidth + trueSpriteOffsetX - runningImage.width, 0, 0, (0,0,0,0))

            if trueHeight + trueSpriteOffsetY > compositeHeight:
                compositeHeight = trueHeight + trueSpriteOffsetY
                runningImage = add_margin(runningImage, 0,  0, trueHeight + trueSpriteOffsetY - runningImage.height, 0, (0,0,0,0))

            #Perform transparency
            if sprite.ABE != 0:
                if sprite.ABR == 0:
                    #50F 50B
                    foregroundAmount = 0.5
                    backgroundAmount = 0.5    
                elif sprite.ABR == 1:
                    #100F 100B
                    foregroundAmount = 1.0
                    backgroundAmount = 1.0
                elif sprite.ABR == 2:
                    #-100F 100B
                    foregroundAmount = -1.0
                    backgroundAmount = 1.0
                elif sprite.ABR == 3:
                    #25F 100B
                    foregroundAmount = 0.25
                    backgroundAmount = 1.0
                    pass
                
                for x in range(trueWidth):
                    for y in range(trueHeight):
                        
                        if sprite.TPFSprite == FOUR_BIT_CLUT:
                            CLUTEntries = 0x10
                        elif sprite.TPFSprite == EIGHT_BIT_CLUT:
                            CLUTEntries = 0x100
                        pixel = spriteImage.getpixel((x,y))
                        
                        pixelArray = []
                        for i in pixel:
                            pixelArray.append(i >>3)
                        
                        pixelArray[3] = 1
                        

                        offset = clutNumber * CLUTEntries
                        #Search for color with transparency bit set, and ignore if not found
                        try:
                            value = searchCLUT.CLUTs[offset:offset+CLUTEntries].index(pixelArray)
                        except ValueError:
                            continue

                        
                        CLUTColor = searchCLUT.CLUTs[offset + value]
                        CLUTtransparencyBit = CLUTColor[3]

                        if CLUTtransparencyBit != 1:
                            continue

                        foregroundPixel = spriteImage.getpixel((x,y))
                        
                        backgroundPixel = runningImage.getpixel((trueSpriteOffsetX + x, trueSpriteOffsetY + y ))
                        
                        red = foregroundPixel[0] * foregroundPixel[3]/255 * foregroundAmount + backgroundPixel[0] * backgroundAmount
                        red = min(red, 255)
                        red = max(red, 0)
                        green = foregroundPixel[1] * foregroundPixel[3]/255 * foregroundAmount + backgroundPixel[1] * backgroundAmount
                        green = min(green, 255)
                        green = max(green, 0)
                        blue = foregroundPixel[2] * foregroundPixel[3]/255 * foregroundAmount + backgroundPixel[2] * backgroundAmount
                        blue = min(blue, 255)
                        blue = max(blue, 0)
                        alpha = max(foregroundPixel[3], backgroundPixel[3])
                        
                        spriteImage.putpixel((x,y), (int(red), int(green), int(blue), alpha))

            runningImage.paste(spriteImage, (trueSpriteOffsetX, trueSpriteOffsetY), mask=spriteImage)
        
        if compositeHeight == compositeWidth == 0:
            print("ANM " + ANM.fileName + " Offset " + str(ANM.offset) +  " Sequence " + str(sequenceNumber) + " contains no valid sprites, skipping it")
            continue

        sequenceImage = Image.new('RGBA', (compositeWidth, compositeHeight), (0,0,0,0))
        for spr in spriteImages:
            imageToAdd = spr[0]
            spriteX = spr[1][0]
            spriteY = spr[1][1]
            sequenceImage.paste(imageToAdd, (spriteX, spriteY), mask=imageToAdd)
            #draw = ImageDraw.Draw(sequenceImage)
            #font = ImageFont.truetype("FONT/GenericMobileSystem.ttf", 12)
            #draw.text((spriteX, spriteY), str(spriteImages.index(spr)), fill='red', font=font, align= "left")

        for spr in spriteImages:
            spriteX = spr[1][0]
            spriteY = spr[1][1]
            draw = ImageDraw.Draw(runningImage)
            font = ImageFont.truetype("FONT/GenericMobileSystem.ttf", 10)
            draw.text((spriteX, spriteY), str(spriteImages.index(spr)), fill='red', font=font, align= "middle")
            #draw.text((spriteX, spriteY + 8), str(sprite.CLX) + '/' + str(sprite.CLY), fill='blue', font=font, align= "middle")
        #sequenceImage.show()
        Path(os.path.join(OUTPUT_FOLDER, ANM.fileName)).mkdir(parents=True, exist_ok=True)
        
        runningImage.save(os.path.join(OUTPUT_FOLDER, ANM.fileName, str(ANM.offset) + '-' + str(sequenceNumber) + '_' + str(sequence.spriteGrpNumber)) + '.PNG')

    return

#Returns an ANM object as binary (bytes)
def repackANM(ANM):
    outputBuffer = b''

    flagBuffer = 0

    ID = ANM.ID
    Version = ANM.version << 8
    TPF = ANM.TPF << 16
    NCLUTS = ANM.NCLUTS << 28
    

    outputBuffer += (ID + Version + TPF + NCLUTS).to_bytes(4, byteorder = 'little')
    NSPRITEGp = len(ANM.spriteGroups)
    NSEQUENCE = len(ANM.sequences) << 16

    outputBuffer += (NSPRITEGp + NSEQUENCE).to_bytes(4, byteorder = 'little')

    for sequence in ANM.sequences:
        SprGpNo = sequence.spriteGrpNumber
        time = sequence.time << 16
        attr = sequence.attr << 28

        outputBuffer += (SprGpNo + time + attr).to_bytes(4, byteorder = 'little')
        
        hotSpotX = sequence.hotSpotX
        hotSpotY = sequence.hotSpotY << 16

        outputBuffer += (hotSpotX + hotSpotY).to_bytes(4, byteorder = 'little')

    
    for spriteGroup in ANM.spriteGroups:
        NSprite = spriteGroup.NSprite
        outputBuffer += (NSprite).to_bytes(4, byteorder = 'little')

        for spriteNumber in range(NSprite):
            u = spriteGroup.sprites[spriteNumber].u
            v = spriteGroup.sprites[spriteNumber].v << 8
            ofsX = spriteGroup.sprites[spriteNumber].ofsX << 16
            ofsY = spriteGroup.sprites[spriteNumber].ofsY << 24

            outputBuffer += (u + v + ofsX + ofsY).to_bytes(4, byteorder = 'little')

            CLX = spriteGroup.sprites[spriteNumber].CLX
            CLY = spriteGroup.sprites[spriteNumber].CLY << 6
            ABE = spriteGroup.sprites[spriteNumber].ABE << 15
            TPN = spriteGroup.sprites[spriteNumber].TexturePageNumber << 16
            ABR = spriteGroup.sprites[spriteNumber].ABR << 21
            TPFSprite = spriteGroup.sprites[spriteNumber].TPFSprite << 23
            RSZ = spriteGroup.sprites[spriteNumber].RSZ << 26
            ROT = spriteGroup.sprites[spriteNumber].ROT << 27
            THW = spriteGroup.sprites[spriteNumber].THW << 28

            outputBuffer += (CLX + CLY + ABE + TPN + ABR + TPFSprite + RSZ + ROT + THW).to_bytes(4, byteorder = 'little')

            if THW == 0:
                W = spriteGroup.sprites[spriteNumber].Width
                H = spriteGroup.sprites[spriteNumber].Height << 16

                outputBuffer += (W + H).to_bytes(4, byteorder = 'little')

            rotationAngle = spriteGroup.sprites[spriteNumber].Rotation
            Flag2Reserve = spriteGroup.sprites[spriteNumber].Flag2Reserve << 16
            CSN = spriteGroup.sprites[spriteNumber].CSN << 24
            BNO = spriteGroup.sprites[spriteNumber].BNO << 30
            
            outputBuffer += (Flag2Reserve + rotationAngle + CSN + BNO).to_bytes(4, byteorder = 'little')

            X = spriteGroup.sprites[spriteNumber].XScaling
            Y = spriteGroup.sprites[spriteNumber].YScaling << 16

            outputBuffer += (X + Y).to_bytes(4, byteorder = 'little')

    for CLUTGrp in ANM.CLUTGrps:
        CLUTbnum = CLUTGrp.bnum
        outputBuffer += CLUTbnum.to_bytes(4, byteorder = 'little')

        DX = CLUTGrp.DX
        DY = CLUTGrp.DY << 16
        outputBuffer += (DX + DY).to_bytes(4, byteorder = 'little')

        CLUTW = CLUTGrp.W
        CLUTH = CLUTGrp.H << 16
        outputBuffer += (W + H).to_bytes(4, byteorder = 'little')

        for CLUTEntry in CLUTGrp.CLUTS:
            red = CLUTEntry[0]
            green = CLUTEntry[1] << 5
            blue = CLUTEntry[2] << 10
            alpha = CLUTEntry[3] << 15

            outputBuffer += (red + green + blue + alpha).to_bytes(2, byteorder = 'little')


        

    return outputBuffer

#Returns an array of x,y coords of pixels that mismatch in image 1 and 2
def getDiffPixels(image1, image2):
    changedPixels = []
    if image1.height != image2.height or image1.width != image2.width:
        raise exception("Image dimensions for diff must match")

    for y in range(image1.height):
        for x in range(image1.width):
            if image1.getpixel((x,y))[3] == 0 and image2.getpixel((x,y))[3] == 0:
                continue
            elif not np.array_equal(image1.getpixel((x,y)),image2.getpixel((x,y))):
                changedPixels += [[x,y]]
    return changedPixels

#Replaces a PXL image using a new PNG and a reference PNG, and a given CLUT
def injectPNG(originalPNGPath, newPNGPath, PXLPath, PXLOffset, CLUTFile, CLUTFileOffset, CLUTNumber):
    newPNGImage = Image.open(newPNGPath).convert('RGBA')
    originalPNGImage = Image.open(originalPNGPath).convert('RGBA')

    changedPixels = getDiffPixels(newPNGImage, originalPNGImage)

    if '4bit' in originalPNGPath:
        PMODE = FOUR_BIT_CLUT
    elif '8bit' in originalPNGPath:
        PMODE = EIGHT_BIT_CLUT
    else:
        raise exception("Source PNG must have color depth in filename")


    CLUT = getCLUT(open(CLUTFile, 'rb'), CLUTFileOffset, CLUTNumber, PMODE)

    PXLFile = open(PXLPath, 'r+b')
  
    
    for changedPixel in changedPixels:
        x = changedPixel[0]
        y = changedPixel[1]
        PXLFile.seek(PXLOffset + PXL_HEADER_SIZE)

        if PMODE == EIGHT_BIT_CLUT:
            PXLFile.read(x + originalPNGImage.width*y)
            rawPixel = newPNGImage.getpixel((x,y))
            searchPixel = [rawPixel[0] >>3, rawPixel[1] >>3, rawPixel[2] >>3, 0]
            newPixel = CLUT.index(searchPixel)
            PXLFile.write(newPixel.to_bytes(1, byteorder='little'))

        elif PMODE == FOUR_BIT_CLUT:
            pixelNumber = x + originalPNGImage.width*y
            PXLFile.read(pixelNumber//2)
            rawPixel = newPNGImage.getpixel((x,y))
            searchPixel = [rawPixel[0] >>3, rawPixel[1] >>3, rawPixel[2] >>3, 0] #rawPixel[3]//255 ]
            newPixel = CLUT.index(searchPixel)
            charToEdit = int.from_bytes(PXLFile.read(1), byteorder='little')

            if pixelNumber % 2 == 0:
                charToEdit = (charToEdit & 0b11110000) | newPixel
                #print("Editing pixel " + str(x) + ',' + str(y) + " (byte " + hex(PXLOffset + PXL_HEADER_SIZE + pixelNumber//2) + ") with value " + str(newPixel))
            else:
                charToEdit = (charToEdit & 0b00001111) | (newPixel << 4)
                #print("Editing pixel " + str(x) + ',' + str(y) + " (byte " + hex(PXLOffset + PXL_HEADER_SIZE + pixelNumber//2) + ") with value " + str(newPixel))
            PXLFile.seek(PXLOffset + PXL_HEADER_SIZE)
            PXLFile.read(pixelNumber//2)
            print(hex(PXLFile.tell()))
            PXLFile.write(charToEdit.to_bytes(1, byteorder='little'))
        elif PMODE == SIXTEEN_BIT_CLUT:
            
            PXLFile.read((x + originalPNGImage.width*y)*2)
            rawPixel = newPNGImage.getpixel((x,y))
            searchPixel = [rawPixel[0] >>3, rawPixel[1] >>3, rawPixel[2] >>3, 0]
            newPixel = CLUT.index(searchPixel)
            PXLFile.write(newPixel.to_bytes(2, byteorder='little'))
            pass

            

    for change in changedPixels:
        newPNGImage.putpixel((change[0],change[1]), (255,0,0))

    newPNGImage.show()
    return


#Produces an Image from a given PXL and CLUT
def generatePNG(PXLs, CLTs, width, height, CLUT_Number, PMODE):
    if not os.path.exists(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

    if PMODE == FOUR_BIT_CLUT:
        CLUT_ENTRIES = 0x10
        width = width * 4
    elif PMODE == EIGHT_BIT_CLUT:
        CLUT_ENTRIES = 0x100
        width = width * 2
    else:
        #TODO handle direct color
        print("Failsafe triggered, resorting to 4 bit mode")
        CLUT_ENTRIES = 0x10
        width = width * 4

    arrayBuffer = np.zeros((height, width, 4), dtype=np.uint8)

    
    CLUT_Offset = CLUT_Number * CLUT_ENTRIES


    for pixelNumber in range(len(PXLs)):
        value = PXLs[pixelNumber]

        CLUT_Entry = CLUT_Offset + value
        
        red   = CLTs[CLUT_Entry][0] << 3
        green = CLTs[CLUT_Entry][1] << 3
        blue  = CLTs[CLUT_Entry][2] << 3
        alpha = CLTs[CLUT_Entry][3] << 3
        
        if red == green == blue == alpha == 0:
            alpha = 0
        else:
            alpha = 255

        
        rowNumber    = pixelNumber//width
        columnNumber = pixelNumber % width
        arrayBuffer[rowNumber][columnNumber] = (red, green, blue, alpha)

        #if rowNumber == columnNumber:
        #    print("Pixel " + str(rowNumber) + ": " + str((red, green, blue, alpha)))


    im = Image.fromarray(arrayBuffer, "RGBA")
    #im.show()

    return im

#Returns the offsets to idividual files in a pac file
def getPacOffsets(file):

    pacFile = open(os.path.join(SOURCE_FOLDER,file), "rb")

    numEntries = int.from_bytes(pacFile.read(4), byteorder='little')

    offsets = []
    for entry in range(numEntries):
        offsets += [int.from_bytes(pacFile.read(4), byteorder='little')]

    return offsets


#Extracts every specified PXL and CLT pair into PNG files
def unpackImages():
    for image in IMAGES:
        PXLPath = image[0]
        CLTPath = image[1]

        offsets = getPacOffsets(PXLPath)

        for offset in offsets:
            extractImage(os.path.join(SOURCE_FOLDER,PXLPath), offset, os.path.join(SOURCE_FOLDER,CLTPath), 0)


    return

#generates a file name for a given image
def generateImageFilePath(path,CLUT_Number, offset, PMODE):
    if PMODE == FOUR_BIT_CLUT:
        PMODEString = '4bit'
    else:
        PMODEString = '8bit'
    fileName = os.path.join(OUTPUT_FOLDER, Path(path).name, format(offset,'x') + "_" + str(CLUT_Number).zfill(3) + "_" + PMODEString + '.PNG')
    if not os.path.exists(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)
    if not os.path.exists(os.path.join(OUTPUT_FOLDER, Path(path).name)):
        os.mkdir(os.path.join(OUTPUT_FOLDER, Path(path).name))
    return fileName



#Turns a PXL and corresponding palette file into their corresponding PNG images
def extractImage(PXLFilePath, PXLFileOffest, CLTFilePath, CLTFileOffset):
    PXLFile = open(PXLFilePath, 'rb')
    PXLFile.read(PXLFileOffest)
    
    PXL_ID    = readInt(PXLFile)
    PXL_PMODE = readInt(PXLFile)
    PXL_bnum  = readInt(PXLFile)
    PXL_DX    = readShort(PXLFile)
    PXL_DY    = readShort(PXLFile)
    PXL_W     = readShort(PXLFile)
    PXL_H     = readShort(PXLFile)
    
    CLTFile = open(CLTFilePath, 'rb')
    CLTFile.read(CLTFileOffset)

    CLT_ID    = readInt(CLTFile)
    CLT_PMODE = readInt(CLTFile)
    CLT_bnum  = readInt(CLTFile)
    CLT_DX    = readShort(CLTFile)
    CLT_DY    = readShort(CLTFile)
    CLT_W     = readShort(CLTFile)
    CLT_H     = readShort(CLTFile)
    

    PXLs = readPXLEntries(PXLFile, PXL_PMODE, PXL_bnum - 0xC)
    CLTs = readCLTEntries(CLTFile, (CLT_bnum - 0xC)//2)
    
    if PXL_PMODE == FOUR_BIT_CLUT:
        CLUT_SIZE = 0x20
    elif PXL_PMODE == EIGHT_BIT_CLUT:
        CLUT_SIZE = 0x200
    

    CLUT_COUNT = (CLT_bnum - 0xC)//CLUT_SIZE

    for CLUT_Number in range(CLUT_COUNT):
        image = generatePNG(PXLs, CLTs, PXL_W, PXL_H, CLUT_Number, PXL_PMODE)
        image.save(generateImageFilePath(PXLFilePath, CLUT_Number, PXLFileOffest, PXL_PMODE))
    

#testPXL = "PS1_Base_Project/cd/working/SZGRP/OPT_PXL.PAC"
#testCLT = "PS1_Base_Project/cd/working/SZGRP/OPT.CLS"
#extractImage(testPXL, 0x18, testCLT, 0)

class SpriteFont:
    def __init__(self, symbolName, TPF, ABR, ABE, CSN, CLX, CLY):
        self.symbolName = symbolName
        self.TPF = TPF
        self.ABR = ABR
        self.ABE = ABE
        self.CSN = CSN
        self.CLX = CLX
        self.CLY = CLY

class SpriteImage:
    def __init__(self, symbolName, TPN, BNO, TPF, CSN, CLX, CLY, ABR, ABE, u, v, width, height, xDelta, yDelta, RSZ, ROT):
        self.symbolName = symbolName
        self.TPN = TPN
        self.BNO = BNO
        self.TPF = TPF
        self.CSN = CSN
        self.ABR = ABR
        self.ABE = ABE
        self.CLX = CLX
        self.CLY = CLY
        self.u = u
        self.v = v
        self.width = width
        self.height = height
        self.xDelta = xDelta
        self.yDelta = yDelta
        self.RSZ = RSZ
        self.ROT = ROT
        self.rotation = DEFAULT_ROTATION
        self.XScaling = DEFAULT_SCALING
        self.YScaling = DEFAULT_SCALING
        self.Flag2Reserved = DEFAULT_FLAG2_RESERVE

#returns a list of unique words in a text file
def getWordList(textFilePath, mode):
    textFile = open(textFilePath, 'r', encoding="utf-8")

    wordList = []
    symbols = []

    #Look over each line, finding all words and adding them to the list
    for line in textFile:
        if line.startswith('//'):#Comment line
            continue
        elif line.startswith(FONT_DEF_STRING):#Font Definition line
            fontSymbol = line[line.index('['):line.index(']') + 1]
            symbols.append(fontSymbol)
            continue
        elif line.startswith(IMG_DEF_STRING):#Image Definition line
            imageSymbol = line[line.index('['):line.index(']') + 1]
            symbols.append(imageSymbol)
            continue
        elif line.startswith(SEQUENCE_DEF_STRING):
            continue
        else:
            if mode == WORD_MODE:
                line = line.rstrip('\n')

                for symbol in symbols:#Erase non-text symbols
                    line = line.replace(symbol, '')
                splitLine = re.split(' ',line)
                
                for word in splitLine:#Add each word with the punctuation trimmed
                    cleanWord = word.strip(PUNCTUATION)

                    if cleanWord != '':
                        wordList.append(cleanWord)

                    #Add each punctuation used
                    remainingPunctuation = word.replace(cleanWord, '')
                
                    for char in remainingPunctuation:
                        wordList.append(char)

            elif mode == LETTER_MODE:
                line = line.rstrip('\n')
                for char in line:
                    if char != ' ':
                        wordList.append(char)
            else:
                assert False, "Unknown insertion mode" + mode
                

    #cull duplicate words
    wordList = sorted(list(set(wordList)))

    return wordList

def getLetterTable(tableFilePath):
    tableFile = open(tableFilePath, 'r', encoding="utf-8")

    letters=[]

    for line in tableFile:
        if line.startswith("//"):
            #Skip comments
            continue

        letter  = line.split('=')[-1].rstrip('\n')
        letters.append(letter)

    return letters

#Returns the left and right borders of each letter in the font
def getLetterCoords(fontImage, letterTable, fontColumns, fontHeight):
    
    letterCoords = []

    for letterNumber in range(len(letterTable)):
        rowNumber = letterNumber//fontColumns
        colNumber = letterNumber % fontColumns
        fontWidth = fontImage.width

        tileWidth = fontWidth//fontColumns
        topLeftCoord = tileWidth*colNumber, fontHeight*rowNumber
        bottomRightCoord = tileWidth*(colNumber+1), fontHeight*(rowNumber+1)

        characterTile = fontImage.crop((topLeftCoord + bottomRightCoord))

        alphaColor = ALPHA_COLOR

        #Check how many blank left-hand columns exist
        leftHandBorderFound = False
        rightHandBorderFound = False
        for x in range(tileWidth):
            for y in range(fontHeight):
                if characterTile.getpixel((x,y)) != alphaColor:
                    leftHandBorder = x
                    leftHandBorderFound = True
                    break
            if leftHandBorderFound == True:
                break
                
        #Letter is blank
        if not leftHandBorderFound:
            letterCoords.append([0,0])
            continue
        
        #Check how many blank right-hand columns exist
        for x in reversed(range(tileWidth)):
            for y in range(fontHeight):
                if characterTile.getpixel((x,y)) != alphaColor:
                    rightHandBorder = x
                    rightHandBorderFound = True
                    break
            if rightHandBorderFound == True:
                break

        letterCoords.append([leftHandBorder,rightHandBorder])

    return letterCoords

#Finds locations to put words in the specified free areas and returns the coordinates, and the remaining areas
def arrangeTextIntoImage(wordList, insertionAreas, fontImage, fontColumns, fontHeight, tableFilePath):
    
    wordCoordinates = []

    numRowsList = []
    widthsRemaining = []
    #Find number of rows that the font can fit for each insertion area
    for insertionArea in insertionAreas:
        
        insertionAreaHeight = insertionArea[1][1] - insertionArea[0][1]
        numRows = insertionAreaHeight//fontHeight
        numRowsList.append(numRows)

        #Initialize remaining widths for each available row
        widthsRemainingCurrentArea = []
        for i in range(numRows):
            widthsRemainingCurrentArea.append(insertionArea[1][0] - insertionArea[0][0])

        widthsRemaining.append(widthsRemainingCurrentArea)


    letterTable = getLetterTable(tableFilePath)
    letterWidths = getLetterCoords(fontImage, letterTable, fontColumns, fontHeight)
    

    #Find next available position for word and add to return list
    for word in wordList:
        
    #    for searchWord in wordList:
    #        if word in searchWord and word != searchWord:
    #            wordIndex = searchWord.indexWord

        #Find word width and bounds for each letter
        wordWidth = 0
        letterBounds = []
        for letter in word:
            letterCoordinate = letterTable.index(letter)
            #Letter width = right hand - left hand + 1
            letterWidth = letterWidths[letterCoordinate][1] - letterWidths[letterCoordinate][0] + 1
            wordWidth += letterWidth
            letterBounds.append([letterWidths[letterCoordinate][0], letterWidths[letterCoordinate][1]])
        
        isWidthFound = False
        #Check each insertion area row by row until space is found to fit it
        for insertionAreaNumber in range(len(insertionAreas)):
            for row in range(numRowsList[insertionAreaNumber]):
                
                if wordWidth <= widthsRemaining[insertionAreaNumber][row]:
                    insertionCoordinate = insertionAreas[insertionAreaNumber][1][0] - widthsRemaining[insertionAreaNumber][row]
                    #Insertion area number, X, Y, letter bounds list for word
                    wordCoordinates.append([insertionAreaNumber, insertionCoordinate, row*fontHeight +  insertionAreas[insertionAreaNumber][0][1], letterBounds])
                    widthsRemaining[insertionAreaNumber][row] -= wordWidth
                    isWidthFound = True
                    break
            
            if isWidthFound:
                break

        assert isWidthFound, "No space left to insert word " + word
            

    return wordCoordinates

#Edits the PXL or TIM target files with the given pixel coordinates and values
def applyImageEdit(pixels, images, TPNs):

    imageFiles = []
    imageWidths = []
    
    ImageTPNs = []


    for imagePathNumber in range(len(images)):
        imageFile = open(images[imagePathNumber][0], 'r+b')
        imageFiles.append(imageFile)
        imageFile.read(images[imagePathNumber][1])
        id = readInt(imageFile)

        
        #Clear TIM file to PXL data
        if id == TIM_ID:
            flag = readInt(imageFile)
            PMode = flag & 0b111
            CLUTFlag = (flag & 0b1000) >> 3 

            PXLOffset = 20


            if CLUTFlag == 1:
                CLUTBnum = readInt(imageFile)
                imageFile.read(CLUTBnum - 4)
                PXLOffset += CLUTBnum
            
        
        #Clear PXL header
        else:
            PXLOffset = 20
            flag = readInt(imageFile)
            PMode = flag & 0b1

        PXLbnum = readInt(imageFile)
        PXLdx   = readShort(imageFile)
        PXLdy   = readShort(imageFile)

        PXLtpn = (PXLdx//64) + (PXLdy//256)*16 #Calculate TPN based on texture location
        ImageTPNs.append(PXLtpn)

        if PMode < 3:
            widthFactor = 2-PMode
            width = readShort(imageFile) * (2**widthFactor)
        else:
            width = (readShort(imageFile) * 3) //2
        imageWidths.append(width)
        height = readShort(imageFile)

    for pixel in pixels:
        pixelX = pixel[0]
        pixelY = pixel[1]
        pixelValue = pixel[2]
        pixelInsertionArea = ImageTPNs.index(TPNs[pixel[3]])

        imageFiles[pixelInsertionArea].seek(images[pixelInsertionArea][1] + PXLOffset)

        imageWidth = imageWidths[pixelInsertionArea]

        if PMode == FOUR_BIT_CLUT:
            evenness = pixelX%2 #WARNING, image width must be even
            pixelOffset = (pixelY * (imageWidth//2) + pixelX//2) + images[pixelInsertionArea][1]  + PXLOffset
            imageFiles[pixelInsertionArea].seek(pixelOffset)

            charToEdit = readByte(imageFiles[pixelInsertionArea])
            if evenness == 0:
                byteToAdd = (charToEdit & 0b11110000) |  pixelValue
            else:
                byteToAdd = (charToEdit & 0b00001111) | (pixelValue << 4)
            
            pixelOffset = (pixelY * (imageWidth//2) + pixelX//2) + images[pixelInsertionArea][1]  + PXLOffset

            imageFiles[pixelInsertionArea].seek(pixelOffset)
            imageFiles[pixelInsertionArea].write(byteToAdd.to_bytes(1, byteorder='little'))
        
        elif PMode == EIGHT_BIT_CLUT:
            pixelOffset = (pixelY * (imageWidth) + pixelX) + images[pixelInsertionArea][1] + PXLOffset
            imageFiles[pixelInsertionArea].seek(pixelOffset)
            imageFiles[pixelInsertionArea].write(pixelValue.to_bytes(1, byteorder='little'))
        elif PMode == SIXTEEN_BIT_CLUT:
            pixelOffset = (pixelY * (imageWidth*2) + pixelX*2) + images[pixelInsertionArea][1]  + PXLOffset
            imageFiles[pixelInsertionArea].seek(pixelOffset)
            imageFiles[pixelInsertionArea].write(pixelValue.to_bytes(2, byteorder='little'))
        elif PMode == TWENTYFOUR_BIT_CLUT:
            pixelOffset = (pixelY * (imageWidth*3) + pixelX*3) + images[pixelInsertionArea][1] + PXLOffset
            imageFiles[pixelInsertionArea].seek(pixelOffset)
            imageFiles[pixelInsertionArea].write(pixelValue.to_bytes(3, byteorder='little'))

    for file in imageFiles:
        file.close()

    return

#Reads the next writable glyphs from the line of text and returns the sprites
def readSpritesFromText(line, wordList, wordCoords, fontList, imageList, currentFont, startPoint, fontHeight, TPNs):
    
    intitialX = startPoint[0]
    sprites = []

    
    while line != '':
        if line.startswith(' '):
            startPoint[0] += SPACE_WIDTH
            line = line.replace(' ', '', 1)
            continue
        
        if line.startswith('\n'):
            startPoint[0] = intitialX
            startPoint[1] += NEWLINE_DISTANCE
            line = line.replace('\n', '', 1)
            continue
        
        
        wasFont = False
        for font in fontList:
            if line.startswith(font.symbolName):
                currentFont = font
                line = line.replace(font.symbolName, '', 1)
                wasFont = True
                break
        if wasFont:
            continue
        
        wasImage = False
        for image in imageList:
            if line.startswith(image.symbolName):
                offsetX = startPoint[0] + image.xDelta
                offsetY = startPoint[1] + image.yDelta

                if image.width == image.height and image.width % 8 ==0:
                    THW = image.width >>3
                else:
                    THW = 0

                if image.RSZ != 0:
                    XScaling = image.XScaling
                    YScaling = image.YScaling
                else:
                    XScaling = DEFAULT_SCALING
                    YScaling = DEFAULT_SCALING

                if image.ROT != 0:
                    rotation = image.rotation
                else:
                    rotation = DEFAULT_ROTATION

                sprite = SPRITE(image.u, image.v, offsetX, offsetY, image.CLX, image.CLY, image.ABE, image.TPN, image.ABR, image.TPF, image.RSZ, image.ROT, THW, image.width, image.height, rotation, DEFAULT_FLAG2_RESERVE, image.CSN, image.BNO, XScaling, YScaling)
                sprites.append(sprite)
                startPoint[0] += image.width
                line = line.replace(image.symbolName, '', 1)
                wasImage = True
                break
        if wasImage:
            continue
        
        longestMatch = ''
        for word in wordList:
            if line.startswith(word) and len(word) > len(longestMatch):
                longestMatch = word
        
        if longestMatch != '':
            wordCoordinate = wordCoords[wordList.index(longestMatch)]
            
            spriteTPN = TPNs[wordCoordinate[0]]
            spriteBNO = 0
            #Who the hell knows why BNO is calculated like this
            if currentFont.CLY > 495:
                spriteBNO = 1
            if currentFont.CLX >= 255:
                spriteBNO += 2
            
            #DEBUG
            #spriteBNO = wordCoordinate[0]

            wordU = wordCoordinate[1]
            wordV = wordCoordinate[2]

            width = 0
            for letter in wordCoordinate[3]:
                letterWidth = letter[1] - letter[0] + 1
                width += letterWidth + LETTER_WHITESPACE

            height = fontHeight
            
            sprite = SPRITE(wordU, wordV, startPoint[0], startPoint[1], currentFont.CLX, currentFont.CLY, currentFont.ABE, spriteTPN,  currentFont.ABR, currentFont.TPF, 0, 0, 0, width, height, DEFAULT_ROTATION, DEFAULT_FLAG2_RESERVE, currentFont.CSN, spriteBNO, DEFAULT_SCALING, DEFAULT_SCALING)
            sprites.append(sprite)
            startPoint[0] += width
            line = line.replace(longestMatch, '', 1)
            continue

        assert False, "UNIDENTIFIED GLYPH FOUND AT START OF LINE:" + line


    return sprites

def modifyANM(ANMFilePath, ANMOffset, scriptFilePath, wordList, wordCoords, fontHeight, TPNs):
    
    ANMObj = readANM(open(ANMFilePath, 'rb'), ANMOffset)

    fontList = []
    imageList = []

    currentSequence = -1
    currentStartPoint = [-1,-1]
    currentFont = NULL
    #currentNSprites = 0

    with open(scriptFilePath, 'r', encoding='utf-8') as scriptFile:
        for line in scriptFile:
            if line.startswith('//'):#Skip comments
                continue
            elif line.startswith(FONT_DEF_STRING):#Font Definition line
                fontSymbol = line[line.index('['):line.index(']') + 1]

                fontParameters = ['fontSymbol','TPF', 'ABR', 'ABE', 'CSN', 'CLX', 'CLY']

                paramStartIndex = line.index(fontSymbol) + len(fontSymbol) + 1

                line = line[paramStartIndex:]
                line = line.rstrip('\n').strip()

                parameters = line.split(',')

                fontSymbol, TPF, ABR, ABE, CSN, CLX, CLY =fontSymbol,0,0,0,0,0,0
                params = [fontSymbol, TPF, ABR, ABE, CSN, CLX, CLY]

                for parameter in parameters:
                    parameter = parameter.strip()

                    parameterName  =     parameter.split('=')[0]
                    parameterValue = int(parameter.split('=')[1])

                    constructorIndex = fontParameters.index(parameterName)
                    params[constructorIndex] = parameterValue

                spriteFont = SpriteFont(*params)
                fontList.append(spriteFont)

                #Default font is first in the list
                if currentFont == NULL:
                    currentFont = spriteFont

            elif line.startswith(IMG_DEF_STRING):#Image Definition line
                imageSymbol = line[line.index('['):line.index(']') + 1]
                imageParameters = ['imageSymbol', 'TPN', 'BNO', 'TPF', 'CSN', 'CLX', 'CLY', 'ABR', 'ABE', 'u', 'v', 'width', 'height', 'xDelta', 'yDelta', 'RSZ', 'ROT']
                paramStartIndex = line.index(imageSymbol) + len(imageSymbol) + 1
                line = line[paramStartIndex:]
                line = line.rstrip('\n').strip()

                parameters = line.split(',')

                TPN, BNO, TPF, CSN, CLX, CLY, ABR, ABE, u, v, width, height, xDelta, yDelta, RSZ, ROT = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
                params = [imageSymbol, TPN, BNO, TPF, CSN, CLX, CLY, ABR, ABE, u, v, width, height, xDelta, yDelta, RSZ, ROT]

                for parameter in parameters:
                    parameter = parameter.strip()

                    parameterName  =     parameter.split('=')[0]
                    parameterValue = int(parameter.split('=')[1])

                    constructorIndex = imageParameters.index(parameterName)
                    params[constructorIndex] = parameterValue

                #If unspecified, set default scaling and rotation
                spriteImage = SpriteImage(*params)
                if ROT == 0:
                    spriteImage.rotation = DEFAULT_ROTATION

                if RSZ == 0:
                    spriteImage.XScaling = DEFAULT_SCALING
                    spriteImage.YScaling= DEFAULT_SCALING

                
                imageList.append(spriteImage)
            elif line.startswith(SEQUENCE_DEF_STRING):#Sequence header
                currentSequence = int(line[line.index(' ') + 1:line.index('>>>')])#isolate number in sequence header
                currentStartCoords = line[line.index('(') + 1:line.index(')')]
                currentStartPoint = [int(currentStartCoords.split(',')[0]), int(currentStartCoords.split(',')[1])]
                seq = ANMObj.sequences[currentSequence]
                ANMObj.spriteGroups[seq.spriteGrpNumber].sprites = []#Clear Sprite group for new injection
                ANMObj.spriteGroups[seq.spriteGrpNumber].NSprite = 0 #

            elif currentSequence != -1:
                
                nextSprites = readSpritesFromText(line, wordList, wordCoords, fontList, imageList, currentFont, currentStartPoint, fontHeight, TPNs)

                sequence = ANMObj.sequences[currentSequence]
                spriteGroup = ANMObj.spriteGroups[sequence.spriteGrpNumber]
                #nSprites = len(spriteGroup)
                #currentNSprites += nSprites

                for sprite in nextSprites:
                    ANMObj.spriteGroups[sequence.spriteGrpNumber].sprites.append(sprite)
                    ANMObj.spriteGroups[sequence.spriteGrpNumber].NSprite += 1
                    

    #Jingle cats has reserved flag set to 1 for first sprite of each sequence because ???
    if GAME_NAME == "Jingle Cats":
        for sequence in ANMObj.sequences:
            spriteGrp = ANMObj.spriteGroups[sequence.spriteGrpNumber]
            spriteGrp.sprites[0].Flag2Reserve = 1
                

    return ANMObj

#inserts the data into slot fileNumber and returns the bytes object
def editPAC(filePath, fileNumber, data):
    file = open(filePath, 'rb')
    
    outputBuffer = b''
    filesContained = readInt(file) #read first int, numFiles
    outputBuffer += filesContained.to_bytes(4, byteorder='little')
    
    offsets = []
    datas = []

    for x in range(filesContained):
        file.seek((x + 1)*4)
        offset = readInt(file)
        offsets.append(offset)

    for x in range(filesContained):
        file.seek(offsets[x])
        
        if x != filesContained - 1:
            fileSize = offsets[x + 1] - offsets[x]
            filedata = file.read(fileSize)
        else:
            filedata = file.read()

        datas.append(filedata)

    datas[fileNumber] = data
    currentSize = (4*(filesContained + 1))
    outputBuffer += currentSize.to_bytes(4, byteorder='little')#write First entry

    for dataNumber in range(len(datas) - 1):
        outputBuffer += (currentSize + len(datas[dataNumber])).to_bytes(4, byteorder='little')
        currentSize += len(datas[dataNumber])
    
    for dataNumber in range(len(datas)):
        outputBuffer += datas[dataNumber]

    file.close()
    outputFile = open(filePath, 'wb')
    outputFile.write(outputBuffer)
    outputFile.close()

    return outputBuffer

#Adds the text in the text file to the corresponding insertion images for ANM, and returns the ANM object, and the widths remaining in the injection areas
def injectText(ANMFilePath, ANMOffsets, images, insertionAreaImages, insertionAreas, fontImagePath, fontCLUTs, textFilePaths, tableFilePath, mode):
    #targetImages = []
    #Load target images
    #for imagePath in targetImagePaths:
    #    image = Image.open(imagePath, 'RGBA')
    #    targetImages.append(image)
    
    #Load font image and read parameters
    fontImage = Image.open(fontImagePath).convert("RGBA")
    
    tableFile = open(tableFilePath,'r', encoding='utf-8')
    header1 = tableFile.readline()
    header2 = tableFile.readline()
    numColumns = int(header1.split('=')[-1].rstrip('\n'))
    fontHeight = int(header2.split('=')[-1].rstrip('\n'))

    wordList = []
    #Load word list
    for textFilePath in textFilePaths:
        wordList += (getWordList(textFilePath, mode))
    wordList = list(dict.fromkeys(wordList)) #remove dupes

    #letterWidths = getLetterCoords(fontImage, letterTable, numColumns, fontHeight, fontCLUT)
    letterTable = getLetterTable(tableFilePath)

    #Insertion area number, X, Y, letter bounds list for word
    wordCoords = arrangeTextIntoImage(wordList, insertionAreas, fontImage, numColumns, fontHeight, tableFilePath)
    injectionPixels = []

    ANMs = []
    imageTPNs = []
    TPNs = []
    #Generate TPN mappings
    for image in images:
        if image[0].endswith('.TIM') or image[0].endswith('.tim'):
            img = TIM(open(image[0], 'rb'))
            pass
        else:
            img = PXL(open(image[0], 'rb'))
            pass
        imageTPNs.append(img.TPN)

    for imageNumber in insertionAreaImages:
        TPNs.append(imageTPNs[imageNumber])

    #Iterate over word objects, copying each letter to target area
    for coordNumber in range(len(wordCoords)):
        insertionAreaNumber = wordCoords[coordNumber][0]
        wordX = wordCoords[coordNumber][1]
        wordY = wordCoords[coordNumber][2]
        letterBounds = wordCoords[coordNumber][3]
        
        word = wordList[coordNumber]

        
        positionInWordX = 0
        for letterIndex in range(len(word)):
            letterNumber = letterTable.index(word[letterIndex])
            letterTileWidth = fontImage.width//numColumns
            letterXStart = (letterNumber % numColumns) * letterTileWidth 
            letterYStart = (letterNumber//numColumns)* fontHeight
            
            letterTopLeft = letterXStart+ letterBounds[letterIndex][0], letterYStart
            letterBottomRight = letterXStart + letterBounds[letterIndex][1], letterYStart + fontHeight
            
            
            #Iterate over all pixels in range
            for y in range(letterBottomRight[1] - letterTopLeft[1]):
                for x in range(letterBottomRight[0] - letterTopLeft[0] + 1):
                    fontPixel = fontImage.getpixel((letterTopLeft[0] + x, letterTopLeft[1] + y))
                    PXLvalue = fontCLUTs[imageTPNs.index(TPNs[insertionAreaNumber])].index(fontPixel)
                    assert PXLvalue >= 0, "Font pixel " + str(x) + "," + str(y) + " is undefined in CLUT!"
                    injectionPixels.append([wordX + x + positionInWordX, wordY + y, PXLvalue, insertionAreaNumber])
            positionInWordX += letterBottomRight[0] - letterTopLeft[0] + 1
    

    #Edit TIM/PXL images
    applyImageEdit(injectionPixels, images, TPNs)

    #Generate ANMs
    for textFileNumber in range(len(textFilePaths)):
        ANMs.append(modifyANM(ANMFilePath, ANMOffsets[textFileNumber], textFilePaths[textFileNumber], wordList, wordCoords, fontHeight, TPNs))

    return ANMs


def findANMOffsets(ANMFile):
    ANM_ID = 0x40000321

    offsets = []
    ANMFile.seek(0, os.SEEK_END)
    size = ANMFile.tell()
    ANMFile.seek(0)
    for word in range(size//4):
        readWord = readInt(ANMFile)
        if readWord == ANM_ID:
            offsets.append(word*4)

    return offsets


def unpackBGDCEL(CELs, BGDs, PXLs, CLTs):
    cellImages = []
    for cel in CELs:
        for cellNumber in range(cel.NCELL):
            
            #Find correct PXL match
            PXLFound = False
            for pxl in PXLs:
                BANK_WIDTH = 64
                SHELF_WIDTH = 16
                SHELF_HEIGHT = 256
                pxlDX = pxl.DX
                pxlDY = pxl.DY

                shelfNumber = cel.CELLS[cellNumber].TPN // SHELF_WIDTH

                if shelfNumber == 0:
                    spriteDY = 0
                elif shelfNumber == 1:
                    spriteDY = SHELF_HEIGHT

                spriteDX = (cel.CELLS[cellNumber].TPN % SHELF_WIDTH) * BANK_WIDTH

                
                spriteIsInRangeX = spriteDX >= pxl.DX and spriteDX < (pxl.DX + pxl.W)
                spriteIsInRangeY = spriteDY >= pxl.DY and spriteDY < (pxl.DY + pxl.H)

                if spriteIsInRangeX and spriteIsInRangeY:
                    pxlMatch = pxl
                    PXLFound = True
                    break
            
            #Find correct CLT match
            clutFound = False
            for searchCLUT in CLTs:
                # %20?
                trueCLUTX = 0x10 *(cel.CELLS[cellNumber].CLX % 20) - searchCLUT.DX
                trueCLUTY = cel.CELLS[cellNumber].CLY - searchCLUT.DY

                if trueCLUTX < searchCLUT.W and trueCLUTY < searchCLUT.H and trueCLUTX >= 0 and trueCLUTY >= 0:
                    #Correct CLUT found
                    clutFound = True
                    break
            
            if searchCLUT.PMODE == FOUR_BIT_CLUT:
                clutNumber = trueCLUTY + trueCLUTX
            elif searchCLUT.PMODE == EIGHT_BIT_CLUT:
                clutNumber = trueCLUTY + 0x10 * trueCLUTX
            else:
                print("TPF Failsafe triggered, resorting to 4bit color")
                clutNumber = trueCLUTY + trueCLUTX
                #raise exception("INVALID CLUT ")

            totalImage = generatePNG(pxlMatch.PXLData, searchCLUT.CLUTs, pxlMatch.W, pxlMatch.H, clutNumber, searchCLUT.PMODE) #sprite.CSN
            
            cellImage = totalImage.crop((cel.CELLS[cellNumber].u, cel.CELLS[cellNumber].v, cel.CELLS[cellNumber].u + BGDs[CELs.index(cel)].CELLW, cel.CELLS[cellNumber].v + BGDs[CELs.index(cel)].CELLH))
            if cel.CELLS[cellNumber].HLP != 0:
                cellImage = Image.transpose(method=Image.FLIP_LEFT_RIGHT)
            if cel.CELLS[cellNumber].VLP != 0:
                cellImage = Image.transpose(method=Image.FLIP_TOP_BOTTOM)

            cellImages.append(cellImage)
    
    for bgdNumber in range(len(BGDs)):
        bgdImage = Image.new('RGBA', (BGDs[bgdNumber].MAPW * BGDs[bgdNumber].CELLW, BGDs[bgdNumber].MAPH * BGDs[bgdNumber].CELLH), (0,0,0,0))

        for y in range(BGDs[bgdNumber].MAPH):
            for x in range(BGDs[bgdNumber].MAPW):
                cellNum = BGDs[bgdNumber].MAP[x + y * BGDs[bgdNumber].MAPW]
                bgdImage.paste(cellImages[cellNum], (x * BGDs[bgdNumber].CELLW, y * BGDs[bgdNumber].CELLH))
        
        bgdImage.show()



    return

#Updates the given ANI file and returns the new and old ANM file offsets 
def updateANI(ANMs, offsets, ANMFilePath):
    '''Edits the ANM files within an ANI package, given some ANM objects and their original offsets'''
    ANMstartID = "21030040"
    

    #Find offsets of original file
    originalFilePath = os.path.join(HAR_ORIGINAL_FOLDER,ANMFilePath.split('/', 1)[1])
    ANIdataOriginal = open(originalFilePath, 'rb').read().hex()
    intSplitsOriginal = re.findall('.'*8, ANIdataOriginal) #split file into 4 byte words for matching ANM start IDs
    ANMstartOffsetsOriginal = [i*4 for i, x in enumerate(intSplitsOriginal) if (x == ANMstartID)]
    #for offset in ANMstartOffsetsOriginal: #Remove non-aligned matches
    #    if offset % 4 != 0:
    #        ANMstartOffsetsOriginal.remove(offset)

    #Add each ANM to package one by one
    for ANMnumber in range(len(ANMs)):
        originalOffset = offsets[ANMnumber]
        ANIindex = ANMstartOffsetsOriginal.index(originalOffset)
        
        #Find offsets of modified file
        ANIdata = open(ANMFilePath, 'rb').read().hex()
        intSplits = re.findall('.'*8, ANIdata) #split file into 4 byte words for matching ANM start IDs
        ANMstartOffsets = [i*4 for i, x in enumerate(intSplits) if (x == ANMstartID)]
        #for offset in ANMstartOffsets: #Remove non-aligned matches
        #    if offset % 4 != 0:
        #        ANMstartOffsets.remove(offset)

        targetOffset = ANMstartOffsets[ANIindex]

        header = ANIdata[0:targetOffset*2]
        if ANIindex == len(ANMstartOffsets) - 1:
            #Add anm obj to last entry
            footer = ''
        else:
            #Add anm obj to not last entry
            footer = ANIdata[ANMstartOffsets[ANIindex + 1]*2:]

        
        
        newData = bytes.fromhex(header) + repackANM(ANMs[ANMnumber]) + bytes.fromhex(footer)

        outFile = open(ANMFilePath, 'wb')
        outFile.write(newData)
        outFile.close()

        
    ANIdata = open(ANMFilePath, 'rb').read().hex()
    intSplits = re.findall('.'*8, ANIdata) #split file into 4 byte words for matching ANM start IDs
    ANMstartOffsets = [i*4 for i, x in enumerate(intSplits) if (x == ANMstartID)]
    #for offset in ANMstartOffsets: #Remove non-aligned matches
    #    if offset % 4 != 0:
    #        ANMstartOffsets.remove(offset)

    return ANMstartOffsets, ANMstartOffsetsOriginal


def updateHarmfulParkOffsets(ANMFilePath, newOffsets, oldOffsets, EXEPath):
    '''Updates the given ANI file offsets for a given ANI file in the Harmful Park EXE'''
    EXEfile = open(EXEPath, 'rb')
    originalEXEPath = os.path.join(HAR_ORIGINAL_FOLDER, EXEPath.split('/',1)[1])
    originalANMPath = os.path.join(HAR_ORIGINAL_FOLDER,ANMFilePath.split('/',1)[1])
    originalANMSize = os.path.getsize(originalANMPath)
    newANMSize = os.path.getsize(ANMFilePath)
    EXEfileOriginal = open(originalEXEPath, 'rb')
    originalEXEhex = EXEfileOriginal.read().hex()
    
    tableToFind = b''

    cursor = 0 #Build table to search for in original EXE
    for offsetNumber in range(len(oldOffsets)):
        if oldOffsets.index(oldOffsets[offsetNumber]) != len(oldOffsets) - 1:
            size = oldOffsets[offsetNumber + 1] - oldOffsets[offsetNumber]
        else:
            size = originalANMSize - oldOffsets[offsetNumber]
        cursor += size
        tableToFind += size.to_bytes(4, 'little')

    tableToInject = b''
    for offsetNumber in range(len(newOffsets)):
        if newOffsets.index(newOffsets[offsetNumber]) != len(newOffsets) - 1:
            size = newOffsets[offsetNumber + 1] - newOffsets[offsetNumber]
        else:
            size = newANMSize - newOffsets[offsetNumber]
        cursor += size
        tableToInject += size.to_bytes(4, 'little')

    try:
        tableOffset = originalEXEhex.index(tableToFind.hex()) //2 #Find offset of table in bytes
    except ValueError:
        print("Table not found for " + ANMFilePath)
        return

    EXEfile.seek(0)
    outfileData = EXEfile.read(tableOffset)
    outfileData += tableToInject
    EXEfile.seek(tableOffset + len(tableToInject))
    outfileData += EXEfile.read()
    EXEfile.close()
    
    outfile = open(HAR_EXE_PATH, 'wb')
    outfile.write(outfileData)
    outfile.close()
    


    return

def testInjectText():
    images = [["PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",0xC, 7],  ["PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",0x8020, 8]]
    #targetImagePaths = ["PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC"]
    #targetImageOffsets = [0xC, 0x8020, 0x8020, 0x8020, 0x8020, 0x8020]
    insertionAreas = [[[0,0],[256,256]], [[16,0],[256, 80]], [[0,80],[160,112]], [[160,134], [256,256]], [[16,112], [160,128]], [[208, 80], [256, 112]]]
    insertionAreaTPNs = [7,8,8,8,8,8]
    fontImagePath = "font/fontmk3.png"
    fontCLUT = [(0,0,0,0), (64,56,56,255), (), (), (0,0,0,255), (184,184,184,255)]
    textFilePaths = ["test.txt"]
    tableFilePath = "table.txt"
    ANMFilePath = "PS1_Base_Project/cd/working/ANM/GUID_ANS.PAC"
    offsets = [0xC]
    newANMs = injectText(ANMFilePath, offsets, images, insertionAreas, fontImagePath, fontCLUT, textFilePaths, tableFilePath)
    

    editPAC(ANMFilePath, 0, repackANM(newANMs[0]))

    return

def testeditHarmfulParkText():
    images = [["HAR/DTIM1/CU0102.TIM", 0x0, 27]]
    insertionAreas = [[[0,0],[256,36]], [[0,32],[196, 52]], [[0,52],[136,68]]]
    insertionAreaImages = [0,0,0]
    fontImagePath = "font/fontmk3.png"
    fontCLUT = [(0,0,0,0), (), (), (), (),(),(),(),(),(),(),(64,56,56,255), (184,184,184,255)]
    textFilePaths = ["script/ANIMESA_1012.txt", "script/ANIMESA_1140.txt","script/ANIMESA_3832.txt","script/ANIMESA_3920.txt"]
    tableFilePath = "table.txt"
    ANMFilePath = "HAR/DTIM1/ANIMEA.ANI"
    oldANMFilePath = "HAR Original/DTIM1/ANIMEA.ANI"
    oldOffsets = [1012, 1140, 3832, 3920]
    
    ANMs = injectText(oldANMFilePath, oldOffsets, images, insertionAreaImages, insertionAreas, fontImagePath, fontCLUT, textFilePaths, tableFilePath)

    newOffsets, oldOffsetsAll = updateANI(ANMs, oldOffsets, ANMFilePath)

    updateHarmfulParkOffsets(ANMFilePath, newOffsets, oldOffsetsAll, HAR_EXE_PATH)


    return


#testJSON()

def testInjectTextTIM():
    BNOs = [["PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",0xC],  ["PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",0x8020]]
    #targetImagePaths = ["PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC",
    #                    "PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC"]
    #targetImageOffsets = [0xC, 0x8020, 0x8020, 0x8020, 0x8020, 0x8020]
    insertionAreas = [[[0,0],[256,256]], [[16,0],[256, 80]], [[0,80],[160,112]], [[160,134], [256,256]], [[16,112], [160,128]], [[208, 80], [256, 112]]]
    insertionAreaBNOIndices = [0,1,1,1,1,1]
    fontImagePath = "font/fontmk3.png"
    fontCLUT = [(0,0,0,0), (64,56,56,255), (), (), (0,0,0,255), (184,184,184,255)]
    textFilePath = "test.txt"
    tableFilePath = "table.txt"
    ANMFilePath = "PS1_Base_Project/cd/working/ANM/GUID_ANS.PAC"
    offset = 0xC
    newANM = injectText(ANMFilePath, offset, BNOs, insertionAreaBNOIndices, insertionAreas, fontImagePath, fontCLUT, textFilePath, tableFilePath)
    editPAC(ANMFilePath, 0, repackANM(newANM))

    return

#testInjectText()

def testANMReading():
    PXLFile1 = open("PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC", "rb")
    PXLFile1.seek(0x8020)
    PXLFile0 = open("PS1_Base_Project/cd/working/ANM/GUID_PXL.PAC", "rb")
    PXLFile0.seek(0xC)
    CLSFile = open("PS1_Base_Project/cd/working/ANM/P00.CLS", "rb")
    #clut = readCLTEntries(CLSFile, 0x200)

    animateANM(readANM(open("PS1_Base_Project/cd/working/ANM/GUID_ANS.PAC", 'rb'), 0xc), [PXL(PXLFile0) ,PXL(PXLFile1)]  , [CLT(CLSFile)])
#testANMReading()


def testTIMANMReading():
    tims1 = [TIM(open("HAR/DATA6/BO0601.TIM", "rb")),
            TIM(open("HAR/DATA6/BO0602.TIM", "rb")),
            TIM(open("HAR/DATA6/STG0601.TIM", "rb")),
            TIM(open("HAR/DATA6/STG0602.TIM", "rb")),
            TIM(open("HAR/DATA6/STG0603.TIM", "rb")),
            TIM(open("HAR/DATA6/STG0604.TIM", "rb")),
            TIM(open("HAR/DATA6/BG0601.TIM", "rb")),
            TIM(open("HAR/DATA6/BG0602.TIM", "rb")),
            TIM(open("HAR/DATA6/BG0603.TIM", "rb")),
            TIM(open("HAR/DATA6/BG0604.TIM", "rb")),
            TIM(open("HAR/DATA6/BG0605.TIM", "rb")),
            TIM(open("HAR/DATA6/BG0606.TIM", "rb"))]

    tims2 = [TIM(open("HAR/DTIMST/OP1.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP2.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP3.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP4.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP5.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP6.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP7.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP8.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP9.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP10.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP11.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP12.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP13.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP14.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP15.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP16.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP17.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP18.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP19.TIM", "rb")),
            TIM(open("HAR/DTIMST/OP20.TIM", "rb")),]

    tims3 = [TIM(open("HAR/DTIMEND/ED0000.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0001.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0100.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0200.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0201.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0300.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0500.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0501.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0600.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0700.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0800.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0900.TIM", "rb"))]     

    tims4 = [TIM(open("HAR/DATA5/BO0501.TIM", "rb")),
            TIM(open("HAR/DATA5/BO0502.TIM", "rb")),
            TIM(open("HAR/DATA5/STG0501.TIM", "rb")),
            TIM(open("HAR/DATA5/STG0502.TIM", "rb")),
            TIM(open("HAR/DATA5/STG0503.TIM", "rb")),
            TIM(open("HAR/DATA5/STG0504.TIM", "rb")),
            TIM(open("HAR/DATA5/BG0501.TIM", "rb")),
            TIM(open("HAR/DATA5/BG0502.TIM", "rb")),
            TIM(open("HAR/DATA5/BG0503.TIM", "rb")),
            TIM(open("HAR/DATA5/BG0504.TIM", "rb")),
            TIM(open("HAR/DATA5/BG0505.TIM", "rb")),
            TIM(open("HAR/DATA5/BG0506.TIM", "rb"))]

    tims5 = [TIM(open("HAR/DTIM1/CU0102.TIM", "rb")), TIM(open("HAR/DTIM1/CU0101.TIM", "rb"))
    ]

    pxls = []
    clts = []

    ANMFilePath = "HAR/DATA6/ANIME6.ANI"
    ANMFilePath2 ="HAR/DTIMST/ANIMES.ANI"
    ANMFilePath3 ="HAR/DTIMEND/ANIMEQ.ANI"
    ANMFilePath4 = "HAR/DATA5/ANIME5.ANI"
    ANMFilePath5 = "HAR/DTIM1/ANIMEA.ANI"
    
    ANMFile = open(ANMFilePath3, 'rb')
    offsets = findANMOffsets(ANMFile)

    for tim in tims3:
        pxl, clt = extractTIM(tim)
        pxls.append(pxl)
        clts.append(clt)

    for offset in offsets:
        ANMobj = readANM(open(ANMFilePath3, 'rb'), offset)
        animateANM(ANMobj, pxls ,clts)

#testTIMANMReading()

def testBGDCELReading():
    CELobjs = [CEL(open("HAR/DATA3/BG0302.CEL", 'rb'))]
    BGDobjs = [BGD(open("HAR/DATA3/BG0302.BGD", 'rb'))]

    tims =  [TIM(open("HAR/DTIMEND/ED0000.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0001.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0100.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0200.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0201.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0300.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0500.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0501.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0600.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0700.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0800.TIM", "rb")),
            TIM(open("HAR/DTIMEND/ED0900.TIM", "rb"))]
    
    tims2 = [TIM(open("HAR/DATA1/BG0101.TIM", 'rb')),
            TIM(open("HAR/DATA1/BG0102.TIM", 'rb')),
            TIM(open("HAR/DATA1/BG0103.TIM", 'rb')),
            TIM(open("HAR/DATA1/BG0104.TIM", 'rb')),
            TIM(open("HAR/DATA1/BG0105.TIM", 'rb')),
            TIM(open("HAR/DATA1/BO0101.TIM", 'rb')),
            TIM(open("HAR/DATA1/BO0102.TIM", 'rb')),
            TIM(open("HAR/DATA1/STG0101.TIM", 'rb')),
            TIM(open("HAR/DATA1/STG0102.TIM", 'rb')),
            TIM(open("HAR/DATA1/STG0104.TIM", 'rb')),
            TIM(open("HAR/DATA1/STG0105.TIM", 'rb'))
            ]

    tims3 = [TIM(open("HAR/DATA2/BG0201.TIM", 'rb')),
            TIM(open("HAR/DATA2/BG0202.TIM", 'rb')),
            TIM(open("HAR/DATA2/BG0203.TIM", 'rb')),
            TIM(open("HAR/DATA2/BG0204.TIM", 'rb')),
            TIM(open("HAR/DATA2/BG0205.TIM", 'rb')),
            #TIM(open("HAR/DATA1/BO0101.TIM", 'rb')),
            #TIM(open("HAR/DATA1/BO0102.TIM", 'rb')),
            #TIM(open("HAR/DATA1/STG0101.TIM", 'rb')),
            #TIM(open("HAR/DATA1/STG0102.TIM", 'rb')),
            #TIM(open("HAR/DATA1/STG0104.TIM", 'rb')),
            #TIM(open("HAR/DATA1/STG0105.TIM", 'rb'))
            ]

    tims4 = [TIM(open("HAR/DATA4/BG0401.TIM", 'rb')),
            TIM(open("HAR/DATA4/BG0402.TIM", 'rb')),
            TIM(open("HAR/DATA4/BG0403.TIM", 'rb')),
            TIM(open("HAR/DATA4/BG0404.TIM", 'rb')),
            TIM(open("HAR/DATA4/BG0405.TIM", 'rb')),
            TIM(open("HAR/DATA4/BO0401.TIM", 'rb')),
            TIM(open("HAR/DATA4/BO0402.TIM", 'rb')),
            TIM(open("HAR/DATA4/STG0401.TIM", 'rb')),
            TIM(open("HAR/DATA4/STG0402.TIM", 'rb')),
            TIM(open("HAR/DATA4/STG0403.TIM", 'rb')),
            TIM(open("HAR/DATA4/STG0404.TIM", 'rb'))
            ]

    tims5 = [TIM(open("HAR/DATA5/BG0501.TIM", 'rb')),
            TIM(open("HAR/DATA5/BG0502.TIM", 'rb')),
            TIM(open("HAR/DATA5/BG0503.TIM", 'rb')),
            TIM(open("HAR/DATA5/BG0504.TIM", 'rb')),
            TIM(open("HAR/DATA5/BG0505.TIM", 'rb')),
            TIM(open("HAR/DATA5/BG0506.TIM", 'rb')),
            TIM(open("HAR/DATA5/BO0501.TIM", 'rb')),
            TIM(open("HAR/DATA5/BO0502.TIM", 'rb')),
            TIM(open("HAR/DATA5/STG0501.TIM", 'rb')),
            TIM(open("HAR/DATA5/STG0502.TIM", 'rb')),
            TIM(open("HAR/DATA5/STG0503.TIM", 'rb')),
            TIM(open("HAR/DATA5/STG0504.TIM", 'rb'))
            ]

    tims5 = [TIM(open("HAR/DATA3/BG0301.TIM", 'rb')),
            TIM(open("HAR/DATA3/BG0302.TIM", 'rb')),
            TIM(open("HAR/DATA3/BG0303.TIM", 'rb')),
            TIM(open("HAR/DATA3/BG0304.TIM", 'rb')),
            TIM(open("HAR/DATA3/BG0305.TIM", 'rb')),
            TIM(open("HAR/DATA3/BO0301.TIM", 'rb')),
            TIM(open("HAR/DATA3/BO0302.TIM", 'rb')),
            TIM(open("HAR/DATA3/STG0301.TIM", 'rb')),
            TIM(open("HAR/DATA3/STG0302.TIM", 'rb')),
            TIM(open("HAR/DATA3/STG0303.TIM", 'rb')),
            TIM(open("HAR/DATA3/STG0304.TIM", 'rb')),
            TIM(open("HAR/DATA3/STG0305.TIM", 'rb'))
            ]

    pxls = []
    clts = []

    for tim in tims5:
        pxl, clt = extractTIM(tim)
        pxls.append(pxl)
        clts.append(clt)

    unpackBGDCEL(CELobjs, BGDobjs, pxls, clts)
    return

#testBGDCELReading()
#testTIMANMReading()

def extractFolder():
    folder = sys.argv[1]
    
    ANMList = []
    ANMFiles = []
    ANMOffsets = []
    CELList = []
    BGDList = []
    TIMList = []
    PXLList = []
    CLTList = []
    for file in os.listdir(folder):
        if file.endswith("ANI"):
            ANMList.append(os.path.join(folder, file))
        elif file.endswith("TIM"):
            TIMList.append(TIM(open(os.path.join(folder, file), 'rb')))
        elif file.endswith("CEL"):
            CELList.append(CEL(open(os.path.join(folder, file), 'rb')))
        elif file.endswith("BGD"):
            BGDList.append(BGD(open(os.path.join(folder, file), 'rb')))
        elif file.endswith("PXL"):
            PXLList.append(PXL(open(os.path.join(folder, file), 'rb')))
        elif file.endswith(CLTList):
            CLTList.append(CLT(open(os.path.join(folder, file), 'rb')))
    
    for tim in TIMList:
        pxl, clt = extractTIM(tim)
        PXLList.append(pxl)
        CLTList.append(clt)

    for anm in ANMList:
        ANMFile = open(ANMList[ANMList.index(anm)], 'rb')
        offsets = findANMOffsets(ANMFile)
        ANMOffsets.append(offsets)
        ANMFiles.append(ANMFile)

    for anmNumber in range(len(ANMList)):
        for offset in ANMOffsets[anmNumber]:
            ANMobj = readANM(open(ANMList[anmNumber], 'rb'), offset)
            animateANM(ANMobj, PXLList ,CLTList)


    unpackBGDCEL(CELList, BGDList, PXLList, CLTList)
    return


#extractFolder()

def testANMRepacking():
    ANMData = repackANM(readANM(open("GUID_ANM1.ANM", 'rb'), 0))
    ANMFile = open("ANMTEST.bin", 'wb')
    ANMFile.write(ANMData)
    ANMFile.close()

#testANMRepacking()

def testUnpackingImages():
    #testPXL = "PS1_Base_Project/cd/working/SZSTAGE/ST0_PXL.PAC"
    #testCLT = "PS1_Base_Project/cd/working/SZSTAGE/ST0.CLS"
    #extractImage(testPXL, 0xC, testCLT, 0)
    unpackImages()

def testImageInjection():    
    injectPNG("TEST/ST0_PXL.PAC/c_000_8bit.PNG", "c_000_8bit.PNG",  "PS1_Base_Project/cd/working/SZSTAGE/ST0_PXL.PAC", 0xC, "PS1_Base_Project/cd/working/SZSTAGE/ST0.CLS", 0, 0)
    injectPNG("TEST/OPT_PXL.PAC/18_000_4bit.PNG", "18_000TEST.PNG",  "PS1_Base_Project/cd/working/SZGRP/OPT_PXL.PAC", 0x18, "PS1_Base_Project/cd/working/SZGRP/OPT.CLS", 0, 0)