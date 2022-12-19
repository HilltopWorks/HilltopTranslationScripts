#########################################################################
# Combines files specified in an xml file into a .PAC files for PS1     #
# game "Dr. Slump"                                                      #
#                                                                       #
#                                                                       #
#########################################################################

# Dr. Slump uses 4 byte little endian pointers followed by 4 byte little 
# endian filesizes


import sys    
import os
import io
from pathlib import Path
import compress
import xml.etree.ElementTree as ET

#Aligns a number to the next multiple of 4
def byteAlign(value):
    ret = value + ((4 - (value % 4)) % 4) 
    return ret


#Reforms a pac file following its definition in its XML file and child files in the given folder
def packPac(node, folder):
    #Size of table section for this node
    tableSize = int(node[0].get('dataOffset'))

    outputStream = io.BytesIO(bytes(tableSize))

    #Current data insertion position
    dataCursor = tableSize

    #recurse into embedded pac files
    for subNode in node.findall('pac'):
        packPac(subNode, folder)

    #compress subnode and add to this node's table and data section
    for subNode in node:
        #compress lzss file and add to parent
        if subNode.tag == 'lzss':

            
            lzssPacked = compress.compressChunk(folder + subNode.get('fileName') + '.uncomp')
            
            #Update XML

            subNode.attrib['dataOffset'] = str(dataCursor)
            dataOffset = str(dataCursor)
            subNode.attrib['size'] = str(len(lzssPacked))
            compressedSize = str(len(lzssPacked))
            subNode.attrib['uncompressedSize'] = str(Path(folder + subNode.get('fileName') + '.uncomp').stat().st_size)
            uncompressedSize = str(Path(folder + subNode.get('fileName') + '.uncomp').stat().st_size)
            tableOffset = subNode.get('tableOffset')


            #write table entry
            outputStream.seek(int(tableOffset))
            outputStream.write(bytes([int(dataOffset) & 0xFF]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF00) >> 8]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF0000) >> 16]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF000000) >> 24]))

            outputStream.write(bytes([int(compressedSize) & 0xFF]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF00) >> 8]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF0000) >> 16]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF000000) >> 24]))


            #write data
            outputStream.seek(dataCursor)
            outputStream.write(lzssPacked + bytes((4 - (int(compressedSize) % 4)) % 4))

            #update cursor,  Align data offset to 4 byte grid
            dataCursor += byteAlign(int(compressedSize))

        # Only update table for mysterious texture symbols
        elif subNode.tag == 'textureSymbol':
            tableOffset = int(subNode.get('tableOffset'))
            dataOffset = int(subNode.get('dataOffset'))
            size = int(subNode.get('size'))

            outputStream.seek(int(tableOffset))
            outputStream.write(bytes([int(dataOffset)  & 0x000000FF]))
            outputStream.write(bytes([(int(dataOffset) & 0x0000FF00) >> 8]))
            outputStream.write(bytes([(int(dataOffset) & 0x00FF0000) >> 16]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF000000) >> 24]))

            outputStream.write(bytes([int(size)  & 0x000000FF]))
            outputStream.write(bytes([(int(size) & 0x0000FF00) >> 8]))
            outputStream.write(bytes([(int(size) & 0x00FF0000) >> 16]))
            outputStream.write(bytes([(int(size) & 0xFF000000) >> 24]))

        #write raw file
        else:
            rawToWrite = open(folder + subNode.get('fileName'), "rb").read()

            subNode.attrib['dataOffset'] = str(dataCursor)
            dataOffset =  str(dataCursor)
            subNode.attrib['size'] = str(len(rawToWrite))
            compressedSize = str(len(rawToWrite))
            tableOffset = subNode.get('tableOffset')

            #write table entry
            outputStream.seek(int(tableOffset))
            outputStream.write(bytes([int(dataOffset)  & 0x000000FF]))
            outputStream.write(bytes([(int(dataOffset) & 0x0000FF00) >> 8]))
            outputStream.write(bytes([(int(dataOffset) & 0x00FF0000) >> 16]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF000000) >> 24]))

            outputStream.write(bytes([int(compressedSize)  & 0x000000FF]))
            outputStream.write(bytes([(int(compressedSize) & 0x0000FF00) >> 8]))
            outputStream.write(bytes([(int(compressedSize) & 0x00FF0000) >> 16]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF000000) >> 24]))


            #write data
            outputStream.seek(dataCursor)
            outputStream.write(rawToWrite + bytes((4 - (int(compressedSize) % 4)) % 4))

            #update cursor,  Align data offset to 4 byte grid
            dataCursor += byteAlign(int(compressedSize))

    #write output file
    
    if os.path.exists(folder + node.get('fileName')):
        os.remove(folder + node.get('fileName'))


    pacOutput = open(folder + node.get('fileName'), "w+b")
    outputStream.seek(0)
    pacOutput.write(outputStream.read())  

#run main loop
for sourceFile in os.listdir("source/"):
    
    if sourceFile.endswith(".PAC"):#$DEBUG
        tree = ET.parse('xml/' + sourceFile + ".xml")
        root = tree.getroot()
    
        packPac(root, 'gen/')

        print(root.get('fileName'))
