#########################################################################
# Forms script text files from script data files                        #
#########################################################################




from cgitb import text
import os
import resource
import textConversion

import filecmp

SCRIPT_OUTPUT_FOLDER = "SCRIPT"
SCRIPT_FOLDER = "SCRIPT_EDITS"
INJECT_OUTPUT_FOLDER = "EXTRACT"
SCRIPT_INPUT_FOLDER  = "BD_EDITS"
TABLE_ENTRY_SIZE = 4
DATA_FOLDER = "BD_EXTRACT"
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
MAID_MYU0 = 3

RAW_MODE = 0
LOAD_ADDR_MODE = 1

RAW_SCRIPT_CONFIGS = [[0x80042f74,0x80042f88,0x80042fac,0x80042fd0,0x80042ffc,0x80043028,0x80043050,0x80043070,0x8004308c,0x800430d0,
                       0x800430e4,0x80043128,0x80043148,0x80043194,0x800431e0,0x8004322c,0x80043278,0x800432c0,0x80043308,0x80043330,
                       0x80043358,0x80043374,0x800433c4,0x80043414], #Memcard ops
                      
                      [0x8009131c, 0x80091334, 0x8009134c], #Save file strings

                      [0x80041000, 0x80041024, 0x80041050, 0x8004107c, 0x800410a4, 0x800410c4, 0x800410e0, 0x800410f4, 0x8004111c, 0x80041160, 0x80041180,
                       0x800411cc, 0x80041218, 0x80041264, 0x800412b0, 0x800412f8, 0x80041340, 0x80041368, 0x80041390, 0x800413ac, 0x800413fc, 0x8004144c,
                       0x80041468, 0x800414bc, 0x80041510], #Memcard TITLE.EXE
                      
                      [0x2a1, 0x2da, 0x313, 0x34c, 0x385, 0x3be, 0x3f7, 0x430, 0x469, 0x4a2, 0x4db, 0x514, 0x54d,
                       0x586, 0x5bf, 0x5f8, 0x631, 0x66a, 0x6a3, 0x6dc, 0x715, 0x74e, 0x787, 0x7c0, 0x7f9, 0x832,
                       0x86b, 0x8a4, 0x8dd, 0x916, 0x94f, 0x988, 0x9c1, 0x9fa, 0xa33, 0xa6c] #MAID MYU0

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

                ("EXTRACT - Original/MOVIE/TITLE.EXE",         0x80040464,       0x800407cc,                 [],     0x80040084,      0x80040464, ASCII_TEXT) #Credits
            
            ] 

                #File                                         #Text Start     #Text End         #TEXT TYPE        #Text Pattern
RAW_SCRIPTS = [ ("EXTRACT - Original/BASE/BB_000.EXE",         0x80042f74,   0x80043430,       NORMAL_TEXT, MEMORY_CARD_STRINGS),#Memcard Text
                ("EXTRACT - Original/BASE/BB_000.EXE",         0x8009131c,   0x80091390,       NORMAL_TEXT, SAVE_FILE_STRINGS), #Numbers and empty file
                
                ("EXTRACT - Original/MOVIE/TITLE.EXE",         0x80041000,   0x80041530,       NORMAL_TEXT, MEMORY_CARD_STRINGS_TITLE),#Memcard Text

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
                ("EXTRACT - Original/BR_MAIN7.EXE",            0x80040f98,   0x80041080,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 2
                ("EXTRACT - Original/BR_MAIN7.EXE",            0x8004117c,   0x80042bcc,       NORMAL_TEXT, LOAD_ADDR_MODE),#Main DIalogue 3

                ("EXTRACT - Original/MOVIE/TITLE.EXE",         0x800407e4,   0x8004091c,       NORMAL_TEXT, LOAD_ADDR_MODE)
            
            ] 

MAID_SCRIPTS_PTRS = [
                    ("ISO_EDITS/SLPS_204.64", 0x0020e0b0, 0x0020e0f0, 0x0022a0b0, 0x0022a1c0, NORMAL_TEXT),
                    ("ISO_EDITS/SLPS_204.64", 0x0020e110, 0x0020e154, 0x0022a1c0, 0x0022a5b0, NORMAL_TEXT),
                    ("ISO_EDITS/SLPS_204.64", 0x0020e170, 0x0020e1a0, 0x0022a5b0, 0x0022a9c0, NORMAL_TEXT),
                    ("ISO_EDITS/SLPS_204.64", 0x0020e1d0, 0x0020e210, 0x0022a9c0, 0x0022ab20, NORMAL_TEXT),
                    ("ISO_EDITS/SLPS_204.64", 0x0020e218, 0x0020e240, 0x0022ab20, 0x0022acd0, NORMAL_TEXT),
                    ("ISO_EDITS/SLPS_204.64", 0x0022fdcc, 0x0022fdd8, 0x0022acd0, 0x0022adb0, NORMAL_TEXT)
                    ]
MAID_RAW_SCRIPTS = [("INSTANCE/MAP_0x266f800_0x267fd40.MYU0.modified", 0x2A1, 0xAA5, NORMAL_TEXT, MAID_MYU0)]

MAID_LOAD_SCRIPTS = [
                    ("ISOrip/SLPS_204.64", 0x00229ec0, 0x0022a050, SJIS_TEXT, LOAD_ADDR_MODE)
                    ]

MMDH_FILES =[
             "MAP_0x5ef1800_0x6345c00_0x6345e80_0x6345fc0_0x6346340.MMDH",
             "MAP_0x6b29800_0x6dc1ac0_0x6dc1d40_0x6dc1ec0_0x6dcbb80.MMDH",
             "MAP_0x6b29800_0x6dc1ac0_0x6dc1d40_0x6dcfcc0_0x6dd1dc0.MMDH",
             "MAP_0x6b29800_0x6dc1ac0_0x6dc1d40_0x6dd5b40_0x6dee340.MMDH",
             "MAP_0x6e14800_0x716b240_0x716b4c0_0x716b640_0x71743c0.MMDH",
             "MAP_0x6e14800_0x716b240_0x716b4c0_0x717de80_0x7189ec0.MMDH",
             "MAP_0x13e5000_0x1502940_0x1509a00_0x150a380.MMDH",
             "MAP_0x66f0000_0x6b019c0_0x6b01c40_0x6b01dc0_0x6b02840.MMDH",
             "MAP_0x66f0000_0x6b019c0_0x6b01c40_0x6b05200_0x6b09840.MMDH",
             "MAP_0x5444000_0x54b1800_0x54b1900_0x54c4d00.MMDH",
             "MAP_0x5444000_0x54b1800_0x54e2c40_0x54f6040.MMDH",
             "MAP_0x5514000_0x591dd00_0x591df80_0x594c100_0x59542c0.MMDH",
             "MAP_0x5963000_0x5ea17c0_0x5ea1a40_0x5ea1b80_0x5eb3840.MMDH",
             "MAP_0x6346800_0x669ab80_0x669ae00_0x66e0480_0x66e41c0.MMDH",
             "MAP_0x6346800_0x669ab80_0x669ae00_0x669af80_0x66aef00.MMDH",
             "MAP_0x7195000_0x73d5ac0_0x73d5d40_0x73d5f40_0x73f7040.MMDH",
             "MAP_0x7195000_0x73d5ac0_0x73d5d40_0x74b4680_0x74bb140.MMDH",
             "MAP_0x7195000_0x73d5ac0_0x73d5d40_0x74d2580_0x74d4a00.MMDH",
             "MAP_0x7195000_0x73d5ac0_0x73d5d40_0x74dba40_0x74eba00.MMDH",
             "MAP_0x7195000_0x73d5ac0_0x73d5d40_0x7507d80_0x751a880.MMDH",
             "MAP_0x7195000_0x73d5ac0_0x73d5d40_0x7445340_0x74663c0.MMDH"
            ]

MAID_FRAGMENTS = ["ISO_EDITS/SLPS_204.64", [   (0x0022fd88, "　", "  "),        (0x0022fdb8, "　⇒　", "  ->  "),
                  (0x0022fdc0, "改造", "Lv. "),   (0x0022fe00, "重量", "Wt. "),    (0x0022fe08, "総合", "Cap "),
                  (0x0022fe10, "／−−", "/ - - "), (0x0022fe18, "／９０", "/ "), (0x226c80, "クリアデータをセーブしますか？", "    Save cleared game data?   ")]]

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


def editMaidFragments(fragment_listing):
    targetFile = open(fragment_listing[0], 'r+b')

    fragments = fragment_listing[1]
    num_fragments = len(fragments)

    base_address = 0xff000

    for x in range(num_fragments):
        offset = fragments[x][0] - base_address
        original_string = fragments[x][1]
        new_string = fragments[x][2]
        new_bytes = bytearray.fromhex(textConversion.scriptTextToHex(new_string, textConversion.NORMAL_TEXT))
        targetFile.seek(offset)
        targetFile.write(new_bytes)
    
    targetFile.close()

    return



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

def extractScriptPtrs(script):
    if not os.path.exists(SCRIPT_OUTPUT_FOLDER):
            os.makedirs(SCRIPT_OUTPUT_FOLDER)
    baseAddress = 0xff000
    fileName = script[0]
    tableStart = script[1]
    tableEnd  = script[2]

    textStart = script[3] - baseAddress
    textEnd = script[4] - baseAddress

    tableSize = tableEnd - tableStart

    inputFilePath = DATA_FOLDER

    inputFile = open(fileName, 'rb')
    inputData = inputFile.read()

    tableCursor = 0

    outputFilePath = SCRIPT_OUTPUT_FOLDER + "/" + os.path.basename(fileName) +"-"+ str(tableStart) + ".txt"
    outputFile = open(outputFilePath, "w", encoding="utf-8")

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

        if (textPointer & 0xFF0000) < 0x100000:
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


        nextLineBinary = inputData[nextEntryStart:nextEntryEnd]
        convertedText = textConversion.hexToText(nextLineBinary.hex())

        outputBuffer += "//" + convertedText.strip().replace("{END}", "{END}\n")  + convertedText + "\n\n"

        tableCursor    += TABLE_ENTRY_SIZE

    headerLine = "//Source: " + fileName + " at offset " + hex(tableStart) + "\n" + "//|Start|End|: |" + str(textStart) + "|" + str(textEnd) + "|\n"

    outputFile.write(headerLine + outputBuffer)
    outputFile.close()
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

    baseAddress = 0x0

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
        is_subtraction = (lo_loads[x] >= 0x8000)
        target_file.seek(hi_offsets[x])
        if is_subtraction:
            target_file.write((hi_loads[x] + 1).to_bytes(2, byteorder='little'))
        else:
            target_file.write(hi_loads[x].to_bytes(2, byteorder='little'))

    for x in range(len(lo_loads)):
        is_subtraction = (lo_loads[x] >= 0x8000)
        target_file.seek(lo_offsets[x])
        if is_subtraction:
            target_file.write((lo_loads[x]).to_bytes(2, byteorder='little'))
        else:
            #TODO:WTF?
            target_file.write(0x10000 - lo_loads[x].to_bytes(2, byteorder='little'))

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

            hi_loads = hi_loads[0:line_number + total_copies] + to_add_hi + hi_loads[line_number + total_copies:]
            lo_loads = lo_loads[0:line_number + total_copies] + to_add_lo + lo_loads[line_number + total_copies:]

            total_copies += num_copies - 1

        elif not nextLine or nextLine.startswith(".startfile"):
            assert False, '[ERROR] Unexpected EOF in load_scripts.txt!!!'






    return hi_loads, lo_loads, hi_offsets, lo_offsets


def injectLoadScript(file_path, line_starts, target_script_number, text_start, text_end):
    Instruction_File = open(LOAD_OFFSET_TEXT_FILE, 'r')
    base_address = 0xff000
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
    for seg in MAID_LOAD_SCRIPTS:
        extractSegment(seg)

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

def injectMaidScripts():
    for script in MAID_SCRIPTS_PTRS:
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
    targetFilePath   = originalFilePath.replace("ISOrip", 'ISO_EDITS')
    #targetFilePath = INJECT_OUTPUT_FOLDER + "/" + os.path.basename(originalFilePath)
    textStart = raw_script[1]
    textEnd = raw_script[2]
    max_size = textEnd - textStart
    tableType = raw_script[3]
    raw_type_index =   raw_script[4]

    baseAddress = 0xff000

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

            dataToAdd = bytearray.fromhex(textConversion.scriptTextToHex(textLine, tableType))
            total_data += dataToAdd
            
            if write_mode == RAW_MODE:
                offset_from_start = RAW_SCRIPT_CONFIGS[raw_type_index][lineNumber] - RAW_SCRIPT_CONFIGS[raw_type_index][0]
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

    #shutil.copyfile(textFilePath, os.path.join(REBUILT_FOLDER, textFilePath.split('/')[-1]))
    lineStarts = getLineStarts(total_data)
    return lineStarts

def injectMYU0Segment(raw_script, write_mode):
    originalFilePath = raw_script[0]
    targetFilePath   = originalFilePath #originalFilePath.replace("ISOrip", 'ISO_EDITS')
    #targetFilePath = INJECT_OUTPUT_FOLDER + "/" + os.path.basename(originalFilePath)
    textStart = raw_script[1]
    textEnd = raw_script[2]
    max_size = textEnd - textStart
    tableType = raw_script[3]
    raw_type_index =   raw_script[4]

    baseAddress = 0x0

    textFilePath = SCRIPT_FOLDER + "/" + os.path.basename(originalFilePath) +"-"+ hex(textStart - baseAddress) + ".txt"
    textFilePath = textFilePath.replace(".modified","")
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

            dataToAdd = bytearray.fromhex(textConversion.scriptTextToHex(textLine, tableType))
            total_data += dataToAdd
            
            if write_mode == RAW_MODE:
                offset_from_start = RAW_SCRIPT_CONFIGS[raw_type_index][lineNumber] - RAW_SCRIPT_CONFIGS[raw_type_index][0]
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

    #shutil.copyfile(textFilePath, os.path.join(REBUILT_FOLDER, textFilePath.split('/')[-1]))
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
    for script in MAID_LOAD_SCRIPTS:
        lineStarts = injectSegment(script, LOAD_ADDR_MODE)
        file_path = script[0]
        text_start = script[1]
        text_end  = script[2]
        print("Injecting CPU load script: " + file_path + " " +  hex(text_start))
        injectLoadScript(file_path.replace("ISOrip", "ISO_EDITS"), lineStarts, script_number, text_start, text_end)
        script_number += 1

    return    

def injectScript(script):
    fileName = script[0]
    tableStart = script[1]
    tableEnd   = script[2]
    tableType  = script[5]
    tableSize  = tableEnd - tableStart


    baseAddress = 0xff000

    scriptFilePath = SCRIPT_FOLDER + "/" + os.path.basename(fileName) +"-"+ str(tableStart) + ".txt"
    outFilePath = "ISO_EDITS/" + os.path.basename(fileName) #fileName.replace(" - Original", '')
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
    textStart = script[3] - baseAddress
    textEnd   = script[4] - baseAddress

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
                
                #textLine = textLine.replace("\n", NEW_LINE_CODE)
                #textLine = re.sub( r", ",",",textLine)
                #textLine = textLine.replace("...", "…")
                
                #Remove line break added after NEXT codes
                #textLine = textLine.replace("{NEXT}" + NEW_LINE_CODE, "{NEXT}")

                #for name in NameCodes:
                #    textLine = textLine.replace("{" + name[1] + "}", '')

                if "<<<" in textLine:
                    assert False, "Line header processed in line " + str(lineNumber) + ":" + textLine

                dataBuffer = textConversion.align_data(dataBuffer)
                tableEntry = len(dataBuffer) + textStart + baseAddress
                tableBuffer += tableEntry.to_bytes(4, byteorder='little', signed=False)

                dataToAdd = bytearray.fromhex(textConversion.scriptTextToHex(textLine, tableType))
                dataBuffer += dataToAdd

        elif entryLine:
            continue

        elif not entryLine:
            break


    assert len(dataBuffer) <= maxTextLength, scriptFilePath + ' is over script budget by ' + str(len(dataBuffer) -maxTextLength)  + ' bytes'

    print ("\t" + str(maxTextLength - len(dataBuffer)) + " bytes remaining in script " + scriptFilePath)

    dataBuffer += bytes(maxTextLength -  len(dataBuffer))

    outFile = open(outFilePath, "r+b")
    outFile.seek(textStart)
    outFile.write(dataBuffer)
    outFile.seek(tableStart - baseAddress)
    outFile.write(tableBuffer)

    #shutil.copyfile(scriptFilePath, os.path.join(REBUILT_FOLDER, scriptFilePath.split('/')[-1]))

    return


def extractPtrs():
    for script in MAID_SCRIPTS_PTRS:
        extractScriptPtrs(script)

def to_TXT(lines):
    txt_buffer = ""

    for x in range(len(lines)):
        for y in range(len(lines[x])):
            txt_buffer += "//BOX " + str(x + 1) + " LINE " + str(y + 1) + "\n"
            txt_buffer += "//" + textConversion.hexToText(lines[x][y].hex()) + "{END}\n"
            txt_buffer += textConversion.hexToText(lines[x][y].hex()) + "{END}\n\n"
    return txt_buffer

def injectMMDH(MMDHpath):
    SCRIPT_OFFSET = 0x10

    scriptFile = open("SCRIPT_EDITS/" + MMDHpath + '.TXT', 'r' ,encoding="utf8")
    
    targetFile = open("INSTANCE/" + os.path.basename(MMDHpath) + ".modified", 'r+b')

    print('\tInjecting Script: ' + MMDHpath)

    targetFile.seek(SCRIPT_OFFSET)
    tableOffset = resource.readInt(targetFile)
    textOffset = resource.readInt(targetFile)

    targetFile.seek(tableOffset + 4)
    textStart = resource.readInt(targetFile)

    tableSize = textOffset - tableOffset

    fileSize = os.path.getsize("INSTANCE/" + os.path.basename(MMDHpath) + ".modified")
    maxTextSize = fileSize - textOffset - textStart

    tableBuffer = b''
    textBuffer = b''

    cursor = 0
    totalTextSize = textStart
    #targetFile.seek(tableOffset)
    while cursor < tableSize:
        targetFile.seek(tableOffset + cursor)
        boxLineCount = resource.readInt(targetFile)
        cursor += 4
        tableBuffer += boxLineCount.to_bytes(4, byteorder = "little")

        for lineNumber in range(boxLineCount):
            linesProcessed = 0
            while True:
                scriptLine = scriptFile.readline()
                if "{END}" in scriptLine and not scriptLine.startswith("//"):
                    tableBuffer += totalTextSize.to_bytes(4, byteorder = "little")
                    scriptLine = scriptLine.replace("\n", '')

                    textBytes = bytearray.fromhex(textConversion.scriptTextToHex(scriptLine, NORMAL_TEXT))
                    #textBytes = textConversion.align_data(textBytes)
                    lineSize = len(textBytes)
                    textBuffer += textBytes

                    

                    totalTextSize += lineSize
                    cursor += 4
                    break

    #
    if textOffset + totalTextSize > fileSize + ((0x40 - fileSize % 0x40) % 0x40):
        print("Skipping " + MMDHpath)
        print ("Script " + MMDHpath + " is " +  str(fileSize + ((0x40 - fileSize % 0x40) % 0x40)  - (textOffset + totalTextSize )) + " bytes over budget.")
        return
    
    targetFile.seek(tableOffset)
    targetFile.write(tableBuffer)

    targetFile.seek(textOffset + textStart)
    targetFile.write(textBuffer)
    
    targetFile.close()
    scriptFile.close()
    return

def extractMMDH(MMDH_script):
    mmdh_file = open(os.path.join(DATA_FOLDER, MMDH_script), 'rb')
    mmdh_file.seek(0x10)
    pointer_tbl_offset = resource.readInt(mmdh_file)
    text_offset = resource.readInt(mmdh_file)
    mmdh_file.seek(pointer_tbl_offset)

    cursor = pointer_tbl_offset

    lines = []

    while cursor < text_offset:
        num_lines = resource.readInt(mmdh_file)
        cursor += 4
        boxLines = []
        for x in range(num_lines):
            line_rel_ptr = resource.readInt(mmdh_file)
            cursor += 4
            current_line = b''
            mmdh_file.seek(text_offset + line_rel_ptr)
            while True:
                nextByte = mmdh_file.read(1)
                if int.from_bytes(nextByte, byteorder="little") == 0:
                    break
                current_line += nextByte
            boxLines += [current_line]
            mmdh_file.seek(cursor)
        lines += [boxLines]
    
    text = to_TXT(lines)
    outputFile = open(os.path.join(SCRIPT_OUTPUT_FOLDER,MMDH_script + ".TXT"), 'w', encoding="utf8")
    outputFile.write(text)

    outputFile.close()

    return
#extractPtrs()
#extractLoadScripts()
def extract_all_mmdh():
    for script in MMDH_FILES:
        extractMMDH(script)

def injectMMDHs():
    for script in MMDH_FILES:
        injectMMDH(script)

#injectMYU0Segment(MAID_RAW_SCRIPTS[0], RAW_MODE)

#extractSegment(MAID_RAW_SCRIPTS[0])
#injectMMDHs()
#injectMaidScripts()
#injectLoadScripts()
#extract_all_mmdh()

#extract_all()
#extractScriptPtrs(MAID_SCRIPTS_PTRS[0])
#extractSegments()
#extractLoadScripts()
#addComments("SCRIPT/BS_MAIN1.EXE-0x800.txt")
#injectLoadScripts()
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