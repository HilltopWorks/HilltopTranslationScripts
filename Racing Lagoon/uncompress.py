#########################################################################
# Uncompresses LZSS stored data in PS1 game "Racing Lagoon"             #
#########################################################################

import sys    
import os

HEADER_LENGTH        = 6
HEADER_LENGTH_TYPE_2 = 2
LZSS_IDENTIFIER    = 0x7301
LENGTH_MASK        = 0b01111000
OFFSET_MASK_1      = 0b00000111
REFERENCE_MASK     = 0b10000000
REPEATER_ID        = 0x7E
DOUBLE_REPEATER_ID = 0x7F



def toInt(bytes):
    return int.from_bytes(bytes, "little", signed=False)

# Takes a lzss compressed fragment of a file and uncompresses it
def uncompressData(inputData):

    #LZSS Identifier
    assert toInt(inputData[4:6]) == LZSS_IDENTIFIER

    #First 4 bytes are the uncompressed file length 
    uncompressedSize = toInt(inputData[0:4])

    bytesWritten = 0
    buffer = b''
    cursor = HEADER_LENGTH

    #Loop until size reached
    while bytesWritten < uncompressedSize and len(inputData) > cursor:
        #Last bit determines if reference or literals block

        #Decodes repetition of a single byte with 1 byte length
        if inputData[cursor] == REPEATER_ID:
            count = inputData[cursor + 1] + 4
            payload = inputData[cursor + 2]

            for x in range(count):
                buffer += bytes([payload])
                

            bytesWritten += count
            cursor += 3
        
        #Decodes repetition of a single byte with 2 byte length
        elif inputData[cursor] == DOUBLE_REPEATER_ID:
            count = toInt(inputData[cursor + 1:cursor + 3])
            payload = inputData[cursor + 3]

            for x in range(count):
                buffer += bytes([payload])
                

            bytesWritten += count
            cursor += 4

        #Decodes a block of literals
        elif not inputData[cursor] & REFERENCE_MASK:
            controlByte = inputData[cursor]

            assert controlByte != 0

            
            buffer += inputData[cursor + 1:cursor + controlByte + 1]
            
            cursor += controlByte + 1
            bytesWritten += controlByte


        #Decodes a reference with 4 bit length and 11 bit offset
        else:
            referenceLength = ((inputData[cursor] & LENGTH_MASK) >> 3) + 3
            bytesToWrite = referenceLength
            offsetNibble1 = inputData[cursor] & OFFSET_MASK_1
            offsetNibble2 = inputData[cursor + 1]
            offset = (offsetNibble1 << 8) + offsetNibble2 + 1

            #Window is initialized to 0's allowing pre-output offsets
            while offset > bytesWritten and bytesToWrite > 0:
                buffer += bytes(1)
               
                offset -= 1
                bytesToWrite -= 1

            while bytesToWrite > 0:
                buffer += bytes([buffer[bytesWritten - offset]])
                
                offset -= 1
                bytesToWrite -= 1 



            cursor += 2
            bytesWritten += referenceLength

        
    return buffer


# Takes a lzss compressed fragment of a file without a filesize and uncompresses it
def uncompressDataType2(inputData):

    #LZSS Identifier
    if toInt(inputData[0:2]) != LZSS_IDENTIFIER:
        raise Exception


    bytesWritten = 0
    buffer = b''
    cursor = HEADER_LENGTH_TYPE_2

    
    #Loop until size reached
    while len(inputData) > cursor:
        
        #Last bit determines if reference or literals block

        #Decodes repetition of a single byte with 1 byte length
        if inputData[cursor] == REPEATER_ID:
            count = inputData[cursor + 1] + 4
            payload = inputData[cursor + 2]

            for x in range(count):
                buffer += bytes([payload])
                

            bytesWritten += count
            cursor += 3
        
        #Decodes repetition of a single byte with 2 byte length
        elif inputData[cursor] == DOUBLE_REPEATER_ID:
            count = toInt(inputData[cursor + 1:cursor + 3])
            payload = inputData[cursor + 3]

            for x in range(count):
                buffer += bytes([payload])
                

            bytesWritten += count
            cursor += 4

        #Decodes a block of literals
        elif not inputData[cursor] & REFERENCE_MASK:
            controlByte = inputData[cursor]

            if controlByte == 0:
                break

            
            buffer += inputData[cursor + 1:cursor + controlByte + 1]
            
            cursor += controlByte + 1
            bytesWritten += controlByte


        #Decodes a reference with 4 bit length and 11 bit offset
        else:
            referenceLength = ((inputData[cursor] & LENGTH_MASK) >> 3) + 3
            bytesToWrite = referenceLength
            offsetNibble1 = inputData[cursor] & OFFSET_MASK_1
            offsetNibble2 = inputData[cursor + 1]
            offset = (offsetNibble1 << 8) + offsetNibble2 + 1

            #Window is initialized to 0's allowing pre-output offsets
            while offset > bytesWritten and bytesToWrite > 0:
                buffer += bytes(1)
               
                offset -= 1
                bytesToWrite -= 1

            while bytesToWrite > 0:
                buffer += bytes([buffer[bytesWritten - offset]])
                
                offset -= 1
                bytesToWrite -= 1 



            cursor += 2
            bytesWritten += referenceLength

        
    return buffer, cursor

#DEBUG
#file = open("LZSSTestOut.bin", "rb")
#out = open("LZSSOUTTestOutUnzipped.bin", "wb")

#out.write(uncompressData(file.read()))

#out.close()
#file.close()