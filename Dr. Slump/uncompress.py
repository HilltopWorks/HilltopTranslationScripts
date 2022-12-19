#########################################################################
# Uncompresses LSZZ stored data in PS1 game "Dr. Slump"                 #
#########################################################################

import sys    
import os


# Takes a lzss compressed fragment of a file at a certain offset into it
# and creates a decompressed version in the genClean folder
def uncompressChunk(fileName, offsetArg, outputName, isroot, inputFolder, outputFolder):
    
    #look for the file in source if it is a source file
    if isroot:
        inputFile = open(inputFolder + fileName, "rb")
    else:
        inputFile = open(outputFolder + fileName, "rb")

    if os.path.exists(outputFolder + outputName + ".uncomp"):
        os.remove(outputFolder + outputName + ".uncomp")

    output = open(outputFolder + outputName + ".uncomp", "w+b")
    
    #clear data to start point
    offset = offsetArg
    inputFile.read(offset+1)

    #read filesize word
    fileSize = int.from_bytes(inputFile.read(4), "little", signed=False)

    #loop until no bytes remaining
    bytesLeft = fileSize
    while bytesLeft > 0:
        
        #control block determines writing of reference(1) or raw byte(0)
        controlBlock = int.from_bytes(inputFile.read(2), "little", signed=False)
        controlBlockCursor = 1

        #iterate over 16 bit long control block
        while controlBlockCursor <= 32768 and bytesLeft > 0:
            if (controlBlock & controlBlockCursor) == 0:
                #write 1 raw byte
                output.write(inputFile.read(1))
                bytesLeft -= 1
                
            else:
                #write from reference block
                referenceBlock = inputFile.read(2)
                #Offset = first 3 bits of byte 1 on byte 2
                offsetNibble1 = int.from_bytes(referenceBlock[0:1], "little", signed=False)

                offsetNibble2 = (int.from_bytes(referenceBlock[1:2], "little", signed=False) & 7) << 8
                seekOffset = offsetNibble1 + offsetNibble2 + 1

                #Number of bytes left to copy = last 5 bits of byte 1 + 3
                copyBytes = (int.from_bytes(referenceBlock[1:2], "little", signed=False) >> 3) + 3
                
                #copy all bytes
                while copyBytes > 0 and bytesLeft > 0:
                    output.seek(-seekOffset, 2)
                    writeByte = output.read(1)
                    output.seek(0,2)
                    output.write(writeByte)
                    copyBytes -= 1
                    bytesLeft -= 1

            #Check for next control bit in next interation
            controlBlockCursor *= 2


    #cleanup    
    inputFile.close()
    output.close()


#debug

