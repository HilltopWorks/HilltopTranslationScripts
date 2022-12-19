
import sys    
import os

def test1ByteCodes():
    for x in range(0x100):
        print((hex(x))[2:] + "=")
    for x in range(0x100):
        print((hex(x) + "00")[2:])

def testD0ByteCodes():
    for x in range(0x100):
        print("d0" + (hex(x))[2:] + "=")
    for x in range(0x100):
        print("d0" + (hex(x))[2:])

def testD0Kanji():
    for x in range(0x100):
        print("d0" + (hex(x))[2:] + "=")
        
    for x in range(0x100):
        print("d0" + (hex(x))[2:] + "00")
        if x % 9 == 0:
            print("df")
    print ("ff")

def testKanji(block):
    for x in range(0x100):
        spacer = ''
        if x < 16:
            spacer = '0'
        print(block + spacer + (hex(x))[2:] + "=")
        
    for x in range(0x100):
        spacer = ''
        if x < 16:
            spacer = '0'
        print(block + spacer + (hex(x))[2:] + "00")
        if x % 14 == 0:
            print("df")
    print ("ff")
    

testKanji("de")