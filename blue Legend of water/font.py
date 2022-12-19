
from PIL import Image,ImageDraw
import os
import numpy as np
import copy

def convert_font(font_path, output_path, font_height, font_width):
    '''Converts a 1bpp font image to a loadable bin'''
    font_image = Image.open(font_path).convert('RGB')

    image_width = font_image.width
    image_height = font_image.height

    columns = image_width // font_width
    rows    = image_height// font_height

    outputfile = open(output_path, 'wb')

    byte_buffer = 0
    byte_cursor = 0
    for y in range(rows):
        for x in range(columns):
            for v in range(font_height):
                for u in range(font_width):
                    pixel = font_image.getpixel((x*font_width + u, y*font_height + v))
                    if pixel != (0,0,0):
                        byte_buffer |= 1

                    byte_cursor += 1
                    if byte_cursor >= 8:
                        outputfile.write(byte_buffer.to_bytes(1, 'little'))
                        #print(bin(byte_buffer))
                        byte_buffer = 0
                        byte_cursor = 0
                    else:
                        byte_buffer <<= 1
    outputfile.close()

    return

#convert_font("IMAGE/font_thick.png", "IMAGE/font.bin", 12, 8)