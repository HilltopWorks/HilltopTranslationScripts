'''Builds ANI files for Harmful Park and edits any relevant tables'''
from sys import byteorder
from tkinter import Y
import ImageProcessor
import os
import json
from pathlib import Path
from distutils.dir_util import copy_tree
import subprocess

SCRIPT_FOLDER = 'script'

BUILD_FOLDER = 'HAR'
TARGET_FOLDER = 'mkpsxiso/HarmfulPark/HAR'
MKPSXISO = 'mkpsxiso.exe'
XML = "HarmfulParkBuild.xml"


BGD_FILE = 'HAR/DTIMEND/EDSTAFF.BGD'
BGD_TEXT_FILE = 'BGD/STAFF.txt'

STAFF_TABLE = [ ( ' ',0xFF ), ( 'A',0xB7 ), ( 'B',0xC8 ) , ( 'C',0xC9), ( 'D',0xCA ), ( 'E',0xCB ), ( 'F',0xCC ), ( 'G',0xCD ), ( 'H',0xCE ), ( 'I',0xB5 ),
                ( 'J',0xD0 ), ( 'K',0xD1 ), ( 'L',0xD2 ), ( 'M',0xD3 ), ( 'N',0xD4 ), ( 'O',0xD5 ), ( 'P',0xD6 ), ( 'Q',0xD7 ), ( 'R',0xD8 ), ( 'S',0xD9 ),
                ( 'T',0xDA ), ( 'U',0xDB ), ( 'V',0xDC ), ( 'W',0xDD ), ( 'X',0xDE ), ( 'Y',0xE0 ), ( 'Z',0xE1 ), ( '0',0xE2 ), ( '1',0xE3 ), ( '2',0xE4 ),
                ( '3',0xE5 ), ( '4',0xE6 ), ( '5',0xE7 ), ( '6',0xE8 ), ( '7',0xE9 ), ( '8',0xEA ), ( '9',0xEB ), ( ' ',0x00 ), ( ':',0xEC ), ( '-',0xED )]

FILL_CHAR = '@'

def applyJSON(JSONFile):
    
    insertionParams = json.load(open(JSONFile))
    images = insertionParams["Images"]
    insertionAreas = insertionParams["InsertionAreas"]
    mode = insertionParams["Mode"]

    for imageNumber in range(len(images)):
        
        currentInsertionAreas = []
        insertionAreaImages = []
        for insertionArea in insertionAreas:
            if insertionArea[2] == imageNumber:
                currentInsertionAreas.append([insertionArea[0], insertionArea[1], 0])
                insertionAreaImages.append(0)
        
        fontImagePath = insertionParams["FontImagePath"]
        fontCLUTs = [insertionParams["FontCLUTs"][imageNumber]]

        for fontCLUT in fontCLUTs:
            for clutNumber in range(len(fontCLUT)):
                fontCLUT[clutNumber] = tuple(fontCLUT[clutNumber])
        
        tableFilePath = insertionParams["TableFile"]
        ANMFilePath = insertionParams["ANMFilePath"]
        oldANMFilePath = insertionParams["OriginalANMFilePath"]
        
        offsetRanges = insertionParams["OffsetRanges"]

        oldOffsets = []
        ANIfileStem = Path(JSONFile).stem

        #check if script is within range
        for fileName in os.listdir(SCRIPT_FOLDER):
            if fileName.endswith('.txt') and fileName.startswith(ANIfileStem):
                offset = int(fileName.replace(ANIfileStem + '_', '').replace('.txt', ''))
                for offsetRange in offsetRanges[imageNumber]:
                    if offset >= offsetRange[0] and offset <= offsetRange[1]:
                        oldOffsets.append(offset)
                        scriptFound = True
                        break

        textFileBase = JSONFile.replace('.json', '_')
        textFilePaths = []
        for offset in oldOffsets:
            textFilePaths.append(textFileBase + str(offset) + '.txt')


        currentImage = [images[imageNumber]]
        

        ANMs = ImageProcessor.injectText(oldANMFilePath, oldOffsets, [images[imageNumber]], insertionAreaImages, currentInsertionAreas, fontImagePath, fontCLUTs, textFilePaths, tableFilePath, mode)

        newOffsets, oldOffsetsAll = ImageProcessor.updateANI(ANMs, oldOffsets, ANMFilePath)

        ImageProcessor.updateHarmfulParkOffsets(ANMFilePath, newOffsets, oldOffsetsAll, ImageProcessor.HAR_EXE_PATH)

    return

def buildANI():
    for fileName in os.listdir(SCRIPT_FOLDER):
        if fileName.endswith('.json'):
            print("Processing " + fileName)
            applyJSON(os.path.join(SCRIPT_FOLDER, fileName))

def readBGD(fileName):
    BGDObj = ImageProcessor.BGD(open(fileName, 'rb'))
    rows = BGDObj.MAPH
    cols = BGDObj.MAPW

    outFileName = 'BGD/STAFF.txt'

    outFile = open(outFileName, 'w', encoding='utf-8')

    for y in range(rows):
        for x in range(cols):
            cellValue = BGDObj.MAP[x + y*cols]
            
            letterFound = False
            for mapping in STAFF_TABLE:
                if mapping[1] == cellValue:
                    outFile.write(mapping[0])
                    letterFound = True
                    break
            
            if not letterFound:
                outFile.write(FILL_CHAR)
        outFile.write('\n')    


    return


def buildBGD(fileName, textFileName):

    print("Processing BGD " + fileName)
    BGDObj = ImageProcessor.BGD(open(fileName, 'rb'))
    rows = BGDObj.MAPH
    cols = BGDObj.MAPW

    BGD_OFFSET = 8

    outFile = open(fileName, 'r+b')
    outFile.seek(BGD_OFFSET)

    textFile = open(textFileName, 'r', encoding='UTF-8')

    for x in range(rows):
        for y in range(cols):
            nextChar = textFile.read(1)
            for mapping in STAFF_TABLE:
                if mapping[0] == nextChar:
                    outFile.write(mapping[1].to_bytes(2, byteorder='little'))
                    break

        textFile.read(1) #read newline away


    return



def build():
    
    
    buildANI()
    #readBGD(BGD_FILE)
    buildBGD(BGD_FILE, BGD_TEXT_FILE)
    copy_tree(BUILD_FOLDER, TARGET_FOLDER)
    os.chdir('mkpsxiso')
    subprocess.run([MKPSXISO, XML])


build()