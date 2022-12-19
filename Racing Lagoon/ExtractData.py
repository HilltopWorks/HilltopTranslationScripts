#########################################################################
# Extracts stored data in PS1 game "Racing Lagoon"                      #
#########################################################################

import sys    
import os
import uncompress

#Table         File containing table    Offset    Length   File containing data
SYSTEM_Table = "SRC/SLPS_020.38",       0x4A4DC,  0x68,    "SYSTEM.BIN"
DATA_Table =   "SRC/SLPS_020.38",       0x4A544,  0x4E4,   "DATA.BIN"
CDRACE_Table = "SRC/SLPS_020.38",       0x4AB44,  0x1A4,   "CD_RACE.BIN"
CAR_Table =    "SRC/LAGOON/SYSTEM.BIN", 0x19F008, 0x4AFC,  "CAR.BIN"
EVENT_Table =  "SRC/LAGOON/SYSTEM.BIN", 0x137D34, 0x1F88,  "EVENT.BIN"

UNCOMPRESSED = 0
LZSS_WITH_FILESIZE = 1
LZSS_WITHOUT_FILESIZE = 2
LZSS_IDENTIFIER    = 0x7301
LZSS_IDENTIFIER2   = 0x7401

PTR_LENGTH = 4

table_list =  SYSTEM_Table, CAR_Table, CDRACE_Table, DATA_Table, EVENT_Table
#table_list =  [EVENT_Table]

def toInt(bytes):
    return int.from_bytes(bytes, "little", signed=False)

def unpackCDRace(data):
    if len(data) < 2:
        return []
    
    if data[0:2] == LZSS_IDENTIFIER:

        uncompressedChunk = uncompress.uncompressDataType2(data)
        uncompressedData  = uncompressedChunk[0]
        compressedLength  = uncompressedChunk[1]
        return  [uncompressedData].append(unpackCDRace(data[compressedLength:]))
    else:
        count = 0

        while len(data[count:]) >= 2:
            if data[count:count+2] == LZSS_IDENTIFIER:
                
                try:
                    lzssCheck = uncompress.uncompressDataType2(data[count:])
                    lzssCheckData   = lzssCheck[0]
                    lzssCheckLength = lzssCheck[1]
                    return [lzssCheckData].append(unpackCDRace(data[lzssCheckLength:]))
                except:
                    count += 1

        return []



def unpack(table):
    tablePath = table[0]
    offset =    table[1]
    length =    table[2]>>2
    fileName =  table[3]


    tableFile = open(tablePath, "rb")
    tableFileBuffer = tableFile.read()

    destinationFolder = 'EXTRACT/' + fileName

    if not os.path.exists(destinationFolder):
         os.makedirs(destinationFolder)


    #Extract each file at each pointer except last one (it's the EOF)
    for x in range(length-1):
        addressStart = offset + x*PTR_LENGTH
        addressEnd   = offset + x*PTR_LENGTH + PTR_LENGTH
        
        
        fileStart = toInt(tableFileBuffer[addressStart:addressEnd]) & 0x7FFFFFFF
        fileEnd   = toInt(tableFileBuffer[addressStart + PTR_LENGTH:addressEnd + PTR_LENGTH]) & 0x7FFFFFFF

        dataFile = open("SRC/LAGOON/" + fileName, "rb")

        print("Extracting File: " + fileName + " " + str(x))

        dataFileBuffer = dataFile.read()
        
        
        #File is compressed with lzss if last bit is set
        if toInt(tableFileBuffer[addressStart:addressEnd]) & 0x80000000:
            lzssType = LZSS_WITH_FILESIZE
        #File is compressed with lzss without filesize if first 2 bytes match lzss ID
        elif uncompress.toInt(dataFileBuffer[fileStart:fileStart + 2]) == LZSS_IDENTIFIER or uncompress.toInt(dataFileBuffer[fileStart:fileStart + 2]) == LZSS_IDENTIFIER2:
            lzssType = LZSS_WITHOUT_FILESIZE
        #TODO: handle second compression type (0x7401)
        else:
            lzssType = UNCOMPRESSED

        
    

        if lzssType == LZSS_WITH_FILESIZE:
            outputBuffer = uncompress.uncompressData(dataFileBuffer[fileStart:fileEnd])
            outputFileName = "EXTRACT/" + fileName + "/" + fileName + "." + str(x).zfill(4) + ".uncompressed"          

            outputFile = open(outputFileName, "wb")

            outputFile.write(outputBuffer)

            outputFile.close()
        elif lzssType == LZSS_WITHOUT_FILESIZE:

            cursorDistance = 0
            fileCount = 0
            while fileStart + cursorDistance < fileEnd:
                try:
                    outputChunk = uncompress.uncompressDataType2(dataFileBuffer[fileStart + cursorDistance:fileEnd])
                except:
                    cursorDistance += 1
                    continue
                    
                
                outputBuffer   = outputChunk[0]
                cursorDistance += outputChunk[1]
                outputFileName = "EXTRACT/" + fileName + "/" + fileName + "." + str(x).zfill(4) + "." + str(fileCount).zfill(4) + ".uncompressedType2"
    



                outputFile = open(outputFileName, "wb")
                outputFile.write(outputBuffer)
                outputFile.close()
                fileCount += 1
        else:
            outputBuffer = dataFileBuffer[fileStart:fileEnd]

            outputFileName = "EXTRACT/" + fileName + "/" + fileName + "." + str(x).zfill(4)            

            outputFile = open(outputFileName, "wb")

            outputFile.write(outputBuffer)

            outputFile.close()




for table in table_list:

    unpack(table)