#########################################################################
# Takes binary text input and converts it to utf-8 text via a table file#
# and vice vera for ps1 game "Dr. Slump"                                #
#                                                                       #
#########################################################################

import sys    
import os
from pathlib import Path
import shutil
import xml

def findTableMatchForHex(hexObj, tableFile):
    
    tableFile.seek(0)
    matchFound = False
    for line in tableFile:
        if line.startswith('#') == False and line != '\n':
            splitLine = line.split('=',1)
            matchHex = splitLine[0]
            #print(hexObj)
            #print(matchHex)
            #print(splitLine[1].strip('\n'))
            if hexObj.startswith(matchHex):
                return line.split('=', 1)[1].strip('\n'), len(matchHex)>>1
    
    #return input hex if no match found
    return '<' + hexObj + '>', len(hexObj)>>1


def hexToText(hexObj):
    tableFile = open("SlumpTable.tbl", 'r', encoding='utf-8')
    
    returnBuffer = ''

    hexLength = len(hexObj)>>1
    bytesConverted = 0
    while bytesConverted < hexLength:
        nextMatch = hexObj[bytesConverted*2:bytesConverted*2 + 8]
        match, matchLength = findTableMatchForHex(nextMatch, tableFile)
        returnBuffer += match
        bytesConverted += matchLength 

    return returnBuffer

def findTableMatchForText(textObj, tableFile):
    tableFile.seek(0)
    matchFound = False
    for line in tableFile:
        if line.startswith('#') == False and line != '\n':
            splitLine = line.split('=',1)
            matchText = splitLine[1].strip('\n')
            #print(hexObj)
            #print(matchHex)
            #print(splitLine[1].strip('\n'))
            if textObj == matchText:
                return line.split('=', 1)[0]
    
    #return input hex if no match found
    print("Invalid character found: " + textObj)
    return '<NOMATCH>'


def textToHex(textObj):
    tableFile = open("SlumpTable.tbl", 'r', encoding='utf-8')

    returnBuffer = ''
    textLength = len(textObj)

    charsConverted = 0

    while charsConverted < textLength:
        nextChar = textObj[charsConverted]
        if nextChar == '[':
            symbol = textObj[charsConverted:].split(']')[0] + ']'
            match = findTableMatchForText(symbol, tableFile)
            returnBuffer+= match
            charsConverted += len(symbol)
        else:
            match = findTableMatchForText(nextChar, tableFile)
            returnBuffer += match
            charsConverted += 1

    while (len(returnBuffer)>>1) % 4 !=0:
        returnBuffer +='00'

    return returnBuffer