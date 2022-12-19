#########################################################################
# Uncompresses LSZZ stored data in PS1 game "Aconcagua"                 #
#########################################################################

#from io import BufferedRWPair
#import sys    
import os
import re
#import math
import datetime
import difflib

#PSX compression
LEN_CONTROL_BLOCK = 8
UPPER_BYTE_MASK = 0b11110000
LOWER_BYTE_MASK = 0b00001111

MAX_REF_SIZE = 18
MIN_REF_SIZE = 3
MAX_REF_DIST = 4096

#Subtitle compression

LOWER_PIXEL_MASK = 0b00001111
UPPER_PIXEL_MASK = 0b11110000
MAX_SEQ_LENGTH = 0b111111111111

LENGTH_SEQ_MASK = 0b0111
EXTEND_BIT_MASK = 0b1000

#logFile = open('logs/compress.log', 'w')


#Find longest hex string match
def __longestSubstringFinder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(0,len1,2):
        for j in range(0,len2,2):
            lcs_temp=0
            match=''
            while ((i+lcs_temp < len1) and (j+lcs_temp<len2) and string1[i+lcs_temp] == string2[j+lcs_temp]):
                match += string2[j+lcs_temp]
                lcs_temp+=1
            if (len(match) > len(answer)):
                answer = match

    if len(answer)%2 == 1:
        answer = answer[:len(answer)-1]

    return answer

def findall(needle, haystack):
    i = 0
    try:
        while True:
            i = haystack.index(needle, i)
            yield i
            i += 1

    except ValueError:
        pass


def __findMatch(toMatch, window):
    searchField = window+window

    longestMatch = ''
    longestMatchDist = -1
    for x in range(0,len(window),2):
        match = __common_start(toMatch,searchField[x: min(x + len(toMatch), len(searchField))])
        if len(match) > len(longestMatch):
            longestMatch = match
            longestMatchDist = len(window) - x
    
    if len(longestMatch)%2 == 1:
        longestMatch = longestMatch[:len(longestMatch) - 1]
        longestMatchDist = longestMatchDist

    return longestMatch, longestMatchDist

def __findMatch2(toMatch, window):
    searchField = window+window

    s = difflib.SequenceMatcher(None,toMatch, searchField)
    matches = s.get_matching_blocks()
    
    longestMatch = -1
    matchPos = 0
    for foundMatch in matches:

        if foundMatch[0] != 0 or foundMatch[2]%2 ==1:
            continue
        elif foundMatch[2] > longestMatch:
            longestMatch = foundMatch[2]
            matchPos = foundMatch[1]

    longestMatchDist = len(window) - matchPos
    
    
    longestMatch = toMatch[0:matchPos]
    
    if len(longestMatch)%2 == 1:
        longestMatch = longestMatch[:len(longestMatch) - 1]
        #longestMatchDist = longestMatchDist

    return longestMatch, longestMatchDist

def findMatch(toMatch, window):
    if len(window) < MAX_REF_DIST*2:
        searchField = window
    else:
        searchField = window+window

    longestMatch = ''
    longestMatchDist = -1

    for copyLength in range(len(toMatch), (MIN_REF_SIZE*2) - 1, -2):
        #matchResult = searchField.find(toMatch[0:copyLength])
        matchResult = -1
        #results = [_.start() for _ in re.finditer(toMatch[0:copyLength],searchField)]
        results = findall(toMatch[0:copyLength],searchField)
        for result in results:
            if result %2 ==0:
                matchResult = result
                break
        #assert matchResult< len(window)
        if matchResult != -1:
            longestMatch = toMatch[0:copyLength]
            longestMatchDist = len(window) - matchResult
            break
        
    
    if len(longestMatch)%2 == 1:
        longestMatch = longestMatch[:len(longestMatch) - 1]
        #longestMatchDist = longestMatchDist

    return longestMatch, longestMatchDist


def __common_start(sa, sb):
    """ returns the longest common substring from the beginning of sa and sb """
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return

    return ''.join(_iter())

def compress(targetFile):
    inputFile = open(targetFile, "rb")


    buffer = b''

    bytesRead    = 0
    bytesWritten = 0

    bytesToCompress = os.path.getsize(targetFile)


    uncompressedData = inputFile.read()
    uncompressedSize = len(uncompressedData)
    goalPercent = 0

    while bytesRead < uncompressedSize:
        if (bytesRead /uncompressedSize)*100 >= goalPercent:
            print(datetime.datetime.now().strftime("%H:%M:%S ") + targetFile + " is " +str(goalPercent) + " percent complete")
            goalPercent += 20
        
        controlBlock = 0b00000000

        sideBuffer = b''
        for controlIndex in range(LEN_CONTROL_BLOCK):
            
            blockToMatch = uncompressedData[bytesRead: min(bytesRead + MAX_REF_SIZE, uncompressedSize)]

            #matchd , matchDistd= __findMatch(blockToMatch.hex(), uncompressedData[max(bytesRead - MAX_REF_DIST,0):bytesRead].hex())

            match , matchDist= findMatch(blockToMatch.hex(), uncompressedData[max(bytesRead - MAX_REF_DIST,0):bytesRead].hex())

            #if len(matchd) >= 6:
            #    assert match == matchd

            match = bytes.fromhex(match)
            if len(match) >= 3:
                controlBlock = controlBlock | (2**controlIndex)
                reference = 0x00

                distanceCoded = 0xFFF - (matchDist>>1) + 1
                byte1 = distanceCoded & 0xFF
                byte2_nibble1 = (distanceCoded & 0xF00) >> 8
                byte2_nibble2 = (len(match)-3)<<4

                sideBuffer += byte1.to_bytes(1,byteorder='little')
                sideBuffer += (byte2_nibble1 | byte2_nibble2).to_bytes(1,byteorder='little')


                bytesRead += len(match)
            elif uncompressedSize > bytesRead:
                sideBuffer += uncompressedData[bytesRead].to_bytes(1,byteorder='little')
                bytesRead +=1

        buffer += controlBlock.to_bytes(1,byteorder='little')
        buffer += sideBuffer
    return buffer

def __getNextPixel(data, pixelsRead):
    byteNumber =  pixelsRead // 2
    bitOffset =  (pixelsRead %  2) * 4
    char = data[byteNumber]    
    nextPixel = (char & (LOWER_PIXEL_MASK << bitOffset))>>bitOffset


    return nextPixel

def __encodeSequence(pixel, count):
    extendsNeeded = ((count.bit_length() - 1) // 3)

    buffer = pixel << 4
    buffer = buffer | (count & LENGTH_SEQ_MASK)
    bitsWritten = 6
    #if extendsNeeded > 0:
    #    buffer = buffer | 0b1000

    for x in range(extendsNeeded):
        buffer = buffer << 4
        bitsToShift = 3*(x+1)
        buffer |= (count >> bitsToShift) & LENGTH_SEQ_MASK
        buffer |= EXTEND_BIT_MASK
        bitsWritten += 4

    #logFile.write("Encoding: " + str(pixel) + " " + str(count) + " times\n")
    #logFile.write("      as: " + bin(buffer) + " of len " + str(bitsWritten)  + "\n")
    return buffer, bitsWritten

def compressSubtitle(data):
    buffer = []
    pixelsRead = 0
    bitsWritten = 0
    while (pixelsRead//2) < len(data):
        nextPixel    =  __getNextPixel(data, pixelsRead)
        pixelsRead   += 1
        currentPixel =  nextPixel
        repeatCount  =  1

        while (pixelsRead//2) < len(data) and __getNextPixel(data, pixelsRead) == currentPixel and repeatCount < MAX_SEQ_LENGTH:
            repeatCount += 1
            pixelsRead  += 1

        tempBuffer = 0

        nextEncoding, encodingLength = __encodeSequence(currentPixel, repeatCount)

        buffer += [[nextEncoding, encodingLength]]

    charBuffer = [0]
    bitsAdded  = 0

    for encoding in buffer:
        nextEncoding       = encoding[0]
        nextEncodingLength = encoding[1]
        bitOffset          = bitsAdded % 8
        bitsToAddByte1     = min((8 - bitOffset), nextEncodingLength)
        bitsToAddByte2     = min(nextEncodingLength - bitsToAddByte1, 8)
        bitsToAddByte3     = nextEncodingLength - (bitsToAddByte1 + bitsToAddByte2)
        
        while bitsAdded//8 >= len(charBuffer):
            charBuffer += [0]
        
        charBuffer[bitsAdded//8] |=  ((nextEncoding & ((2**bitsToAddByte1)-1)) << bitOffset)

        if bitsToAddByte2 > 0:
            charBuffer += bytes([   (nextEncoding >> bitsToAddByte1) & 0xFF   ]) 

        if bitsToAddByte3 > 0:
            charBuffer += bytes([   (nextEncoding >> (bitsToAddByte1 + bitsToAddByte2))   ]) 

        bitsAdded += nextEncodingLength

    outputData = bytearray()

    for char in charBuffer:
        outputData.append(char)

    return outputData


#__findMatch3(mat, hex)

#print(findMatch("apple pie available", "apple pies"))
#print(longestSubstringFinder("apples", "appleses"))
#print(longestSubstringFinder("bap pales", "cappl eses"))

#testFile = open("testComp.bin", 'wb')
#testFile.write(compress('EXTRACT-ORIGINAL\PSX.03655680.bodyUncompressed'))
#testFile.close()
#outputFile = open("EngLine1.bin", 'wb')
#outputFile.write(compressSubtitle(open("Subtitles/EngLine1.png.bin", 'rb').read()))


