#Turns 2352 byte sectors files into 2336 byte sector files by removing the header

import sys    
import os
import io
from functools import partial

from cv2 import VideoCapture

inFile = "REBUILT/SE01_00RAW.STR"
outFile = "REBUILT/SE01_00.STR"

AUDIO = 0x64
VIDEO = 0x48
END_SECTOR = 0x80

#Reads little endian int from file and advances cursor
def readInt(file):
    integer = int.from_bytes(file.read(4), byteorder='little')
    return integer

#Reads little endian short from file and advances cursor
def readShort(file):
    readShort = int.from_bytes(file.read(2), byteorder='little')
    return readShort

#Reads little endian byte from file and advances cursor
def readByte(file):
    readByte = int.from_bytes(file.read(1), byteorder='little')
    return readByte


def stripSTR():
    inputFile = open(inFile, 'rb')
        
    outputFile = open(outFile, 'wb')    

    for chunk in iter(partial(inputFile.read, 2352), b''):
        outputFile.write(chunk[16:2353])

    inputFile.close()
    outputFile.close()
    return

class sector:
    def __init__(self, *args):
        if len(args) == 1:
            self.interleaved = readByte(args[0])
            self.channel = readByte(args[0])
            self.submode = readByte(args[0])
            self.is_audio = readByte(args[0])
            
            self.interleaved2 = readByte(args[0])
            self.channel2 = readByte(args[0])
            self.submode2 = readByte(args[0])
            self.is_audio2 = readByte(args[0])

            self.magic = readInt(args[0])

            self.chunk_number = readShort(args[0])
            self.chunks_in_frame = readShort(args[0])
            self.frame_number = readInt(args[0])
            self.used_demux_size = readInt(args[0])
            self.width = readShort(args[0])
            self.height = readShort(args[0])
            self.quant_scale = readShort(args[0])

            self.payload = args[0].read(2336 - 0x1E)

    #blank sector
        elif len(args) == 0:
            self.interleaved = 0
            self.channel = 0
            self.submode = 0
            self.is_audio = 0
            
            self.interleaved2 = 0
            self.channel2 = 0
            self.submode2 = 0
            self.is_audio2 = 0

            self.magic = 0

            self.chunk_number = 0
            self.chunks_in_frame = 0
            self.frame_number = 0
            self.used_demux_size = 0
            self.width = 0
            self.height = 0
            self.quant_scale = 0

            self.payload = bytes(2336 - 0x1E)


    def to_bin(self):
        buffer = b''
        buffer += self.interleaved.to_bytes(1, byteorder='little')
        buffer += self.channel.to_bytes(1, byteorder='little')
        buffer += self.submode.to_bytes(1, byteorder='little')
        buffer += self.is_audio.to_bytes(1, byteorder='little')

        buffer += self.interleaved2.to_bytes(1, byteorder='little')
        buffer += self.channel2.to_bytes(1, byteorder='little')
        buffer += self.submode2.to_bytes(1, byteorder='little')
        buffer += self.is_audio2.to_bytes(1, byteorder='little')

        buffer += self.magic.to_bytes(4, byteorder='little')

        buffer += self.chunk_number.to_bytes(2, byteorder='little')
        buffer += self.chunks_in_frame.to_bytes(2, byteorder='little')
        buffer += self.frame_number.to_bytes(4, byteorder='little')
        buffer += self.used_demux_size.to_bytes(4, byteorder='little')
        buffer += self.width.to_bytes(2, byteorder='little')
        buffer += self.height.to_bytes(2, byteorder='little')
        buffer += self.quant_scale.to_bytes(2, byteorder='little')
        buffer += self.payload
        return buffer
    
    def is_blank(self):
        if self.channel == 0 and self.submode == 0:
            return True
        else:
            return False

    def is_video(self):
        if self.submode == VIDEO:
            return True
        else:
            return False




def expand_blanks(STR_path, output_path):
    filesize = os.path.getsize(STR_path)
    sector_size = 2336

    assert filesize % sector_size == 0, "Filesize not multiple of 2336"

    str_file = open(STR_path, 'rb')

    sectors = []

    ID_short = 0xF3E3

    num_channels = 8
    current_frame = -1
    current_channel = -1
    current_magic = 0
    current_chunks_in_frame = 0
    current_chunk_number = 0
    current_demux = 0
    current_width = 0
    current_height = 0
    current_quant = 0
    frame_complete = False
    addr  = 0x0

    for sector_number in range(filesize//sector_size):
        print("Sector at: " + hex(addr))
        addr += 2336
        

        
        curr_sector = sector(str_file)

        #Break at final sector
        if curr_sector.submode == END_SECTOR:
            break
        
        #Update with new max chunkss
        if curr_sector.is_video() and curr_sector.frame_number > 0xB:
            curr_sector.chunks_in_frame = ID_short
        

        #Skip blank sectors before first frame
        if (curr_sector.submode == 0 and current_frame == -1):
            sectors.append(curr_sector)
            continue
        
        #Skip frames before 11 frame offset
        if (not curr_sector.is_audio) and (current_frame < 0xC):
            sectors.append(curr_sector)
            current_channel = (current_channel + 1) % num_channels
            current_frame = curr_sector.frame_number
            continue

        current_channel = (current_channel + 1) % num_channels

        #Skip audio sector
        if curr_sector.submode == AUDIO:
            sectors.append(curr_sector)
            if current_frame == -1:
                current_frame = 0
            continue
        
        #Update with current frame info
        if not curr_sector.is_blank():
            current_frame = curr_sector.frame_number
            current_magic = curr_sector.magic
            current_chunks_in_frame = curr_sector.chunks_in_frame
            current_chunk_number = curr_sector.chunk_number
            current_demux = curr_sector.used_demux_size
            current_width = curr_sector.width
            current_height = curr_sector.height
            current_quant = curr_sector.quant_scale
            
            sectors.append(curr_sector)
        #Format blank sector
        else:
            new_sector = sector()
            new_sector.interleaved = 1
            new_sector.interleaved2 = 1
            new_sector.channel = current_channel
            new_sector.channel2 = current_channel
            new_sector.submode = VIDEO
            new_sector.submode2 = VIDEO
            new_sector.is_audio = 0
            new_sector.is_audio2 = 0
            new_sector.magic = current_magic
            new_sector.chunk_number = (current_chunk_number + 1) % 8
            new_sector.chunks_in_frame = ID_short
            new_sector.frame_number = current_frame
            new_sector.used_demux_size = current_demux
            new_sector.width = current_width
            new_sector.height = current_height
            new_sector.quant_scale = current_quant
            new_sector.payload = bytes(2336 - 0x1E)
            sectors.append(new_sector)

            current_chunk_number = (current_chunk_number + 1) % 8


    
    

    output_file = open(output_path, 'wb')
    buffer = b''
    for __sector in sectors:
        output_file.write(__sector.to_bin())
    output_file.close()

    in_file = open(output_path, 'rb')
    buffer = in_file.read()
    
    #Fix max chunks
    for frame_number in range(current_frame):
        count = buffer.count(bytes(1) + ID_short.to_bytes(2,byteorder='little') + frame_number.to_bytes(4, byteorder='little'))

        buffer = buffer.replace(bytes(1) + ID_short.to_bytes(2,byteorder='little') + frame_number.to_bytes(4, byteorder='little'),
                                bytes(1) + count.to_bytes(2,byteorder='little') + frame_number.to_bytes(4, byteorder='little'))
    output_file = open(output_path, 'wb')
    output_file.write(buffer)    

    


    return

expand_blanks("PNG/TEST.str", "PNG/TEST-out.str")