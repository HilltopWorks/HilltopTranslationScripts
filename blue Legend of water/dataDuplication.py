#########################################################################
# Propagates reduplicated data for B.L.U.E.                             #
#########################################################################


from datetime import datetime
import os
import glob

WORKING_FOLDER = "INSTANCE"
TARGET_FOLDER = "EXTRACT"
SEARCH_FOLDER = "EXTRACT - Original"
TARGET_EXTENSIONS = ['EXE']

FILE_NOT_FOUND = -1

LOG_FOLDER = "LOG"

logfile = open(LOG_FOLDER + "/" + "duplication_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".log", 'w')

MEM_PTR_OFFSET = 0x18
def __getMemoryBaseAddress(fileName):
    headerFile = open(fileName, "rb")
    headerData = headerFile.read()
    headerFile.close()
    memPTR  = int.from_bytes(headerData[MEM_PTR_OFFSET  :MEM_PTR_OFFSET  + 4], byteorder="little", signed=False)

    return memPTR


def propagateFile(filename):
    matchData = open(WORKING_FOLDER + '/' + filename,'rb').read()

    #for targetFile in os.listdir(TARGET_FOLDER):
    for r,d,targetFiles in os.walk(TARGET_FOLDER): 
        for targetFile in targetFiles:
            extension = targetFile.split('.')[-1]

            if extension in TARGET_EXTENSIONS:
                targetPath = os.path.join(r,targetFile)
                searchPath = targetPath.replace(TARGET_FOLDER, SEARCH_FOLDER, 1)

                if not os.path.isfile(searchPath):
                    continue

                searchData = open(searchPath,'rb').read()
                matchPosition = searchData.find(matchData)

                if matchPosition != FILE_NOT_FOUND:
                    try:
                        memAddr = hex(__getMemoryBaseAddress(targetPath) + matchPosition)
                        logfile.write("Writing " + filename + " into " + targetFile + " at memory address " + memAddr + " / file offset " + hex(matchPosition) + "\n")
                    except BaseException:
                        memAddr = hex(matchPosition)
                        logfile.write("Writing " + filename + " into " + targetFile + " at offset " + memAddr + "\n")

                    replaceData = open(WORKING_FOLDER + '/' + filename + '.modified','rb').read()
                    targetData  = open(targetPath,'rb').read()
                    replacementLength = len(replaceData)
                    
                    assert len(replaceData) == len(matchData)

                    outputBuffer = targetData[0:matchPosition]
                    outputBuffer += replaceData
                    outputBuffer += targetData[matchPosition + replacementLength:]

                    assert len(searchData) == len(outputBuffer)
                    try:
                        os.makedirs(os.path.dirname(targetFile), exist_ok=True)
                    except FileNotFoundError:
                        pass
                    outPutFile = open(targetPath,'wb')
                    outPutFile.write(outputBuffer)
                    outPutFile.close()


    return


def propagateFiles():
    try:    
        os.mkdir(LOG_FOLDER)
    except FileExistsError:
        pass
    #logfile = open(LOG_FOLDER + "/" + "duplication_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".log", 'w')
    for reduplicationFile in os.listdir(WORKING_FOLDER):
        if '.modified' not in reduplicationFile:
            print("Propagating " + reduplicationFile)
            propagateFile(reduplicationFile)
    #logfile.close()
    return

#propagateFiles()
#propagateFile("STOCK_TEXT_1")