#########################################################################
# Processes image data in PS1 game "Aconcagua"                          #
#########################################################################

from asyncio.windows_events import NULL
import chunk
from fileinput import filename
from io import BufferedReader
from pickle import TRUE
import sys    
import os
from turtle import width
import numpy as np
import decompress
import compress
import math
import shutil
import filecmp

from PIL import Image,ImageDraw, ImageFont

BPP = 4

SUBTITLE_PALETTE = [(255,255,255,  0), #0 = Alpha
                    (  0,  0,  0,255), #1 = Black
                    (255,255,255,255), #2 = White
                    (128,128,128,255)] #3 = Gray

SUBTITLE_HEIGHTS = [16,32]

FONT_SRC_PATH    = 'INSTANCE/FONT'
FONT_SRC_FILE = "font/HALF_WIDTH_MODIFIED.PNG"
FONT_TARGET_PATH = 'INSTANCE/FONT.modified'

REBUILT_FOLDER = 'REBUILT'

SUB_FOLDER       = 'Subtitles/data'

FONT_WIDTH  = 256
FONT_HEIGHT = 16
FONT_CHANNELS = 4
FONT_PALETTE = [(  0,  0,  0,255), #0 = Black
                (255,255,255,255)] #1 = White

#Disc 1 audio str folders:
SRC_FOLDER = "src"
DISC_1_STR_FOLDERS = ["ST01_01", "ST02_01", "ST03_01", "ST04_04"]

TARGET_SRC_PATH   = 'mkpsxiso/Aconcagua/'
TARGET_SRC_PATH_2 = 'mkpsxiso/Aconcagua2/'
LOG_PATH = 'logs/subtitleInjector.log'
SUSPICIOUS_MATCH_MAX_LEN = 3
MAX_MATCHES = 100

SUBTITLE_HEIGHT_EXCEPTIONS =        ['SE03_01_TOP_0010', 'SE05_02_BOT_0001']
SUBTITLE_HEIGHT_EXCEPTIONS_VALUES = [17,                 18]


SUBTITLE_MATCH_EXEMPTIONS = [
                            ["SE01_01_TOP_0001-14", [289864,509448,731368,953288,1177544,1397316,1619236,1841156,2065412,2284996]],
                            ["SE01_01_TOP_0001-19", [317896,537480,759400,981320,1205576,1425348,1647268,1869188,2093444,2313028]],

                            ["SE01_05_BOT_0004-3", [3616940,3687020,3757100,3827180,3897260,3967340,4037420,4107500,4177580,4247660]],
                            ["SE01_05_BOT_0004-7", [3640300,3710380,3780460,3850540,3920620,3990700,4060780,4130860,4200940,4271020]],

                            ["SE02_01_BOT_0002-19", [1892936,2145224,2395176,2647464,2897416,3149704,3401908,3654196,3901764,4154100]],
                            
                            ["SE02_03_BOT_0002-80", [11424268,11979852,12533484,13091788,13642896,14199396,14755020,15309788,15862420,16418368]],

                            ["SE02_03_TOP_0001-71", [620672,1181352,1741300,2301864,2862580,3423220,3983652,4544500,5105892,5665436]],

                            ["SE02_03_TOP_0005-7", [20868688,20941104,21008848,21081264,21149008,21221424,21289168,21361584,21429328,21501744]],
                            ["SE02_03_TOP_0005-8", [20875696,20943440,21015856,21083600,21156016,21223760,21296176,21363920,21436336,21504080]],
                            
                            ["SE02_05_TOP_0002-24", [2803872,4194096,5586560,6973688,8363448,9754208,11143912,12534452,13923636,15314128]],
                            ["SE02_05_TOP_0002-37", [2955712,4346144,5736272,7125348,8519432,9906020,11296032,12688600,14075504,15466216]],
                            ["SE02_05_TOP_0002-39", [2979072,4371840,5759632,7148708,8540456,9929380,11319392,12709624,14098864,15491912]],
                            ["SE02_05_TOP_0002-40", [2990752,4381184,5773648,7160388,8552136,9941060,11331072,12721304,14110544,15501256]],
                            ["SE02_05_TOP_0002-45", [3049132,4439584,5829712,7218760,8612872,9999516,11389472,12782012,14168944,15559656]],
                            ["SE02_05_TOP_0002-48", [3084172,4474624,5867088,7253800,8645576,10034528,11424484,12814716,14203984,15594696]],
                            ["SE02_05_TOP_0002-49", [3095852,4486304,5876432,7267816,8657256,10046208,11436136,12826396,14215664,15606376]],
                            ["SE02_05_TOP_0002-54", [3156932,4544704,5934832,7323880,8715252,10104664,11495684,12884796,14276400,15664776]],
                            ["SE02_05_TOP_0002-60", [3224676,4614784,6004912,7393932,8785304,10174772,11568100,12954876,14344144,15734856]],
                            ["SE02_05_TOP_0002-70", [3344020,4731584,6121712,7510732,8901560,10291320,11682564,13071648,14463280,15851656]],
                            ["SE02_05_TOP_0002-76", [3411764,4801664,6191792,7580840,8971640,10361380,11755168,13141728,14531024,15921736]],
                            ["SE02_05_TOP_0002-78", [3437440,4825024,6215152,7604200,8995000,10384712,11776108,13165088,14556720,15945096]],
                            ["SE02_05_TOP_0002-80", [3458464,4848384,6240128,7627560,9018360,10408072,11799280,13188448,14577744,15968456]],
                            ["SE02_05_TOP_0002-81", [3470144,4860064,6249472,7641576,9030040,10419752,11810424,13199428,14589424,15980136]],

                            ["SE03_02_TOP_0002-3", [2065848,2133404,2205820,2273564,2345980,2413724,2486328,2554072,2626488,2694232]],
                            ["SE03_02_TOP_0002-5", [2075192,2145084,2215164,2285244,2355324,2425412,2495672,2565752,2635840,2705912]],
                            ["SE03_02_TOP_0002-8", [2093888,2161436,2233852,2301596,2374012,2441764,2514360,2582104,2654520,2722264]],

                            ["SE03_10_TOP_0005-0", [19343308,19518508,19695856,19868720,20043732,20218932,20394132,20569332,20744532,20919544]],
                            ["SE03_10_TOP_0005-3", [19378348,19553548,19728560,19903572,20078772,20256308,20429172,20604372,20779572,20954584]],
                            ["SE03_10_TOP_0005-4", [19390028,19565228,19740240,19915252,20090452,20265652,20443188,20616052,20791252,20966264]],
                            ["SE03_10_TOP_0005-7", [19425068,19602604,19775280,19950292,20125492,20300692,20475892,20651092,20826104,21003640]],
                            ["SE03_10_TOP_0005-8", [19436748,19611948,19789296,19961972,20137172,20312372,20487572,20662772,20837784,21012984]],
                            ["SE03_10_TOP_0005-11", [19471788,19646800,19822000,19997012,20172212,20349748,20522612,20697812,20872824,21048024]],
                            ["SE03_10_TOP_0005-12", [19483468,19658480,19833680,20008692,20183892,20359092,20536628,20709492,20884504,21059704]],
                            ["SE03_10_TOP_0005-14", [19509164,19681840,19857040,20032052,20207252,20382452,20557652,20732852,20910200,21083064]],

                            ["SE04_08_TOP_0008-17", [12283972,12709076,13138268,13561348,13988460,14413612,14841100,15268360,15693784,16118900]],
                            ["SE04_08_TOP_0008-19", [12297988,12720756,13147612,13573028,14000140,14427628,14852780,15277704,15707800,16130580]],
                            ["SE04_08_TOP_0008-21", [12307144,12732436,13159292,13587044,14011820,14436972,14866796,15289384,15717144,16142260]],
                            ["SE04_08_TOP_0008-22", [12311816,12739444,13166300,13591716,14016492,14446316,14869132,15296372,15721816,16149268]],
                            ["SE04_08_TOP_0008-24", [12325812,12751124,13175644,13605732,14028172,14455660,14852780,15308300,15735832,16160948]],
                            ["SE04_08_TOP_0008-27", [12344500,12767476,13194332,13619748,14046860,14474348,14899500,15324652,15754528,16177300]],
                            ["SE04_08_TOP_0008-30", [12358516,12786164,13213020,13638436,14063212,14493036,14915852,15343340,15768544,16195988]],
                            ["SE04_08_TOP_0008-32", [12372532,12797844,13222364,13652452,14074892,14502380,14927532,15355020,15782560,16207668]],
                            ["SE04_08_TOP_0008-34", [12381876,12811860,13233932,13661796,14086572,14514060,14941548,15366700,15791876,16221684]],
                            ["SE04_08_TOP_0008-36", [12393744,12820572,13245800,13673476,14100588,14525740,14950892,15380716,15803548,16231028]],
                            ["SE04_08_TOP_0008-37", [12400752,12825244,13252808,13680484,14105260,14530412,14960236,15383052,15810556,16235764]],
                            ["SE04_08_TOP_0008-50", [12475476,12904668,13327560,13755236,14180012,14607500,15034988,15460140,15885356,16315180]],
                            ["SE04_08_TOP_0008-52", [12486968,12914012,13339240,13766916,14194028,14619180,15044332,15474156,15897036,16324524]],
                            ["SE04_08_TOP_0008-53", [12493976,12918684,13346248,13773924,14198700,14623852,15053676,15476492,15904044,16329196]],
                            ["SE04_08_TOP_0008-56", [12512636,12937372,13362600,13792612,14215052,14642540,15067692,15495180,15922732,16347884]],
                            ["SE04_08_TOP_0008-57", [12517308,12942044,13371944,13794948,14222060,14647212,15074700,15502188,15927404,16352556]],
                            ["SE04_08_TOP_0008-60", [12533660,12960732,13385960,13813636,14240748,14665900,15091052,15520876,15943764,16371244]],

                            ["SE06_01B_TOP_0002-4", [3504728,4189148,4871824,5556272,6238008,6924416,7606528,8288536,8970724,9655200]],
                            ["SE06_01B_TOP_0002-56", [3808408,4495728,5177840,5859952,6541312,7225760,7907872,8592320,9274140,9961216]],

                            ["SE06_08_TOP_03-24", [5076628,5303220,5532148,5758740,5990192,6214448,6443376,6671928,6898520,7125112]],
                            ["SE06_08_TOP_03-33", [5130356,5356948,5583540,5812656,6039248,6270512,6494768,6723320,6952248,7179216]],

                            ["SE08_09_TOP_08-13", [11290328,11411800,11535608,11657080,11783224,11904696,12026168,12147640,12271448,12392920]],

                            ["SE09_00_TOP_02-17", [7736232,8282440,8831400,9379684,9928644,10477792,11026772,11577388,12127048,12674160]],
                            ["SE09_00_TOP_02-22", [7792296,8340840,8889800,9438084,9987044,10538528,11085172,11635092,12183112,12732560]],

                            ["SE09_00_TOP_04-0", [30894772,32310576,33721332,35134920,36548388,37961548,39374828,40788108,42200488,43616120]],
                            ["SE09_00_TOP_04-5", [30953172,32366640,33779732,35193320,36609124,38019948,39433228,40846508,42258888,43672184]],
                            ["SE09_00_TOP_04-11", [31023252,32436720,33849812,35263360,36676868,38090028,39505644,40915688,42328968,43742264]],
                            ["SE09_00_TOP_04-28", [31221812,32635092,34048372,35461920,36875428,38290924,39701868,41114248,42527528,43940824]],
                            ["SE09_00_TOP_04-31", [31256852,32670132,34085748,35496960,36910468,38323648,39736908,41149288,42562568,43975864]],
                            ["SE09_00_TOP_04-42", [31385332,32798612,34211892,35625420,37038948,38452108,39865388,41280104,42691008,44104344]],
                            ["SE09_00_TOP_04-43", [31397012,32810292,34223572,35637100,37050628,38463788,39879404,41289448,42702688,44116024]],
                            ["SE09_00_TOP_04-58", [31572212,32985492,34398772,35812548,37225828,38638988,40052268,41466984,42877888,44291244]],
                            ["SE09_00_TOP_04-67", [31677332,33090612,34503892,35917668,37330908,38744108,40159724,41569768,42983008,44396364]],
                            ["SE09_00_TOP_04-73", [31749748,33160692,34573972,35987748,37400928,38814188,40227468,41639848,43055424,44466444]],
                            ["SE09_00_TOP_04-80", [31829172,33244788,34655732,36069508,37482668,38895948,40309228,41721608,43134848,44550540]],
                            ["SE09_00_TOP_04-85", [31887760,33300852,34714132,36127908,37543404,38954348,40367628,41780008,43193304,44606604]],
                            ["SE09_00_TOP_04-89", [31936816,33347572,34761348,36174628,37587788,39001068,40414348,41826728,43242360,44653324]],
                            ["SE09_00_TOP_04-90", [31946160,33359252,34773028,36186308,37599468,39012748,40426028,41840744,43251704,44665004]],
                            ["SE09_00_TOP_04-97", [32030256,33441012,34854600,36268068,37681228,39094508,40507788,41920168,43335800,44746764]],
                            ["SE09_00_TOP_04-103", [32098000,33511092,34927016,36338148,37751308,39164588,40577868,41990248,43403544,44816844]],
                            ["SE09_00_TOP_04-109", [32168080,33581172,34994760,36408228,37823724,39234668,40647948,42060328,43473624,44886924]]
                            
                             ]
SUBTITLE_CHUNK_LENGTH_EXCEPTIONS = [['SE03_10_TOP_0005', 0xC]]

SUBTITLE_CHUNK_PATTERN_EXCEPTIONS= [
                                    [ 'SE03_10_BOT_0005' , [0x330,0x274,0x11F]]
                                   ]



#subtitle image processing

#Converts the specified raw Aconcagua subtitle image file to PNG
#returns an Image object
def binToPNG(fileName, width, height):

    sourceFile = open(fileName, 'rb')
    sourceData = sourceFile.read()

    arrayBuffer = np.zeros((height, width, 4), dtype=np.uint8)

    byteCursor = 0
    for byte in sourceData:
        
        rowNumber    = byteCursor//(width//(8//BPP))
        columnNumber = byteCursor % (width//(8//BPP))
        pixel1    =  byte & 0b00001111
        pixel2    = (byte & 0b11110000) >> 4

        arrayBuffer[rowNumber][columnNumber*2]     = SUBTITLE_PALETTE[pixel1]
        arrayBuffer[rowNumber][columnNumber*2 + 1] = SUBTITLE_PALETTE[pixel2]

        byteCursor += 1

    im = Image.fromarray(arrayBuffer, "RGBA")
    #im.show()

    #im.save( fileName + ".PNG")

    return im

def getChunkPatternExemption(file):
    for exception in SUBTITLE_CHUNK_PATTERN_EXCEPTIONS:
        if exception[0] == file:
            return exception[1]

    return NULL

def isChunkPatternExemption(file):
    for exception in SUBTITLE_CHUNK_PATTERN_EXCEPTIONS:
        if exception[0] == file:
            return True

    return False

def getSubtitleExemption(file, chunkNumber):
    chunkID = file + '-' + str(chunkNumber)
    for exception in SUBTITLE_MATCH_EXEMPTIONS:
        if exception[0] == chunkID:
            return exception[1]
    return NULL

def isSubtitleExemption(file, chunkNumber):
    chunkID = file + '-' + str(chunkNumber)

    for exception in SUBTITLE_MATCH_EXEMPTIONS:
        if exception[0] == chunkID:
            return True

    return False

def getChunkLengthExemption(file):
    for exception in SUBTITLE_CHUNK_LENGTH_EXCEPTIONS:
        if exception[0] == file:
            return exception[1]
    return NULL

def isChunkLengthExemption(file):
    for exception in SUBTITLE_CHUNK_LENGTH_EXCEPTIONS:
        if exception[0] == file:
            return True
    return False

#Converts the specified PNG to an Aconcagua subtitle image file
#Returns the binary image
def PNGToBin(fileName):
    sourceImage = Image.open(fileName)

    RGB = sourceImage.convert('RGBA')

    buffer = b''
    tempChar = 0
    #pixels = sourceImage.load()
    for y in range(sourceImage.height):
        for x in range(sourceImage.width):
            px = RGB.getpixel((x, y))
            
            if px[0:3] == (0,0,0) and px[3] != 0:
                px = SUBTITLE_PALETTE[1]
            
            try:
                pixelColor = SUBTITLE_PALETTE.index(px)
            except ValueError:
                if px[3] == 0:
                    pixelColor = 0
                else:
                    pixelColor = 1

            if x % 2 == 0:
                byteToAdd = pixelColor
                tempChar = byteToAdd
            else:
                #bytePos = (y*sourceImage.width)//2 + (x//2)
                buffer += bytes([tempChar | (pixelColor << 4)])
                tempChar = 0
            pass

    #outFile = open(fileName + ".bin", 'wb')
    #outFile.write(buffer)
    #outFile.close()
    sourceImage.close()
    return buffer

#Converts the font image to an editable PNG
def extractFont():
    srcFile = open(FONT_SRC_PATH,'rb')
    srcData = srcFile.read()
    arrayBuffer = np.zeros((FONT_HEIGHT * FONT_CHANNELS, FONT_WIDTH, 4), dtype=np.uint8)

    bytesRead = 0
    for byte in srcData:
        for channel in range(FONT_CHANNELS):
            cursor =  (0b1 << channel)
            pixelColor1 = FONT_PALETTE[int(bool( byte     & cursor))]
            pixelColor2 = FONT_PALETTE[int(bool((byte>>4) & cursor))]
            xCoord1 = (bytesRead*2) % FONT_WIDTH
            xCoord2 = xCoord1 + 1
            yCoord = ((bytesRead*2) //FONT_WIDTH) + (channel * FONT_HEIGHT) 
            arrayBuffer[yCoord,xCoord1] = pixelColor1
            arrayBuffer[yCoord,xCoord2] = pixelColor2

        bytesRead += 1
    im = Image.fromarray(arrayBuffer, "RGBA")
    im.show()

    im.save( "FONT/HALF_WIDTH" + ".PNG")

    return


def injectFont():
    sourceImage = Image.open(FONT_SRC_FILE)
    RGB = sourceImage.convert('RGBA')

    buffer = b''
    tempChar = 0
    for y in range(FONT_HEIGHT):
        for x in range(sourceImage.width):
            px1 = RGB.getpixel((x, y + FONT_HEIGHT * 0))
            px2 = RGB.getpixel((x, y + FONT_HEIGHT * 1))
            px3 = RGB.getpixel((x, y + FONT_HEIGHT * 2))
            px4 = RGB.getpixel((x, y + FONT_HEIGHT * 3))
            
            color1 = FONT_PALETTE.index(px1)
            color2 = FONT_PALETTE.index(px2)
            color3 = FONT_PALETTE.index(px3)
            color4 = FONT_PALETTE.index(px4)

            nibbleToAdd = bool(color1) + (bool(color2)<<1) + (bool(color3)<<2) + (bool(color4)<<3)

            if x % 2 == 0:
                byteToAdd = nibbleToAdd
                tempChar = byteToAdd
            else:
                buffer += bytes([tempChar | (nibbleToAdd << 4)])
                tempChar = 0
            pass

    outFile = open(FONT_TARGET_PATH, 'wb')
    outFile.write(buffer)
    outFile.close()
    sourceImage.close()

    return

def findLongestMatch(needle, haystack):
    buffer = ''

    index = 1
    while haystack.find(needle[:index])!= -1:

        index+=1
        if index > len(needle):
            break

    match = needle[:index - 1]
    #matchPos = haystack.find(match)

    return match

def fixCompressedFileLengths():
    for root, subdirectories, files in os.walk(SUB_FOLDER):
        for file in files:
            if "." not in file:
                subsBin, trueLength = decompress.decompressSubtitle(os.path.join(root,file), 0)
                compFile = open(os.path.join(root,file), 'rb+')
                compFile.truncate(trueLength)
                compFile.close()
    return

#Produces the raw PNGs, .txt, and uncompressed files from base compressed files
def unpackSubs():
    fixCompressedFileLengths()
    for root, subdirectories, files in os.walk(SUB_FOLDER):
        for file in files:
            if "." not in file:
                subsBin, trueLength = decompress.decompressSubtitle(os.path.join(root,file), 0)
                uncompressedFile = open(os.path.join(root,file) + '.uncompressed', 'wb')
                uncompressedFile.write(subsBin)
                uncompressedFile.close()
                for height in SUBTITLE_HEIGHTS:
                    numPixels = len(subsBin)*2
                    if file in SUBTITLE_HEIGHT_EXCEPTIONS:
                                height = SUBTITLE_HEIGHT_EXCEPTIONS_VALUES[SUBTITLE_HEIGHT_EXCEPTIONS.index(file)]
                    width = numPixels//height
                    if not os.path.isfile(os.path.join(root,file) + '_' + str(height) + '.PNG'):
                        try:
                            image = binToPNG(os.path.join(root,file) + '.uncompressed', width, height)
                        except:
                            print("Subtitle " + file + " could not be converted to height " + str(height))
                            continue
                        image.save(os.path.join(root,file) + '_' + str(height) + '.PNG')

                if not os.path.isfile(os.path.join(root,file) + '.txt'):
                    textFile = open(os.path.join(root,file) + '.txt','w')
                    textFile.write("//Lines:1\nTest 1")
                    textFile.close()
    return

#Looks at the appropriate PNG and compresses it to the .modified file
def compressSubs():
    for root, subdirectories, files in os.walk(SUB_FOLDER):
        for file in files:
            if "." not in file:
                targetFileExtension = '.modified'
                textFilePath = os.path.join(root,file) + '.txt'
                textFile = open(textFilePath, 'r')
                firstLine = textFile.readline()
                textFile.close()

                lines = int(firstLine[8:9])
                if file in SUBTITLE_HEIGHT_EXCEPTIONS:
                    height = SUBTITLE_HEIGHT_EXCEPTIONS_VALUES[SUBTITLE_HEIGHT_EXCEPTIONS.index(file)]
                    rawImage = PNGToBin(os.path.join(root,file) + "_" + str(height) + ".PNG")
                elif lines == 1:
                    rawImage = PNGToBin(os.path.join(root,file) + "_16.PNG")
                elif lines == 2:
                    rawImage = PNGToBin(os.path.join(root,file) + "_32.PNG")

                compressedImage = compress.compressSubtitle(rawImage)

                outputFilePath = os.path.join(root,file) + targetFileExtension
                outputFile = open(outputFilePath, 'wb')
                outputFile.write(compressedImage)
                outputFile.close()

    return

def getValue(param, field):
    try:
        index = field.index(param)
        value = field[index + len(param) + 1:].split(' ')[0].rstrip('\n')
    except:
        return -1

    return value

def printSubtitle(PNGFilePath):
    sourceFile = Image.open(PNGFilePath)
    textFile = open(PNGFilePath[:-7] + '.txt','r', encoding='utf8')
    header = textFile.readline()
    customFontSize = getValue('FontSize', header)



    imageHeight = sourceFile.height
    imageWidth  = sourceFile.width
    canvas = Image.new('RGBA', (imageWidth,imageHeight), color=SUBTITLE_PALETTE[0])
    draw = ImageDraw.Draw(canvas)
    mySpacing = 1
    myFont = 'font/GenericMobileSystemNuevo.ttf'
    fontSize = FONT_HEIGHT
    heightModifier = 0
    if customFontSize != -1:
        fontSize = int(customFontSize)
        draw.fontmode = "1"
        mySpacing = -1
        myFont = 'font/Franklin Gothic Medium Regular.ttf'
        heightModifier = 0
    fontColor = SUBTITLE_PALETTE[2]
    fontStroke = SUBTITLE_PALETTE[1]

    imFont = ImageFont.truetype(myFont, fontSize)
    
    
    
    draw.text((1 + (imageWidth//2), (imageHeight + heightModifier)//2), text = textFile.read(), fill = fontColor, font=imFont,
               anchor='mm', spacing = mySpacing, align='center', stroke_width=1, stroke_fill=fontStroke)

    return canvas

def printSubsToFMV(PNG_folder, STR_name, text_file_path):
    END_TOKEN = "{END}"
    textFile = open(text_file_path, 'r', encoding='utf-8')

    Yposition = 5/6  #Default subtitle vertical position
    Xposition = 1/2  #Default subtitle horizontal position
    anchoring = 'mm' #Default anchoring
    while True:
        line = textFile.readline()
        if line.startswith("//"):
            continue
        
        elif line.startswith("Subtitle X:"):
            Xposition = float(line.split(':')[1].rstrip("\n"))
            continue
            
        elif line.startswith("Subtitle Y:"):
            Yposition = float(line.split(':')[1].rstrip("\n"))
            continue

        elif line.startswith("Anchoring:"):
            anchoring = line.split(':')[1].rstrip("\n")
            continue
        
        elif line.startswith("Range:"):
            frame_range = line.split(':')[1]
            rangeStart = int(frame_range.split("-")[0])
            rangeEnd = int(frame_range.split("-")[1].rstrip("\n"))
            
            subtitle_line = ''
            while END_TOKEN not in subtitle_line:
                subtitle_line += textFile.readline()

            subtitle_line = subtitle_line.replace("{END}", '').rstrip("\n")

            spacer1 = ''
            spacer2 = ''

            if "9" in STR_name:
                spacer1 = '['
                spacer2 = ']'

            for frame_number in range(rangeStart, rangeEnd):
                frame_file_path = os.path.join(PNG_folder, STR_name) + '[0][' + str(frame_number).zfill(4) + '].png'
                frame_file = Image.open(frame_file_path)
                draw = ImageDraw.Draw(frame_file)
                imageHeight = frame_file.height
                imageWidth  = frame_file.width

                mySpacing = 1
                myFont = 'font/GenericMobileSystemNuevo.ttf'
                fontSize = 16
                fontColor = SUBTITLE_PALETTE[2]
                fontStroke = SUBTITLE_PALETTE[1]

                imFont = ImageFont.truetype(myFont, fontSize)

                if "9" in STR_name:
                    draw.rectangle((0,imageHeight*0.7, imageWidth, imageHeight), fill='black')

                draw.text((imageWidth*Xposition, imageHeight*Yposition), text = subtitle_line, fill = fontColor, font=imFont,
                        anchor=anchoring, spacing = mySpacing, align='center', stroke_width=1, stroke_fill=fontStroke)

                frame_file.save(os.path.join(PNG_folder, STR_name) + '[0][' + str(frame_number).zfill(4) + '].png')

        elif line == "\n":
            continue

        else:
            break

    return



#Looks at the appropriate .PNG and updates it with the text
def printSubs():
    for root, subdirectories, files in os.walk(SUB_FOLDER):
        for file in files:
            if "." not in file:
                textFilePath = os.path.join(root,file) + '.txt'
                textFile = open(textFilePath, 'r')
                firstLine = textFile.readline()
                secondLine = textFile.readline()

                if secondLine == 'Test 1' or 'skip' in firstLine:
                    continue

                lines = int(firstLine[8:9])

                if file in SUBTITLE_HEIGHT_EXCEPTIONS:
                    height = SUBTITLE_HEIGHT_EXCEPTIONS_VALUES[SUBTITLE_HEIGHT_EXCEPTIONS.index(file)]
                else:
                    height = lines * FONT_HEIGHT

                outPath = os.path.join(root,file) + '_' + str(height) + '.PNG'
               
                printedImage = printSubtitle(outPath)
                printedImage.save(outPath)
            
    return


def isSubUnmodified(root, file):
    try:
        os.makedirs('REBUILT_FOLDER')
    except:
        pass


    try:
        unmodified = filecmp.cmp(os.path.join(root, file + '.txt'), os.path.join(REBUILT_FOLDER, file + '.txt') )
    except FileNotFoundError:
        return False

    return unmodified

#Looks at .modified compressed subs and injects them into the str
def injectSubs():
    logFile = open(LOG_PATH, 'w')
    for root, subdirectories, files in os.walk(SUB_FOLDER):
        for file in files:
            if "." not in file: 
                if isSubUnmodified(root, file):
                    continue
                print("Injecting: " + file)
                discNumber = int(file[3:4])//5 + 1
                compressedSubData = open(os.path.join(root,file),'rb').read()
                modifiedSubData = open(os.path.join(root,file) + '.modified','rb').read()

                assert len(compressedSubData) - SUSPICIOUS_MATCH_MAX_LEN >= len(modifiedSubData), "Subtitle " + file + " is " + str(len(modifiedSubData) - len(compressedSubData) + 3) + " too many bytes!!!"

                if 'A_' in file or 'B_' in file:
                    parentFilePath = 'src/' + 'Disk' + str(discNumber) + '/ST0' + file[3:4] + '_01/' + file[:8] + '.STR'
                    targetPath = 'ST0' + file[3:4] + '_01/' + file[:8] + '.STR'
                else:
                    parentFilePath = 'src/' + 'Disk' + str(discNumber) + '/ST0' + file[3:4] + '_01/' + file[:7] + '.STR'
                    targetPath = 'ST0' + file[3:4] + '_01/' + file[:7] + '.STR'
                
                if discNumber == 1:
                    targetParentFolder = TARGET_SRC_PATH
                else:
                    targetParentFolder = TARGET_SRC_PATH_2
                targetParentFile = open(targetParentFolder + targetPath, 'r+b')
                #subsBin = decompress.decompressSubtitle(SUB_FOLDER + '/' + file, 0)
                parentFile = open(parentFilePath, 'r+b')
                #targetParentFile = open(TARGET_SRC_PATH + 'ST0' + file[3:4] + '_01/' + file[:7] + '.STR', 'r+b')
                parentFileData = parentFile.read()
                
                longestMatch = findLongestMatch(compressedSubData,parentFileData)

                matches = compress.findall(longestMatch,parentFileData)
                
                if isChunkLengthExemption(file):
                    longestMatch = longestMatch[:getChunkLengthExemption(file)]

                numChunks = math.ceil(len(compressedSubData)/len(longestMatch))
                logFile.write("Injecting subtitle " + file + " into " + parentFilePath + ':\n')

                if isChunkPatternExemption(file):
                    chunkLengths = getChunkPatternExemption(file)
                    numChunks = len(chunkLengths)
                    logFile.write("Chunk pattern length exemption" +'\n')

                logFile.write("Chunk length: " + str(len(longestMatch)) + " Number of chunks: " + str(numChunks) +'\n')
                

                for chunkNumber in range(numChunks):
                    logFile.write('-Injecting chunk: ' + str(chunkNumber) +'\n')
                    if isChunkPatternExemption(file):
                        offset = sum(getChunkPatternExemption(file)[:chunkNumber])
                        chunk = compressedSubData[offset:offset + getChunkPatternExemption(file)[chunkNumber]]
                        modifiedChunk = modifiedSubData[offset:offset + getChunkPatternExemption(file)[chunkNumber]]
                    else:
                        chunk = compressedSubData[chunkNumber*len(longestMatch):(chunkNumber+1)*len(longestMatch)]
                        modifiedChunk = modifiedSubData[chunkNumber*len(longestMatch):(chunkNumber+1)*len(longestMatch)]
                    
                    if isSubtitleExemption(file, chunkNumber):
                        matches = getSubtitleExemption(file, chunkNumber)
                        logFile.write('Using exception to inject ' + file + '\n')
                    else:
                        matches = compress.findall(chunk,parentFileData)
                    

                    matchString = ''

                    if len(chunk) <= SUSPICIOUS_MATCH_MAX_LEN:
                            logFile.write('---Suspicious match found at: ' + str(match) + ' of length ' + str(len(chunk)) + '\n')
                            print('---Suspicious match found at: ' + str(match) + ' of length ' + str(len(chunk)) + '\n')
                            continue
                    
                    matchesMatched = 0
                    for match in matches:
                        if matchesMatched < MAX_MATCHES:
                            if match %4 != 0:
                                #logFile.write('-Trimming non-aligned match: ' + str(match) + ' of length ' + str(len(chunk)) + '\n')
                                continue

                            matchString += str(match) + ','
                            targetParentFile.seek(match)

                            targetParentFile.write(modifiedChunk)
                            matchesMatched += 1

                    logFile.write('-Match offsets: ' + matchString.rstrip(',') +'\n')
                
                shutil.copyfile(os.path.join(root, file + '.txt'), os.path.join(REBUILT_FOLDER, file + '.txt'))

                    
    logFile.close()
    return

def buildSubtitles():
    print("Printing subtitles...")
    printSubs()
    print("Compressing subtitles...")
    compressSubs()
    print("Injecting subtitles...")
    injectSubs()


def copyFolder(folder_src, folder_out):
    for root, subdirectories, files in os.walk(folder_src):
        for file in files:
            if os.path.exists(os.path.join(folder_out, file)):
                os.remove(os.path.join(folder_out, file))
            shutil.copyfile(os.path.join(folder_src, file),(os.path.join(folder_out, file)))

def fix_frame_names(folder_path):
    for root, subdirectories, files in os.walk(folder_path):
        for file in files:
            if file[14] != '[':
                fileName = file[0:14] + '[' + file[14:18] + ']' + '.png'
                shutil.copyfile(os.path.join(root, file),(os.path.join(root, fileName)))


#copyFolder("PNG/SE01_00.STR - Clean", "PNG/SE01_00.STR")
#fix_frame_names("PNG/SE01_00.STR")

#printSubsToFMV("PNG/SE01_00.STR", "SE01_00.STR", "PNG/SE01_00.STR.txt")
#copyFolder("./PNG/ST09_01.STR - Clean", "./PNG/SE09_01.STR")
#printSubsToFMV("PNG/SE09_01.STR", "SE09_01.STR", "PNG/SE09_01.STR.txt")

#unpackSubs()
#buildSubtitles()
#fixCompressedFileLengths()
#compressSubs()
#injectSubs()
#printSubs()
#unpackSubs()
#results = compress.findall(bytes(2), b'\x01\x02\x00\x00\xf5\x00\x00\x00')
#for result in results:
#    print(str(result))
#injectFont()

#extractFont()
#testFile = open("testFile", 'wb')
#testFile.write(PNGToBin("Subtitles\data\SE01_05\SE01_05_TOP_0007_32.PNG"))
#testFile.close()

#im = binToPNG("testFile", 200, 32)
#im.show()

#fixCompressedFileLengths()