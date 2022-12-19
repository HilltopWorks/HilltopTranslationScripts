#########################################################################
# Separates and repacks PROGRAM.BIN in PS1 game "Aconcagua"             #
#########################################################################

import sys
import os
import shutil
import math
from pathlib import Path

from numpy import zeros

             #"PS-X EXE" in ascii
PSX_HEADER = b'PS-X EXE'

UNCOMPRESSED_LENGTH_OFFSET   = 0x1C
SECTOR_LENGTH_OFFSET         = 0xD0
UNCOMPRESSED_LENGTH_OFFSET_2 = 0xD4
COMPRESSED_LENGTH_OFFSET     = 0xD8
IS_COMPRESSED_OFFSET         = 0xDC

PROGRAM_OUT_FOLDER = "REBUILT"
REBUILT_FOLDER = 'EXTRACT-BUILT'
ORIGINAL_FOLDER = 'EXTRACT-ORIGINAL'


SECTOR_LENGTH = 0x800

DATA_FOLDER = "EXTRACT"

def __getValues(offset):
    headerFile = open(DATA_FOLDER + "/PSX." + str(offset).zfill(8) + ".header", "rb")
    headerData = headerFile.read()

    uncompressedSize  = int.from_bytes(headerData[UNCOMPRESSED_LENGTH_OFFSET  :UNCOMPRESSED_LENGTH_OFFSET  + 4], byteorder="little")
    sizeInSectors     = int.from_bytes(headerData[SECTOR_LENGTH_OFFSET        :SECTOR_LENGTH_OFFSET        + 4], byteorder="little")
    #uncompressedSize2 = int.from_bytes(headerData[UNCOMPRESSED_LENGTH_OFFSET_2 :UNCOMPRESSED_LENGTH_OFFSET_2 + 4], byteorder="little")
    compressedSize    = int.from_bytes(headerData[COMPRESSED_LENGTH_OFFSET    :COMPRESSED_LENGTH_OFFSET    + 4], byteorder="little")
    isCompressed      = int.from_bytes(headerData[IS_COMPRESSED_OFFSET        :IS_COMPRESSED_OFFSET        + 4], byteorder="little")
    return uncompressedSize, sizeInSectors, compressedSize, isCompressed

def __setValues(offset, uncompressedSize, sizeInSectors, compressedSize, isCompressed):
    headerFile = open(DATA_FOLDER + "/PSX." + str(offset).zfill(8) + ".header", "r+b")
    
    headerFile.seek(IS_COMPRESSED_OFFSET)
    headerFile.write(isCompressed.to_bytes(4, byteorder="little"))
        
    headerFile.seek(UNCOMPRESSED_LENGTH_OFFSET)
    headerFile.write(uncompressedSize.to_bytes(4, byteorder="little"))
    headerFile.seek(UNCOMPRESSED_LENGTH_OFFSET_2)
    headerFile.write(uncompressedSize.to_bytes(4, byteorder="little"))

    headerFile.seek(COMPRESSED_LENGTH_OFFSET)
    headerFile.write(compressedSize.to_bytes(4, byteorder="little"))

    headerFile.close()
    return

def __getOffsets():
    offsets = {0}

    for fileName in os.listdir(DATA_FOLDER):
        offset = int(fileName.split('.')[1])
        
        offsets.add(offset)

    return sorted(offsets)



def separate():

    if not os.path.exists("EXTRACT"):
        os.makedirs("EXTRACT")

    program_file = open("src/Disk1/PROGRAM.BIN", "rb")
    program_bin = program_file.read()
    fileSize = Path('src/Disk1/PROGRAM.BIN').stat().st_size

    cursor = 0
    while cursor < fileSize:
        #Save Header
                                
        identifier = program_bin[cursor:cursor+8]

        assert identifier == PSX_HEADER

        uncompressedLengthOffset  = UNCOMPRESSED_LENGTH_OFFSET + cursor
        uncompressedLengthOffset2 = UNCOMPRESSED_LENGTH_OFFSET_2 + cursor
        compressedLengthOffset    = COMPRESSED_LENGTH_OFFSET + cursor
        isCompressedOffset        = IS_COMPRESSED_OFFSET + cursor

        uncompressedSize  = int.from_bytes(program_bin[uncompressedLengthOffset  :uncompressedLengthOffset  + 4], byteorder="little")
        uncompressedSize2 = int.from_bytes(program_bin[uncompressedLengthOffset2 :uncompressedLengthOffset2 + 4], byteorder="little")
        compressedSize    = int.from_bytes(program_bin[compressedLengthOffset    :compressedLengthOffset    + 4], byteorder="little")
        isCompressed      = int.from_bytes(program_bin[isCompressedOffset        :isCompressedOffset        + 4], byteorder="little")

        #assert uncompressedSize == uncompressedSize2


        if   isCompressed == 0:
            #assert uncompressedSize == compressedSize
            pass
        elif isCompressed == 1:
            assert compressedSize < uncompressedSize
        else:
            #isCompressed must be 1 or 0
            assert False
        
        headerFile = open(DATA_FOLDER + '/PSX.' + str(cursor).zfill(8) + ".header", "wb+")

        headerFile.write(program_bin[cursor:cursor + SECTOR_LENGTH])

        headerFile.close()


        #Save Body

        if isCompressed:
            bodyFile = open("EXTRACT/PSX." + str(cursor).zfill(8) + ".bodyCompressed", "wb+")
            bodyFile.write(program_bin[cursor + SECTOR_LENGTH:cursor + SECTOR_LENGTH + compressedSize])
            cursor += compressedSize + SECTOR_LENGTH
        else:
            bodyFile = open("EXTRACT/PSX." + str(cursor).zfill(8) + ".body", "wb+")
            bodyFile.write(program_bin[cursor + SECTOR_LENGTH:cursor + SECTOR_LENGTH + uncompressedSize])
            cursor += uncompressedSize + SECTOR_LENGTH

        #bodyFile.write(program_bin[cursor + sectorLength:cursor + sectorLength + compressedSize])

        bodyFile.close()


        #cursor += compressedSize + sectorLength

        #round up cursor to next sector
        if cursor % SECTOR_LENGTH !=0:
            cursor += SECTOR_LENGTH - (cursor % SECTOR_LENGTH)

        
def repack():
    offsets = __getOffsets()
    
    buffer = b''
    
    for offset in offsets:
        oldUncompressedSize, oldSizeInSectors, oldCompressedSize, isCompressed = __getValues(offset)

        headerFileName = 'PSX.' +  str(offset).zfill(8) + '.header'

        if isCompressed:
            bodyExtensionCompressed = '.bodyCompressed'
            compressedFileName = 'PSX.' +  str(offset).zfill(8) + bodyExtensionCompressed

            bodyExtensionUncompressed = '.bodyUncompressed'
            uncompressedFileName = 'PSX.' +  str(offset).zfill(8) + bodyExtensionUncompressed

            compressedSize = os.path.getsize(DATA_FOLDER + '/' + compressedFileName)
            uncompressedSize = os.path.getsize(DATA_FOLDER + '/' + uncompressedFileName)

            sizeInSectors = math.ceil(uncompressedSize/0x800)

            #Update header
            __setValues(offset, uncompressedSize, sizeInSectors, compressedSize, isCompressed)

            #Append header
            buffer += open(DATA_FOLDER + '/' + headerFileName, 'rb').read()

            #ZFILL and append compressed body
            compressedDataBuffer = open(DATA_FOLDER + '/' + compressedFileName, 'rb').read()

            oldLength  = os.path.getsize(ORIGINAL_FOLDER + '/' + compressedFileName)
            while len(compressedDataBuffer) < oldLength:
                compressedDataBuffer += bytes(1)

            if len(compressedDataBuffer) % SECTOR_LENGTH != 0:
                compressedDataBuffer += bytes( SECTOR_LENGTH - (len(compressedDataBuffer) % SECTOR_LENGTH) )

            buffer += compressedDataBuffer

            
        else:
            bodyExtension = '.body'
            bodyFileName = 'PSX.' + str(offset).zfill(8) + bodyExtension
            buffer += open(DATA_FOLDER + '/' + headerFileName, 'rb').read()
            buffer += open(DATA_FOLDER + '/' + bodyFileName, 'rb').read()


    if not os.path.exists(PROGRAM_OUT_FOLDER):
        os.mkdir(PROGRAM_OUT_FOLDER)

    outputFile = open(PROGRAM_OUT_FOLDER + '/' + 'PROGRAM.BIN', "wb")
    outputFile.write(buffer)
    outputFile.close()


    for file in os.listdir(REBUILT_FOLDER):
        os.remove(REBUILT_FOLDER + '/' + file)

    for file in os.listdir(DATA_FOLDER):
        #fileName = os.fsdecode(DATA_FOLDER + '/' + file)
        shutil.copyfile(DATA_FOLDER + '/' + file, REBUILT_FOLDER + '/' + file)

        

    return    
        
#__setValues(5402624, 0x13C000, 0x278, 0xBEB23, 1)
#repack()
#__setValues(69, 253, 255, 254)