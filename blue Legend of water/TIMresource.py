#Contains a number of resources for using PS1 image files
from PIL import Image,ImageDraw
import os
import numpy as np
import copy

#User configurable values
OUTPUT_FOLDER = "OUTPUT"
LOG_FOLDER = "LOG"
#End of user configurable values

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



#Reads little endian int from file and advances cursor
def readInt(file):
    integer = int.from_bytes(file.read(4), byteorder='little')
    return integer

#Reads little endian short from file and advances cursor
def readShort(file):
    readShort = int.from_bytes(file.read(2), byteorder='little')
    return readShort

#Reads little endian byte from file and advances cursor
def readByte(file):
    readByte = int.from_bytes(file.read(1), byteorder='little')
    return readByte

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

        elif PMODE == SIXTEEN_BIT_CLUT:
            PXL_Entries += [pixels]

        else:
            raise ValueError("UNRECOGNIZED PMODE")

    return PXL_Entries

def readCLTEntries(file, numEntries):
    CLT_Entries = []
    for x in range(numEntries):
        entry = readShort(file)

        red   =  entry & 0b0000000000011111
        green = (entry & 0b0000001111100000) >> 5
        blue  = (entry & 0b0111110000000000) >>10
        alpha = (entry & 0b1000000000000000) >> 15

        CLT_Entries += [[red, green, blue, alpha]]


    return CLT_Entries


class CLUT:
    def __init__(self, *args):

        if len(args) == 1:
            
            self.bnum = readInt(args[0])
            self.DX = readShort(args[0])
            self.DY = readShort(args[0])
            self.W = readShort(args[0])
            self.H = readShort(args[0])

            self.palette = readCLTEntries(args[0], (self.bnum - 0xC)//2)
        
        elif len(args) == 9:
            self.bnum = args[0]
            self.DX = args[1]
            self.DY = args[2]
            self.W = args[3]
            self.H = args[4]

            self.palette = args[5]
        else:
            raise ValueError("CLT constructor arguments must be 1 file or 8 parameters!")

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
            raise ValueError("PXL constructor arguments must be 1 file or 9 parameters!")


class TIM:
    def __init__(self, *args):
        if len(args) == 1:
            self.ID = readByte(args[0])
            self.version = readByte(args[0])
            self.ID_upper = readShort(args[0])
            self.Flag = readInt(args[0])
            self.PMD = self.Flag & 0b111
            self.CF = (self.Flag & 0b1000) >>3
            if self.CF == 0b1:
                self.CLUT = CLUT(args[0])

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

        elif len(args) == 11:
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
            self.CLUT = args[10]
            self.TPN = (self.DX//64) + (self.DY//256)*16
        
        else:
            raise ValueError("TIM constructor arguments must be 1 file or 10 parameters(no clut) or 11 parameters(clut)!")

    def to_bin(self):
        buffer = b''
        buffer += self.ID.to_bytes(1,'little')
        buffer += self.version.to_bytes(1,'little')
        buffer += self.ID_upper.to_bytes(2,'little')
        buffer += self.Flag.to_bytes(4,'little')

        if self.CF != 0:
            buffer += self.CLUT.bnum.to_bytes(4,'little')
            buffer += self.CLUT.DX.to_bytes(2,'little')
            buffer += self.CLUT.DY.to_bytes(2,'little')
            buffer += self.CLUT.W.to_bytes(2,'little')
            buffer += self.CLUT.H.to_bytes(2,'little')
            for palette in self.CLUT.palette:
                pixel = palette[0] + (palette[1] << 5) + (palette[2] << 10) + (palette[3] << 15)
                buffer += pixel.to_bytes(2, 'little')
            
        buffer += self.bnum.to_bytes(4,'little')
        buffer += self.DX.to_bytes(2,'little')
        buffer += self.DY.to_bytes(2,'little')
        buffer += self.W.to_bytes(2,'little')
        buffer += self.H.to_bytes(2,'little')
        if self.PMD == FOUR_BIT_CLUT:
            entry_buffer = 0
            entry_counter = 0
            for entry in self.PXLData:
                if entry_counter % 2 != 0:
                    entry_buffer += entry << 4
                    buffer += entry_buffer.to_bytes(1,'little')
                    entry_buffer = 0
                else:
                    entry_buffer += entry
                entry_counter += 1
                pass
        elif self.PMD == EIGHT_BIT_CLUT:
            for entry in self.PXLData:
                buffer += entry.to_bytes(1,'little')
        elif self.PMD == SIXTEEN_BIT_CLUT:
            for entry in self.PXLData:
                buffer += entry.to_bytes(2,'little')
        else:
            raise ValueError("TIM PMODE UNRECOGNIZED")

        return buffer

    def get_PXL_start(self):
        pxl_start = 8 + 0xC
        if self.CF != 0:
            pxl_start += self.CLUT.bnum
        
        return pxl_start

def isTIM(filePath):
    testFile = open(filePath, 'rb')
    
    ext = int.from_bytes(testFile.read(4), byteorder="little")

    TIM_EXT = 0x00000010

    if ext == TIM_EXT:
        return True
    else:
        return False

#Convert a PXL array into PXL binary data
def PXL_data_to_bytes(PXL_data, PMODE):
    if PMODE == FOUR_BIT_CLUT:
        bits_per_entry = 4
    elif PMODE == EIGHT_BIT_CLUT:
        bits_per_entry = 8
    elif PMODE == SIXTEEN_BIT_CLUT:
        bits_per_entry = 16
        
    byte_buffer = b''
    pixels_added = 0
    

    while pixels_added < len(PXL_data):
        if PMODE == SIXTEEN_BIT_CLUT:
            byte_1 = (PXL_data[pixels_added] & 0b1111111100000000) >> 8
            pixels_added += 1
            byte_2 =  PXL_data[pixels_added] & 0b0000000011111111
            pixels_added += 1

            byte_buffer += (byte_1 + byte_2).to_bytes(2, "little")

        elif PMODE == EIGHT_BIT_CLUT:
            byte_buffer += PXL_data[pixels_added].to_bytes(1, "little")
            pixels_added += 1
        
        elif PMODE == FOUR_BIT_CLUT:
            nibble_1 = PXL_data[pixels_added]
            nibble_2 = PXL_data[pixels_added + 1] << 4

            byte_buffer += (nibble_1 & nibble_2).to_bytes(1, "little")
            pixels_added += 1


    return byte_buffer


def getDiffPixels(image1, image2):
    '''Returns an array of x,y coords of pixels that mismatch in image 1 and 2'''

    changedPixels = []
    if image1.height != image2.height or image1.width != image2.width:
        raise ValueError("Image dimensions for diff must match")

    for y in range(image1.height):
        for x in range(image1.width):
            if image1.getpixel((x,y))[3] == 0 and image2.getpixel((x,y))[3] == 0:
                continue
            elif not np.array_equal(image1.getpixel((x,y)),image2.getpixel((x,y))):
                changedPixels += [[x,y]]
    return changedPixels

def injectPNG(originalPNGPath, newPNGPath, PXL_data, CLUT_data):
    '''Returns a PXL object of a PNG image updated with '''
    newPNGImage = Image.open(newPNGPath).convert('RGBA')
    originalPNGImage = Image.open(originalPNGPath).convert('RGBA')

    changedPixels = getDiffPixels(newPNGImage, originalPNGImage)
    
    new_PXL = copy.deepcopy(PXL_data)
    
    for changedPixel in changedPixels:
        x = changedPixel[0]
        y = changedPixel[1]

        rawPixel = newPNGImage.getpixel((x,y))
        try:
            searchPixel = [rawPixel[0] >>3, rawPixel[1] >>3, rawPixel[2] >>3, 0]
            newPixel = CLUT_data.index(searchPixel)
        except ValueError:
            searchPixel = [rawPixel[0] >>3, rawPixel[1] >>3, rawPixel[2] >>3, 1]
            newPixel = CLUT_data.index(searchPixel)
        new_PXL[x + originalPNGImage.width*y] = newPixel
            

    for change in changedPixels:
        newPNGImage.putpixel((change[0],change[1]), (255,0,0))

    #newPNGImage.show()
    return new_PXL

def PNG_to_TIM(originalTIMPath, modifiedPNGPath):
    TIMfile = open(originalTIMPath, 'rb')

    TIM_obj = TIM(TIMfile)
    original_image = generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
    original_image.save("temp.PNG")

    newPXL = injectPNG("temp.PNG", modifiedPNGPath, TIM_obj.PXLData, TIM_obj.CLUT.palette)

    TIM_obj.PXLData = newPXL

    newTIMbinary = TIM_obj.to_bin()

    return newTIMbinary

#Produces an Image from a given PXL and CLUT
def generatePNG(PXL_data, CLUT_data, width, height, CLUT_Number, PMODE):
    if not os.path.exists(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

    if PMODE == FOUR_BIT_CLUT:
        CLUT_ENTRIES = 0x10
        width = width * 4
    elif PMODE == EIGHT_BIT_CLUT:
        CLUT_ENTRIES = 0x100
        width = width * 2
    elif PMODE == SIXTEEN_BIT_CLUT:
        for pixelNumber in range(len(PXL_data)):
            value = PXL_data[pixelNumber]
            
            red   = value & 0b0000000000011111
            green = value & 0b0000001111100000
            blue  = value & 0b0111110000000000
            alpha = value & 0b1000000000000000
            
            if red == green == blue == alpha == 0:
                alpha = 0
            else:
                alpha = 255

            
            rowNumber    = pixelNumber//width
            columnNumber = pixelNumber % width
            arrayBuffer[rowNumber][columnNumber] = (red, green, blue, alpha)
            im = Image.fromarray(arrayBuffer, "RGBA")

            return im

    arrayBuffer = np.zeros((height, width, 4), dtype=np.uint8)

    
    CLUT_Offset = CLUT_Number * CLUT_ENTRIES


    for pixelNumber in range(len(PXL_data)):
        value = PXL_data[pixelNumber]

        CLUT_Entry = CLUT_Offset + value
        
        red   = CLUT_data[CLUT_Entry][0] << 3
        green = CLUT_data[CLUT_Entry][1] << 3
        blue  = CLUT_data[CLUT_Entry][2] << 3
        alpha = CLUT_data[CLUT_Entry][3] << 3
        
        if red == green == blue == alpha == 0:
            alpha = 0
        else:
            alpha = 255

        
        rowNumber    = pixelNumber//width
        columnNumber = pixelNumber % width
        arrayBuffer[rowNumber][columnNumber] = (red, green, blue, alpha)


    im = Image.fromarray(arrayBuffer, "RGBA")
    #im.show()

    return im