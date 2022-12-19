import sys    
import os
import math
from PIL import Image
import numpy as np


imageOutputFolder = "CONSTRUCTEDIMAGES"
dataOutputFolder  = "INJECTOROUTPUT"

#Graphic                                              File path  Strip width    Image Height          Offset      bpp       Greyscale
warningScreen = "EXTRACT/EVENT.BIN/EVENT.BIN.0477.uncompressed",          16,            192,           528,       16,          False
spencer = "EXTRACT/EVENT.BIN/EVENT.BIN.0594.uncompressed",                16,            192,        0xBA10,       16,          False
sunset =  "EXTRACT/EVENT.BIN/EVENT.BIN.1995.uncompressed",                16,            160,       0x166B0,       16,          False

sunsetText1 = "EXTRACT/EVENT.BIN/EVENT.BIN.1995.uncompressed",            64,            -1,           0x20,       4,          True

sunsetText2 = "EXTRACT/EVENT.BIN/EVENT.BIN.1995.uncompressed",            32,            -1,           0x10,       8,          True

Kenzo1   = "EXTRACT/EVENT.BIN/EVENT.BIN.1996.uncompressed",               64,             -1,           0x20,        4,           True
Kenzo1_2   = "EXTRACT/EVENT.BIN/EVENT.BIN.1996.uncompressed",             32,             -1,           0x10,        8,           True 
Kenzo2   = "EXTRACT/EVENT.BIN/EVENT.BIN.1997.uncompressed",               32,             -1,           -0x10,        8,           True  

ranks         = "EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0006"           ,         248,             -1,            48,        2,           True

starScroll    = "EXTRACT/EVENT.BIN/EVENT.BIN.0905.uncompressed",          16,            144,       0x19900,        8,           True  

starScroll2   = "EXTRACT/EVENT.BIN/EVENT.BIN.0904.uncompressed",          64,             -1,           0x0,        4,           True  

starScroll3    = "EXTRACT/EVENT.BIN/EVENT.BIN.0903.uncompressed",         64,           144,           0x0,        4,           True

KyojiIsDead    = "EXTRACT/EVENT.BIN/EVENT.BIN.1162.uncompressed",         64,           -1,           32,         4,             True

Newspaper = "EXTRACT/EVENT.BIN/EVENT.BIN.1176.uncompressed",               32,            176,           16,       8,          True 
Newspaper2 = "EXTRACT/EVENT.BIN/EVENT.BIN.1177.uncompressed",               32,            96,           16,       8,          True 

#DEBUG
debug1 =  "EXTRACT/EVENT.BIN/EVENT.BIN.0413.uncompressed",                16,            96,       0x0,       16,  False

debug2=  "EXTRACT/EVENT.BIN/EVENT.BIN.0414.uncompressed",                16,           216,       0x10,       16,  False

debug3=  "EXTRACT/EVENT.BIN/EVENT.BIN.0421.uncompressed",                16,           80,       0x10,       16,  False

debug4=  "EXTRACT/EVENT.BIN/EVENT.BIN.0456.uncompressed",                16,           154,       0x10,       16,  False

IQ = "SANDR.IMG",                                                      256,             256,           0,     16, True

#converts a file into an image with bpp of 1, 2, 4, or 8
def convertFileToImage(graphic):
    pathToImage = graphic[0]
    stripWidth  = graphic[1]

    offset      = graphic[3]
    bpp         = graphic[4]

    pixelsPerByte = int(8/bpp)

    if not os.path.exists(imageOutputFolder):
            os.makedirs(imageOutputFolder)

    imageFile = open(pathToImage, "rb")

    imageData   = imageFile.read()
    imageFile.seek(0,0)
    rowSize = stripWidth * (bpp/8)
    imageHeight = math.ceil((len(imageData) + (offset/pixelsPerByte))/rowSize)

    imageArray  = [[[np.uint8(0),np.uint8(0),np.uint8(0)] for x in range(stripWidth)] for y in range(imageHeight)]


    rowPixelsWritten = offset
    for y in range(imageHeight):
        #rowPixelsWritten = 0
        while rowPixelsWritten < stripWidth:
            
            nextByte = int.from_bytes(imageFile.read(1), signed=False, byteorder="little")
            #nextByte = imageData[y*rowSize + rowPixelsWritten/pixelsPerByte]
            
            for pixelNumber in range(pixelsPerByte):
                bits = 2**bpp - 1
                value = (nextByte & (bits << (pixelNumber*bpp))) >> ((pixelNumber*bpp))
                scalingFactor = 8 - bpp
                imageArray[y][rowPixelsWritten + pixelNumber] = [np.uint8(value<<scalingFactor),np.uint8(value<<scalingFactor),np.uint8(value<<scalingFactor)]
                
            
            
            rowPixelsWritten += pixelsPerByte
        rowPixelsWritten = 0

    npArray = np.array(imageArray)
    print(npArray.shape)

    img = Image.fromarray(npArray)
    img.show()
    img.save(imageOutputFolder + "/" +  pathToImage.split("/")[-1] + ".BMP")
    imageFile.close()
        #outputFile.close()

def convertImageToFile(graphic):
    pathToImage = graphic[0]
    stripWidth  = graphic[1]
    imageHeight = graphic[2]
    offset      = graphic[3]
    bpp         = graphic[4]

    pixelsPerByte = int(8/bpp)

    bmpFile = Image.open(imageOutputFolder + "/" + pathToImage.split("/")[-1] + ".BMP")
    rgbImg = bmpFile.convert('RGB')
    bmpFile.close()

    sourceFile = open(pathToImage, 'rb')
    #header = sourceFile.read(offset/pixelsPerByte)

    pixelBuffer = b''
    scalingFactor = 8 - bpp
    pixelsConverted = offset
    for y in range(rgbImg.height):
        
        while pixelsConverted < rgbImg.width:
            nextByte = 0
            for pixelNumber in range(pixelsPerByte):

                r,g,b = rgbImg.getpixel((pixelsConverted + pixelNumber,y))
                value = r >> scalingFactor
                
                nextByte = nextByte | (value << (pixelNumber*bpp))

            pixelBuffer += bytes([nextByte])
            pixelsConverted += pixelsPerByte
        pixelsConverted = 0

    #sourceFile.seek(0)
    #Trim to original file length
    pixelBuffer = pixelBuffer[0:len(sourceFile.read())]

    outputFile = open(dataOutputFolder + '/' + pathToImage.split("/",1)[1], "wb")

    outputFile.write(pixelBuffer)

    outputFile.close()
    sourceFile.close()



#Takes in a 24bpp rgb pixel and returns a 16bpp bgr pixel 
def formatPixelForGame(r,g,b):
    pixel = 0b0000000000000000

    #24bpp to 15bpp conversion
    blue  = b >> 3
    green = g >> 3 
    red   = r >> 3
    #Set high bit
    pixel = pixel | 0x8000
    #add BGR colors to 2 byte pixel 
    pixel = pixel | (blue << 10)
    pixel = pixel | (green << 5)
    pixel = pixel |  red
    
    return pixel.to_bytes(2,"little")


#Converts the 24bpp color bitmap to a scattered game binary, either a 15bpp color image or a 8bpp greyscale
def convertBMPToScatter(graphic):
    pathToImage = graphic[0]
    stripWidth  = graphic[1]
    imageHeight = graphic[2]
    offset      = graphic[3]
    bpp         = graphic[4]
    greyscale   = graphic[5]
    
    bmpFile = Image.open(imageOutputFolder + "/" + pathToImage.split("/")[-1] + ".BMP")
    rgbImg = bmpFile.convert('RGB')
    bmpFile.close()

    sourceFile = open(pathToImage, 'rb')
    header = sourceFile.read(offset)

    pixelBuffer = b''

    numColumns = math.ceil(len(sourceFile.read())/((bpp/8)*stripWidth*imageHeight))
    for z in range(numColumns):
        for y in range(rgbImg.height):
            for x in range(stripWidth):
                xPos = z*stripWidth + x
                r,g,b = rgbImg.getpixel( (xPos,y))
                if greyscale:
                    gamePixel = bytes([r>>(bpp-8)])
                else:
                    gamePixel = formatPixelForGame(r,g,b)
                pixelBuffer += gamePixel
    
    sourceFile.seek(0)
    #Trim to original file length
    pixelBuffer = pixelBuffer[0:len(sourceFile.read()) - offset]

    outputFile = open(dataOutputFolder + '/' + pathToImage.split("/",1)[1], "wb")

    outputFile.write(header + pixelBuffer)

    outputFile.close()
    sourceFile.close()
                

def convertScatterToBMP(graphic):

    pathToImage = graphic[0]
    stripWidth  = graphic[1]
    imageHeight = graphic[2]
    offset      = graphic[3]
    bpp         = graphic[4]
    greyscale   = graphic[5]


    imageFile = open(pathToImage, "rb")

    #clear to offset
    imageFile.read(offset)

    if not os.path.exists(imageOutputFolder):
            os.makedirs(imageOutputFolder)

    #outputFile = open(imageOutputFolder + "/" +  pathToImage.split("/")[-1], "wb")
    
    #Number of strips to construct image
    numColumns = math.ceil(len(imageFile.read())/((bpp/8)*stripWidth*imageHeight))

    imageFile.seek(offset)
    #imageArray = []
    #for x in range(imageHeight):
    #    imageArray.append([])

    #Initialize array
    imageArray = [[[np.uint8(0),np.uint8(0),np.uint8(0)] for x in range(numColumns*stripWidth)] for y in range(imageHeight)]

    #for y in range(imageHeight):
    #    for x in range(numColumns * stripWidth):
    #        imageArray[y][x] = 
    
    try:
        #Until all image data read
        while True:
            #Iterate over all strips
            for z in range(numColumns):
                
                for y in range(imageHeight):
                    for x in range(stripWidth):
                        if greyscale:
                            #1 byte pixels
                            pixel = imageFile.read(bpp>>3)
                            value = int.from_bytes(pixel, signed=False, byteorder="little")
                            imageArray[y][x + z*stripWidth] = [np.uint8(value),np.uint8(value),np.uint8(value)]
                            
                        else:
                            #2 byte pixels
                            pixel = imageFile.read(2)
                            #first bit is alpha/unused
                            pixelA = (pixel[1] & 0b10000000) >> 7
                            #Next 5 bits is Blue
                            pixelB = (pixel[1] & 0b01111100) >> 2
                            #Next 5 bits is Green
                            pixelG =((pixel[1] & 0b00000011) << 3) | ((pixel[0] & 0b11100000) >> 5)
                            #Next 5 bits is Red
                            pixelR =  pixel[0] & 0b00011111
                            #Add pixel to the array
                            imageArray[y][x + z*stripWidth] = [np.uint8(pixelR*8),np.uint8(pixelG*8),np.uint8(pixelB*8)]
            raise ValueError('Image fully read')
                   
                
    except:
        npArray = np.array(imageArray)
        print(npArray.shape)
        w, h = 512, 512

        img = Image.fromarray(npArray)
        img.show()
        img.save(imageOutputFolder + "/" +  pathToImage.split("/")[-1] + ".BMP")
        imageFile.close()
        #outputFile.close()

def convertZigScatterToBMP(graphic):

    pathToImage = graphic[0]
    stripWidth  = graphic[1]
    imageHeight = graphic[2]
    offset      = graphic[3]
    bpp         = graphic[4]
    greyscale   = graphic[5]


    imageFile = open(pathToImage, "rb")

    #clear to offset
    imageFile.read(offset)

    if not os.path.exists(imageOutputFolder):
            os.makedirs(imageOutputFolder)

    #outputFile = open(imageOutputFolder + "/" +  pathToImage.split("/")[-1], "wb")
    
    #Number of strips to construct image
    numColumns = math.ceil(len(imageFile.read())/((bpp/8)*stripWidth*imageHeight))

    imageFile.seek(offset)
    #imageArray = []
    #for x in range(imageHeight):
    #    imageArray.append([])

    #Initialize array
    imageArray = [[[np.uint8(0),np.uint8(0),np.uint8(0)] for x in range(numColumns*stripWidth//2)] for y in range(imageHeight*2)]

    #for y in range(imageHeight):
    #    for x in range(numColumns * stripWidth):
    #        imageArray[y][x] = 
    
    try:
        #Until all image data read
        while True:
            #Iterate over all strips
            for z in range(numColumns):
                
                for y in range(imageHeight):
                    for x in range(stripWidth):
                        if greyscale:
                            #1 byte pixels
                            pixel = imageFile.read(bpp>>3)
                            value = int.from_bytes(pixel, signed=False, byteorder="little")
                            if y%stripWidth < stripWidth>>1:
                                if x >=stripWidth>>1:
                                    imageArray[y + (y//stripWidth)*stripWidth + (stripWidth>>1)][x - (stripWidth>>1) + (z*stripWidth>>1)] = [np.uint8(value),np.uint8(value),np.uint8(value)]
                                    #print(str(y + (y//stripWidth)*stripWidth + stripWidth>>1), str(x - (stripWidth>>1) + (z*stripWidth>>1)))
                                else:    
                                    imageArray[y + (y//stripWidth)*stripWidth][x + (z*stripWidth>>1)] = [np.uint8(value),np.uint8(value),np.uint8(value)]
                                    #print(str(y + (y//stripWidth)*stripWidth),str(x + (z*stripWidth>>1)))
                            else:
                                if x >=stripWidth>>1:
                                    imageArray[y + (y//stripWidth)*stripWidth + stripWidth][x - (stripWidth>>1) + (z*stripWidth>>1)] = [np.uint8(value),np.uint8(value),np.uint8(value)]
                                    #print(str(y + (y//stripWidth)*stripWidth + stripWidth),str(x - (stripWidth>>1) + z*stripWidth>>1))
                                else:    
                                    imageArray[y + (y//stripWidth)*stripWidth + (stripWidth>>1)][x +(z*stripWidth>>1)] = [np.uint8(value),np.uint8(value),np.uint8(value)]
                                    #print(str(y + (y//stripWidth)*stripWidth + stripWidth>>1),str(x + z*stripWidth>>1))
                            
                        else:
                            #2 byte pixels
                            pixel = imageFile.read(2)
                            #first bit is alpha/unused
                            pixelA = (pixel[1] & 0b10000000) >> 7
                            #Next 5 bits is Blue
                            pixelB = (pixel[1] & 0b01111100) >> 2
                            #Next 5 bits is Green
                            pixelG =((pixel[1] & 0b00000011) << 3) | ((pixel[0] & 0b11100000) >> 5)
                            #Next 5 bits is Red
                            pixelR =  pixel[0] & 0b00011111
                            #Add pixel to the array
                            imageArray[y][x + z*stripWidth] = [np.uint8(pixelR*8),np.uint8(pixelG*8),np.uint8(pixelB*8)]
            raise ValueError('Image fully read')
                   
                
    except:
        npArray = np.array(imageArray)
        print(npArray.shape)
        w, h = 512, 512

        img = Image.fromarray(npArray)
        img.show()
        img.save(imageOutputFolder + "/" +  pathToImage.split("/")[-1] + ".BMP")
        imageFile.close()


#Converts the 8bpp greyscale zigzag images to a scattered game binary
def convertBMPToZig(graphic):
    pathToImage = graphic[0]
    stripWidth  = graphic[1]
    imageHeight = graphic[2]
    offset      = graphic[3]
    bpp         = graphic[4]
    greyscale   = graphic[5]
    
    bmpFile = Image.open(imageOutputFolder + "/" + pathToImage.split("/")[-1] + ".BMP")
    rgbImg = bmpFile.convert('RGB')
    bmpFile.close()

    sourceFile = open(pathToImage, 'rb')
    header = sourceFile.read(offset)

    pixelBuffer = b''

    numColumns = math.ceil(len(sourceFile.read())/((bpp/8)*stripWidth*imageHeight))
    for z in range(numColumns):
        for y in range(rgbImg.height):
            for x in range(stripWidth):
                xPos = z*stripWidth + x
                r,g,b = rgbImg.getpixel( (xPos,y))
                if greyscale:
                    gamePixel = bytes([r>>(bpp-8)])
                else:
                    gamePixel = formatPixelForGame(r,g,b)
                pixelBuffer += gamePixel
    
    sourceFile.seek(0)
    #Trim to original file length
    pixelBuffer = pixelBuffer[0:len(sourceFile.read()) - offset]

    outputFile = open(dataOutputFolder + '/' + pathToImage.split("/",1)[1], "wb")

    outputFile.write(header + pixelBuffer)

    outputFile.close()
    sourceFile.close()

#convertScatterToBMP(bugger)
#convertImageToFile(ranks)
#convertScatterToBMP(starScroll)
#convertBMPToScatter(starScroll)
#
convertFileToImage(IQ)
#convertImageToFile(KyojiIsDead)
#convertZigScatterToBMP(Newspaper2)

#convertScatterToBMP(sunset)

#convertFileToImage(Kenzo1)

#convertImageToFile(Kenzo1)

#convertFileToImage(Kenzo1_2)

#convertImageToFile(Kenzo1_2)

#convertFileToImage(Kenzo2)

#convertImageToFile(Kenzo2)

#convertFileToImage(sunsetText1)

#convertImageToFile(sunsetText1)

#convertFileToImage(sunsetText2)

#convertImageToFile(sunsetText2)

#convertScatterToBMP(debug4)