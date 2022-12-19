#########################################################################
# Uncompresses data in PS1 game "Aconcagua"                             #
#########################################################################

import sys    
import os
import math

targetFile = "src/Disk1/PROGRAM.BIN"
outputFolder = "uncompressed"
subtitleOutputFolder = "uncompressedSubtitles"


LEN_CONTROL_BLOCK = 8
UPPER_BYTE_MASK = 0b11110000
LOWER_BYTE_MASK = 0b00001111

BITS_IN_BYTE = 8
BYTES_IN_WORD = 4



# Takes a lzss compressed file at a certain offset into a file
# to an endpoint and returns a decompressed file
def decompress(targetFile, offset, end):
    inputFile = open(targetFile, "rb")

    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)
    
    #outputFile = open(outputFolder + "/PROGRAM.BIN." + str(offset) + ".uncompressed", 'wb')

    #Skip to file
    inputFile.seek(offset)

    buffer = b''

    bytesRead    = 0
    bytesWritten = 0

    #Iterate until file is fully read
    while bytesWritten < end:
        #Cycle begins by reading control block
        controlByte = inputFile.read(1)
        bytesRead += 1

        #Read each bit in control block
        for i in range(LEN_CONTROL_BLOCK):
            cursor = 0x1 << i
            
            if cursor & int.from_bytes(controlByte, byteorder='little'):
                #Decode 2 byte reference
                r1 = int.from_bytes(inputFile.read(1), byteorder='little')
                r2 = int.from_bytes(inputFile.read(1), byteorder='little')
                bytesRead += 2

                referenceLength = ((r2 & UPPER_BYTE_MASK) >> 4) + 3
                referenceDist   = ((r2 & LOWER_BYTE_MASK) << 8) + r1
                                
                referenceDistanceDecoded = 0xFFF - referenceDist + 1


                for j in range(referenceLength):
                    if (j >= referenceDistanceDecoded):
                        buffer += bytes([buffer[-(0xFFF + referenceDistanceDecoded + 1)]])
                    else:
                        buffer += bytes([buffer[-referenceDistanceDecoded]])
                    

                bytesWritten += referenceLength
            else:
                #Decode literal
                buffer += inputFile.read(1)
                bytesWritten += 1
                bytesRead += 1

        

    buffer = buffer[0:end]
    return buffer
    #outputFile.write(buffer)
    #outputFile.close()
    #inputFile.close()

def __readBits(numOfBits,  offset, data):
    bytesIn = offset//(BITS_IN_BYTE)
    byte1 = int.from_bytes(data[bytesIn     :bytesIn + 1], byteorder="little") 
    byte2 = int.from_bytes(data[bytesIn + 1 :bytesIn + 2], byteorder="little") 
    
    combinedWord = (byte2 << BITS_IN_BYTE) | byte1
    
    offsetInByte = offset % (BITS_IN_BYTE)

    bitMask = (2**(numOfBits)) - 1
    bits = (combinedWord >> offsetInByte) & bitMask
    return bits

def __pixelArrayToBinary(pixelArray):
    outputBuffer = b''

    for byteNum in range(len(pixelArray)//2):
        nibble1 = pixelArray[ byteNum*2     ]
        nibble2 = pixelArray[(byteNum*2) + 1]
        nextByte = ((nibble2 << 4) | nibble1).to_bytes(1, byteorder='little')
        outputBuffer += nextByte

    return outputBuffer

def decompressSubtitle(targetFile, offset):

    inputFile = open(targetFile, "rb")
    inputFile.seek(offset)
    inputData = inputFile.read()

    if not os.path.exists(subtitleOutputFolder):
        os.mkdir(subtitleOutputFolder)

    buffer = []

    bitsRead = 0
    pixelsWritten = 0

    escapeSeqEncountered = False

    #DEBUG
    longestExtend = 0

    while escapeSeqEncountered == False:
        numOfExtends = 0
        pixelsToWrite = __readBits(3, bitsRead, inputData)
        bitsRead += 3
        extendFlag = __readBits(1, bitsRead, inputData)
        bitsRead += 1

        if pixelsToWrite == 0 and extendFlag == 0:
            escapeSeqEncountered = True
            break

        while extendFlag != 0:
            numOfExtends += 1

            nextLengthNibble = __readBits(3, bitsRead, inputData)
            bitsRead += 3
            pixelsToWrite = (pixelsToWrite << 3) + nextLengthNibble
            extendFlag = __readBits(1, bitsRead, inputData)
            bitsRead += 1

        pixelColor = __readBits(2, bitsRead, inputData)
        bitsRead += 2

        #DEBUG
        if numOfExtends > longestExtend:
            longestExtend = numOfExtends

        buffer += [pixelColor] * pixelsToWrite
        pixelsWritten += pixelsToWrite

    #DEBUG
    #print(str(longestExtend) + '\n')

    return __pixelArrayToBinary(buffer), math.ceil(bitsRead/8)


#decompress(targetFile, 0x800, 0x15000)

#DEBUG
#testOut = open("000Out.bin", "wb")
#testOut.write(decompressSubtitle("Subtitles/data/SE01_00_BOT_0001.modified",0)[0])
