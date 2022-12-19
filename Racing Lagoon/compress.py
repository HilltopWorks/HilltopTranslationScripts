#########################################################################
# Compresses LZSS data for PS1 game "Racing Lagoon" into bytes format   #
#########################################################################

# Racing Lagoon uses references with 11-bit offsets and 4-bit lengths,
# corresponding to a 2048-byte window, and reference lengths in the range
# 3..18 bytes. With a 1 bit identifier for references.

import sys    
import os
from pathlib import Path

WSIZE = 0b100000000000   # window size

MAX_REF_LEN        = 18  # maximum copy length
MIN_REF_LEN        = 3   # minimum copy length

REPEATER_ID        = 0x7E
DOUBLE_REPEATER_ID = 0x7F

LENGTH_MASK               = 0b01111000
OFFSET_MASK_1             = 0b00000111
REFERENCE_MASK_DOUBLE     = 0b1000000000000000


#Compresses the given file and returns a bytes string of the compressed file
def compressChunk(inputData):
 
  writeBuffer = b''

  #write header -  [4 BYTE LITTLE ENDIAN UNCOMPRESSED FILESIZE] 
  #                [0x0173]  
  fileSize = len(inputData)
 
  writeBuffer += bytes([ fileSize &       0xFF])
  writeBuffer += bytes([(fileSize &     0xFF00)>>8])
  writeBuffer += bytes([(fileSize &   0xFF0000)>>16])
  writeBuffer += bytes([(fileSize & 0xFF000000)>>24])
  writeBuffer += b'\x01\x73'

  #write compressed blocks until file size reached
  
  bytesWritten = 0
  windowLeft = 0
  windowRight = 0

  inLiteralBlock = False
  literalBlockSize = 0

  while bytesWritten < fileSize:
    referenceFound = False
    
    #######Test for reference
    #check all valid upcoming string lengths for matches in our dictionary window
    if referenceFound == False:
      for copyLength in range(MAX_REF_LEN, MIN_REF_LEN - 1, -1):
        
        #Check if search window extends past EOF
        if bytesWritten + copyLength >= fileSize:
          continue
        else:
          windowRight = bytesWritten + copyLength

        searchString = inputData[bytesWritten:windowRight]

        #Search valid window for result
        searchResult = inputData.find(searchString, windowLeft, windowRight - 1)
        if searchResult != -1:
          
          #Truncate and append literal block chain, if exists
          if inLiteralBlock == True:
            writeBuffer += bytes([literalBlockSize])
            writeBuffer += inputData[bytesWritten - literalBlockSize: bytesWritten]
            
            inLiteralBlock = False
            literalBlockSize = 0


          #create reference block with pattern 0b1YYYYZZZZZZZZZZZ (Y is length-3, Z is reference offset-1)
          lengthNibble = (copyLength-3) << 11
          offsetNibble = bytesWritten - searchResult - 1
          
          referenceBlock = REFERENCE_MASK_DOUBLE | lengthNibble | offsetNibble

          writeBuffer +=  bytes([(referenceBlock & 0xFF00)>>8]) + bytes([referenceBlock & 0xFF])
          referenceFound = True

          #
          bytesWritten += copyLength
          
          break
  
    #######Test for repeated chars of length
    if referenceFound == False:

      #If at least next 4 bytes are identical, write repeater block
      if bytesWritten + 4 < fileSize and inputData[bytesWritten] == inputData[bytesWritten+1] == inputData[bytesWritten + 2] == inputData[bytesWritten+3]:
        #Truncate and append literal block chain, if exists
        if inLiteralBlock == True:
          writeBuffer += bytes([literalBlockSize])
          writeBuffer += inputData[bytesWritten - literalBlockSize: bytesWritten]
          
          inLiteralBlock = False
          literalBlockSize = 0

        count = 4

        while len(inputData) > (bytesWritten + count) and inputData[bytesWritten + count] == inputData[bytesWritten + count - 1]:
          count+=1

        #Max length = 0xFFFF
        count = count % 0xFFFF
        
        #Double repeater block used if count is greater than 0xFF+0x04  
        if count <=0x103:
          writeBuffer += bytes([REPEATER_ID])
          writeBuffer += bytes([count-4])
        else:
          writeBuffer += bytes([DOUBLE_REPEATER_ID])
          writeBuffer += count.to_bytes(2, byteorder="little")
        
        writeBuffer += bytes([inputData[bytesWritten]])

        referenceFound = True
        bytesWritten += count

        
      
    #######write literal block
    if referenceFound == False:
      
      literalBlockSize += 1
      bytesWritten +=1
      inLiteralBlock = True

      #If max literal block size reached, truncate and write block
      if literalBlockSize == REPEATER_ID - 1:
        writeBuffer += bytes([literalBlockSize])
        writeBuffer += inputData[bytesWritten - literalBlockSize: bytesWritten]
        
        inLiteralBlock = False
        literalBlockSize = 0
  

    #update window
    if bytesWritten > WSIZE:
      windowLeft = bytesWritten - WSIZE

  #Truncate and append literal block chain, if exists
  if inLiteralBlock == True:
    writeBuffer += bytes([literalBlockSize])
    writeBuffer += inputData[bytesWritten - literalBlockSize: bytesWritten]

  return writeBuffer



#inputfile = open("LZSSOUTRight.bin", "rb")

#data = compressChunk(inputfile.read())

#outputFile = open("LZSSTestOut.bin", "wb")

#outputFile.write(data)

#outputFile.close()
#inputfile.close()