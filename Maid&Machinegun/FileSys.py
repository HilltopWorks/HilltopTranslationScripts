import shutil
import subprocess
import os
import resource
from pathlib import Path

OUTPUT_FOLDER = "BD_EXTRACT"

def ReadString(file):
    read_string = ""
    initial_pos = file.tell()

    while True:
        byte = file.read(1)
        if int.from_bytes(byte, "little") == 0:
            file.seek(initial_pos)
            return read_string
        else:
            byteval = int.from_bytes(byte, "little")
            if byteval < 0x30 or (byteval > 0x39 and byteval < 0x41) or byteval > 0x7A  or (byteval > 0x5a and byteval < 0x61):
                continue
            else:
                read_string += byte.decode()


def UnpackBD1(file_path):
    basename = os.path.basename(file_path)
    stem =     Path(file_path).stem

    directory_file = open(file_path, "rb")
    

    if basename == "MAP.BD1":
        data_file = open(file_path.replace(basename, "MAM.BD2"), "rb")
    else:
        data_file = open(file_path, "rb")
    

    directory_file.seek(0x10)

    package_entries = resource.readInt(directory_file)
    

    for x in range(package_entries):
        #in bytes
        package_start = resource.readInt(directory_file)
        package_size  = resource.readInt(directory_file)
    
        directory_file.seek(package_start)
    
        
        for x in range(package_size//8):
            #in sectors
            file_start = resource.readInt(directory_file)
            file_size = resource.readInt(directory_file)
            data_file.seek(file_start * 0x800)
            file_extension = ReadString(data_file)
            data_file.seek(file_start * 0x800)
            file_bytes = data_file.read(file_size * 0x800)

            if not os.path.exists(OUTPUT_FOLDER):
                os.mkdir(OUTPUT_FOLDER)
            
            output_path = os.path.join(OUTPUT_FOLDER, stem + "_" + padhexa(hex(file_start*0x800),7) + "." + file_extension)

            output_file = open(output_path, "wb")
            output_file.write(file_bytes)
            output_file.close()

            if file_extension == "BD1":
                UnpackBD2(output_path)

    return

def getLastOffset(filename):
    lastHex = filename.split("0x")[-1].split(".")[0]
    lastOffset = int(lastHex, 16)

    return lastOffset
    
def padhexa(s, z):
    return '0x' + s[2:].zfill(z)

def UnpackBD2(file_path):
    basename = os.path.basename(file_path)
    stem =     Path(file_path).stem

    directory_file = open(file_path, "rb")

    directory_file.seek(0x10)

    package_entries = resource.readInt(directory_file)
    

    for x in range(package_entries):
        #in bytes
        file_start = resource.readInt(directory_file)
        file_size  = resource.readInt(directory_file)
        cursor = directory_file.tell()
        directory_file.seek(file_start)
        file_extension = ReadString(directory_file)
        directory_file.seek(file_start)

        output_bytes = directory_file.read(file_size)
        

        if not os.path.exists(OUTPUT_FOLDER):
            os.mkdir(OUTPUT_FOLDER)
        
        lastOffset = getLastOffset(stem)

        output_path = os.path.join(OUTPUT_FOLDER, stem + "_" + padhexa(hex(lastOffset + file_start), 7) + "." + file_extension)

        output_file = open(output_path, "wb")
        output_file.write(output_bytes)
        output_file.close()

        if file_extension == "BD1":
            UnpackBD2(output_path)
        directory_file.seek(cursor)

    return


#UnpackBD1("ISOrip/DATA/MAP.BD1")