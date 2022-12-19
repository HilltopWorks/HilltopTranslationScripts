#########################################################################
# Propagates reduplicated data for Aconcagua                            #
#########################################################################


import os

WORKING_FOLDER = "INSTANCE"
TARGET_FOLDER = "ISO_EDITS/DATA"
SEARCH_FOLDER = "ISOrip/DATA"
TARGET_EXTENSIONS = ['BD2']

FILE_NOT_FOUND = -1

def propagateFile(filename):
    matchData = open(WORKING_FOLDER + '/' + filename,'rb').read()

    for targetFile in os.listdir(TARGET_FOLDER):
        extension = targetFile.split('.')[-1]


        if extension in TARGET_EXTENSIONS:
            searchData = open(SEARCH_FOLDER + '/' + targetFile,'rb').read()
            matchPosition = searchData.find(matchData)

            if matchPosition != FILE_NOT_FOUND:
                print("Match found for " + filename)
                replaceData = open(WORKING_FOLDER + '/' + filename + '.modified','rb').read()
                targetData  = open(TARGET_FOLDER  + '/' + targetFile,'rb').read()
                replacementLength = len(replaceData)
                
                assert len(replaceData) == len(matchData)

                outputBuffer = targetData[0:matchPosition]
                outputBuffer += replaceData
                outputBuffer += targetData[matchPosition + replacementLength:]

                assert len(searchData) == len(outputBuffer)

                outPutFile = open(TARGET_FOLDER + '/' + targetFile,'wb')
                outPutFile.write(outputBuffer)
                outPutFile.close()


    return


def propagateFiles():
    for reduplicationFile in os.listdir(WORKING_FOLDER):
        if '.modified' not in reduplicationFile:
            print("Propagating " + reduplicationFile)
            propagateFile(reduplicationFile)

    return

#propagateFiles()
#propagateFile("STOCK_TEXT_1")