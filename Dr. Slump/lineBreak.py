# Runs a command line tool to take any text string and return a version of it with correctly
# spaced new line characters

import sys    
import os
from pathlib import Path
import shutil

#These symbols reset char count to 0
reset16Symbols = ['[nl]']
#These symbols do not change char count
controlSymbols = ['[WHITE]', '[YELLOW]', '[BLUE]', '[RED]', '[BLUE]', '[END]', 
                  '[GREEN]', '[GREY]', '[PINK]', '[SHORT_PAUSE]', '[MEDIUM_PAUSE]']
#These symbols can be replaced with newline characters
spaces = [' ']
#These symbols reset char count to 1
reset15Symbols = ['[nl_space]']

#Copies output text to system clipboard
def addToClipBoard(text):
    command = 'echo | set /p nul=' + text.strip() + '| clip'
    os.system(command)



#Returns the character count of a text string after counting symbols
def findLength(inputText):
    
    charCount = 0
    inSymbol = False
    
    symbol = ''

    for char in inputText:
        if inSymbol == False:
            if char == '[':
                inSymbol = True
                symbol = '['
            else:
                charCount += 1
            
        else:
            symbol += char
            if char ==']':
                inSymbol = False
                if symbol in reset15Symbols:
                    charCount = 1
                elif symbol in reset16Symbols:
                    charCount = 0
                elif symbol in controlSymbols:
                    continue
                elif symbol in spaces:
                    print("ERROR: EXTRA SPACE FOUND!: "+ symbol)
                    break
                else:
                    charCount += 1
                symbol = ''


    return charCount

#Returns a text string with text correctly spaced at a maximum of 16 characters per line 
def addSpacing(inputText):

    if '@' in inputText or inputText=='\n' or inputText=='' or '[nl]' in inputText:
        return inputText
    
    splitLine = inputText.split(' ')

    splitCursor = 0
    
    output = ''
    while splitCursor < len(splitLine):
        lineTotal = 0
        output = output.strip()
        while splitCursor < len(splitLine):
            
            lineTotal += findLength(splitLine[splitCursor])
            if lineTotal > 16:
                output = output.strip()
                output += '[nl]'
                lineTotal = 0
            else:
                output += splitLine[splitCursor] + ' '
                lineTotal += 1
                splitCursor += 1
    
    return '*' + output.strip()

#Run input loop
while True:
    inputLine = input()
    fixedLine = addSpacing(inputLine.strip('*').replace('[nl]', ' '))
    #addToClipBoard(fixedLine)
    print(fixedLine)
