#########################################################################
# Forms script text files from script data files                        #
#########################################################################



from ast import Assert
import os
import textConversion
import re
import shutil
import filecmp

SCRIPT_OUTPUT_FOLDER = "SCRIPT-JP"
SCRIPT_FOLDER = "SCRIPT"
INJECT_OUTPUT_FOLDER = "EXTRACT"
SCRIPT_INPUT_FOLDER  = "EXTRACT"
TABLE_ENTRY_SIZE = 4
DATA_FOLDER = "EXTRACT-ORIGINAL"
MEM_PTR_OFFSET = 0x18
REBUILT_FOLDER = 'REBUILT'
COMMENT = "//"
OPENER = "<"
CLOSER = ">"
DELIMITER = "❖"

LOAD_OFFSET_TEXT_FILE = "load_scripts.txt"

CONTROL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"

NORMAL_TEXT = 0
SJIS_TEXT = 1
ASCII_TEXT = 2

logFile = open('LOG/scriptExtractor.log', 'w')

MEMORY_CARD_STRINGS = 0
SAVE_FILE_STRINGS = 1
MEMORY_CARD_STRINGS_TITLE = 2

RAW_MODE = 0
LOAD_ADDR_MODE = 1

RAW_SCRIPT_CONFIGS = [[0x80042f74,0x80042f88,0x80042fac,0x80042fd0,0x80042ffc,0x80043028,0x80043050,0x80043070,0x8004308c,0x800430d0,
                       0x800430e4,0x80043128,0x80043148,0x80043194,0x800431e0,0x8004322c,0x80043278,0x800432c0,0x80043308,0x80043330,
                       0x80043358,0x80043374,0x800433c4,0x80043414], #Memcard ops
                      
                      [0x8009131c, 0x80091334, 0x8009134c], #Save file strings

                      [0x80041000, 0x80041024, 0x80041050, 0x8004107c, 0x800410a4, 0x800410c4, 0x800410e0, 0x800410f4, 0x8004111c, 0x80041160, 0x80041180,
                       0x800411cc, 0x80041218, 0x80041264, 0x800412b0, 0x800412f8, 0x80041340, 0x80041368, 0x80041390, 0x800413ac, 0x800413fc, 0x8004144c,
                       0x80041468, 0x800414bc, 0x80041510] #Memcard TITLE.EXE
                      
                      ] 

                 #File,                                       table start,        Table end,   Excluded Entries,     Text Start,        Text End
SCRIPTS =   [   ("EXTRACT - Original/BASE/BB_000.EXE",         0x80090c04,       0x80090ca0,                 [],     0x80040130,      0x80042354, NORMAL_TEXT), #Main Dialogue
                ("EXTRACT - Original/BASE/BB_000.EXE",         0x80092cb0,       0x80092d08,                 [],     0x8004374c,      0x8004392f, SJIS_TEXT),   #Toast text
                ("EXTRACT - Original/BASE/BB_000.EXE",         0x8009119c,       0x800912c8,                 [],     0x8004282c,      0x80042f54, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BASE/BB_000.EXE",         0x80043620,       0x80043650,                 [],     0x80043504,      0x80043620, NORMAL_TEXT), #Prompts

                #<<<<<<<<<<<<< UNUSED >>>>>>>>>>>>>>
                ("EXTRACT - Original/BASE/BB_001.EXE",         0x8008745c,       0x800874b4,                 [],     0x8003c05c,      0x8003d0d4, NORMAL_TEXT), #Main Dialogue

                ("EXTRACT - Original/BASE/BB_100.EXE",         0x800938ac,       0x80093a24,                 [],     0x80040148,      0x80045abc, NORMAL_TEXT), #Main Dialogue
                ("EXTRACT - Original/BASE/BB_100.EXE",         0x80095a34,       0x80095a8c,                 [],     0x80046eb4,      0x80047074, SJIS_TEXT),   #Toast text
                ("EXTRACT - Original/BASE/BB_100.EXE",         0x80093f20,       0x8009404c,                 [],     0x80045f94,      0x800466bc, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BASE/BB_100.EXE",         0x80046d88,       0x80046db8,                 [],     0x80046c6c,      0x80046d88, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BASE/BB_101.EXE",         0x8009481c,       0x80094914,                 [],     0x80040128,      0x80044f40, NORMAL_TEXT), #Main Dialogue
                ("EXTRACT - Original/BASE/BB_101.EXE",         0x80096928,       0x80096980,                 [],     0x80046338,      0x800464f8, SJIS_TEXT),   #Toast text
                ("EXTRACT - Original/BASE/BB_101.EXE",         0x80094e14,       0x80094f40,                 [],     0x80045418,      0x80045b40, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BASE/BB_101.EXE",         0x8004620c,       0x8004623c,                 [],     0x800460f0,      0x8004620c, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BASE/BB_200.EXE",         0x80091314,       0x800913e4,                 [],     0x80040138,      0x80043658, NORMAL_TEXT), #Main Dialogue
                ("EXTRACT - Original/BASE/BB_200.EXE",         0x800933f8,       0x80093450,                 [],     0x80044a50,      0x80044c10, SJIS_TEXT),   #Toast text
                ("EXTRACT - Original/BASE/BB_200.EXE",         0x800918e4,       0x80091a10,                 [],     0x80043b30,      0x80044258, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BASE/BB_200.EXE",         0x80044924,       0x80044954,                 [],     0x80044808,      0x80044924, NORMAL_TEXT), #Prompts

                
                ("EXTRACT - Original/BASE/BB_201.EXE",         0x80090f7c,       0x8009100c,                 [],     0x80040138,      0x800428c8, NORMAL_TEXT), #Main Dialogue
                ("EXTRACT - Original/BASE/BB_201.EXE",         0x80093020,       0x80093078,                 [],     0x80043cc0,      0x80043e80, SJIS_TEXT),   #Toast text
                ("EXTRACT - Original/BASE/BB_201.EXE",         0x8009150c,       0x80091638,                 [],     0x80042da0,      0x800434c8, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BASE/BB_201.EXE",         0x80043b94,       0x80043bc4,                 [],     0x80043a78,      0x80043b94, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BASE/BB_300.EXE",         0x8008f930,       0x8008f97c,                 [],     0x80040138,      0x80041fb0, NORMAL_TEXT), #Main Dialogue
                ("EXTRACT - Original/BASE/BB_300.EXE",         0x8009198c,       0x800919e4,                 [],     0x800433a8,      0x80043568, SJIS_TEXT),   #Toast text
                ("EXTRACT - Original/BASE/BB_300.EXE",         0x8008fe78,       0x8008ffa4,                 [],     0x80042488,      0x80042bb0, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BASE/BB_300.EXE",         0x8004327c,       0x800432ac,                 [],     0x80043160,      0x8004327c, NORMAL_TEXT), #Prompts

                
                ("EXTRACT - Original/BASE/BB_400.EXE",         0x80091f30,       0x80091f88,                 [],     0x80040130,      0x8004384c, NORMAL_TEXT), #Main Dialogue
                ("EXTRACT - Original/BASE/BB_400.EXE",         0x80093f9c,       0x80093ff4,                 [],     0x80044c44,      0x80044e04, SJIS_TEXT),   #Toast text
                ("EXTRACT - Original/BASE/BB_400.EXE",         0x80092488,       0x800925b4,                 [],     0x80043d24,      0x8004444c, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BASE/BB_400.EXE",         0x80044b18,       0x80044b48,                 [],     0x800449fc,      0x80044b18, NORMAL_TEXT), #Prompts

                #----------------------------------------------------------------------------------------------------------------------------------------------

                ("EXTRACT - Original/BR_MAIN1.EXE",            0x800b3468,       0x800b3594,                 [],     0x80040c58,      0x80041380, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BR_MAIN1.EXE",            0x80041a4c,       0x80041a7c,                 [],     0x80041930,      0x80041a4c, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BS_MAIN1.EXE",            0x800b20d8,       0x800b2204,                 [],     0x800413c0,      0x80041ae8, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BS_MAIN1.EXE",            0x800421b4,       0x800421e4,                 [],     0x80042098,      0x800421b4, NORMAL_TEXT), #Prompts
                ("EXTRACT - Original/BS_MAIN1.EXE",            0x800b1af4,       0x800b1b04,                 [],     0x800b1a24,      0x800b1af4, NORMAL_TEXT), #Missing text

                ("EXTRACT - Original/BR_MAIN2.EXE",            0x800bc5f4,       0x800bc720,                 [],     0x800415c8,      0x80041cf0, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BR_MAIN2.EXE",            0x800423bc,       0x800423ec,                 [],     0x800422a0,      0x800423bc, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BR_MAIN3.EXE",            0x800b6dcc,       0x800b6ef8,                 [],     0x80040d04,      0x8004142c, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BR_MAIN3.EXE",            0x80041af8,       0x80041b28,                 [],     0x800419dc,      0x80041af8, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BR_MAIN4.EXE",            0x800ba528,       0x800ba654,                 [],     0x80040f3c,      0x80041664, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BR_MAIN4.EXE",            0x80041d30,       0x80041d60,                 [],     0x80041c14,      0x80041d30, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BR_MAIN5.EXE",            0x800aea94,       0x800aebc0,                 [],     0x80040b54,      0x8004127c, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BR_MAIN5.EXE",            0x80041948,       0x80041978,                 [],     0x8004182c,      0x80041948, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BR_MAIN6.EXE",            0x800b6bac,       0x800b6cd8,                 [],     0x80040cd4,      0x800413fc, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BR_MAIN6.EXE",            0x80041ac8,       0x80041af8,                 [],     0x800419ac,      0x80041ac8, NORMAL_TEXT), #Prompts

                ("EXTRACT - Original/BR_MAIN7.EXE",            0x800b7584,       0x800b76b0,                 [],     0x800432b4,      0x800439dc, NORMAL_TEXT), #Item text
                ("EXTRACT - Original/BR_MAIN7.EXE",            0x800440a8,       0x800440d8,                 [],     0x80043f8c,      0x800440a8, NORMAL_TEXT),  #Prompts

                ("EXTRACT - Original/MOVIE/TITLE.EXE",         0x80040464,       0x800407cc,                 [],     0x80040084,      0x80040464, ASCII_TEXT), #Credits
                ("EXTRACT - Original/MOVIE/TITLE.EXE",         0x80041698,       0x800416ac,                 [],     0x80041604,      0x80041698, NORMAL_TEXT) #Prompts
            ] 

                #File                                         #Text Start     #Text End         #TEXT TYPE        #Text Pattern
RAW_SCRIPTS = [ ("EXTRACT - Original/BASE/BB_000.EXE",         0x80042f74,   0x80043430,       NORMAL_TEXT, MEMORY_CARD_STRINGS),#Memcard Text
                ("EXTRACT - Original/BASE/BB_000.EXE",         0x8009131c,   0x80091390,       NORMAL_TEXT, SAVE_FILE_STRINGS),  #Numbers and empty file
                
                ("EXTRACT - Original/MOVIE/TITLE.EXE",         0x80041000,   0x80041530,       NORMAL_TEXT, MEMORY_CARD_STRINGS_TITLE),#Memcard Text

                ("EXTRACT - Original/BS_MAIN1.EXE",            0x800426c0,   0x800426f8,       NORMAL_TEXT, [0x800426c0]) #Single Myuu line
                #("EXTRACT - Original/BR_MAIN1.EXE",            0x800413a0,   0x8004185c,       NORMAL_TEXT, MEMORY_CARD_STRINGS),#Memcard Text
                #("EXTRACT - Original/BR_MAIN1.EXE",            0x800b3618,   0x800b365c,       NORMAL_TEXT, MEMORY_CARD_STRINGS),#Save File String 1
                #("EXTRACT - Original/BR_MAIN1.EXE",            0x800b3600,   0x800b3614,       NORMAL_TEXT, MEMORY_CARD_STRINGS),#Save File String 2 
                #("EXTRACT - Original/BR_MAIN1.EXE",            0x800b35e8,   0x800b3600,       NORMAL_TEXT, MEMORY_CARD_STRINGS),#Save File String 3
            
            ] 


LOAD_SCRIPTS = [("EXTRACT - Original/BR_MAIN1.EXE",            0x80040000,   0x80040264,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1
                ("EXTRACT - Original/BR_MAIN1.EXE",            0x800402c4,   0x800405d4,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2

                ("EXTRACT - Original/BS_MAIN1.EXE",            0x80040000,   0x8004063c,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1
                ("EXTRACT - Original/BS_MAIN1.EXE",            0x8004078c,   0x80040bb0,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2

                ("EXTRACT - Original/BR_MAIN2.EXE",            0x80040000,   0x80040484,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1
                ("EXTRACT - Original/BR_MAIN2.EXE",            0x80040628,   0x80040e24,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2

                ("EXTRACT - Original/BR_MAIN3.EXE",            0x80040000,   0x800401a0,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1
                ("EXTRACT - Original/BR_MAIN3.EXE",            0x800402c4,   0x8004060c,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2

                ("EXTRACT - Original/BR_MAIN4.EXE",            0x80040000,   0x80040160,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1
                ("EXTRACT - Original/BR_MAIN4.EXE",            0x8004037c,   0x80040754,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2
                
                ("EXTRACT - Original/BR_MAIN5.EXE",            0x80040168,   0x800405a0,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1

                ("EXTRACT - Original/BR_MAIN6.EXE",            0x80040000,   0x800402ac,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1
                ("EXTRACT - Original/BR_MAIN6.EXE",            0x800403ec,   0x80040440,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2
                ("EXTRACT - Original/BR_MAIN6.EXE",            0x80040488,   0x80040628,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 3

                ("EXTRACT - Original/BR_MAIN7.EXE",            0x80040000,   0x80040f88,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main Dialogue 1
                ("EXTRACT - Original/BR_MAIN7.EXE",            0x80040f98,   0x80041080,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2 1798
                ("EXTRACT - Original/BR_MAIN7.EXE",            0x8004117c,   0x80042bcc,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 3

                ("EXTRACT - Original/MOVIE/TITLE.EXE",         0x800407e4,   0x8004091c,       NORMAL_TEXT, LOAD_ADDR_MODE)
            
            ] 
                #File                                #Load HI       #Load LO
#LOAD_OFFSETS_HI = [("EXTRACT - Original/BR_MAIN1.EXE",  [0x80045bbc, 0x80045be0, 0x80045bcc, 0x80045d64, 3, 0x80046018, 0x800474b4, 0x80047c38, 0x800463dc, 0x80046478, 0x80046e10, 0x80047128, 0x8004733c, #Dialogue 1
#                                                         0x80047374, 0x800473a0, 0x800473ac, 0x8004749c, 0x8004753c, 0x80047b8c, 0x80047bb8, 0x80047bc4, 0x80047ba4, 80048294],         
#                                                        [0x80045bdc, 0x80045be4, 0x80045c08, 0x80045d5c, 3, 0x80046020, 0x800474bc, 0x80047c40, 0x800463e4, 0x80046480, 0x80046e18, 0x80047130, 0x80047344,
#                                                         0x8004737c, 0x800473a8, 0x800473b0, 0x800474a4, 80047548, 0x80047bb4, 0x80047bc0, 0x80047bcc, 0x80047bd0, 0x8004829c]),
#                   ("EXTRACT - Original/BR_MAIN1.EXE",  [80043890, ],#Dialogue 2
#                                                        [80043abc, ])
#                  ]

END_CHARS = ["{END}"]
END_CHAR = "{END}"
NEW_LINE_CODE = "{NEWLINE}"
NEW_SPEAKER_CODE = "\f"

#TODO
NameCodes = [("<N1>", "Maia"),
             ("<N2>", "Herbert"),
             ("<N3>", "Seiryu"),
             ("<N4>", "Pasganon"),
             ("<N5>", "Kodachi"),
             ("<N6>", "Graves"),
             ("<N9>", "Luka"),
             ("<N-1>", "?")]


def __getMemoryBaseAddress(fileName):
    headerFile = open(fileName, "rb")
    headerData = headerFile.read()
    headerFile.close()
    memPTR  = int.from_bytes(headerData[MEM_PTR_OFFSET  :MEM_PTR_OFFSET  + 4], byteorder="little", signed=False)

    return memPTR


def get_portrait_name(name_code):
    for name_match in NameCodes:
        if name_match[0] == name_code:
            return "{" + name_match[1] + "}"

    return "{?}"

def strip_codes(text):
    '''Removes control codes from a piece of text for extraction'''
    cursor = 0
    
    output_buffer = ''

    control_codes = ["{NEXT}","{END}","\n","\f"]

    assert text.count("<") == text.count(">")

    while len(text) > 0:
        #Handle portrait names
        textChunk = text.split("<")[0]

        if text.startswith("<N"):
            name_code = text.split(">")[0] + '>'
            output_buffer += get_portrait_name(name_code)
            text = text[text.index('>') + 1:]
        elif text.startswith("<"):
            
            text = text[text.index('>') + 1:]
        
        #elif textChunk == '' or textChunk.strip() in control_codes:
        #    text = text[len(textChunk):]
        else:
            #if textChunk not in control_codes: 
            output_buffer += "❖" + textChunk
            #else:
            #    output_buffer += textChunk
            text = text[len(textChunk):]
        
        cursor += 1
        

    return output_buffer

def getLineStarts(textBinary):
    starts = [0]
    END_CHAR = 0

    for x in range(len(textBinary)):
        if textBinary[x] == END_CHAR:
            starts += [x + 1]

    return starts[:-1] #Last element is invalid

def extractScript(script):
    if not os.path.exists(SCRIPT_OUTPUT_FOLDER):
            os.makedirs(SCRIPT_OUTPUT_FOLDER)

    fileName = script[0]
    baseAddress = __getMemoryBaseAddress(fileName) - 0x800
    tableStart = script[1]
    tableEnd  = script[2]

    textStart = script[4] - baseAddress
    textEnd  = script[5] - baseAddress

    tableSize = tableEnd - tableStart

    inputFilePath = DATA_FOLDER

    inputFile = open(fileName, 'rb')
    inputData = inputFile.read()

    tableCursor = 0

    outputFilePath = SCRIPT_OUTPUT_FOLDER + "/" + os.path.basename(fileName) +"-"+ str(tableStart) + ".txt"
    verboseFilePath = SCRIPT_OUTPUT_FOLDER + "/" + os.path.basename(fileName) +"-"+ str(tableStart) + "-verbose.txt"
    outputFile = open(outputFilePath, "w", encoding="utf-8")
    verboseFile = open(verboseFilePath, "w", encoding="utf-8")

    lineEntriesRead = []
    lineEntryNumbers = []
    outputBuffer = ''
    verboseBuffer = ''
    if textStart <= 0 and textEnd <= 0:
        textStart = 0xFFFFFFFF
        textEnd = 0
        defined_destination = False
    else:
        defined_destination = True

    while tableCursor <= tableSize:
        inputFile.seek(tableStart + tableCursor - baseAddress)
        textPointer = int.from_bytes(inputFile.read(4),byteorder='little', signed=False)
        nextEntryStart = textPointer - baseAddress

        

        lineNumber = tableCursor//4

        if textPointer & 0xFF000000 != 0x80000000:
            tableCursor    += TABLE_ENTRY_SIZE
            outputBuffer += '<<<LINE ' + str(lineNumber).zfill(4) + ' is table embedded text(' + hex(textPointer) + ')\n\n'
            verboseBuffer += '<<<LINE ' + str(lineNumber).zfill(4) + ' is table embedded text(' + hex(textPointer) + ')\n\n'
            continue

        if nextEntryStart in lineEntriesRead:
            tableCursor    += TABLE_ENTRY_SIZE
            entryNum = lineEntriesRead.index(nextEntryStart)
            outputBuffer += '<<<LINE ' + str(lineNumber).zfill(4) + " points to LINE " + str(lineEntryNumbers[entryNum]).zfill(4) + '>>>\n\n'
            verboseBuffer += '<<<LINE ' + str(lineNumber).zfill(4) + " points to LINE " + str(lineEntryNumbers[entryNum]).zfill(4) + '>>>\n\n'
            continue

        lineEntriesRead.append(nextEntryStart)
        lineEntryNumbers.append(lineNumber)
        
        intEntries =  [x for x in inputData[nextEntryStart:]]
        nextEntryEnd   =  intEntries.index(0) + nextEntryStart + 1
        
        if not defined_destination:
            if nextEntryStart < textStart:
                textStart = nextEntryStart

            if nextEntryEnd > textEnd and not (lineNumber > 0 and ((nextEntryEnd - textEnd) > 0x010000)):
                textEnd = nextEntryEnd

        
        lineHeader = '<<<LINE ' + str(lineNumber).zfill(4) + '>>>\n'
        outputBuffer += lineHeader
        verboseBuffer += lineHeader

        nextLineBinary = inputData[nextEntryStart:nextEntryEnd]
        convertedText = textConversion.hexToText(nextLineBinary.hex())
        verboseText = convertedText
        convertedText = strip_codes(convertedText)
        convertedText = convertedText.replace("{NEWLINE}", "\n")
        convertedText = convertedText.replace("{NEXT}", "{NEXT}\n")
        convertedText = convertedText.replace("{END}", "{END}\n\n")

        verboseText = verboseText.replace("{NEWLINE}", "\n")
        verboseText = verboseText.replace("{NEXT}", "{NEXT}\n")
        verboseText = verboseText.replace("{END}", "{END}\n\n")
        #convertedText = convertedText.replace("ctrlEND}", "ctrlEND}\n")

        

        outputBuffer += "//" + convertedText.strip().replace("\n", "\n//") + "\n//\n" + convertedText
        verboseBuffer += "//" + verboseText.strip().replace("\n", "\n//") + "\n//\n" + verboseText

        tableCursor    += TABLE_ENTRY_SIZE

    headerLine = "//Source: " + fileName + " at offset " + hex(tableStart) + "\n" + "//|Start|End|: |" + str(textStart) + "|" + str(textEnd) + "|\n"

    outputFile.write(headerLine + outputBuffer)
    verboseFile.write(headerLine + verboseBuffer)
    outputFile.close()
    verboseFile.close()
    inputFile.close()

def addComments(textFilePath):
    textFile = open(textFilePath, "r+", encoding="utf8")
    total_text = ""
    while True:
        nextLine = textFile.readline()
        total_text += nextLine
        
        if nextLine.startswith("<<<LINE"):
            current_lines = []

            while True:
                nextLine = textFile.readline()
                current_lines += [nextLine]
                if "{END}" in nextLine:
                    break

            for line in current_lines:
                total_text += "//" + line
                if not line.endswith("\n"):
                    total_text += "\n"

            for line in current_lines:
                total_text += line

        elif not nextLine:
            break
            
    output = open(textFilePath, 'w', encoding="utf8")
    output.write(total_text)
    return

def extractSegment(segment):
    filePath = segment[0]
    textOffset = segment[1]
    textLength = segment[2] - segment[1]
    if not os.path.exists(SCRIPT_OUTPUT_FOLDER):
            os.makedirs(SCRIPT_OUTPUT_FOLDER)

    baseAddress = __getMemoryBaseAddress(filePath) - 0x800

    textOffset = textOffset - baseAddress

    inputFile = open(filePath, 'rb')
    inputFile.read(textOffset)

    outputFilePath = SCRIPT_OUTPUT_FOLDER + "/" + filePath.split('/')[-1] + "-" + hex(textOffset) + ".txt"
    logFile.write("Extracting " + hex(textLength) + " bytes of " + filePath + " at " + hex(textOffset) + " into " + outputFilePath + "\n")

    outputFile = open(outputFilePath, "w", encoding="utf-8")

    textBinary = inputFile.read(textLength)

    convertedText = textConversion.hexToText(textBinary.hex())

    convertedText = convertedText.replace("{END}{END}{END}{END}", "{END}")
    convertedText = convertedText.replace("{END}{END}{END}", "{END}")
    convertedText = convertedText.replace("{END}{END}", "{END}")

    outputBuffer = "//Source: " + filePath.split('/')[-1] + " at offset " + hex(textOffset) + "\n" + "<<<LINE 0001>>>" + "\n"

    lineNumber = 2
    lines = convertedText.count("{END}")
    convertedText = convertedText.replace("{NEWLINE}", "\n")
    convertedText = convertedText.replace("{NEXT}", "{NEXT}\n")
    convertedText = convertedText.replace("{END}", "{END}\n\n" + "<<<LINE XXXX>>>" + "\n", lines-1)

    while lineNumber <= lines + 1:
        convertedText = convertedText.replace("<<<LINE XXXX>>>", "<<<LINE " + str(lineNumber).zfill(4) +  ">>>",1)
        lineNumber+=1


    outputFile.write(outputBuffer + convertedText)
    outputFile.close()

    addComments(outputFilePath)

    inputFile.close()

def extractSegments():
    for seg in RAW_SCRIPTS:
        extractSegment(seg)

def injectLoadAddresses(file_path, hi_loads, lo_loads, hi_offsets, lo_offsets):

    assert len(hi_loads) == len(hi_offsets), "HI loads/offsets mismatch"
    assert len(lo_loads) == len(lo_offsets), "LO loads/offsets mismatch"

    target_file = open(file_path, "r+b")

    for x in range(len(hi_loads)):
        target_file.seek(hi_offsets[x])
        target_file.write(hi_loads[x].to_bytes(2, byteorder='little'))

    for x in range(len(lo_loads)):
        target_file.seek(lo_offsets[x])
        target_file.write(lo_loads[x].to_bytes(2, byteorder='little'))

    target_file.close()
    return

def getOffsetsAndLoads(Instruction_File, line_starts, text_start, base_address):
    hi_loads = []
    lo_loads = []
    hi_offsets = []
    lo_offsets = []

    for start in line_starts:
        start_hi = ((start + text_start) & 0xFFFF0000) >> 16
        start_lo =  (start + text_start) & 0x0000FFFF
        hi_loads += [start_hi]
        lo_loads += [start_lo]
    
    line_number = 0
    total_copies = 0
    while True:
        nextLine = Instruction_File.readline()
        if nextLine.startswith(COMMENT):
            continue
        elif nextLine.startswith(".endfile"):
            break

        splitLine = nextLine.split(" ")

        if len(splitLine) >= 2:
            hi_offsets += [int("0x" + splitLine[1].rstrip(), 16) - base_address]
            lo_offsets += [int("0x" + splitLine[0], 16) - base_address]
            line_number += 1
        elif len(splitLine) == 1:
            num_copies = int(splitLine[0].rstrip())
            to_add_hi = []
            to_add_lo = []
            for x in range(num_copies - 1):
                #TODO
                #to_add_hi += [hi_loads[line_number + total_copies]]
                #to_add_lo += [lo_loads[line_number + total_copies]]
                to_add_hi += [hi_loads[line_number]]
                to_add_lo += [lo_loads[line_number]]

            #hi_loads = hi_loads[0:line_number + total_copies] + to_add_hi + hi_loads[line_number + total_copies:]
            #lo_loads = lo_loads[0:line_number + total_copies] + to_add_lo + lo_loads[line_number + total_copies:]
            hi_loads = hi_loads[0:line_number] + to_add_hi + hi_loads[line_number:]
            lo_loads = lo_loads[0:line_number] + to_add_lo + lo_loads[line_number:]

            total_copies += num_copies - 1

        elif not nextLine or nextLine.startswith(".startfile"):
            assert False, '[ERROR] Unexpected EOF in load_scripts.txt!!!'






    return hi_loads, lo_loads, hi_offsets, lo_offsets


def injectLoadScript(file_path, line_starts, target_script_number, text_start, text_end):
    Instruction_File = open(LOAD_OFFSET_TEXT_FILE, 'r')
    base_address = __getMemoryBaseAddress(file_path) - 0x800
    script_number = 0

    while True:
        nextline = Instruction_File.readline()

        if nextline.startswith(COMMENT):
            continue
        elif nextline.startswith(".startfile"):
            if script_number == target_script_number:
                hi_loads, lo_loads, hi_offsets, lo_offsets = getOffsetsAndLoads(Instruction_File, line_starts, text_start, base_address)
                injectLoadAddresses(file_path, hi_loads, lo_loads, hi_offsets, lo_offsets)
                Instruction_File.close()
                return

            else:
                script_number += 1
                continue
            
        elif nextline:
            continue
        elif not nextline:
            break

    return


def extractLoadScripts():
    for seg in LOAD_SCRIPTS:
        extractSegment(seg)



def extractScripts():
    for script in SCRIPTS:
        extractScript(script)

def isScriptUnmodified(file):
    try:
        os.makedirs(REBUILT_FOLDER)
    except:
        pass

    try:
        unmodified = filecmp.cmp(os.path.join(SCRIPT_FOLDER, file), os.path.join(REBUILT_FOLDER, file) )
    except FileNotFoundError:
        return False

    return unmodified

def injectScripts():
    for script in SCRIPTS:
        injectScript(script)

def getLine(file_path, lineNumber):
    '''Gets the given text line from the given text file'''
    text_file = open(file_path, 'r', encoding='utf-8')

    full_line = ''

    #Seek to line start
    while True:
        line = text_file.readline()
        if line.startswith("<<<LINE " + str(lineNumber).zfill(4)):
            break
        if not line:
            raise Exception("Line " + str(lineNumber) + " was not found in file " + file_path)
    
    while True:
        #read rest of line
        nextLine = text_file.readline()
        if nextLine.startswith(COMMENT):
            continue
        elif nextLine.startswith("<<<") or not nextLine:
            raise Exception("Line " + str(lineNumber) + " is not properly terminated in file " + file_path)

        full_line = full_line + nextLine

        if END_CHAR in nextLine:
            break

    return full_line

def getNextCleanText(text_line):

    if OPENER in text_line:
        return text_line[:text_line.index(OPENER)]
    else:
        return text_line

    """if OPENER not in text_line and CLOSER not in text_line:
        #Final chunk of text
        return text_line
    elif not text_line.startswith(OPENER):
        #Cursor at text 
        return(text_line[:text_line.index(OPENER)])
    
    cursor = 0

    while True:
        cursor = text_line.index(OPENER, cursor) + 1
        if text_line[cursor] == OPENER:
            continue

    return"""

def getNextControlBlock(text_line):
    
    start_pos = text_line.index(OPENER)

    cursor = 0
    while True:
        cursor = text_line.index(CLOSER, cursor) + 1
        if text_line[cursor] == OPENER:
            continue
        elif END_CHAR not in text_line:
            raise Exception("Line: " + text_line + " is missing END char.")
        else:
            break
        
    return text_line[start_pos:cursor]


def reinsert_control_codes(textLine, lineNumber, verbose_file_path):
    #TODO
    buffer = ''
    cursor = 0
    verbose_line = getLine(verbose_file_path, lineNumber)

    
    split_line = textLine.split(DELIMITER)
    
    verbose_split_line = verbose_line.split(DELIMITER)
    split_index = 1

    if verbose_line.startswith(OPENER):
        next_control = getNextControlBlock(verbose_line)
        buffer += next_control
        cursor = len(buffer)


    while True:
        buffer += split_line[split_index]
       
        split_index += 1
        if split_index >= len(split_line):
            break
        next_verbose_control_pos = verbose_line[cursor:].index(getNextControlBlock(verbose_line[cursor:]))
        cursor += next_verbose_control_pos

        if verbose_line[cursor:]:
            next_control = getNextControlBlock(verbose_line[cursor:])
            buffer += next_control
            cursor += len(next_control)

        
        


    return buffer

def injectSegment(raw_script, write_mode):
    originalFilePath = raw_script[0]
    targetFilePath   = originalFilePath.replace(" - Original", '')
    #targetFilePath = INJECT_OUTPUT_FOLDER + "/" + os.path.basename(originalFilePath)
    textStart = raw_script[1]
    textEnd = raw_script[2]
    max_size = textEnd - textStart
    tableType = raw_script[3]
    raw_type_index =   raw_script[4]

    baseAddress = __getMemoryBaseAddress(originalFilePath) - 0x800

    textFilePath = SCRIPT_FOLDER + "/" + os.path.basename(originalFilePath) +"-"+ hex(textStart - baseAddress) + ".txt"

    originalFile = open(originalFilePath, 'rb')
    originalFile.seek(textStart)

    targetFile = open(targetFilePath, 'r+b')
    targetFile.seek(textStart)
    
    textFile = open(textFilePath, 'r', encoding="utf-8")
    textFile.seek(0)
    
    curr_offset = 0
    total_data = b''
    while True:
        nextByte = originalFile.read(1)
        entryLine = textFile.readline()

        if entryLine.startswith("<<<LINE "):

            lineNumber = int(entryLine[8:12]) - 1

            endCount = 0
            textLine = ''
            while endCount == 0:
                nextLine = textFile.readline()

                if nextLine.startswith('//'):
                    continue
                
                textLine += nextLine
                

                for endChar in END_CHARS:
                    endCount += textLine.count(endChar)
                    textLine = textLine.replace(endChar + "\n",endChar)
            
            textLine = textLine.replace("\n", NEW_LINE_CODE)
            
            #Remove line break added after NEXT codes
            textLine = textLine.replace("{NEXT}" + NEW_LINE_CODE, "{NEXT}")

            for name in NameCodes:
                textLine = textLine.replace("{" + name[1] + "}", '')

            if "<<<" in textLine:
                assert False, "Line header processed in line " + str(lineNumber) + ":" + textLine

            textLine = textLine.replace(NEW_LINE_CODE, ' ')
            textLine = textLine.replace('  ', ' ')
            textLine = addSpacing(textLine)
            
            dataToAdd = bytearray.fromhex(textConversion.textToHex(textLine, tableType))
            total_data += dataToAdd
            
            if write_mode == RAW_MODE:
                try:
                    offset_from_start = RAW_SCRIPT_CONFIGS[raw_type_index][lineNumber] - RAW_SCRIPT_CONFIGS[raw_type_index][0]
                except TypeError:
                    #If only 1 entry it starts at 0
                    offset_from_start = 0
                offset = textStart + offset_from_start - baseAddress
            elif write_mode == LOAD_ADDR_MODE:
                offset = textStart + curr_offset - baseAddress
            
            curr_offset += len(dataToAdd)

            if curr_offset < max_size:
                targetFile.seek(offset)
                targetFile.write(dataToAdd)

        elif entryLine:
            continue

        elif not entryLine:
            break
    
    assert max_size >= curr_offset, "[ERROR] TEXT FILE " + textFilePath + " IS OVER BUDGET BY " + str(curr_offset - max_size) + " MOJI/BYTES!!! LINES SKIPPED!!!"
    if not os.path.exists(INJECT_OUTPUT_FOLDER):
        os.mkdir(INJECT_OUTPUT_FOLDER)

    shutil.copyfile(textFilePath, os.path.join(REBUILT_FOLDER, textFilePath.split('/')[-1]))
    lineStarts = getLineStarts(total_data)
    return lineStarts

def injectSegments():
    for segment in RAW_SCRIPTS:
        try:
            injectSegment(segment, RAW_MODE)
        except FileNotFoundError:
            print("[WARNING] FILE " + segment[0] + " NOT FOUND, SKIPPING")

    return

def injectLoadScripts():
    script_number = 0
    for script in LOAD_SCRIPTS:
        try:
            lineStarts = injectSegment(script, LOAD_ADDR_MODE)
        except FileNotFoundError:
            print("[WARNING] FILE " + script[0] + " NOT FOUND, SKIPPING")
        file_path = script[0]
        text_start = script[1]
        text_end  = script[2]
        print("Injecting CPU load script: " + file_path + " " +  hex(text_start))
        injectLoadScript(file_path.replace(" - Original", ''), lineStarts, script_number, text_start, text_end)
        script_number += 1

    return    

def findLength(inputText):
    
    charCount = 0
    inSymbol = False
    
    symbol = ''

    CHARS = ['{TRIANGLE}', '{CIRCLE}', '{ESQ}', '{SQUARE}', '{CROSS}', '{ANGLE_RIGHT}', '{ANGLE_LEFT}']
    APOS = ["'v","'r","'t","'n","'s","''","'l","'d"]
    APOS3 = ["'m"]
    for char in inputText:
        if inSymbol == False:
            if char == '{' or char == '<':
                inSymbol = True
                symbol = char
            else:
                charCount += 1
            
        else:
            symbol += char
            if char =='}' or char == '>':
                inSymbol = False
                if symbol in CHARS:
                    charCount +=1
                elif symbol == "{NEXT}":
                    charCount = 0
                else:
                    continue
                symbol = ''

    for apo_code in APOS:
        subCount = inputText.count(apo_code)
        charCount = charCount - subCount
    
    for apo3_code in APOS3:
        if inputText.endswith(apo3_code):
            charCount = charCount - 1

    return charCount


#Returns a text string with text correctly spaced at a maximum of 32 characters per line 
def addSpacing(inputText):

    #if '@' in inputText or inputText=='\n' or inputText=='' or NEW_LINE_CODE in inputText:
    #    return inputText
    
    next_split = inputText.split("{NEXT}")

    output = ''
    for entry_num in range(len(next_split)):
        splitLine = next_split[entry_num].split(' ')

        splitCursor = 0
        
        while splitCursor < len(splitLine):
            lineTotal = 0
            output = output.strip()
            while splitCursor < len(splitLine):
                
                lineTotal += findLength(splitLine[splitCursor])
                if lineTotal > 32:
                    if findLength(splitLine[splitCursor]) > 32:
                        print("TEXT LINE TOO LONG: " + splitLine[splitCursor])
                        output += splitLine[splitCursor] + ' '
                        lineTotal += 1
                        splitCursor += 1
                    else:
                        output = output.strip()
                        output += NEW_LINE_CODE
                        lineTotal = 0
                elif lineTotal == 32:
                    output += splitLine[splitCursor]
                    lineTotal = 0
                    splitCursor += 1
                else:
                    output += splitLine[splitCursor] + ' '
                    lineTotal += 1
                    splitCursor += 1
        if entry_num < len(next_split) - 1:
            output = output.strip() + "{NEXT}"
    
    return output.strip()

#print(addSpacing("That's not what I mean! I'm... I'm Chris!"))

def injectScript(script):
    fileName = script[0]
    tableStart = script[1]
    tableEnd   = script[2]
    tableType  = script[6]
    exclusions = script[3]
    tableSize  = tableEnd - tableStart

    if not os.path.exists(INJECT_OUTPUT_FOLDER):
        os.mkdir(INJECT_OUTPUT_FOLDER)

    if not os.path.exists(os.path.join(INJECT_OUTPUT_FOLDER,os.path.basename(fileName))):
        shutil.copyfile(fileName, os.path.join(INJECT_OUTPUT_FOLDER,os.path.basename(fileName)))


    baseAddress = __getMemoryBaseAddress(fileName) - 0x800

    scriptFilePath = SCRIPT_FOLDER + "/" + os.path.basename(fileName) +"-"+ str(tableStart) + ".txt"
    outFilePath = fileName.replace(" - Original", '')
    #outFilePath = INJECT_OUTPUT_FOLDER + "/" + os.path.basename(fileName)
    
    #TODO: UNCOMMENT FOR PRODUCTION
    #if isScriptUnmodified(os.path.basename(fileName) +"-"+ str(tableStart) + ".txt"):
    #    return

    print('\tInjecting Script: ' + scriptFilePath)
    try:
        inputScript = open(scriptFilePath, mode='r', encoding='utf-8')
    except FileNotFoundError:
        print('[WARNING] English script not found: ' + scriptFilePath)
        return
    inputScript.readline()
    boundsLine = inputScript.readline()
    textStart = script[4] - baseAddress
    textEnd   = script[5] - baseAddress

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
                #inputScript.readline()
            elif "table embedded text" in entryLine:
                tableBuffer += tableEntry.to_bytes(4, byteorder = "little", signed=False)
                #inputScript.readline()
            else:
                lineNumber = int(entryLine[8:12])
                if lineNumber in exclusions:
                    continue

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
                
                #Remove line break added after NEXT codes
                textLine = textLine.replace("{NEXT}" + NEW_LINE_CODE, "{NEXT}")

                for name in NameCodes:
                    textLine = textLine.replace("{" + name[1] + "}", '')

                if "<<<" in textLine:
                    assert False, "Line header processed in line " + str(lineNumber) + ":" + textLine

                dataBuffer = textConversion.align_data(dataBuffer)
                tableEntry = len(dataBuffer) + textStart + baseAddress
                tableBuffer += tableEntry.to_bytes(4, byteorder='little', signed=False)
                
                verbose_file_path = scriptFilePath.split(".txt")[0] + "-verbose.txt"
                try:
                    textLine = reinsert_control_codes(textLine, lineNumber, verbose_file_path)
                except ValueError:
                    assert False, "VERBOCITY ERROR!!! File " + verbose_file_path + " LINE: " + str(lineNumber)


                textLine = textLine.replace(NEW_LINE_CODE, ' ')
                textLine = textLine.replace('  ', ' ')
                textLine = addSpacing(textLine)

                dataToAdd = bytearray.fromhex(textConversion.textToHex(textLine, tableType))
                dataBuffer += dataToAdd

        elif entryLine:
            continue

        elif not entryLine:
            break


    #assert len(dataBuffer) <= maxTextLength, scriptFilePath + ' is over script budget by ' + str(len(dataBuffer) -maxTextLength)  + ' bytes'
    if len(dataBuffer) > maxTextLength:

        print(scriptFilePath + ' is over script budget by ' + str(len(dataBuffer) -maxTextLength)  + ' bytes. Skipping...')
        return


    print ("\t" + str(maxTextLength - len(dataBuffer)) + " bytes remaining in script " + scriptFilePath)

    dataBuffer += bytes(maxTextLength -  len(dataBuffer))

    '''
    parentData = open(outFilePath.replace(" - Original", ""),'r+b').read()
    outputBuffer = parentData[:textStart]
    outputBuffer += dataBuffer
    outputBuffer += parentData[len(outputBuffer):]

    assert len(parentData) == len(outputBuffer), "Len original: " + str(len(parentData)) + ", Len new:" + str(len(outputBuffer))

    secondBuffer = outputBuffer[:tableStart - baseAddress]
    secondBuffer += tableBuffer
    secondBuffer += outputBuffer[len(secondBuffer):]

    #outputBuffer += parentData[textEnd:tableStart]
    #outputBuffer += tableBuffer
    #outputBuffer += parentData[tableStart + tableSize:]

    assert len(parentData) == len(secondBuffer), "Len original: " + str(len(parentData)) + ", Len new:" + str(len(secondBuffer))
    if not os.path.exists(INJECT_OUTPUT_FOLDER):
        os.mkdir(INJECT_OUTPUT_FOLDER)
    outputFile = open(outFilePath, 'wb')
    outputFile.write(secondBuffer)
    '''

    outFile = open(outFilePath, "r+b")
    outFile.seek(textStart)
    outFile.write(dataBuffer)
    outFile.seek(tableStart - baseAddress)
    outFile.write(tableBuffer)



    

    shutil.copyfile(scriptFilePath, os.path.join(REBUILT_FOLDER, scriptFilePath.split('/')[-1]))

    return

def testRTF():
    file = open("Texts/test_tl.rtf", 'r', encoding="utf-8")
    
    while True:
        line = file.readline()
        print(line)
        if not line:
            break

def extract_all():
    print("Extracting Segments...")
    extractSegments()
    print("Extracting Normal Scripts...")
    extractScripts()
    print("Extracting CPU Load Scripts...")
    extractLoadScripts()

#extract_all()
#extractSegment(RAW_SCRIPTS[3])

#extractSegments()
#extractLoadScripts()
#addComments("SCRIPT/BS_MAIN1.EXE-0x800.txt")
#sinjectLoadScripts()
#extractLoadScripts()
#extractSegments()
#injectSegment(RAW_SCRIPTS[0])
#extractSegment(RAW_SCRIPTS[3][0], RAW_SCRIPTS[3][1], RAW_SCRIPTS[3][2] - RAW_SCRIPTS[3][1])
#testRTF()
#extractScript(SCRIPTS[1])
#injectScript(SCRIPTS[0])
#extractScript((12447744,          0x13A4A8,       0x3EC))
#injectScript((12447744,          0x13A4A8,       0x3EC))
#extractScripts()
#print(textConversion.textToHex('{left}{Katoh}{neutral}{argsEnd}{ID=0x34303935}{ctrlEND3}{NEWLINE}メッセージ不明{NEWLINE}{END}'))
#injectScript(SCRIPTS[0])
#extractScript(SCRIPTS[0])
#extractSegment("EXTRACT/PSX.05402624.bodyUncompressed" , 0x1E40, 0x5001, 0, 0)
#extractSegment("EXTRACT/PSX.12447744.bodyUncompressed" , 0x21C0, 0x562D, 0, 0)