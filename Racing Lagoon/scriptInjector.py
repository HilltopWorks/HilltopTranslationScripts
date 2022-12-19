#########################################################################
# Forms binary script files from text script files                      #
#########################################################################

import os
from pathlib import Path
import re
import dataConversion

outputFolder = "EXTRACT/"
ENDCHARS = ["{END}","{F-END}","{EOF}"]
NEWLINECODE = "{NL}"

gameMenu1Location = 0x25BB0
gameMenu1End      = 0x2D67E
gameMenu1File     = "SYSTEM.BIN.0024.uncompressed"

gameMenu2Location = 0x2D684
gameMenu2End      = 0x2DB00
gameMenu2File     = "SYSTEM.BIN.0024.uncompressed"

gameMenu3Location = 0xEB24
gameMenu3End      = 0xF105
gameMenu3File     = "SYSTEM.BIN.0007"

scriptBaseAddress = 0x8008d780

#List of script files allowed to bypass sector limit
allowances = ["EVENT.BIN.0519.txt"]


def injectEvent():
    binaryFolder  = "EXTRACT - ORIGINAL/EVENT.BIN/"
    binaryPackage = "EVENT.BIN/"

    scriptFolder = "SCRIPT/EVENT.BIN/"

    for scriptFileName in os.listdir(scriptFolder):
        print("Script file: " + scriptFileName)
        #Strip ".txt"
        binaryFileName = scriptFileName[:-4]

        binaryFile = open(binaryFolder + binaryFileName, "rb")
        binaryFileData = binaryFile.read()
        binaryFile.close()

        scriptFile = open(scriptFolder + scriptFileName, "r", encoding='utf-8')

        if not os.path.exists(outputFolder + binaryPackage):
            os.makedirs(outputFolder + binaryPackage)

        outputFile = open(outputFolder + binaryPackage + binaryFileName, 'wb')

        #firstline format: //Source: [FILENAME] 
        rawLine = scriptFile.readline()

        dataBuffer = b''

        #Convert text to binary data
        while True:
            entryLine = scriptFile.readline()
            if entryLine.startswith("<<<LINE "):

                endCount = 0
                textLine = ''
                while endCount == 0:
                    textLine += scriptFile.readline()
                    

                    for endChar in ENDCHARS:
                        endCount += textLine.count(endChar)
                        textLine = textLine.replace(endChar + "\n",endChar)
                
                textLine = textLine.replace("\n", NEWLINECODE)
                textLine = re.sub( r", ",",",textLine)
                textLine = textLine.replace("...", "…")
                
                #Only replace single spaces with buffer opcode, spaces in sequence are replaced with default width buffer
                #textLine = textLine.replace("{BUFFER=0x04}{BUFFER=0x04}", "{BUFFER=0x14}")
                #textLine = textLine.replace("{BUFFER=0x14}{BUFFER=0x04}", "{BUFFER=0x1E}")
                #textLine = textLine.replace("{BUFFER=0x04}{BUFFER=0x14}", "{BUFFER=0x1E}")
                scriptFile.readline()

                dataBuffer += bytearray.fromhex(dataConversion.textToHex(textLine))

            else:
                break

        controlOffset = dataConversion.toInt(binaryFileData[:4])
        controlEnd    = dataConversion.toInt(binaryFileData[4:8])
        #Seek to text start
        #binaryFile.read(8)

        #Header word 1, original offset
        outputBuffer  = controlOffset.to_bytes(4, byteorder="little")
        #Header word 2, file end
        outputBuffer += (controlEnd + controlOffset - len(dataBuffer)).to_bytes(4, byteorder="little")
        #Header word 3, text start
        outputBuffer += (controlEnd - controlOffset).to_bytes(4, byteorder="little")
        #Header word 4, Script base address minus original offset 
        outputBuffer += (scriptBaseAddress - controlOffset).to_bytes(4, byteorder="little")
        
        outputBuffer += binaryFileData[0x10  + controlOffset: 0x10 + controlEnd]
        
        outputBuffer += dataBuffer

        print("File size: " + str(len(dataBuffer)) + " bytes. Spare bytes: " + str(len(binaryFileData) - len(outputBuffer)))
        print()
        

        if scriptFileName not in allowances:
            assert len(outputBuffer) <= len(binaryFileData)
        


        outputFile.write(outputBuffer)
        outputFile.close()
        scriptFile.close()

def injectSystemMenu():
    targetFolder  = "EXTRACT/SYSTEM.BIN/"
    targetPackage = "SYSTEM.BIN/"
    targetFileName    = "SYSTEM.BIN.0008"

    offset = 0x12b4
    length = 0x1295


    scriptFile = open("SCRIPT/SYSTEM.BIN/SYSTEM.BIN.0008.txt", 'r', encoding='utf-8')

    print("Injecting: " + targetFileName + ".txt")

    if not os.path.exists(outputFolder + targetPackage):
         os.makedirs(outputFolder + targetPackage)

    
    targetFile = open(targetFolder + targetFileName, 'rb')
    #firstline format: //Source: [FILENAME] 
    rawLine = scriptFile.readline()
    
    

    dataBuffer = b''

    while True:
        entryLine = scriptFile.readline()
        if entryLine.startswith("<<<LINE "):

            endCount = 0
            textLine = ''
            while endCount == 0:
                textLine += scriptFile.readline()
                

                for endChar in ENDCHARS:
                    endCount += textLine.count(endChar)
                    textLine = textLine.replace(endChar + "\n",endChar)
            
            textLine = textLine.replace("\n", NEWLINECODE)
            textLine = re.sub( r"\s","{BUFFER=0x04}",textLine)
            textLine = re.sub( r", ",",",textLine)
            #Only replace single spaces with buffer opcode, spaces in sequence are replaced with default width buffer
            textLine = textLine.replace("{BUFFER=0x04}{BUFFER=0x04}", "{BUFFER=0x14}")
            textLine = textLine.replace("{BUFFER=0x14}{BUFFER=0x04}", "{BUFFER=0x1E}")
            textLine = textLine.replace("{BUFFER=0x04}{BUFFER=0x14}", "{BUFFER=0x1E}")
            scriptFile.readline()

            dataBuffer += bytearray.fromhex(dataConversion.textToHex(textLine))

        else:
            break

    
    #Can't make menu longer than existing text
    assert len(dataBuffer) <= length

    #Inflate text to original length
    while len(dataBuffer) < length:
        dataBuffer += bytes(1)

    #construct finished file from original + new script + rest of original
    outputData = targetFile.read(offset)
    outputData += dataBuffer
    targetFile.read(length)
    outputData += targetFile.read()
    targetFile.close()
    #write data to file
    outputFile = open(outputFolder + targetPackage + targetFileName, 'wb')
    outputFile.write(outputData)
    outputFile.close()
    
    scriptFile.close()

def injectGameMenu(location, end, file):
    targetFolder     = "EXTRACT/SYSTEM.BIN/"
    targetPackage    = "SYSTEM.BIN/"
    targetFileName   = file

    scriptFolder = "SCRIPT/SYSTEM.BIN/"

    offset = location
    length = end - location


    scriptFile = open(scriptFolder + targetFileName + "." + str(location) + ".txt", 'r', encoding='utf-8')

    print("Injecting: " + targetFileName + "." + str(location) + ".txt")

    if not os.path.exists(outputFolder + targetPackage):
         os.makedirs(outputFolder + targetPackage)

    
    targetFile = open(targetFolder + targetFileName, 'rb')
    #firstline format: //Source: [FILENAME] 
    rawLine = scriptFile.readline()
    
    

    dataBuffer = b''

    while True:
        entryLine = scriptFile.readline()
        if entryLine.startswith("<<<LINE "):

            endCount = 0
            textLine = ''
            while endCount == 0:
                textLine += scriptFile.readline()
                

                for endChar in ENDCHARS:
                    endCount += textLine.count(endChar)
                    textLine = textLine.replace(endChar + "\n",endChar)
            
            textLine = textLine.replace("\n", NEWLINECODE)
            textLine = re.sub( r"\s","{BUFFER=0x04}",textLine)
            textLine = re.sub( r", ",",",textLine)
            #Only replace single spaces with buffer opcode, spaces in sequence are replaced with default width buffer
            textLine = textLine.replace("{BUFFER=0x04}{BUFFER=0x04}", "{BUFFER=0x14}")
            textLine = textLine.replace("{BUFFER=0x14}{BUFFER=0x04}", "{BUFFER=0x1E}")
            textLine = textLine.replace("{BUFFER=0x04}{BUFFER=0x14}", "{BUFFER=0x1E}")
            scriptFile.readline()

            dataBuffer += bytearray.fromhex(dataConversion.textToHex(textLine))

        else:
            break

    
    #Can't make menu longer than existing text
    print("Length of Script:" + str(len(dataBuffer)) + " Max Length: " +  str(length))
    print(" ")
    assert len(dataBuffer) <= length

    #Inflate text to original length
    while len(dataBuffer) < length:
        dataBuffer += bytes(1)

    #construct finished file from original + new script + rest of original
    outputData = targetFile.read(offset)
    outputData += dataBuffer
    targetFile.read(length)
    outputData += targetFile.read()
    targetFile.close()
    #write data to file
    outputFile = open(outputFolder + targetPackage + targetFileName, 'wb')
    outputFile.write(outputData)
    outputFile.close()
    
    scriptFile.close()




#Execute
injectSystemMenu()
injectGameMenu(gameMenu1Location, gameMenu1End, gameMenu1File)
injectGameMenu(gameMenu2Location, gameMenu2End, gameMenu2File)
injectGameMenu(gameMenu3Location, gameMenu3End, gameMenu3File)
injectEvent()
