#!/usr/bin/env python
#
# img2c.py
#
# Converts an image into a byte array expressed as C code.
#
# Usage:
#     img2c.py inputfile [outputfile]
#
# Example:
#     img2c.py mylogo.tif mylogo.h
#
# If outputfile is not provided, then the input file's filename will
# be used, except with a .c extension (be careful not to accidentally
# clobber any important source code).
#
# The variable name given to the image in the source code will be
# the input file's basename (i.e. mylogo.tif creates var MYLOGO).
#
# Copyright (c) 2011 Eric Jiang
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import Image # Use PIL
import sys
import os
import string
import math

helpmessage = """Usage: image2code.py input-image [output-file]"""

if(len(sys.argv) == 1):
    print helpmessage
    exit()

infile = sys.argv[1]

if(len(sys.argv) > 2):
    outfile = sys.argv[2]
else:
    outfile = "%s.c" % os.path.splitext(infile)[0]

im = Image.open(infile)
om = open(outfile, 'w')
immode = im.mode

def number2ascii(n):
    if(n > 255):
        raise IndexError()
    if(n < 33 or n > 126):
        return "\\%o" % n
    if(n == 92): # backslash
        return "\\\\"
    if(n == 34): # double quote
        return "\\\""
    if(n >= 48 and n <= 57): # make sure numbers don't get mucked onto the previous escape sequence
        return "\"\"%s" % chr(n)
    else:
        return chr(n)

def bpp(img):
    f = img.mode
    if(f == '1'):
        return 1
    elif(f == 'L'):
        return 8
    elif(f == 'RGB'):
        return 24
    elif(f == 'RGBA'):
        return 36
    elif(f == 'CMYK'):
        return 36
    else:
        raise Exception("Unknown image mode: %s" % f)

# def outputbitmap(p):
#     return "\\%s" % p
# 
# def outputL(p):
#     return number2ascii(n)
# 
# def outputRGB(r, g, b):
#     return number2ascii(n)

om.write("""static const struct {
    unsigned int   width;
    unsigned int   height;
    unsigned int   bits_per_pixel;
    unsigned char  pixel_data[%d]
} %s = {
    %d, %d, %d,
""" % (math.ceil(im.size[0] * im.size[1] * bpp(im)/8)+1,
    string.upper(os.path.splitext(os.path.basename(infile))[0]),
    im.size[0], im.size[1], bpp(im)))

imdata = im.getdata()
c = 0

if(bpp(im) > 1):
    for p in imdata:
        if(c == 0):
            om.write("  \"")
        t = number2ascii(p)
        c = c + len(t)
        om.write(t)
        if(c > 72):
            om.write("\"\n")
            c = 0
else:
    w = im.size[0]
    curr = 0
    bits = 0
    for i, p in enumerate(imdata):
        bits = bits + 1
        print("i = %d" % i)
        if(p == 0):
            curr = curr << 1
        else:
            curr = (curr << 1) + 1
        if(bits == 8 or i % w == w - 1):
            print "write"
            if(c == 0):
                om.write("  \"")
            t = number2ascii(curr)
            c = c + len(t)
            om.write(t)
            if(c > 72):
                om.write("\"\n")
                c = 0
            curr = 0
            bits = 0

om.write("\"};")
