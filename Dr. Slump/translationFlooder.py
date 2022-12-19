#Searches for duplicate translation entries and adds them to untranslated files
#

import sys    
import os
from pathlib import Path
import shutil



translatedLines = []
originalLines = []
fileCheck = []


#Populates the lists of translated and original lines for use in propagating translations
def populateMap(translatedFolder, originalsFolder):
    for sourceFile in os.listdir(translatedFolder):
        translatedFile = open(translatedFolder + sourceFile, 'r', encoding='utf8')

        translatedFile.readline()

        for line in translatedFile:
            if '@' not in line and line != '\n' and line:
                translatedLines.append(line)
                fileCheck.append(sourceFile)

        originalFile = open(originalsFolder + sourceFile, 'r', encoding='utf8')

        for line in originalFile:
            if '@' not in line and line != '\n' and line:
                originalLines.append(line)
    
        translatedFile.close()
        originalFile.close()


#Edits scripts in the target folder to include lines already translated in the "Done" folder
def propagateTranslations(targetFolder):
    
    numberChanges = 0

    for root, dirs, files in os.walk(targetFolder):
        for targetFile in files:
            openTarget = open(targetFolder + targetFile, 'r', encoding='utf8')

            targetData = openTarget.readlines()
            openTarget.close()
            
            for line in range(0, len(targetData)):
                if '@' not in targetData[line] and targetData[line] != '\n' and line and targetData[line] in originalLines:
                    index = originalLines.index(targetData[line])
                    targetData[line] = translatedLines[index]
                    print(translatedLines[index])
                    print(originalLines[index] + '\n')
                    numberChanges += 1

            outputFile = open(targetFolder + targetFile, 'w', encoding='utf8')
            outputFile.writelines(targetData)

            outputFile.close()
            

        print(numberChanges)
        break
                
                

populateMap('translations/Done/', 'translations/Originals/')

#write output to text file for debugging
with open('newlines.txt', 'w', encoding = 'utf-8') as f:
    for i in range(len(translatedLines)):
        f.write("%s" % translatedLines[i])
        f.write("%s\n" % originalLines[i])

propagateTranslations('translations/')