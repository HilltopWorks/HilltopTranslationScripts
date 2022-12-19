#################################################################################
# Dumps script from script files and applies a table file for PS1 game          #
# "Dr. Slump"                                                                   #
# Searches 'script' folder and places files in the 'translations/done' folder   #                                                                     #
#################################################################################

import sys    
import os
from pathlib import Path
import shutil
import xml
import xml.etree.ElementTree as ET
import xml.dom.minidom
import dataConversion


#Each translation entry has a positional ID and binary offset
class LineEntry:
    def __init__(self, text, dataOffset, newID):
        self.text = text
        self.dataOffset = [dataOffset]
        self.entryIDs = [newID]

    def addID(self, collisionID):
        self.entryIDs.append(collisionID)

    def addOffset(self, offset):
        self.dataOffset.append(offset)    

#Each script file has a list of entries and a parent file
class Script:
    def __init__(self, fileName, textStart, numEntries):
        self.entries = []
        self.numEntries = numEntries
        self.fileName = fileName
        self.textStart = textStart
        self.textEnd = str(Path("script/" + fileName).stat().st_size)

    def addEntry(self, entry):
        for myEntry in self.entries:
            if bool(set(myEntry.dataOffset) & set(entry.dataOffset)) or entry.text == myEntry.text:
                myEntry.addID(entry.entryIDs[0])
                myEntry.addOffset(entry.dataOffset[0])
                return
        self.entries.append(entry)

    def addCollision(self, checkID, offset):
        for myEntry in self.entries:
            if offset == myEntry.dataOffset:
                myEntry.addID(checkID)
                return

    def containsEntry(self, offset):
        for myEntry in self.entries:
            if offset == myEntry.dataOffset:
                return True
        return False
         
    def containsText(self, text):
        for myEntry in self.entries:
            if myEntry.text == text:
                return True
        else:
            return False

#Alignes a value to the next 4 byte position
def byteAlign(value):
    ret = value + ((4 - (value % 4)) % 4) 
    return ret

#converts a byte object to integer
def toInt(byteObj):
    return int.from_bytes(byteObj, "little", signed = False)

#looks in the script folder and dumps each binary script file to a txt file
def unpackScript():
    for script in os.listdir("script/"):
        if script.endswith('uncomp'):
            
            scriptFile = open("script/" + script, 'rb')
           
            numEntries = toInt(scriptFile.read(2))
            textStart = toInt(scriptFile.read(2))
            
            thisScript = Script(script, textStart,numEntries)
            
            for lineNumber in range(0, numEntries):
                scriptFile.seek(2 + (lineNumber * 2))
                linePosition = toInt(scriptFile.read(2))  
                if thisScript.containsEntry(linePosition):
                    thisScript.addCollision(lineNumber, linePosition)
                else:
                    scriptFile.seek(linePosition)
                    lineBytes = b''
                    endOfLine = False
                    while endOfLine == False:
                        charToAdd1 = scriptFile.read(1)
                        charToAdd2 = scriptFile.read(1)
                        lineBytes += charToAdd1 + charToAdd2
                        

                        if charToAdd1 == b'\xFF' or charToAdd2 == b'\xFF':
                            endOfLine = True

                    newLine = LineEntry(dataConversion.hexToText(lineBytes.hex()), linePosition, lineNumber)
                    
                    thisScript.addEntry(newLine)

            
            if os.path.exists("translations/Originals/" + thisScript.fileName + ".txt"):
                os.remove("translations/Originals/" + thisScript.fileName + ".txt")

            with open("translations/Originals/" + thisScript.fileName +".txt", "w", encoding='utf-8') as f: 

                f.write('@@' + thisScript.fileName + '@@' + str(thisScript.numEntries) + '@@' + str(thisScript.textStart) + '@@' + str(thisScript.textEnd) + "\n")
                for entry in thisScript.entries:
                    lineInfoBuffer = '@'
                    for ID in entry.entryIDs:
                        lineInfoBuffer += str(ID) +'/'
                    lineInfoBuffer = lineInfoBuffer.strip('/')

                    lineInfoBuffer += '@'
                    for offset in entry.dataOffset:
                        lineInfoBuffer += str(offset) +'/'
                    lineInfoBuffer = lineInfoBuffer.strip('/')

                    #lineInfoBuffer += str(entry.dataOffset)
                    f.write(lineInfoBuffer + "\n")
                    f.write('*' + entry.text + "\n")

                f.close()


#looks in the script folder and dumps each text block to an xml file
def unpackScriptOld():
    for script in os.listdir("script/"):
        if script.endswith('uncomp'):
            
            scriptFile = open("script/" + script, 'rb')

            root = ET.Element('source')

            root.attrib['fileName'] = script

            numEntries = toInt(scriptFile.read(2))
            root.attrib['entries']=str(numEntries)

            root.attrib['textStart']=str(toInt(scriptFile.read(2)))
            root.attrib['textEnd']=str(Path("script/" + script).stat().st_size)
            
            occupiedOffsets = []

            for lineNumber in range(0, numEntries):
                scriptFile.seek(2 + (lineNumber * 2))
                linePosition = toInt(scriptFile.read(2))  

                if linePosition not in occupiedOffsets:
                    occupiedOffsets.append(linePosition)

                    scriptFile.seek(linePosition)
                    lineBytes = b''
                    endOfLine = False
                    while endOfLine == False:
                        charToAdd1 = scriptFile.read(1)
                        charToAdd2 = scriptFile.read(1)
                        lineBytes += charToAdd1 + charToAdd2
                        

                        if charToAdd1 == b'\xFF' or charToAdd2 == b'\xFF':
                            endOfLine = True

                    elem = ET.SubElement(root, 'line')
                    elem.attrib['entryIDs'] = str(lineNumber)
                    elem.attrib['dataOffset'] = str(linePosition)
                
                    elem.text = dataConversion.hexToText(str(lineBytes.hex()))
                else:
                    for child in root:
                        if child.get("dataOffset") == str(linePosition):
                            child.attrib['entryIDs'] += '/' + str(lineNumber) 

                



            # Converting the xml data to byte object, 
            # for allowing flushing data to file  
            # stream 
            b_xml = ET.tostring(root) 
            
            print(b_xml)

            dom = xml.dom.minidom.parseString(b_xml)

            if os.path.exists("translations/" + root.get("fileName")+".xml"):
                os.remove("translations/" + root.get("fileName")+".xml")

            with open("translations/" + root.get("fileName")+".xml", "w") as f: 

                f.write(dom.toprettyxml())

unpackScript()