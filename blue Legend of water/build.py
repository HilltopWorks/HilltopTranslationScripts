
from pickle import FALSE
import shutil
import subprocess
import os
import script
import font
import compress
import dataDuplication

EXE_files = ["EXTRACT/BASE/BB_000.EXE","EXTRACT/BASE/BB_001.EXE","EXTRACT/BASE/BB_100.EXE","EXTRACT/BASE/BB_101.EXE","EXTRACT/BASE/BB_200.EXE","EXTRACT/BASE/BB_201.EXE","EXTRACT/BASE/BB_300.EXE",
             "EXTRACT/BASE/BB_400.EXE","EXTRACT/BR_MAIN1.EXE","EXTRACT/BR_MAIN2.EXE","EXTRACT/BR_MAIN3.EXE","EXTRACT/BR_MAIN4.EXE","EXTRACT/BR_MAIN5.EXE","EXTRACT/BR_MAIN6.EXE",
             "EXTRACT/BR_MAIN7.EXE","EXTRACT/BS_MAIN1.EXE","EXTRACT/MOVIE/TITLE.EXE"]

REPACKED_FILES = ["INIT1.DTI", "MOVIE/END.DTI", "MOVIE/END2.DTI", "BASE/HP.DAT", "BASE/BASEMAP.DAT"]

ARMIPS_DEFS = ["BB_000","BB_001","BB_100","BB_101","BB_200","BB_201","BB_300","BB_400","BR_MAIN1","BR_MAIN2","BR_MAIN3","BR_MAIN4","BR_MAIN5","BR_MAIN6","BR_MAIN7","BS_MAIN1","TITLE"]

FONT_PATH = "IMAGE/font_thick.png"
FONT_BIN  = "IMAGE/font.bin"
FONT_HEIGHT = 12
FONT_WIDTH = 8

FULL_BUILD = False  

def build():
    dataDuplication.propagateFiles()
    print("Injecting standard scripts...")
    script.injectScripts()
    print("Injecting raw scripts...")
    script.injectSegments()
    print("Injecting load address scripts...")
    script.injectLoadScripts()

    #Convert font PNG
    font.convert_font(FONT_PATH, FONT_BIN, FONT_HEIGHT, FONT_WIDTH)

    #Perform assembly hack on every EXE
    for definition in ARMIPS_DEFS:
        print("Applying ASM patch to " + definition + ".EXE")
        subprocess.call(['armips.exe', 'TextAdjustment_' + definition + '.asm', "-definelabel", definition , str(1)])
    
    if FULL_BUILD:
        compress.repack_all()

    dataDuplication.propagateFiles()

    for EXE_file in EXE_files:
        shutil.copyfile(EXE_file, "mkpsxiso/" + EXE_file)
    
    for repacked_file in REPACKED_FILES:
        shutil.copyfile("EXTRACT/" + repacked_file, "mkpsxiso/EXTRACT/" + repacked_file)
    
    os.chdir("mkpsxiso")
    if os.path.exists("B. L. U. E. - Legend of Water (Japan) (Track 1).bin"):
        os.remove('B. L. U. E. - Legend of Water (Japan) (Track 1).bin')
    if os.path.exists("B. L. U. E. - Legend of Water (Japan).cue"):
        os.remove('B. L. U. E. - Legend of Water (Japan).cue')


    subprocess.call(['mkpsxiso.exe', 'BLUE.xml'])
    shutil.copyfile('B. L. U. E. - Legend of Water (Japan) - Original.cue', 'B. L. U. E. - Legend of Water (Japan).cue')

    return

build()