############################################################
# Forms disc ready binary packages from individual files   #
#  for ps1 game "Racing Lagoon"                            #
#                                                          #
############################################################

import sys    

import os
from os import path
import shutil
import compress


outputFolder = "REBUILT"

#Table         File containing table                Offset    Length   File containing data
SYSTEM_Table = outputFolder + "/SLPS_020.38",       0x4A4DC,  0x68,    "SYSTEM.BIN"
DATA_Table =   outputFolder + "/SLPS_020.38",       0x4A544,  0x4E4,   "DATA.BIN"
CDRACE_Table = outputFolder + "/SLPS_020.38",       0x4AB44,  0x1A4,   "CD_RACE.BIN"
CAR_Table =    outputFolder + "/LAGOON/SYSTEM.BIN", 0x19F008, 0x4AFC,  "CAR.BIN"
EVENT_Table =  outputFolder + "/LAGOON/SYSTEM.BIN", 0x137D34, 0x1F88,  "EVENT.BIN"

#MBTEST
eventExceptions = [ 'EXTRACT/EVENT.BIN/EVENT.BIN.0477.uncompressed', 
                    'EXTRACT/EVENT.BIN/EVENT.BIN.0903.uncompressed',
                    'EXTRACT/EVENT.BIN/EVENT.BIN.0904.uncompressed',
                    'EXTRACT/EVENT.BIN/EVENT.BIN.0905.uncompressed',
                    'EXTRACT/EVENT.BIN/EVENT.BIN.1162.uncompressed',
                    'EXTRACT/EVENT.BIN/EVENT.BIN.1995.uncompressed',
                    'EXTRACT/EVENT.BIN/EVENT.BIN.1996.uncompressed',
                    'EXTRACT/EVENT.BIN/EVENT.BIN.1997.uncompressed']

#SYSTEM _MUST_ be before CAR and EVENT
#table_list =  [SYSTEM_Table]
#table_list =  SYSTEM_Table, EVENT_Table
table_list =  SYSTEM_Table, EVENT_Table, DATA_Table
#table_list =  SYSTEM_Table, EVENT_Table, DATA_Table,  CAR_Table

def toInt(bytes):
    return int.from_bytes(bytes, "little", signed=False)

    
def buildFromTable(table):
    tablePath = table[0]
    offset =    table[1]
    length =    table[2]>>2
    fileName =  table[3]

    dataBuffer = b''
    tableBuffer = b''

    tableCursor = 0
    dataOffset  = 0

    tableFile = open(tablePath, "rb")
    tableFile.read(offset)


    #Iterate over all entries except last
    while tableCursor < length-1:
        
        nextEntry      = toInt(tableFile.read(4))
        isCompressed   = nextEntry & 0x80000000
        nextEntry      = nextEntry & 0x7FFFFFFF
        targetFileName = "EXTRACT/" + fileName + "/" + fileName + "." + str(tableCursor).zfill(4)
        #MBTEST
        srcFileName    = "SRC/LAGOON/" + fileName


        if isCompressed:
            targetFileName = targetFileName + ".uncompressed"
            #MBTEST
            if targetFileName in eventExceptions or fileName != 'EVENT.BIN':
                print("Compressing and packing: " + targetFileName)
                dataToAdd = compress.compressChunk(open(targetFileName, "rb").read())
            else:
                print("Fetching from SRC file:  " + targetFileName)
                
                srcDataFile = open(srcFileName, 'rb')
                srcTableFile = open('SRC/LAGOON/SYSTEM.BIN', 'rb')
                srcTableFile.seek(offset + 4*tableCursor)
                startPosBytes = srcTableFile.read(4)
                endPosBytes = srcTableFile.read(4)
                startPos = int.from_bytes(startPosBytes,byteorder='little') & 0x7FFFFFFF
                endPos = int.from_bytes(endPosBytes,byteorder='little') & 0x7FFFFFFF
                srcDataFile.seek(startPos)
                dataToAdd = srcDataFile.read(endPos-startPos)

                srcTableFile.close()
                srcDataFile.close()

        else:
            print("Packing:                 " + targetFileName)
            dataToAdd = open(targetFileName, "rb").read()
        
        #align data to 0x800
        while (len(dataToAdd) % 0x800) != 0:
            dataToAdd += bytes(1)

        dataBuffer += dataToAdd

        tableEntry = dataOffset
        if isCompressed:
            tableEntry = tableEntry | 0x80000000
            
        
        tableBuffer += tableEntry.to_bytes(4, byteorder ="little")
        

        tableCursor += 1
        dataOffset += len(dataToAdd)
    
    #Add EOF table entry
    tableBuffer += dataOffset.to_bytes(4, byteorder ="little")
    assert len(tableBuffer) >>2  == length
    
    #Write output file
    builtFile = open(outputFolder + "/LAGOON/" + fileName, "wb")
    builtFile.write(dataBuffer)
    builtFile.close()

    #Update parent table
    tableFile.seek(0,0)
    tableFileBuffer = tableFile.read(offset)
    tableFileBuffer += tableBuffer

    tableFile.read(len(tableBuffer))
    tableFileBuffer += tableFile.read()

    tableFileOutput = open(tablePath, "wb")
    tableFileOutput.write(tableFileBuffer)
    tableFileOutput.close()




def build():
    if not path.exists(outputFolder):
        os.makedirs(outputFolder)

    if not path.exists(outputFolder  + "/LAGOON"):
        os.makedirs(outputFolder + "/LAGOON")

    if not path.exists(outputFolder + "/SLPS_020.38"):
        shutil.copyfile("SRC/SLPS_020.38", outputFolder + "/SLPS_020.38")



    for table in table_list:
        buildFromTable(table)

build()