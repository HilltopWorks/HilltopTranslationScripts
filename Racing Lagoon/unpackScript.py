#########################################################################
# Forms script text files from script data files                        #
#########################################################################


import os
from pathlib import Path

import dataConversion

newlines = ["{NL}"]
endcodes = ["{END}","{F-END}"]


systemMenuLocation = 0x12b4
systemMenuLength   = 0x1295
systemMenuEnd      = 0x2549

gameMenu1Location = 0x25BB0
gameMenu1End      = 0x2D67E

gameMenu2Location = 0x2D684
gameMenu2End      = 0x2DB00

gameMenu3Location = 0xEB24
gameMenu3End      = 0xF105

eventFolder = "EXTRACT - ORIGINAL/EVENT.BIN"
systemFolder = "EXTRACT - ORIGINAL/SYSTEM.BIN"
eventOutputFolder = "SCRIPT - Original Japanese/EVENT.BIN"
systemMenuOutputFolder = "SCRIPT - Original Japanese/SYSTEM.BIN"


def unpackEvent():
    if not os.path.exists(eventOutputFolder):
            os.makedirs(eventOutputFolder)

    for fileName in os.listdir(eventFolder):
        inputFile = open(eventFolder + "/" + fileName, "rb")


        #First 4 bytes are offset to control block
        controlBlockStart = dataConversion.toInt(inputFile.read(4))
        #Second 4 bytes are offset to end of control block
        controlBlockEnd = dataConversion.toInt(inputFile.read(4))
        #Third 4 bytes are offset to start of text block
        textBlockStart = dataConversion.toInt(inputFile.read(4))
        #Fourth 4 bytes are unused
        buffer = dataConversion.toInt(inputFile.read(4))

        scriptFileCheck = buffer != 0 or controlBlockEnd <= controlBlockStart or (textBlockStart != 0 and textBlockStart != 0xFFFFFFFF)

        #skip file if not a script
        if scriptFileCheck:
            continue

        if textBlockStart == 0xFFFFFFFF:
            print("Empty File at " + fileName)

        print("Extracting Scriptfile: " + fileName)

        outputFile = open(eventOutputFolder + "/" + fileName + ".txt", "w", encoding="utf-8")

        text = inputFile.read(controlBlockStart)

        convertedText = dataConversion.hexToText(text.hex())

        outputBuffer = "//Source: " + fileName + "\n" + "<<<LINE 0001>>>" + "\n"

        lineNumber = 2
        convertedText = convertedText.replace("{NL}", "\n")
        convertedText = convertedText.replace("{END}", "{END}\n\n" + "<<<LINE XXXX>>>" + "\n")
        convertedText = convertedText.replace("{F-END}", "{F-END}\n\n" + "<<<LINE XXXX>>>" + "\n")

        lines = convertedText.count("{END}") + convertedText.count("{F-END}")

        while lineNumber <= lines + 1:
            convertedText = convertedText.replace("<<<LINE XXXX>>>", "<<<LINE " + str(lineNumber).zfill(4) +  ">>>----------------]",1)
            lineNumber+=1


        outputFile.write(outputBuffer + convertedText)
        outputFile.close()
        inputFile.close()

def unpackSystemMenu():
    if not os.path.exists(systemMenuOutputFolder):
            os.makedirs(systemMenuOutputFolder)

    fileName = "SYSTEM.BIN.0008"

    inputFile = open(systemFolder + "/" + fileName, "rb")


    print("Extracting: " + fileName)

    outputFile = open(systemMenuOutputFolder + "/" + fileName + ".txt", "w", encoding="utf-8")

    inputFile.read(systemMenuLocation)
    text = inputFile.read(systemMenuLength)

    convertedText = dataConversion.hexToText(text.hex())

    outputBuffer = "//Source: " + fileName + "\n" + "<<<LINE 0001>>>" + "\n"

    lineNumber = 2
    convertedText = convertedText.replace("{NL}", "\n")
    convertedText = convertedText.replace("{END}", "{END}\n\n" + "<<<LINE XXXX>>>" + "\n")
    convertedText = convertedText.replace("{F-END}", "{F-END}\n\n" + "<<<LINE XXXX>>>" + "\n")

    lines = convertedText.count("{END}") + convertedText.count("{F-END}")

    while lineNumber <= lines + 1:
        convertedText = convertedText.replace("<<<LINE XXXX>>>", "<<<LINE " + str(lineNumber).zfill(4) +  ">>>",1)
        lineNumber+=1


    outputFile.write(outputBuffer + convertedText)
    outputFile.close()
    inputFile.close()        

def unpackGameMenu(fileName, location, end):
    if not os.path.exists(systemMenuOutputFolder):
            os.makedirs(systemMenuOutputFolder)

    

    inputFile = open(systemFolder + "/" + fileName, "rb")


    print("Extracting: " + fileName)

    outputFile = open(systemMenuOutputFolder + "/" + fileName + "." + str(location) + ".txt", "w", encoding="utf-8")

    inputFile.read(location)
    text = inputFile.read(end - location)

    convertedText = dataConversion.hexToText(text.hex())

    outputBuffer = "//Source: " + fileName + "\n" + "<<<LINE 0001>>>" + "\n"

    lineNumber = 2
    convertedText = convertedText.replace("{NL}", "\n")
    convertedText = convertedText.replace("{END}", "{END}\n\n" + "<<<LINE XXXX>>>" + "\n")
    convertedText = convertedText.replace("{F-END}", "{F-END}\n\n" + "<<<LINE XXXX>>>" + "\n")

    lines = convertedText.count("{END}") + convertedText.count("{F-END}")

    while lineNumber <= lines + 1:
        convertedText = convertedText.replace("<<<LINE XXXX>>>", "<<<LINE " + str(lineNumber).zfill(4) +  ">>>",1)
        lineNumber+=1


    outputFile.write(outputBuffer + convertedText)
    outputFile.close()
    inputFile.close()  
    

unpackGameMenu("SYSTEM.BIN.0024.uncompressed", gameMenu1Location, gameMenu1End)
unpackGameMenu("SYSTEM.BIN.0024.uncompressed", gameMenu2Location, gameMenu2End)
unpackGameMenu("SYSTEM.BIN.0007", gameMenu3Location, gameMenu3End)
unpackSystemMenu()
unpackEvent()