# SHAPES draws simple geometric shapes by rendering vertical lines.
# There is a separate function for each supported shape (see below),
# as well as a generic object Shape for drawing user-defined shapes.
# All shapes can be rendered in one of five different drawing modes:
#   shapes.fill       = fill shape
#   shapes.outline    = fill shape with black outline
#   shapes.bg_fill    = fill shape in black
#   shapes.bg_outline = black shape with white outline
#   shapes.xor        = XOR shape with existing image
#
# shapes.rect(x0, y0, x1, y1, mode)
#  - draw filled rectangle from top left (x0, y0) to bottom right (x1, y1)
#  - according to mode, and automatically clipped to screen
# 
# shapes.rect_outline(x0, y0, x1, y1, mode)
#  - draw rectangle outline (1px width) according to mode (with outline versions ignored)
#  - from top left (x0, y0) to bottom right (x1, y1), automatically clipped to screen
#  - aims to be as fast as possible (unlike thumby.display.drawRectangle())
#
# shapes.ellipse(x, y, rx, ry, mode)
#  - draw filled ellipse around (x, y) with radii rx and ry
#  - according to mode, and automatically clipped to screen
#
# shapes.lozenge(x, y, size, mode)
#  - only for testing purposes
#  - lozenge of width and height size, centered at (x, y)
#
# shp = shapes.Shape() creates an object for rendering arbitrary shapes,
# which must be convex along the y-axis. The shape is defined by setting
# the start and end of the vertical line to be drawn at each x-coordinate
# in internal arrays shp.y1[] and shp.y2[]. Only the part of the arrays
# actually rendered to screen needs to be updated.
#
# shp.draw(x1, x2, mode)
#  - draw shape by rendering vertical lines for x-coordinates from x1 to x2 
#  - x1 < 0 and x2 >= 72 are allowed, indicating that border is outside screen
#  - shp.y1[] and shp.y2[] can also be out of range, which determines whether
#    a border is drawn at the top and bottom of the vertical line
#  - no scanlines are drawn for x with shp.y2[x] < shp.y1[x]
#  
# shp.reset()
#  - reset internal arrays shp.y1[] and shp.y2[] for defensive programming
#
# Internal rendering functions are also available for maximal flexibility:
#
# shapes.vline(x1, x2, y1, y2, mode)
#  - draw vertical line from (x, y1) to (x, y2) inclusive with call shapes.vline(x, x, y1, y2, mode)
#  - specify x2 > x1 to draw wide line (x2 - x1 + 1 pixels) efficiently (used e.g. by rect())
#  - automatically clipped to screen, no line is drawn if y2 < y1 or x2 < x1
#  - draws line according to mode (fill, bg_fill, xor), outline modes are ignored
#
# shapes.hline(y, x1, x2, mode)
#  - draw horizontal line from (x1, y) to (x2, y) inclusive
#  - automatically clipped to screen, no line is drawn if x1 < x2
#  - draws line according to mode (fill, bg_fill, xor), outline modes are ignored
#  - this function is useful for drawing horizontal outline or grid, but inefficient for shapes
#

import thumby
import math

fill = const(1)
outline = const(2)
bg_fill = const(3)
bg_outline = const(4)
xor = const(5)

@micropython.viper
def vline(x1: int, x2: int, y1: int, y2: int, mode: int):
    scr = ptr8(thumby.display.display.buffer)
    y1_ = y1 if y1 >= 0 else 0
    y2_ = y2 if y2 < 40 else 39
    x1_ = x1 if x1 >= 0 else 0
    x2_ = x2 if x2 < 72 else 71
    if y2_ < y1_:
        return # no line to draw (also captures vline outside screen)
    if x2_ < x1_:
        return # no line to draw (as above)
    fg = mode == fill or mode == outline
    bdry = mode == outline or mode == bg_outline
    
    y1_byte = y1_ >> 3
    y1_lsb = y1_ & 0x07
    y1_mask = 0xff << y1_lsb
    
    y2_byte = y2_ >> 3
    y2_msb = y2_ & 0x07
    y2_mask = 0xff >> (7 - y2_msb)
    
    if y2_byte == y1_byte:
        mask = y1_mask & y2_mask
        if mode == xor:
            for x in range(x1_, x2_ + 1):
                scr[y1_byte * 72 + x] ^= mask
        elif fg:
            for x in range(x1_, x2_ + 1):
                scr[y1_byte * 72 + x] |= mask
        else:
            for x in range(x1_, x2_ + 1):
                scr[y1_byte * 72 + x] &= 0xff ^ mask
    else:
        if mode == xor:
            for x in range(x1_, x2_ + 1):
                scr[y1_byte * 72 + x] ^= y1_mask
                for yb in range(y1_byte + 1, y2_byte):
                    scr[yb * 72 + x] ^= 0xff
                scr[y2_byte * 72 + x] ^= y2_mask
        elif fg:
            for x in range(x1_, x2_ + 1):
                scr[y1_byte * 72 + x] |= y1_mask
                for yb in range(y1_byte + 1, y2_byte):
                    scr[yb * 72 + x] = 0xff
                scr[y2_byte * 72 + x] |= y2_mask
        else:
            for x in range(x1_, x2_ + 1):
                scr[y1_byte * 72 + x] &= 0xff ^ y1_mask
                for yb in range(y1_byte + 1, y2_byte):
                    scr[yb * 72 + x] = 0x00
                scr[y2_byte * 72 + x] &= 0xff ^ y2_mask
    
    if bdry: # to draw boundary, simply invert pixels at y1 and y2
        for x in range(x1_, x2_ + 1):
            if y1_ == y1:
                scr[y1_byte * 72 + x] ^= 1 << y1_lsb
            if y2_ == y2 and y1 != y2: # make sure we don't invert twice if y1 == y2
                scr[y2_byte * 72 + x] ^= 1 << y2_msb
    
@micropython.viper
def hline(y: int, x1: int, x2: int, mode: int):
    scr = ptr8(thumby.display.display.buffer)
    if not (0 <= y < 40):
        return
    if x1 < 0:
        x1 = 0
    if x2 >= 72:
        x2 = 71
    if x2 < x1:
        return
    
    y_byte_offset = (y >> 3) * 72
    y_bit = y & 0x07
    y_mask = 1 << y_bit
    if mode == xor:
        for x in range(x1, x2 + 1):
            scr[y_byte_offset + x] ^= y_mask  # xor
    elif mode == fill or mode == outline:
        for x in range(x1, x2 + 1):
            scr[y_byte_offset + x] |= y_mask  # fill
    else:
        y_mask = 0xff ^ y_mask
        for x in range(x1, x2 + 1):
            scr[y_byte_offset + x] &= y_mask  # bg_fill

@micropython.viper
def lozenge(x0: int, y0: int, size: int, mode: int):
    for i in range(size):
        j = size - i - 1
        vline(x0 - i, x0 - i, y0 - j, y0 + j, mode)
        if i > 0:
            vline(x0 + i, x0 + i, y0 - j, y0 + j, mode)

@micropython.viper
def rect(x0: int, y0: int, x1: int, y1: int, mode: int):
    bdry = mode == outline or mode == bg_outline
    if not bdry:
        vline(x0, x1, y0, y1, mode)
    else:
        bdry_mode = fill if mode == bg_outline else bg_fill
        fill_mode = bg_fill if mode == bg_outline else fill
        if x0 < x1 and y0 < y1:
            vline(x0 + 1, x1 - 1, y0 + 1, y1 - 1, fill_mode)
        rect_outline(x0, y0, x1, y1, bdry_mode)

# NB: buggy as long as vline() still draws the outline points
@micropython.viper
def rect_outline(x0: int, y0: int, x1: int, y1: int, mode: int):
    if x1 < x0 or y1 < y0:
        return
    vline(x0, x0, y0, y1, mode)
    if x0 < x1:
        vline(x1, x1, y0, y1, mode)
    if x0 + 1 < x1:
        hline(y0, x0 + 1, x1 - 1, mode)
        if y0 < y1:
            hline(y1, x0 + 1, x1 - 1, mode)

@micropython.native
def ellipse(x: int, y: int, rx: int, ry: int, mode: int):
    if rx < 0 or ry < 0:
        return
    vline(x, x, y - ry, y + ry, mode)
    if rx < 1:
        return
    bdry = mode == outline or mode == bg_outline
    bdry_mode = fill if mode == bg_outline else bg_fill
    ratio = ry / rx
    C = rx * rx
    dx = 0.5
    prev_dy = ry
    for r in range(rx):
        dy = int(ratio * math.sqrt(C - dx * dx) + .5)
        vline(x - r - 1, x - r - 1, y - dy, y + dy, mode)
        vline(x + r + 1, x + r + 1, y - dy, y + dy, mode)
        if bdry and dy < prev_dy - 1:
            vline(x + r, x + r, y - prev_dy, y - dy - 1, bdry_mode)
            vline(x + r, x + r, y + dy + 1, y + prev_dy, bdry_mode)
            vline(x - r, x - r, y - prev_dy, y - dy - 1, bdry_mode)
            vline(x - r, x - r, y + dy + 1, y + prev_dy, bdry_mode)
        prev_dy = dy
        dx += 1.0
    if bdry:
        vline(x + rx, x + rx, y - dy, y + dy, bdry_mode)
        vline(x - rx, x - rx, y - dy, y + dy, bdry_mode)
        
