#########################################################################
# Forms script text files from script data files                        #
#########################################################################


import os
from pathlib import Path
import textConversion
import re
import shutil
import filecmp

SCRIPT_OUTPUT_FOLDER = "SCRIPT"
SCRIPT_INPUT_FOLDER  = "EXTRACT"
TABLE_ENTRY_SIZE = 4
DATA_FOLDER = "EXTRACT-ORIGINAL"
MEM_PTR_OFFSET = 0x18
REBUILT_FOLDER = 'REBUILT'

logFile = open('logs/scriptExtractor.log', 'w')
          #Parent offset,        table start,   table size
SCRIPTS =     [ (5402624,           0x13B798,       0x36C),
                (6187008,           0x13D49C,       0x36C),
                (6975488,           0xF542C,        0x290),
                (12447744,          0x13A4A8,       0x3EC),
                (17020928,          0x140868,       0xD0),
                (17819648,          0x13F1E8,       0x298),
                (18667520,          0x124274,       0x108),
                (19470336,          0x14A744,       0x1F8),
                (25827328,          0x1418AC,       0x64C),
                (26542080,          0x14FB48,       0x5C0),
                (27242496,          0x14CA7C,       0x3F0),
                (32593920,          0x1580F4,       0x2C0),
                (33406976,          0x1583E0,       0x264),
                (34222080,          0x157950,       0x1FC),
                (39245824,          0x14F3B4,       0x614),
                (40052736,          0x14F1C4,       0x614),
                (40857600,          0x14FC9C,       0x614),
                (46626816,          0x13E124,       0x218),
                (47355904,          0x13630C,       0x2A0),
                (48095232,          0x151C30,       0x46C),
                (56272896,          0x15AF34,       0x208),
                (57092096,          0x14BDEC,       0x154),
                (57856000,          0xFBC4C,        0xD8),
                (58472448,          0x12EF04,       0x114),
                (59183104,          0x12EF24,       0x114),
                (59893760,          0x12ED38,       0x114),
                (60604416,          0x12EE18,       0x114)]

END_CHARS = ['{END}']
NEW_LINE_CODE = "{NEWLINE}"

def __getMemoryBaseAddress(offset):
    headerFile = open(DATA_FOLDER + "/PSX." + str(offset).zfill(8) + ".header", "rb")
    headerData = headerFile.read()
    headerFile.close()
    memPTR  = int.from_bytes(headerData[MEM_PTR_OFFSET  :MEM_PTR_OFFSET  + 4], byteorder="little", signed=False)

    return memPTR

def extractScript(script):
    if not os.path.exists(SCRIPT_OUTPUT_FOLDER):
            os.makedirs(SCRIPT_OUTPUT_FOLDER)

    fileOffset = script[0]
    baseAddress = __getMemoryBaseAddress(fileOffset)
    tableStart = script[1]
    tableSize  = script[2]

    inputFilePath = DATA_FOLDER

    inputFileName = 'PSX.' + str(fileOffset).zfill(8) + ".bodyUncompressed"
    inputFile = open(DATA_FOLDER + '/' + inputFileName, 'rb')
    inputData = inputFile.read()


    tableCursor = 0

    outputFilePath = SCRIPT_OUTPUT_FOLDER + "/" + inputFileName.split('.body')[0] + ".txt"
    outputFile = open(outputFilePath, "w", encoding="utf-8")


    

    lineEntriesRead = []
    lineEntryNumbers = []
    outputBuffer = ''

    textStart = 0xFFFFFFFF
    textEnd = 0

    while tableCursor < tableSize:
        inputFile.seek(tableStart + tableCursor)
        textPointer = int.from_bytes(inputFile.read(4),byteorder='little', signed=False)
        nextEntryStart = textPointer - baseAddress

        

        lineNumber = tableCursor//4

        if textPointer & 0xFF000000 != 0x80000000:
            tableCursor    += TABLE_ENTRY_SIZE
            outputBuffer += '<<<LINE ' + str(lineNumber).zfill(4) + ' is table embedded text(' + hex(textPointer) + ')\n\n'
            continue

        if nextEntryStart in lineEntriesRead:
            tableCursor    += TABLE_ENTRY_SIZE
            entryNum = lineEntriesRead.index(nextEntryStart)
            outputBuffer += '<<<LINE ' + str(lineNumber).zfill(4) + " points to LINE " + str(lineEntryNumbers[entryNum]).zfill(4) + '>>>\n\n'
            continue

        lineEntriesRead.append(nextEntryStart)
        lineEntryNumbers.append(lineNumber)
        
        intEntries =  [x for x in inputData[nextEntryStart:]]
        nextEntryEnd   =  intEntries.index(0) + nextEntryStart + 1
        
        if nextEntryStart < textStart:
            textStart = nextEntryStart

        if nextEntryEnd > textEnd and not (lineNumber > 0 and ((nextEntryEnd - textEnd) > 0x010000)):
            textEnd = nextEntryEnd

        
        lineHeader = '<<<LINE ' + str(lineNumber).zfill(4) + '>>>\n'
        outputBuffer += lineHeader

        nextLineBinary = inputData[nextEntryStart:nextEntryEnd]
        convertedText = textConversion.hexToText(nextLineBinary.hex())
        convertedText = convertedText.replace("{NEWLINE}", "\n")
        convertedText = convertedText.replace("{NEXT}", "{NEXT}\n")
        convertedText = convertedText.replace("{END}", "{END}\n\n")
        convertedText = convertedText.replace("ctrlEND}", "ctrlEND}\n")

        outputBuffer += convertedText

        tableCursor    += TABLE_ENTRY_SIZE

    headerLine = "//Source: " + inputFileName + " at offset " + hex(fileOffset) + "\n" + "//|Start|End|: |" + str(textStart) + "|" + str(textEnd) + "|\n"

    outputFile.write(headerLine + outputBuffer)
    outputFile.close()
    inputFile.close()

def extractSegment(filePath, textOffset, textLength, tableOffset, tableLength):
    if not os.path.exists(SCRIPT_OUTPUT_FOLDER):
            os.makedirs(SCRIPT_OUTPUT_FOLDER)


    inputFile = open(filePath, 'rb')
    inputFile.read(textOffset)

    outputFilePath = SCRIPT_OUTPUT_FOLDER + "/" + filePath.split('/')[-1] + "." + hex(textOffset) + ".txt"

    logFile.write("Extracting " + hex(textLength) + " bytes of " + filePath + " at " + hex(textOffset) + " into " + outputFilePath + "\n")

    outputFile = open(outputFilePath, "w", encoding="utf-8")

    textBinary = inputFile.read(textLength)

    convertedText = textConversion.hexToText(textBinary.hex())

    outputBuffer = "//Source: " + filePath.split('/')[-1] + " at offset " + hex(textOffset) + "\n" + "<<<LINE 0001>>>" + "\n"

    lineNumber = 2
    convertedText = convertedText.replace("{NEWLINE}", "\n")
    convertedText = convertedText.replace("{NEXT}", "{NEXT}\n")
    convertedText = convertedText.replace("{END}", "{END}\n\n" + "<<<LINE XXXX>>>" + "\n")
    convertedText = convertedText.replace("{ctrlEND1}", "{ctrlEND1}\n")
    convertedText = convertedText.replace("{ctrlEND3}", "{ctrlEND3}\n")
    convertedText = convertedText.replace("{ctrlEND5}", "{ctrlEND5}\n")

    lines = convertedText.count("{END}")

    while lineNumber <= lines + 1:
        convertedText = convertedText.replace("<<<LINE XXXX>>>", "<<<LINE " + str(lineNumber).zfill(4) +  ">>>",1)
        lineNumber+=1


    outputFile.write(outputBuffer + convertedText)
    outputFile.close()
    inputFile.close()
    #logFile.close()

def extractScripts():
    for script in SCRIPTS:
        extractScript(script)

def isScriptUnmodified(file):
    try:
        os.makedirs('REBUILT_FOLDER')
    except:
        pass

    try:
        unmodified = filecmp.cmp(os.path.join(SCRIPT_OUTPUT_FOLDER, file), os.path.join(REBUILT_FOLDER, file) )
    except FileNotFoundError:
        return False

    return unmodified

def injectScripts():
    for script in SCRIPTS:
        injectScript(script)

def injectScript(script):
    fileOffset = script[0]
    tableStart = script[1]
    tableSize  = script[2]

    

    baseAddress = __getMemoryBaseAddress(fileOffset)

    scriptFilePath = SCRIPT_OUTPUT_FOLDER + '/PSX.' + str(fileOffset).zfill(8) + ".txt"
    outFilePath = SCRIPT_INPUT_FOLDER + '/PSX.' + str(fileOffset).zfill(8) + ".bodyUncompressed"
    if isScriptUnmodified('PSX.' + str(fileOffset).zfill(8) + ".txt"):
        return

    print('Injecting Script: PSX.' + str(fileOffset).zfill(8) + '.txt')
    inputScript = open(scriptFilePath, mode='r', encoding='utf-8')
    inputScript.readline()
    boundsLine = inputScript.readline()
    textStart = int(boundsLine.split('|')[4])
    textEnd   = int(boundsLine.split('|')[5])

    maxTextLength = textEnd - textStart

    dataBuffer  = b''
    tableBuffer = b''

    while True:
        entryLine = inputScript.readline()


        if entryLine.startswith("<<<LINE "):

            if "points to" in entryLine:
                refNumber = int(entryLine[28:32])
                tableEntry = int.from_bytes(tableBuffer[refNumber*4:refNumber*4 + 4], byteorder='little', signed=False)
                tableBuffer += tableEntry.to_bytes(4, byteorder = "little", signed=False)
                inputScript.readline()
            elif "table embedded text" in entryLine:
                tableBuffer += tableEntry.to_bytes(4, byteorder = "little", signed=False)
                inputScript.readline()
            else:
                lineNumber = int(entryLine[8:12])
                endCount = 0
                textLine = ''
                while endCount == 0:
                    nextLine = inputScript.readline()

                    if nextLine.startswith('//'):
                        continue
                    
                    textLine += nextLine
                    

                    for endChar in END_CHARS:
                        endCount += textLine.count(endChar)
                        textLine = textLine.replace(endChar + "\n",endChar)
                
                textLine = textLine.replace("\n", NEW_LINE_CODE)
                #textLine = re.sub( r", ",",",textLine)
                #textLine = textLine.replace("...", "…")
                
                #Only replace single spaces with buffer opcode, spaces in sequence are replaced with default width buffer
                textLine = textLine.replace("{NEXT}{NEWLINE}", "{NEXT}")
                textLine = textLine.replace("ctrlEND}{NEWLINE}", "ctrlEND}")
                if "<<<" in textLine:
                    assert False
                inputScript.readline()

                tableEntry = len(dataBuffer) + textStart + baseAddress
                tableBuffer += tableEntry.to_bytes(4, byteorder='little', signed=False)
                
                dataToAdd = bytearray.fromhex(textConversion.textToHex(textLine))
                dataBuffer += dataToAdd

            

        else:
            break

    assert len(dataBuffer) <= maxTextLength, str(fileOffset) + ' is over script budget by ' + str(len(dataBuffer) -maxTextLength)  + ' bytes'

    print (str(maxTextLength - len(dataBuffer)) + " bytes remaining in script " + str(fileOffset))

    dataBuffer += bytes(maxTextLength -  len(dataBuffer))


    parentData = open(DATA_FOLDER + '/PSX.' + str(fileOffset).zfill(8) + ".bodyUncompressed",'rb').read()
    outputBuffer = parentData[:textStart]
    outputBuffer += dataBuffer
    outputBuffer += parentData[textEnd:tableStart]
    outputBuffer += tableBuffer
    outputBuffer += parentData[tableStart + tableSize:]

    assert len(parentData) == len(outputBuffer)

    outputFile = open(outFilePath, 'wb')
    outputFile.write(outputBuffer)

    shutil.copyfile(scriptFilePath, os.path.join(REBUILT_FOLDER, scriptFilePath.split('/')[-1]))


#extractScript((12447744,          0x13A4A8,       0x3EC))
#injectScript((12447744,          0x13A4A8,       0x3EC))
#extractScripts()
#print(textConversion.textToHex('{left}{Katoh}{neutral}{argsEnd}{ID=0x34303935}{ctrlEND3}{NEWLINE}メッセージ不明{NEWLINE}{END}'))
#injectScript(SCRIPTS[0])
#extractScript(SCRIPTS[0])
#extractSegment("EXTRACT/PSX.05402624.bodyUncompressed" , 0x1E40, 0x5001, 0, 0)
#extractSegment("EXTRACT/PSX.12447744.bodyUncompressed" , 0x21C0, 0x562D, 0, 0)