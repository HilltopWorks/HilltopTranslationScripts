############################################################################
# Finds script and tim files among uncompressed lzss files for PS1 game    #
# "Dr. Slump"                                                              #
# Searches 'gen' folder and places files in the 'script' and 'tim' folders #                                                                     #
############################################################################

import sys    
import os
from pathlib import Path
import shutil


TIM_ID = 0x10

#scripts start with a pointer to the end of the table header
def isScript(short1, short2):
    endOfTable = (short1 * 2) + 2
    alignedTable = endOfTable + (4 - endOfTable % 4)%4
    textStart = short2

    if alignedTable == textStart:
        return True
    else:
        return False

#tim image files start with 0x10
def isTim(short1, short2):
    value1 = short2 << 16
    value2 = short1

    if value1 + value2 == TIM_ID:
        return True
    else:
        return False


#run main loop
for sourceFile in os.listdir("gen/"):

    if sourceFile.endswith(".uncomp"):
        
        openFile = open('gen/' + sourceFile, 'rb')

        shortAtZero = int.from_bytes(openFile.read(2), 'little', signed=False)
        shortAtTwo = int.from_bytes(openFile.read(2), 'little', signed=False)

        if isTim(shortAtZero, shortAtTwo):
            shutil.copyfile('gen/' + sourceFile, 'tim/' + sourceFile)
        elif isScript(shortAtZero, shortAtTwo):
            shutil.copyfile('gen/' + sourceFile, 'script/' + sourceFile)