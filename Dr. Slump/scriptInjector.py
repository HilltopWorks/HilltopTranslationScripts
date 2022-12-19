####################################################################################
# Injects script files into container files for PS1 game                           #
# "Dr. Slump"                                                                      #
# Searches 'translations' folder and adds files in the 'translatedScripts' folder  #
####################################################################################

import sys    
import os
from pathlib import Path
import shutil
import dataConversion
def injectScript(inputFolder, outputFolder):
    for script in os.listdir(inputFolder):
        scriptFile = open(inputFolder + script, 'r', encoding='utf-8')

        if os.path.exists(outputFolder + script.strip('.txt')):
            os.remove(outputFolder + script.strip('.txt'))

        outputFile = open(outputFolder + script.strip('.txt'), 'wb')

        #firstline format: @@[FILENAME]@@[NUMBER OF ENTRIES]@@[DATA START]@@[DATA END]
        rawLine = scriptFile.readline()
        firstLine = rawLine.split('@@')
        fileName = firstLine[1]
        numEntries = int(firstLine[2])
        dataStart = int(firstLine[3])
        dataEnd = int(firstLine[4])


        #Write number of bytes entry in first 2 bytes of output
        outputFile.write(bytes([numEntries & 0xFF, numEntries>>8]))

        IDs = []
        Offsets = []
        Texts = []

        while True:
            entryLine = scriptFile.readline()
            if entryLine.startswith("@"):
                block = entryLine.split("@")
                blockIDs = block[1]
                blockOffsets = block[2].strip('\n')
                
                IDs.append(blockIDs.split('/'))
                Offsets.append(blockOffsets.split('/'))

                textLine = scriptFile.readline().split('*')[1].strip('\n')
                Texts.append(textLine)

            else:
                break


        #write to binary file
        cursorOffset = dataStart
        offsetsWritten = []
        pointersWritten = []
        for nextEntry in range(0,numEntries):
            for ID in IDs:
                parentPosition = IDs.index(ID)
                if str(nextEntry) in ID:

                    if Offsets[parentPosition][ID.index(str(nextEntry))] not in offsetsWritten:
                        childPosition = ID.index(str(nextEntry))
                        entryOffset = Offsets[parentPosition][childPosition]

                        textToWrite = Texts[parentPosition]

                        #write the entry
                        outputFile.seek(nextEntry * 2 + 2)
                        outputFile.write(cursorOffset.to_bytes(2, 'little'))

                        convertedText = dataConversion.textToHex(textToWrite)

                        outputFile.seek(cursorOffset)

                    
                        outputFile.write(bytes.fromhex(convertedText))
                        
                        offsetsWritten.append(entryOffset)
                        pointersWritten.append(cursorOffset)
                        #update cursor
                        cursorOffset += (len(convertedText)>>1)

                        
                    else: 
                        childPosition = ID.index(str(nextEntry))
                        entryOffset = Offsets[parentPosition][childPosition]
                        
                        outputFile.seek(nextEntry * 2 + 2)
                        outputFile.write(pointersWritten[offsetsWritten.index(entryOffset)].to_bytes(2, 'little'))

                        
                
        print(fileName)


injectScript("translations/Done/", "gen/")

