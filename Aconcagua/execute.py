import extract
import decompress
import compress
import dataDuplication
import scriptExtractor
import os
import filecmp
import datetime
import shutil
import subprocess
import imageProcessor
import re

             #"PS-X EXE" in ascii
PSX_HEADER = b'PS-X EXE'

uncompressedLengthOffset  = 0x1C
uncompressedLengthOffset2 = 0xD4
compressedLengthOffset    = 0xD8
isCompressedOffset        = 0xDC

bodyStartPtr              = 0x18

sectorLength = 0x800

dataFolder  = "EXTRACT"
builtFolder = "EXTRACT-BUILT"
originalFolder = "EXTRACT-ORIGINAL"

#compresses modified files in EXTRACT
def compressModified():
    logFile = open('logs/compressModified.log', 'w')
    for file in os.listdir(dataFolder):

        fileName = os.fsdecode(file)
        extension = fileName.split('.')[-1]

        if extension == 'bodyUncompressed':
            unmodified = filecmp.cmp(dataFolder  + '/' + fileName,
                                     builtFolder + '/' + fileName)
            
            if not unmodified:
                print(str(datetime.datetime.now()) + " Compressing modified file: " + fileName)
                logFile.write(str(datetime.datetime.now()) + " Compressing modified file: " + fileName + '\n')

                newFile = compress.compress(dataFolder + '/' + fileName)

                newLength  = len(newFile)
                oldLength  = os.path.getsize(originalFolder + '/' + fileName.replace("Uncompressed","Compressed"))
                maxLength = oldLength - (oldLength % -sectorLength)

                assert newLength <= maxLength, "Compressed file too big: " + file + " by " + str(newLength - maxLength) + " bytes"

                #while len(newFile) < maxLength:
                #    newFile += bytes(1)

                outputFile = open(dataFolder + '/' + fileName.replace("Uncompressed","Compressed"), 'wb')
                outputFile.write(newFile)
                outputFile.close()

    return


def prepSTR(filePath):

    inFile = open(filePath, 'rb+')


    searchString = '004001d000'
    inData = inFile.read()

    hexString = inData.hex()

    matches = [m.start() for m in re.finditer(searchString, hexString)]

    for match in matches:
        hexString = hexString[:match + 16] + '0038' + hexString[match + 20:]

    inFile.close()

    outFile = open(filePath + 'test', 'wb')
    outFile.write(bytes.fromhex(hexString))
    return

#Uncompress compressed files
def uncompressFiles():
    for file in os.listdir(dataFolder):
        filename = os.fsdecode(file)
        
        if filename.endswith("Compressed") and not os.path.isfile("EXTRACT/" + filename.replace("Compressed", "Uncompressed")):
            print("Uncompressing " + filename)
            uncompressedSize,compressedSize,isCompressed = extract.__getValues(filename[4:12])
            if isCompressed == 1:
                decompressedData = decompress.decompress(dataFolder + "/" + filename, 0, uncompressedSize)
                outputFileName = filename[0:17] + "Uncompressed"
                outputFile = open(dataFolder + "/" + outputFileName, "wb+")
                outputFile.write(decompressedData)
                outputFile.close()

#Debug Uncompress one file
def testFile(lookFor):
    for file in os.listdir(dataFolder):
        filename = os.fsdecode(file)
        
        if filename.endswith(lookFor):
            print("Uncompressing " + filename)
            uncompressedSize,compressedSize,isCompressed = extract.__getValues(filename[4:12])
            if isCompressed == 1:
                decompressedData = decompress.decompress(dataFolder + "/" + filename, 0, uncompressedSize)
                outputFileName = filename[0:17] + "Uncompressed"
                outputFile = open(dataFolder + "/" + outputFileName, "wb+")
                outputFile.write(decompressedData)
                outputFile.close()

def compileGame():
    shutil.copyfile("REBUILT/PROGRAM.BIN","mkpsxiso/Aconcagua/PROGRAM.BIN")
    shutil.copyfile("REBUILT/PROGRAM.BIN","mkpsxiso/Aconcagua2/PROGRAM.BIN")
    if os.path.exists("mkpsxiso/Aconcagua (Japan) (Disc 1).bin"):
        os.remove("mkpsxiso/Aconcagua (Japan) (Disc 1).bin")
        os.remove("mkpsxiso/Aconcagua (Japan) (Disc 1).cue")
    if os.path.exists("mkpsxiso/Aconcagua (Japan) (Disc 2).bin"):
        os.remove("mkpsxiso/Aconcagua (Japan) (Disc 2).bin")
        os.remove("mkpsxiso/Aconcagua (Japan) (Disc 2).cue")
    os.chdir("mkpsxiso")
    subprocess.check_call(["mkpsxiso.exe", "Aconcagua.xml"])
    subprocess.check_call(["mkpsxiso.exe", "Aconcagua2.xml"])
    return


def print_subs():
    print("Cleaning Intro Video...")
    imageProcessor.copyFolder("./PNG/ST09_01.STR - Original", "./PNG/SE09_01.STR")
    print("Printing Intro Subs...")
    imageProcessor.printSubsToFMV("PNG/SE09_01.STR", "SE09_01.STR", "PNG/SE09_01.STR.txt")
    print("Cleaning Ending Video...")
    imageProcessor.copyFolder("PNG/SE01_00.STR - Clean", "PNG/SE01_00.STR")
    print("Printing Ending Video...")
    imageProcessor.fix_frame_names("PNG/SE01_00.STR")
    imageProcessor.printSubsToFMV("PNG/SE01_00.STR", "SE01_00.STR", "PNG/SE01_00.STR.txt")


def build():
    print_subs()
    scriptExtractor.injectScripts()
    imageProcessor.injectFont()
    dataDuplication.propagateFiles()
    compressModified()
    extract.repack()
    imageProcessor.buildSubtitles()
    compileGame()
    os.chdir("../PNG/")
    print("Replacing Intro Frames")
    subprocess.check_call(["java", "-jar", ".\jpsxdec.jar", "-x", ".\disk1.idx", "-i", "60", "-replaceframes", ".\SE01_00.STR.xml"])
    print("Replacing Ending Frames")
    subprocess.check_call(["java", "-jar", ".\jpsxdec.jar", "-x", ".\disk2.idx", "-i", "77", "-replaceframes", ".\SE09_01.STR.xml"])

build()


