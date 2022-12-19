#########################################################################
# Takes binary text input and converts it to utf-8 text via a table file#
# and vice vera for ps1 game "B.L.U.E."                                 #
#                                                                       #
#########################################################################

import sys    
import os
from pathlib import Path
import shutil
import xml
import re

tableFileName = 'sjis.tbl'
injectionTableFileName = 'sjis.tbl'
asciiTableFileName = "ascii.tbl"
sjisTableFileName = "sjis.tbl"

NORMAL_TEXT = 0
SJIS_TEXT = 1
ASCII_TEXT = 2

xFill = ['','XX','XXXX','XXXXXX', 'XXXXXXXX']
EOFs = ['0000000000',
        '000000000000',
        '00000000000000',
        '0000000000000000'] 

NO_MATCH = "<NO_MATCH>"


def toInt(byteObj):
    return int.from_bytes(byteObj, "little", signed = False)

def align_data(bytes_obj):
    '''Aligns a bytes object to 32 bits'''
    buffer = b''

    alignment = (4 - (len(bytes_obj) % 4)) % 4
    buffer += bytes_obj + bytes(alignment)
    return buffer

def __findTableMatchForHex__(hexObj, tableFile):
    
    tableFile.seek(0)

    for line in tableFile:
        if line.startswith('#') == False and line != '\n':
            splitLine = line.split('=',1)
            matchHex = splitLine[0]
            parameterLength = 0

            #TODO WHY?
            #if hexObj.startswith("00"):
            #    return "0", 1

            if hexObj.startswith(matchHex.lower()):
                    
                parameters = ""
                if parameterLength != 0:
                    parameters = "=0x" + hexObj[2:2 + parameterLength*2]

                returnMatch = re.sub(r"=X+", parameters, line.split('=', 1)[1].strip('\n'))

                return returnMatch, (len(matchHex) + parameterLength*2)>>1
    
    #return input hex if no match found
    print("HEX MATCH ERROR: " + hexObj + " in line:" + hexObj)
    return '<' + hexObj + '>', len(hexObj)>>1


def hexToText(hexObj):
    tableFile = open(tableFileName, 'r', encoding='utf-8')
    
    returnBuffer = ''

    hexLength = len(hexObj)>>1
    hexConverted = 0
    while hexConverted < hexLength:
        
        nextMatch = hexObj[hexConverted*2:hexConverted*2 + 32]

        
        match, matchLength = __findTableMatchForHex__(nextMatch, tableFile)

        returnBuffer += match
        hexConverted += matchLength 

    return returnBuffer

def __findTableMatchForText__(textObj, tableFile):
    tableFile.seek(0)
    matchFound = False
    for line in tableFile:
        if line.startswith('#') == False and line != '\n':
            splitLine = line.split('=',1)
            matchText = splitLine[1].strip('\n')

            if textObj == matchText:
                return line.split('=', 1)[0]
    
    #return input text if no match found
    print("TEXT MATCH ERROR: " + textObj)
    return NO_MATCH

def textToHex(textObj, tableType):
    tableFile = open(injectionTableFileName, 'r', encoding='utf-8')
    #asciiTable = open(asciiTableFileName, 'r', encoding='utf-8')
    sjisTable = open(sjisTableFileName, 'r', encoding='utf-8')
    
    if tableType == SJIS_TEXT:
        tableFile = sjisTable
    #elif tableType == ASCII_TEXT:
    #    tableFile = asciiTable
    
    returnBuffer = ''
    textLength = len(textObj)
    charsConverted = 0

    while charsConverted < textLength:
        nextChar = textObj[charsConverted]
        if nextChar == '{': #Custom tag processing
            symbol = textObj[charsConverted:].split('}')[0] + '}'
            match = __findTableMatchForText__(symbol, tableFile)
            returnBuffer += match.lower()
            charsConverted += len(symbol)
        else:
            match = __findTableMatchForText__(nextChar, tableFile)
            returnBuffer += match.lower()
            charsConverted += 1

    return returnBuffer

def scriptTextToHex(textObj, tableType):
    tableFile = open("INJECT.tbl", 'r', encoding='utf-8')
    #elif tableType == ASCII_TEXT:
    #    tableFile = asciiTable
    
    returnBuffer = ''
    textLength = len(textObj)
    charsConverted = 0

    while charsConverted < textLength:
        nextChar = textObj[charsConverted]
        if nextChar == '{': #Custom tag processing
            symbol = textObj[charsConverted:].split('}')[0] + '}'
            match = __findTableMatchForText__(symbol, tableFile)
            returnBuffer += match.lower()
            charsConverted += len(symbol)
        else:
            char1 = nextChar
            char2 = textObj[charsConverted + 1]
            if char2 == "{":
                char2 = ' '
                charsConverted -= 1
            match = __findTableMatchForText__(char1 + char2, tableFile)
            returnBuffer += match.lower()
            charsConverted += 2

    return returnBuffer

#print(textToHex("Hilltop{NL}Wouldn't it be great if you{NL}could play this untranslated{NL}Squaresoft classic in English?{END}"))
#print(textToHex("trash"))
#print(textToHex("Kenzo{NL}This{BUFFER=0x04}ain't{BUFFER=0x04}exactly{BUFFER=0x04}the{NL}type{BUFFER=0x04}of{BUFFER=0x04}night{BUFFER=0x04}for{BUFFER=0x04}a{NL}debut.{COLOR=0x0001}{END}"))

#testFile = open("test.txt", "w", encoding="utf-8")
#testFile.write(hexToText( open("test.bin", "rb").read().hex()))

#testFile = open("test.txt", "w", encoding="utf-8")
#testFile.write(hexToText( open("test.bin", "rb").read().hex()))