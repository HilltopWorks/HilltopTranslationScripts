from PIL import Image,ImageDraw
import os
import numpy
import copy
import shutil
import numpy as np
from pathlib import Path
import resource

PALETTE_END_ADDR = 0x28
PALETTE_START = 0xa0
GRAPHIC_START = 0x500

#After PALETTE_END_ADDR value
GRAPHIC_WIDTH_ADDR  = 0x30
GRAPHIC_HEIGHT_ADDR = 0x34

GRAPHIC_WIDTH = 0x100
GRAPHIC_HEIGHT = 0x80

TEX_SIZE = 0x8800

#Font
FONT_END = 0x5c0c0
FONT_START = 0xc0

FONT_WIDTH_PX = 32
FONT_HEIGHT_PX = 32
FONT_WIDTH_BYTES = 0x10

FONT_PATH = "C:\dev\maid\BD_EXTRACT\MAP_0x17b6800_0x17f6840"
FONT_CLUT = [0,0x1D,0x27,0x30,0x39,0x3f,0x8c,0x9c,0xa8,0xb3,0xc1,0xd4,0xe4,0xee,0xf6,0xff]

GLYPH_SIZE = FONT_WIDTH_BYTES * FONT_HEIGHT_PX
NUM_GLYPHS = (FONT_END - FONT_START)//GLYPH_SIZE

EDIT_FOLDER = "IMAGE_EDITS"
REBUILD_FOLDER = "BD_EDITS"
INPUT_FOLDER = "BD_EXTRACT"
OUTPUT_FOLDER = "GFXrip" #TEST / GFXrip

def TEX_to_PNG(tex_file_path, offset):
    stem = Path(tex_file_path).stem
    basename = os.path.basename(tex_file_path)
    TEX_file = open(tex_file_path, 'rb')
    
    filename = resource.ReadString(TEX_file)
    if filename != "TEX":
        TEX_offset = 0
        
        while resource.ReadString(TEX_file) != "TEX":
            TEX_offset += 4
            TEX_file.seek(offset + TEX_offset)

        offset += TEX_offset

    palette_start = offset + PALETTE_START
    TEX_file.seek(PALETTE_END_ADDR + offset)
    palette_end = resource.readInt(TEX_file)
    
    TEX_file.seek(PALETTE_START + offset)
    palette = []
    CLUT_array = numpy.zeros((16, 16 , 4), dtype=numpy.uint8)
    for x in range(256):
        palette += [int.from_bytes(TEX_file.read(4), "little")]

        red =    palette[x] &       0xFF
        green = (palette[x] &     0xFF00) >> 8
        blue =  (palette[x] &   0xFF0000) >> 16
        alpha = (palette[x] & 0xFF000000) >> 24
        if x % 32 >= 8 and x % 32 < 24:
            flipper = x % 16
            if flipper >= 8:
                CLUT_array[1 + (x//16)][x%8] = (red, green, blue, alpha)
            else:
                CLUT_array[(x//16) - 1][8 + (x%8)] = (red, green, blue, alpha)
        else:
            CLUT_array[x//16][x%16] = (red, green, blue, alpha)

    clut_im = Image.fromarray(CLUT_array, "RGBA")
    clut_im.save(os.path.join(OUTPUT_FOLDER, "CLUT/", stem + "_" + hex(offset) + "_CLUT.png"))

    graphics = []
    TEX_file.seek(palette_end + offset + GRAPHIC_WIDTH_ADDR)
    graphics_w = resource.readInt(TEX_file)
    graphics_h = resource.readInt(TEX_file)

    TEX_file.seek(palette_end + 0x60 + offset)
    for x in range(graphics_w * graphics_h):
        graphics += [int.from_bytes(TEX_file.read(1), "little")]

    image_array = numpy.zeros((graphics_h, graphics_w , 4), dtype=numpy.uint8)
    for pixel_number in range(graphics_w * graphics_h):
        #red =   palette[(graphics[pixel_number])]  &     0xFF
        #green = (palette[(graphics[pixel_number])] &   0xFF00) >> 8
        #blue =  (palette[(graphics[pixel_number])] & 0xFF0000) >> 16
        x = graphics[pixel_number]
        red =   CLUT_array[x//16][x%16][0]
        green = CLUT_array[x//16][x%16][1]
        blue =  CLUT_array[x//16][x%16][2]
        alpha = min(CLUT_array[x//16][x%16][3] * 2, 255)
        

        pixel_color = (red, green, blue,  alpha)
        
        image_array[pixel_number//graphics_w][pixel_number%graphics_w] = pixel_color

    im = Image.fromarray(image_array, "RGBA")
    im.save(os.path.join(OUTPUT_FOLDER, stem + "_offset_" + hex(offset) + ".png"))
    
    file_size = (graphics_w * graphics_h) + palette_end + 0x60
    file_size_filled = file_size + (0x800 - (file_size % 0x800)) % 0x800
    return file_size

def unpackTEX(path):
    TEX_file = open(path, 'rb')

    total_size = os.stat(path).st_size 
    
    cursor = 0
    while cursor < total_size:
        tex_size = TEX_to_PNG(path, cursor)
        cursor += tex_size

def unpackTEX2(path):
    TEX_file = open(path, 'rb')

    total_size = os.stat(path).st_size 
    TEX_offset = 0
    while TEX_offset < total_size:
        
        filename = resource.ReadString(TEX_file)
        
        if filename == "TEX":
            tex_size = TEX_to_PNG(path, TEX_offset)
            TEX_offset += tex_size
            TEX_file.seek(TEX_offset)
        else:
            while resource.ReadString(TEX_file) != "TEX" and TEX_offset < total_size:
                TEX_offset += 4
                TEX_file.seek(TEX_offset)

def unpackAllTex():
    for file in os.listdir(INPUT_FOLDER):
        if ".TEX" in file:
            unpackTEX2(os.path.join(INPUT_FOLDER,file))

def unpackFont(filepath):
    font_file = open(filepath, 'rb')
    font_file.seek(FONT_START)

    columns = 32
    rows = NUM_GLYPHS //columns

    font_array = numpy.zeros((rows * FONT_HEIGHT_PX, columns * FONT_WIDTH_PX , 3), dtype=numpy.uint8)
    
    for glyph_number in range(NUM_GLYPHS):
        base_x = (glyph_number % columns) * FONT_WIDTH_PX
        base_y =  (glyph_number // columns) * FONT_HEIGHT_PX
        for v in range(FONT_HEIGHT_PX):
            for u in range(FONT_WIDTH_BYTES):
                next_byte = int.from_bytes(font_file.read(1), 'little')
                pixel1 = (next_byte & 0xF0) >> 4
                pixel2 = (next_byte & 0x0F)

                if pixel1 == 0:
                    font_array[base_y + v][base_x + u*2] = (255,0,255)
                else:
                    greyscale_color = FONT_CLUT[pixel1]
                    font_array[base_y + v][base_x + u*2] = (greyscale_color,greyscale_color,greyscale_color)

                if pixel2 == 0:
                    font_array[base_y + v][base_x + u*2 + 1] = (255,0,255)
                else:
                    greyscale_color = FONT_CLUT[pixel2]
                    font_array[base_y + v][base_x + u*2 + 1] = (greyscale_color,greyscale_color,greyscale_color)

    im = Image.fromarray(font_array, "RGB")
    im.show()

    return

def packFont(input_png_path, input_font_path, output_path):
    #TODO
    input_image = Image.open(input_png_path)



    return



def packTEX(target_path, offset, input_png_path):
    image = convertTo8Bit(input_png_path)
    palette = image.palette.tobytes()
    graphics = image.tobytes()

    target_file = open(target_path, "r+b")
    target_file.seek(offset + PALETTE_START)
    target_file.write(palette)

    target_file.seek(offset + GRAPHIC_START)
    target_file.write(graphics)

    target_file.close()

def closest(colors,color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = int(np.where(distances==np.amin(distances))[0][0])
    smallest_distance = colors[index_of_smallest]
    return index_of_smallest 

def getAlpha(palette):
    for color_num in range(256):
        if palette[color_num][3] == 0:
            return color_num

    #print("ERROR: ALPHA NOT FOUND!!!!")
    return 0

def get_palette(target_TEX_path, offset):
    tex_file = open(target_TEX_path, 'rb')
    tex_file.seek(offset + PALETTE_START)

    palette = []
    CLUT_array = numpy.zeros((16, 16 , 4), dtype=numpy.uint8)
    for x in range(256):
        palette += [int.from_bytes(tex_file.read(4), "little")]

        red =    palette[x] &       0xFF
        green = (palette[x] &     0xFF00) >> 8
        blue =  (palette[x] &   0xFF0000) >> 16
        alpha = (palette[x] & 0xFF000000) >> 24
        if x % 32 >= 8 and x % 32 < 24:
            flipper = x % 16
            if flipper >= 8:
                CLUT_array[1 + (x//16)][x%8] = (red, green, blue, alpha)
            else:
                CLUT_array[(x//16) - 1][8 + (x%8)] = (red, green, blue, alpha)
        else:
            CLUT_array[x//16][x%16] = (red, green, blue, alpha)
    
    return CLUT_array

def packTEX2(target_TEX_path, offset, reference_PNG_path, edited_PNG_path):
    stem = Path(reference_PNG_path).stem
    basename = os.path.basename(reference_PNG_path)

    ref_im = Image.open(reference_PNG_path)
    edited_im = Image.open(edited_PNG_path)
    edited_im = edited_im.convert("RGBA")
    target_file = open(target_TEX_path, "r+b")

    target_file.seek(offset)

    

    #index_image = ref_im.convert('P', dither=Image.NONE, palette=Image.ADAPTIVE, colors=256)
    parent_tex = os.path.join("BD_EXTRACT", stem.split("_offset_")[0] + ".TEX")
    parent_offset = int(stem.split("_offset_0x")[1], base=16)
    palette_2D = get_palette(parent_tex, parent_offset)#ref_im.palette.colors
    palette = []
    for y in range(16):
        for x in range(16):
            palette += [palette_2D[y][x]]
    palette_array = []
    #for x in range(256):
    #    palette_array = palette_array + [palette[x]]

    for v in range(ref_im.height):
        for u in range(ref_im.width):
            ref_color = np.asarray(ref_im.getpixel((u,v)))
            ref_color[3] = min(255, ref_color[3]*2)
            edited_color = np.asarray(edited_im.getpixel((u,v)))
            edited_color[3] = min(255, edited_color[3]*2)

            if not np.array_equiv(ref_color, edited_color):
                if edited_color[3] == 0:
                    #Find any color with alpha=0
                    closest_color = getAlpha(palette)
                else:
                    closest_color = closest(palette, edited_color)
                
                graphics_val = closest_color
                target_file.seek(offset + v*ref_im.width + u)
                target_file.write(graphics_val.to_bytes(1, "little"))

    #target_file.seek(offset + GRAPHIC_START + v*ref_im.width + u + 1)
    '''
    fileSize =  ref_im.width * ref_im.height #target_file.tell() - (offset + GRAPHIC_START) 
    target_file.seek(offset + GRAPHIC_START)
    TexBytes = target_file.read(fileSize)
    instanceFile = open("INSTANCE/" + basename + ".modified",'wb')
    instanceFile.write(TexBytes)
    instanceFile.close()

    
    referenceTexFile = open("BD_EXTRACT/" + stem,'rb')
    referenceTexFile.seek(offset + GRAPHIC_START)
    referenceData = referenceTexFile.read(fileSize)
    referenceTexFile.close()

    instanceReferenceFile = open("INSTANCE/" + basename,'wb')
    instanceReferenceFile.write(referenceData)

    instanceReferenceFile.close()
    target_file.close()'''
    return

def packTEX3(target_TEX_path, offset, reference_PNG_path, edited_PNG_path):
    ref_im = Image.open(reference_PNG_path)
    edited_im = Image.open(edited_PNG_path)
    target_file = open(target_TEX_path, "r+b")

    target_file.seek(offset + GRAPHIC_START)

    oldpalette = ref_im.palette

    convertedImage = edited_im.convert("P", dither=Image.NONE, palette=oldpalette)
    target_file.write(convertedImage.tobytes())
    target_file.close()

#takes path to an image and returns 8 bit indexed image with 32 bit RGBA clut
def convertTo8Bit(imagePath):
    stem = Path(imagePath).stem
    directory = os.path.dirname(imagePath)
    basename = os.path.basename(imagePath)

    image = Image.open(imagePath)
    #image.show()
    convertedImage = image.convert("P", palette=Image.ADAPTIVE, colors=256)
    #convertedImage.show()
    #print(len(convertedImage.palette.tobytes()))
    #print(convertedImage.tobytes())
    #convertedImage.save(os.path.join(directory, stem + "_8bit.png"))
    return convertedImage

def repack():

    for file in os.listdir(EDIT_FOLDER):
        stem = Path(file).stem
        directory = os.path.dirname(file)
        basename = os.path.basename(file)
        extension = Path(file).suffix
        if extension == ".png" or extension == ".PNG":
            parent_name = basename.split("_offset_")[0] + ".TEX"
            #TEX_file = open(os.path.join(REBUILD_FOLDER, parent_name), 'r+b')
            offset = basename.split("0x")[-1].split(".")[0]
            offset = int(offset, 16)
            reference_PNG_path = os.path.join(OUTPUT_FOLDER, file)
            edited_PNG_path =  os.path.join(EDIT_FOLDER, file)
            print("Packing Graphic: ", basename)
            referenceFilePath = os.path.join("INSTANCE", basename)
            parentFilePath = os.path.join("INSTANCE", basename + ".modified")
            shutil.copyfile(referenceFilePath, parentFilePath)
            if not os.path.exists(parentFilePath):
                shutil.copyfile( os.path.join("BD_EXTRACT", parent_name),parentFilePath)
                shutil.copyfile( os.path.join("BD_EXTRACT", parent_name),referenceFilePath)
            packTEX2(parentFilePath, 0, reference_PNG_path, edited_PNG_path)

    return

def prepareInsertionFiles():
    for file in os.listdir(EDIT_FOLDER):
        extension = Path(file).suffix
        basename = os.path.basename(file)
        if extension == ".png" or extension == ".PNG":
            parent_name = basename.split("_offset_")[0] + ".TEX"


#packTEX("C:\dev\maid\MAP_0x1521800_0x1546e00.TEX", 0x92d00, "C:\dev\maid\GFXrip\MAP_0x1521800_0x1546e00_offset_0x92d00 - Copy copy.png")
#convertTo8Bit("C:/Users/alibu/Desktop/MAP_0x1521800_0x15a8c00_133632.png")
#packTEX2("C:\dev\maid\BD_EDITS\MAP_0x7639000_0x7639040.TEX", 0, "C:\dev\maid\GFXrip\MAP_0x7639000_0x7639040_offset_0x0.png", "C:\dev\maid\IMAGE_EDITS\MAP_0x7639000_0x7639040_offset_0x0.png")
#unpackFont(FONT_PATH)
#unpackTEX2("C:\dev\maid\BD_EDITS\MAP_0x7639000_0x7639040.TEX")
#unpackAllTex()
#repack()