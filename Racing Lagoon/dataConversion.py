#########################################################################
# Takes binary text input and converts it to utf-8 text via a table file#
# and vice vera for ps1 game "Racing Lagoon"                            #
#                                                                       #
#########################################################################

import sys    
import os
from pathlib import Path
import shutil
import xml
import re

xFill = ['','XX','XXXX','XXXXXX']
EOFS = ['de','de00']

def toInt(byteObj):
    return int.from_bytes(byteObj, "little", signed = False)

def findTableMatchForHex(hexObj, tableFile):
    
    tableFile.seek(0)

    for line in tableFile:
        if line.startswith('#') == False and line != '\n':
            splitLine = line.split('=',1)
            matchHex = splitLine[0]
            parameterLength = splitLine[1].count('X') >> 1

            if hexObj.startswith("00"):
                return "0", 1

            if hexObj.startswith(matchHex.lower()):
                    
                parameters = ""
                if parameterLength != 0:
                    parameters = "=0x" + hexObj[2:2 + parameterLength*2]

                returnMatch = re.sub(r"=X+", parameters, line.split('=', 1)[1].strip('\n'))

                return returnMatch, (len(matchHex) + parameterLength*2)>>1
    
    #return input hex if no match found
    print("HEX MATCH ERROR: " + hexObj)
    return '<' + hexObj + '>', len(hexObj)>>1


def hexToText(hexObj):
    tableFile = open("RacingLagoon.tbl", 'r', encoding='utf-8')
    
    returnBuffer = ''

    hexLength = len(hexObj)>>1
    bytesConverted = 0
    while bytesConverted < hexLength:
        
        nextMatch = hexObj[bytesConverted*2:bytesConverted*2 + 16]

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

            if textObj == matchText:
                return line.split('=', 1)[0]
    
    #return input text if no match found
    print("TEXT MATCH ERROR: " + textObj)
    return '<NOMATCH>'


def textToHex(textObj):
    tableFile = open("RacingLagoon.tbl", 'r', encoding='utf-8')

    returnBuffer = ''
    textLength = len(textObj)

    charsConverted = 0

    while charsConverted < textLength:
        nextChar = textObj[charsConverted]
        if nextChar == '{':
            symbol = textObj[charsConverted:].split('}')[0] + '}'
            if "=" in symbol:
                parameters = symbol.split("=")[1].replace("0x",'').strip("}\n")
                parameterLength = len(parameters) >>1
                cleanParameters = "=" + xFill[parameterLength]
                cleanSymbol = re.sub( r"=0x[0-9A-Fa-f]*}",cleanParameters + "}" ,symbol)
                match = findTableMatchForText(cleanSymbol, tableFile)
                returnBuffer += (match + parameters).lower()
                charsConverted += (len(symbol))

            else:
                match = findTableMatchForText(symbol, tableFile)
                if match in EOFS:
                    match = EOFS[0]
                returnBuffer+= match.lower()
                charsConverted += len(symbol)
        else:
            match = findTableMatchForText(nextChar, tableFile)
            returnBuffer += match.lower()
            charsConverted += 1

    return returnBuffer



#print(textToHex("Hilltop{NL}Wouldn't it be great if you{NL}could play this untranslated{NL}Squaresoft classic in English?{END}"))
#print(textToHex("trash"))
#print(textToHex("Kenzo{NL}This{BUFFER=0x04}ain't{BUFFER=0x04}exactly{BUFFER=0x04}the{NL}type{BUFFER=0x04}of{BUFFER=0x04}night{BUFFER=0x04}for{BUFFER=0x04}a{NL}debut.{COLOR=0x0001}{END}"))

#testFile = open("test.txt", "w", encoding="utf-8")
#testFile.write(hexToText( open("test.bin", "rb").read().hex()))

#testFile = open("test.txt", "w", encoding="utf-8")
#testFile.write(hexToText( open("test.bin", "rb").read().hex()))