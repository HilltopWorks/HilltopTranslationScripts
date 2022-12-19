#########################################################################
# Separates .pac files into individual .lzss files for PS1 game         #
# "Dr. Slump"                                                           #
#                                                                       #
#########################################################################

# Dr. Slump uses 4 byte little endian pointers followed by 4 byte little 
# endian filesizes


import sys    
import os
from pathlib import Path
import uncompress
import xml.etree.ElementTree as ET

LZSS_IDENTIFIER = 1


#Adds the next embedded entry to its parent
def writeXMLEntry(fileStream, node):
    #first 4 bytes form pointer to lzss data chunk or embedded .pac file
    lzssPtr      = int.from_bytes(fileStream.read(4), "little", signed=False)
    #last 4 bytes form size of compressed lzss data chunk or embedded .pac file
    lzssFileSize = int.from_bytes(fileStream.read(4), "little", signed=False)

    #Skip blank entries
    if lzssPtr + lzssFileSize != 0 and lzssFileSize != 0xFFFFFFFF and lzssPtr != 0xFFFFFFFF and lzssFileSize!=0x44444444:
        #return file cursor to pointer table after inserting entry
        returnPos = fileStream.tell()
        fileStream.seek(lzssPtr)
        
        #read identifying byte
        chunkID = int.from_bytes(fileStream.read(1), "little", signed = False)
        
        if chunkID == LZSS_IDENTIFIER:
            chunkType = "lzss"
            elem = ET.SubElement(node, chunkType)

            uncompressedSize = fileStream.read(4)
            elem.attrib['uncompressedSize'] = str(int.from_bytes(uncompressedSize, "little", signed = False))

        else:
            
            fileStream.seek(lzssPtr)

            typeFound = False
            while typeFound == False:
                testReading = int.from_bytes(fileStream.read(4), "little", signed = False)

                #if testReading == 0x11F00415 or testReading == 0x1004041A or testReading % 2 == 1 or testReading == 0x001F0014 or testReading == 0x10000230:
                if testReading == 0x11F00415 or testReading == 0x1004041A or testReading % 2 == 1 or testReading == 0x001F0014 or testReading == 0x10000230:
                    chunkType = "raw"
                    typeFound = True
                    break
                if testReading != 0:
                    chunkType = "pac"
                    typeFound = True
                    break

            #chunkType = "pac" or "raw"
            elem = ET.SubElement(node, chunkType)

        #initialize leaf element
        elem.attrib['tableOffset'] = str(returnPos - 8)
        elem.attrib['fileName'] = node.get('fileName') + '.' + elem.get('tableOffset') + '.' + chunkType
        elem.attrib['size'] = str(lzssFileSize)
        elem.attrib['dataOffset'] = str(lzssPtr)
        
        fileStream.seek(returnPos)

    #Seemingly invalid entries affect texture mapping
    elif lzssFileSize == 0xFFFFFFFF or  lzssPtr == 0xFFFFFFFF or lzssFileSize==0x44444444:
        elem = ET.SubElement(node, "textureSymbol")
        elem.attrib['tableOffset'] = str(fileStream.tell()-8)
        elem.attrib['dataOffset'] = str(lzssPtr)
        elem.attrib['size'] = str(lzssFileSize)
        

    return lzssPtr

#Searches the file for all embedded children and updates the xml file
def findData(currNode, isroot, inputFolder, outputFolder):
    if isroot == True:
        inputFile = open(inputFolder + currNode.get("fileName"), "rb")#DEBUG
    else:
        inputFile = open(outputFolder +currNode.get("fileName"), "rb")
    dataOffset = 0
    indexCursor = 0
    
    #find first pointer in file to find end of pointer block
    while True:
        print(ET.tostring(currNode))
        searchResult = writeXMLEntry(inputFile, currNode)
        print(ET.tostring(currNode))
        #Skip entries with values of 0
        if  searchResult != 0:
            dataOffset = searchResult
            indexCursor += 8
            break
        indexCursor += 8

    #iterate over all pointers in pointer block
    while indexCursor < dataOffset:
        writeXMLEntry(inputFile, currNode)
        indexCursor += 8

    for node in currNode.findall('lzss'):
        print(node.get('fileName'))

        uncompress.uncompressChunk(currNode.get('fileName'), int(node.get('dataOffset')), node.get('fileName'), isroot, inputFolder, outputFolder)

    for node in currNode.findall('raw'):
        print(node.get('fileName'))

        if os.path.exists(outputFolder + node.get('fileName')):
            os.remove(outputFolder + node.get('fileName'))

        pacOutput = open(outputFolder + node.get('fileName'), "w+b")
        inputFile.seek(int(node.get('dataOffset')))
        pacOutput.write(inputFile.read(int(node.get('size'))))
        pacOutput.close()
    
    for node in currNode.findall('pac'):
        print(node.get('fileName'))

        if os.path.exists(outputFolder + node.get('fileName')):
            os.remove(outputFolder + node.get('fileName'))

        pacOutput = open(outputFolder + node.get('fileName'), "w+b")
        inputFile.seek(int(node.get('dataOffset')))
        pacOutput.write(inputFile.read(int(node.get('size'))))
        pacOutput.close()
        findData(node, False, inputFolder, outputFolder)    

    #cleanup
    inputFile.close()


#Run main loop, iterating over all files in "source" and outputting to "genClean"
for sourceFile in os.listdir("source/"):
    isSource = True

    if sourceFile.endswith(".PAC"):#$DEBUG
        root = ET.Element('source')

        
        root.attrib['fileName'] = sourceFile
        root.attrib['tableOffset']="0"
        root.attrib['size']=str(Path("source/" + sourceFile).stat().st_size)
        
        findData(root, isSource, "source/", "genClean/")

        # Converting the xml data to byte object, 
        # for allowing flushing data to file  
        # stream 
        b_xml = ET.tostring(root) 
        
        with open("xml/" + root.get("fileName")+".xml", "wb") as f: 
            f.write(b_xml) 