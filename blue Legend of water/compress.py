#Compress and decompress TIM files in BLUE
from fileinput import filename
import TIMresource
from pathlib import Path
import os
import datetime

LEN_CONTROL_BLOCK = 8
UPPER_BYTE_MASK = 0b11110000
LOWER_BYTE_MASK = 0b00001111

MAX_REF_SIZE = 17
MIN_REF_SIZE = 2
OFFSET_ARRAY_LENGTH = 16 #number of entries in reference distance array
OFFSET_INVALID = 0
#MAX_REF_DIST = 4096

IMAGE_FOLDER = "IMAGE"
FILE_FOLDER  = "EXTRACT"

FILE_ASSOCIATIONS = [ ["END.DTI", "MOVIE/END.DTI"], ["END2.DTI", "MOVIE/END2.DTI"], ["TITLE.DTI", "MOVIE/TITLE.DTI"], ["INIT1.DTI", "INIT1.DTI"]]
RAW_ASSOCIATIONS  = [ ["HP", "BASE/HP.DAT"], ["BASEMAP", "BASE/BASEMAP.DAT"]]

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

def __common_start(sa, sb):
    """ returns the longest common substring from the beginning of sa and sb """
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return

    return ''.join(_iter())

def getSearchFields(window, TIM, cursor):

    offsets = []
    TIMwidth = TIM.W
    PXL_offset = TIM.CLUT.bnum + 20
    offsets += [-2, -4, -6, -8]
    offsets += [TIMwidth*-4  + 4, TIMwidth*-4  + 2, TIMwidth*-4 + 0, TIMwidth*-4 - 2, TIMwidth*-4 - 4, TIMwidth*-4 - 6]
    offsets += [TIMwidth*-8  + 2, TIMwidth*-8  + 0, TIMwidth*-8 - 2, TIMwidth*-8 - 4]
    offsets += [TIMwidth*-12 + 0, TIMwidth*-12 - 2]
    
    searchFields = []

    for offset in offsets:
        if cursor + offset + PXL_offset <= 0:
            searchFields += [OFFSET_INVALID]
        else:
            searchFields += [window[ PXL_offset*2 + cursor * 2 + offset:min(PXL_offset*2 + cursor * 2 + offset + MAX_REF_SIZE * 2, len(window))]]

    return searchFields

def findMatch(toMatch, window, TIM, cursor):

    searchFields = getSearchFields(window, TIM, cursor)

    overallLongestMatch = ''
    overallBestIndex = -1
    
    for x in range(OFFSET_ARRAY_LENGTH):
        if searchFields[x] == OFFSET_INVALID:
            continue

        result = os.path.commonprefix([toMatch,searchFields[x]])
        
        if len(result) > len(overallLongestMatch):
            overallLongestMatch = result
            overallBestIndex = x

    if len(overallLongestMatch)%2 == 1:
        overallLongestMatch = overallLongestMatch[:len(overallLongestMatch) - 1]

    return overallLongestMatch, overallBestIndex

def compressTIM(targetFile):
    inputFile = open(targetFile, "rb")
    inputTIM = TIMresource.TIM(inputFile)

    buffer = b''

    bytesRead    = 0
    bytesWritten = 0

    bytesToCompress = os.path.getsize(targetFile)

    PXL_offset = inputTIM.CLUT.bnum + 20
    inputFile.seek(0)
    uncompressedData = inputFile.read()
    uncompressedSize = len(uncompressedData) - PXL_offset
    goalPercent = 0

    while bytesRead < uncompressedSize:
        if (bytesRead /uncompressedSize)*100 >= goalPercent:
            print(datetime.datetime.now().strftime("%H:%M:%S ") + targetFile + " is " +str(goalPercent) + " percent complete")
            goalPercent += 20
        
        controlBlock = 0b00000000

        sideBuffer = b''
        for controlIndex in range(LEN_CONTROL_BLOCK):
            
            blockToMatch = uncompressedData[PXL_offset + bytesRead: min(PXL_offset + bytesRead + MAX_REF_SIZE, PXL_offset + uncompressedSize)]

            #matchd , matchDistd= __findMatch(blockToMatch.hex(), uncompressedData[max(bytesRead - MAX_REF_DIST,0):bytesRead].hex())

            #match , match_index = findMatch(blockToMatch.hex(), uncompressedData[max(bytesRead - (inputTIM.W * 6 + 1),0):min(bytesRead + MAX_REF_SIZE,len(uncompressedData))].hex(), inputTIM.W)
            match , match_index = findMatch(blockToMatch.hex(), uncompressedData.hex(), inputTIM, bytesRead)

            #if len(matchd) >= 6:
            #    assert match == matchd

            match = bytes.fromhex(match)
            if len(match) >= 2:
                controlBlock = controlBlock | (2**controlIndex)
                reference = 0x00

                distanceCoded = match_index
                sizeCoded = (len(match)-2)<<4
                #byte1 = distanceCoded & 0xFF
                #byte2_nibble1 = (distanceCoded & 0xF00) >> 8
                #byte2_nibble2 = (len(match)-3)<<4

                sideBuffer += (distanceCoded | sizeCoded).to_bytes(1,byteorder='little')
                #sideBuffer += (byte2_nibble1 | byte2_nibble2).to_bytes(1,byteorder='little')


                bytesRead += len(match)
            elif uncompressedSize > bytesRead:
                sideBuffer += uncompressedData[PXL_offset + bytesRead].to_bytes(1,byteorder='little')
                bytesRead +=1
            else:
                break

        buffer += controlBlock.to_bytes(1,byteorder='little')
        buffer += sideBuffer
    print(datetime.datetime.now().strftime("%H:%M:%S ") + targetFile + " is 100 percent complete")
    
    inputFile.seek(0)
    header = inputFile.read(PXL_offset)
    print("Filesize: " + str(len(header) + len(buffer)))
    return header + buffer + bytes(2)

def uncompressTIM(TIMfile):
    '''Takes a file open to the start of a compressed TIM and returns the uncompressed TIM'''
    '''
          [CONTROL BYTE]                        [REFERENCE BYTE] 
                |                                      |
    1 for ref byte, 0 for literal Byte        Size = Top 4 bits + 2
                                          Distance = OFFSETS[bottom 4 bits]

           [OFFSETS]: Int array of length 16 and values:
                      [-1,-2,-3,-4] +
                      [width*-2 + 2, width*-2 + 1, width*-2 + 0, width*-2 - 1, width*-2 - 2, width*-2 - 3] +
                      [width*-4 + 1, width*-4 + 0, width*-4 - 1, width*-4 - 2] +
                      [width*-6 + 0, width*-6 - 1]

    '''
    TIM_obj = TIMresource.TIM(TIMfile)
    TIM_bin = TIM_obj.to_bin()
    PXL_start = TIM_obj.get_PXL_start()
    width = TIM_obj.W
    height = TIM_obj.H

    end_size = width*height*2

    bytes_written = 0
    PXL_cursor = 0

    output_buffer = b''


    offsets = []

    #Temporal reference compression
    offsets += [-1,-2,-3,-4]
    offsets += [width*-2 + 2, width*-2 + 1, width*-2 + 0, width*-2 - 1, width*-2 - 2, width*-2 - 3]
    offsets += [width*-4 + 1, width*-4 + 0, width*-4 - 1, width*-4 - 2]
    offsets += [width*-6 + 0, width*-6 - 1]

    while bytes_written < end_size:
        control_byte = TIM_bin[PXL_start + PXL_cursor] #TIM_obj.PXLData[PXL_cursor]
        control_cursor = 1
        PXL_cursor += 1

        while control_cursor < 2**8 and bytes_written < end_size:
            if control_cursor & control_byte != 0:
                #write reference
                referenceByte =  TIM_bin[PXL_start + PXL_cursor]
                reference_size = (referenceByte >> 4) + 2
                reference_offset_index = referenceByte & 0b00001111
                offset = offsets[reference_offset_index]

                for b in range(reference_size):
                    output_buffer +=  output_buffer[offset].to_bytes(1, 'little')
                
                bytes_written += reference_size

            else:
                #write 1 literal byte
                output_buffer += TIM_bin[PXL_start + PXL_cursor].to_bytes(1,'little')
                bytes_written += 1
            
            PXL_cursor += 1
            control_cursor <<= 1


    return TIM_bin[0:PXL_start] + output_buffer

def unpackDTI(DTI_path):
    '''Unpacks all TIMs from a DTI package and extracts a PNG from each.'''
    if not os.path.exists("IMAGE/" + os.path.basename(DTI_path) + '/'):
        os.mkdir("IMAGE/" + os.path.basename(DTI_path) + '/')
    
    DTI_file = open(DTI_path, 'rb')

    num_entries = TIMresource.readInt(DTI_file)
    
    offsets = []

    for entry_number in range(num_entries):
        offsets += [TIMresource.readInt(DTI_file)]

    for offset in offsets:
        DTI_file.seek(offset)
        TIM_data = uncompressTIM(DTI_file)
        TIM_path = "IMAGE/" + os.path.basename(DTI_path) +'/'+ hex(offset) + '.TIM'
        PNG_path = "IMAGE/" + os.path.basename(DTI_path) +'/'+ hex(offset) + '.PNG'
        writer = open(TIM_path, 'wb')
        writer.write(TIM_data)
        writer.close()
        uncompressed_data = open(TIM_path, 'rb')
        #uncompressed_data.seek(0x10000 * imageNumber)
        TIM_obj = TIMresource.TIM(uncompressed_data)
        
        
        image = TIMresource.generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
        image.save(PNG_path)
    return

def unpackINIT1():
    unpackDTI("EXTRACT - Original/INIT1.DTI")

    DAT_path = "EXTRACT - Original/INIT1.DTI"
    offsets = [0x2484, 0x2618, 0x2790, 0x2970, 0x2Ca0, 0x2E4c, 0x3054, 0x3234, 0x33F4, 0x35e8, 0x3754, 0x38dc, 0x3a68, 0x3be0, 0x3cc4, 0x3db4, 0x3f70, 0x5d78, 0x6c34, 0x6dbc, 0x8690,
               0x9050, 0x9a2c, 0xa54c, 0xb050, 0xba94, 0xc5f0, 0xd140, 0xdc10, 0xe3e0, 0xebb0, 0xf468, 0xffb4]
    dat_file = open(DAT_path, 'rb')
    for offset  in offsets:
        dat_file.seek(offset)
        TIM_data = uncompressTIM(dat_file)
        writer = open("IMAGE/INIT1.DTI/" + hex(offset)+ '.TIM', 'wb')
        writer.write(TIM_data)
        writer.close()
        uncompressed_data = open("IMAGE/INIT1.DTI/" + hex(offset) + '.TIM', 'rb')
        #uncompressed_data.seek(0x10000 * imageNumber)
        TIM_obj = TIMresource.TIM(uncompressed_data)
        
        
        image = TIMresource.generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
        image.save("IMAGE/INIT1.DTI/" + hex(offset) + '.PNG')



    return

def unpackHP():
    numEntries = 47
    DAT_path = "EXTRACT/BASE/HP.DAT"

    dat_file = open(DAT_path, 'rb')

    for imageNumber in range(numEntries):
        dat_file.seek(0x10000 * imageNumber)
        TIM_data = uncompressTIM(dat_file)
        writer = open("IMAGE/HP/" + str(imageNumber) + '.TIM', 'wb')
        writer.write(TIM_data)
        writer.close()
        uncompressed_data = open("IMAGE/HP/" + str(imageNumber) + '.TIM', 'rb')
        #uncompressed_data.seek(0x10000 * imageNumber)
        TIM_obj = TIMresource.TIM(uncompressed_data)
        
        
        image = TIMresource.generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
        image.save("IMAGE/HP/" + str(imageNumber) + '.PNG')
    return

def unpackBASEMAP():
    numEntries = 131
    DAT_path = "EXTRACT/BASE/BASEMAP.DAT"
    dat_file = open(DAT_path, 'rb')
    for imageNumber in range(numEntries):
        dat_file.seek(imageNumber*0x10000 + 0x26ac)
        TIM_data = uncompressTIM(dat_file)
        writer = open("IMAGE/BASEMAP/" + str(imageNumber)+ "_" + str(imageNumber*0x10000 + 0x26ac) +  '.TIM', 'wb')
        writer.write(TIM_data)
        writer.close()
        uncompressed_data = open("IMAGE/BASEMAP/" + str(imageNumber) + '.TIM', 'rb')
        #uncompressed_data.seek(0x10000 * imageNumber)
        TIM_obj = TIMresource.TIM(uncompressed_data)
        
        
        image = TIMresource.generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
        image.save("IMAGE/BASEMAP/" + str(imageNumber) + '.PNG')


def unpackTITLE():
    DAT_path = "EXTRACT/MOVIE/TITLE.DTI"
    offsets = [0x200, 0x1238, 0x6790, 0xB8AC, 0xBe0c, 0x1586c, 0x20f78, 0x2323c, 0x23460]
    dat_file = open(DAT_path, 'rb')
    for offset  in offsets:
        dat_file.seek(offset)
        TIM_data = uncompressTIM(dat_file)
        writer = open("IMAGE/TITLE/" + hex(offset)+ '.TIM', 'wb')
        writer.write(TIM_data)
        writer.close()
        uncompressed_data = open("IMAGE/TITLE/" + hex(offset) + '.TIM', 'rb')
        #uncompressed_data.seek(0x10000 * imageNumber)
        TIM_obj = TIMresource.TIM(uncompressed_data)
        
        
        image = TIMresource.generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
        image.save("IMAGE/TITLE/" + hex(offset) + '.PNG')

def unpackEND():
    DAT_path = "EXTRACT/MOVIE/END.DTI"
    offsets = [0x200, 0x79f8, 0xe024, 0x14b34, 0x19c54, 0x1f7d0, 0x24924, 0x2A34c]
    dat_file = open(DAT_path, 'rb')
    count = 0
    for offset  in offsets:
        dat_file.seek(offset)
        TIM_data = uncompressTIM(dat_file)
        writer = open("IMAGE/END/" + str(count) + '.TIM', 'wb')
        writer.write(TIM_data)
        writer.close()
        uncompressed_data = open("IMAGE/END/" + str(count) + '.TIM', 'rb')
        #uncompressed_data.seek(0x10000 * imageNumber)
        TIM_obj = TIMresource.TIM(uncompressed_data)
        
        
        image = TIMresource.generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
        image.save("IMAGE/END/END" + hex(offset) + '.PNG')
        count += 1

    DAT_path = "EXTRACT/MOVIE/END2.DTI"
    offsets = [0x200, 0x21b4, 0x412c, 0x5984, 0x728c, 0x8f38, 0xc524, 0xe22c, 0xfdB8]
    dat_file = open(DAT_path, 'rb')
    for offset  in offsets:
        dat_file.seek(offset)
        TIM_data = uncompressTIM(dat_file)
        writer = open("IMAGE/END/END2-" + hex(offset)+ '.TIM', 'wb')
        writer.write(TIM_data)
        writer.close()
        uncompressed_data = open("IMAGE/END/END2-" + hex(offset) + '.TIM', 'rb')
        #uncompressed_data.seek(0x10000 * imageNumber)
        TIM_obj = TIMresource.TIM(uncompressed_data)
        
        
        image = TIMresource.generatePNG(TIM_obj.PXLData, TIM_obj.CLUT.palette, TIM_obj.W, TIM_obj.H, 0, TIM_obj.PMD)
        image.save("IMAGE/END/END2-" + hex(offset) + '.PNG')

def repack(file_association):
    image_path = os.path.join(IMAGE_FOLDER, file_association[0])
    file_path = os.path.join(FILE_FOLDER, file_association[1])

    target_file = open(file_path, "r+b")

    for file_name in os.listdir(image_path):
        if file_name.endswith(".PNG"):
            TIM_path = file_name.replace(".PNG", ".TIM")
            TIM_bin = TIMresource.PNG_to_TIM(os.path.join(image_path, TIM_path), os.path.join(image_path, file_name))
            modified_file_path = os.path.join(image_path, TIM_path + "-modified")
            modified_TIM_file = open(modified_file_path, 'wb')
            modified_TIM_file.write(TIM_bin)
            modified_TIM_file.close()
            compressed_TIM = compressTIM(modified_file_path)

            TIM_location = int(file_name.replace(".PNG", ''), base=16)
            
            target_file.seek(TIM_location)

            target_file.write(compressed_TIM)

    return

def repackRaw(file_association):
    image_path = os.path.join(IMAGE_FOLDER, file_association[0])
    file_path = os.path.join(FILE_FOLDER, file_association[1])

    dat_file = open(file_path, 'r+b')

    for file_name in os.listdir(image_path):
        if file_name.endswith(".PNG"):
            TIM_path = file_name.replace(".PNG", ".TIM")
            TIM_bin = TIMresource.PNG_to_TIM(os.path.join(image_path, TIM_path), os.path.join(image_path, file_name))
            modified_file_path = os.path.join(image_path, TIM_path + "-modified")
            modified_TIM_file = open(modified_file_path, 'wb')
            modified_TIM_file.write(TIM_bin)
            modified_TIM_file.close()
            compressed_TIM = compressTIM(modified_file_path)

            file_number = int(file_name.replace(".PNG", ''))

            if file_association[0] == "BASEMAP":
                TIM_location = (file_number * 0x10000) + 0x26AC
            else:
                TIM_location = file_number * 0x10000
            
            dat_file.seek(TIM_location)

            dat_file.write(compressed_TIM)
    return

    

def repack_all():
    for association in RAW_ASSOCIATIONS:
        repackRaw(association)

    for association in FILE_ASSOCIATIONS:
        repack(association)

    return

#repack(FILE_ASSOCIATIONS[1])
#repack_all()
#repackRaw(RAW_ASSOCIATIONS[1])
#repack(FILE_ASSOCIATIONS[3])

#unpackDTI("EXTRACT - Original/MOVIE/TITLE.DTI")

#testTIM = TIMresource.PNG_to_TIM("IMAGE/END/END0x1f7d0.TIM", "IMAGE/END/END0x1f7d0 - Copy.PNG")
#testFile = open("TEST/timtest.TIM", 'wb')
#testFile.write(testTIM)
#testFile.close()

def compressTest():
    compressTest = compressTIM("IMAGE/END.DTI/0x14b34.TIM-modified")
    outputTest = open("testCompress.LZ", 'wb')
    outputTest.write(compressTest)
    #unpackINIT1()
    #unpackTITLE()
    #unpackBASEMAP()
    file = open("testCompress.LZ", 'rb')
    #file.seek(0x20000)
    data = uncompressTIM(file)

    writer = open("TEST/testUncompressUR.TIM", 'wb')
    writer.write(data)

#compressTest()