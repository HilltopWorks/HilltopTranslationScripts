################################################
# Defines and applies modifications to files   #
#  for ps1 game "Racing Lagoon"                #
#                                              #
################################################

import subprocess
#from os import path
#import shutil
#import compress


modifications = []


#Modifications
#                            Target File                     Offset      Payload

#Modifies default name in name entry screen to "Sho Akasaki", by modifying the ASM that prints characters, as well as the default names in the overlay
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",   0x558, bytes.fromhex("B8 00 03 24 BC 53 43 A4 C7 00 03 24 BE 53 43 A4 CE 00 03 24 C0 53 43 A4 A6 00 05 24 CC 53 45 A4 CA 00 03 24 CE 53 43 A4 D6 53 43 A4 C0 00 03 24 D0 53 43 A4 D4 53 43 A4 D2 00 03 24 D2 53 43 A4 C8 00 03 24 D8 53 43 A4 C6 53 40 A4 C8 53 40 A4 CA 53 40 A4 C2 53 40 A4 C4 53 40 A4 C4 53 40 A4 DA 53 40 A4 DC 53 40 A4 DE 53 40 A4 E0 53 40 A4 E2 53 40 A4 E4 53 40 A4 E6 53 40 A4 E8 53 40 A4 EA 53 40 A4 EC 53 40 A4 EE 53 40 A4")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x47F8, bytes.fromhex("41 6B 61 73 61 6B 69 20 20")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014", 0x10CAC, bytes.fromhex("0A 14 0A 1C 0A 14 12 FF 00 00 00")])
#Removes length limit on name entry screen, by bypassing the minimum length check
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x11F2, bytes.fromhex("60")])
#Changes default name entry screen to english characters, overwriting the table of characters
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x4834, bytes.fromhex("A600A700A800A900AA00AB00AC00AD00AE00AF00B000B100B200B300B400B500B600B700B800B900BA00BB00BC00BD00BE00BF000000000000000000C000C100C200C300C400C500C600C700C800C900CA00CB00CC00CD00CE00CF00D000D100D200D300D400D500D600D700D800D90004000000000000009C009D009E009F00A000A100A200A300A400A5000000")])
#Removes gap in underline beneath name entry, modifying the DMA call for the green lines
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x32CC, bytes.fromhex("2C")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x32FC, bytes.fromhex("2C")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x332C, bytes.fromhex("2C")])
#Shifts the second half of the name entry input to the left, modifying the DMA calls for the letters
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x3280, bytes.fromhex("21")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x3230, bytes.fromhex("1F")])
#Shifts the cursor left on the second half of name entry screen, modifying the DMA call for the cursor
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x4AE8, bytes.fromhex("1F 01 3F 01 5F 01 7F 01")])
#Changes the default tab label on name entry screen to english, modifying the DMA calls to scroll the texture
#modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x2E0C, bytes.fromhex("78")])
#modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x2DC0, bytes.fromhex("78")])
#modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x2DC8, bytes.fromhex("1D")])
#modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0x2E14, bytes.fromhex("1D")])
#Changes space character width to 4, modifying the entry in the spacing table
#modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x10EA4, bytes.fromhex("04")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x10E19, bytes.fromhex("04")])
#Modifies the dummy space character to 0 width to remove the need to fix the single space bug
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x10EA4, bytes.fromhex("00")])
#Changes the Remove Part text to english in Machine Complete, overwriting the text encoded in SHIFT-JIS
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x15E66, bytes.fromhex("82718264826C826E8275826482598259")])
#Moves control blocks to start of script files by modifying offset calculations to use new header location
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x2428, bytes.fromhex("7CD7")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x2500, bytes.fromhex("7CD7")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x27CC, bytes.fromhex("7CD7")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x28C4, bytes.fromhex("7CD7")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0014",  0x295C, bytes.fromhex("7CD7")])
#Modifies the win/loss letters in the pause screen to be english
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0006",  0x2F0, bytes.fromhex("5725")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0006",  0x380, bytes.fromhex("57")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0006",  0x384, bytes.fromhex("4C")])
#Fixes the space after first name if name is too short DEPRECATED
#modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0012",  0xE74, bytes.fromhex("00")])
#Changes "IN the CAR" and "BEHIND the CAR" text to "Bumper cam" and "Chase cam"
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0008",  0x614, bytes.fromhex("62 75 6D 70 65 72 20 63 61 6D 00 00 63 68 61 73 65 20 63 61 6D 20 20 20 20 20")])
#Moves the {FIRST_NAME} text in the pause menu slightly to the left
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0006",  0x2C60, bytes.fromhex("78")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0006",  0x2C88, bytes.fromhex("79")])
#Fixes empty text files to include the text hack formatting to prevent crashing
modifications.append(["EXTRACT/EVENT.BIN/EVENT.BIN.0989",  0x0C, bytes.fromhex("80D70880")])
modifications.append(["EXTRACT/EVENT.BIN/EVENT.BIN.1002",  0x0C, bytes.fromhex("80D70880")])
modifications.append(["EXTRACT/EVENT.BIN/EVENT.BIN.1043",  0x0C, bytes.fromhex("80D70880")])
modifications.append(["EXTRACT/EVENT.BIN/EVENT.BIN.1342",  0x0C, bytes.fromhex("80D70880")])
modifications.append(["EXTRACT/EVENT.BIN/EVENT.BIN.1998",  0x0C, bytes.fromhex("80D70880")])
modifications.append(["EXTRACT/EVENT.BIN/EVENT.BIN.1999",  0x0C, bytes.fromhex("80D70880")])
#Changes name of vehicle "City-Bus" to english
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17C15, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17D40, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17E66, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17F8F, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x180AD, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1826B, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1839C, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x184C9, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x185F7, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18725, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x189B9, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18AEB, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18CD6, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18E01, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18FFE, bytes.fromhex("43 69 74 79 2D 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19134, bytes.fromhex("43 69 74 79 2D 42 75 73")])
#Changes name of vehicle "Modified City Bus" to english
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x189C3, bytes.fromhex("54 75 6E 65 64 43 69 74 79 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18AF5, bytes.fromhex("54 75 6E 65 64 43 69 74 79 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18CE0, bytes.fromhex("54 75 6E 65 64 43 69 74 79 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18E0B, bytes.fromhex("54 75 6E 65 64 43 69 74 79 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19008, bytes.fromhex("54 75 6E 65 64 43 69 74 79 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1913E, bytes.fromhex("54 75 6E 65 64 43 69 74 79 42 75 73")])
#Changes name of vehicle "High speed bus" to english
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1932F, bytes.fromhex("53 70 65 65 64 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19474, bytes.fromhex("53 70 65 65 64 42 75 73")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x195BD, bytes.fromhex("53 70 65 65 64 42 75 73")])
#Changes name of vehicle "High speed truck" to english
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19339, bytes.fromhex("46 61 73 74")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1947E, bytes.fromhex("46 61 73 74")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x195C7, bytes.fromhex("46 61 73 74")])
#Changes name of vehicle "Truck" to english
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17C1F, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17D4A, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17E70, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17F99, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x180B7, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18275, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x183A6, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x184D3, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18601, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1872F, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x189C7, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18AF9, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18CE4, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x18E0F, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1900C, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1933D, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19482, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x195CB, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1A0BE, bytes.fromhex("42 6F 78 54 72 75 63 6B")])
#Changes "改" vehicle names to English
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19241, bytes.fromhex("20 4B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19751, bytes.fromhex("20 4B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1975D, bytes.fromhex("20 4B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19768, bytes.fromhex("20 4B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x19773, bytes.fromhex("20 4B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1977E, bytes.fromhex("20 4B")])
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x1978A, bytes.fromhex("20 4B")])
#Corrects typo on "Defuser" parts
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x17ADA, bytes.fromhex("46 44 69 66 66 75 73 65 72 0D 0A 52 44 69 66 66 75 73 65 72")])
#Fixes typo on part "Talantura"
modifications.append(["EXTRACT/SYSTEM.BIN/SYSTEM.BIN.0024.uncompressed",  0x16438, bytes.fromhex("72 61 6E 74 75 6C")])

#writes the payload to the file at filepath at the offset
def applyModification(filePath, offset, payload):

    targetFile = open(filePath, "rb")

    head = targetFile.read(offset)

    targetFile.read(len(payload))

    modifiedData = head + payload + targetFile.read()

    targetFile.close()

    writeFile = open(filePath, "wb")

    writeFile.write(modifiedData)
    writeFile.close()

#Execute
for modification in modifications:
    applyModification(modification[0], modification[1], modification[2])

subprocess.call(['armips.exe', 'main.asm'])