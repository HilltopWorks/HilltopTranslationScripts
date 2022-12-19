#Turns 2352 byte sectors files into 2336 byte sector files by removing the header

import sys    
import os
import io
from functools import partial

rawFolder = "rawSTR/"
STRFolder = "STR/"

if not os.path.exists(STRFolder):
    os.makedirs(STRFolder)

for sourceFile in os.listdir(rawFolder):
    inputFile = open(rawFolder + sourceFile, 'rb')
    
    outputFile = open(STRFolder + sourceFile, 'wb')    

    for chunk in iter(partial(inputFile.read, 2352), b''):
        outputFile.write(chunk[16:2353])

    inputFile.close()
    outputFile.close()
