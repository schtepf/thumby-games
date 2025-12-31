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
# Some shape drawing functions take floating-point coordinates and
# dimensions as arguments for precise placement. Integer coordinates
# are placed in the centre of each pixel, e.g. (0, 0) is the centre 
# of the top left pixel, which covers coordinates [-0.5, 0.5) x [-0.5, 0.5).
# A floating-point coordinate pair (x, y) is thus mapped to the pixel at
# (int(math.floor(x + 0.5)), int(math.floor(x + 0.5))); note the need for
# math.floor() as int() rounds towards zero and round() follows half-0.5 rule.
# When rendering geometric shapes, pixels should be drawn whenever the shape 
# overlaps with the pixel rectangle (no matter how small the overlap).
# This requires some care to find appropriate test points within the pixel
# square (usually setting the x-coordinate at the left or right boundary).
# If this is too complicated, we will fall back on evaluating float test points
# at 1-pixel increments and mapping them to pixel coordinates.

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
# in internal arrays shp.upper[] and shp.lower[]. Only the part of the arrays
# actually rendered to screen needs to be updated.
#
# shp.draw(x1, x2, mode)
#  - draw shape by rendering vertical lines for x-coordinates from x1 to x2 
#  - x1 < 0 and x2 >= 72 are allowed, indicating that border is outside screen
#  - shp.y1[] and shp.y2[] can also be out of range, which determines whether
#    a border is drawn at the top and bottom of the vertical line
#  - no vlines are drawn for x with shp.y2[x] < shp.y1[x]
#  - in outline modes, y1[] and y2[] specify the outer boundary of the shape,
#    i.e. an inner outline is drawn with all pixels between y1[x] and y2[x]
#  - the outline will be incomplete at the left and right borders of the screen
#    because we would need to known y1[-1], y2[-1], y1[72], y2[72] for correct
#    rendering; this is accepted to keep array offsets simple
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
#  - draws line according to mode (fill, bg_fill, xor), with single-pixel outline for outline and bg_outline
#
# shapes.hline(y, x1, x2, mode)
#  - draw horizontal line from (x1, y) to (x2, y) inclusive
#  - automatically clipped to screen, no line is drawn if x1 < x2
#  - draws line according to mode (fill, bg_fill, xor), outline modes are ignored
#  - this function is useful for drawing horizontal outline or grid, but inefficient for shapes
#

import thumby
import math
from array import array

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

class Shape:
    def __init__(self):
        self.upper = array("l", [39 for x in range(0, 72)])
        self.lower = array("l", [0 for x in range(0, 72)])

    def reset(self):
        upper = ptr32(self.upper)
        lower = ptr32(self.lower)
        for x in range(0, 72):
            upper[x] = 39
            lower[x] = 0
    
    @micropython.viper
    def draw(self, x1: int, x2: int, mode: int):
        bdry = mode == outline or mode == bg_outline
        x1_ = x1 if x1 >= 0 else 0
        x2_ = x2 if x2 < 72 else 71
        upper = ptr32(self.upper)
        lower = ptr32(self.lower)
        if not bdry:
            # filled shapes (fill, bg_fill, xor) are easy and fast
            for x in range(x1_, x2_ + 1):
                y1_ = upper[x]
                y2_ = lower[x]
                vline(x, x, y1_, y2_, mode)
        else:
            # shapes with boundary require quite a bit of extra work
            bdry_mode = bg_fill if mode == outline else fill
            for x in range(x1_, x2_ + 1):
                y1_ = upper[x]
                y2_ = lower[x]
                # left / right end of the shape: draw boundary only
                if x == x1 or x == x2:
                    vline(x, x, y1_, y2_, bdry_mode)
                    continue
                # otherwise draw vline with single-pixel boundary
                vline(x, x, y1_, y2_, mode)
                # fill in rest of boundary if neighbouring lines are shorter by more than one pixel
                y1_bdry = y1_
                y2_bdry = y2_
                if x < x2_:
                    y1_nb = upper[x + 1]
                    y2_nb = lower[x + 1]
                    if y1_nb <= y2_nb:
                        if y1_nb > y1_bdry:
                            y1_bdry = y1_nb
                        if y2_nb < y2_bdry:
                            y2_bdry = y2_nb
                if x > x1_:
                    y1_nb = upper[x - 1]
                    y2_nb = lower[x - 1]
                    if y1_nb <= y2_nb:
                        if y1_nb > y1_bdry:
                            y1_bdry = y1_nb
                        if y2_nb < y2_bdry:
                            y2_bdry = y2_nb
                if y1_bdry - 1 > y1_:
                    vline(x, x, y1_ + 1, y1_bdry - 1, bdry_mode)
                if y2_bdry + 1 < y2_:
                    vline(x, x, y2_bdry + 1, y2_ - 1, bdry_mode)

shape = Shape() # shared by drawing functions

@micropython.native
def lozenge(x0: float, y0: float, rx: float, ry: float, mode: int):
    if rx <= 0.0 or ry <= 0.0:
        return
    x_min_shp = int(math.floor(x0 - rx + 0.5)) # range of pixel coordinates to be drawn
    x_max_shp = int(math.ceil(x0 + rx - 0.5))
    x_min = x_min_shp if x_min_shp >= 0 else 0
    x_max = x_max_shp if x_max_shp < 72 else 0
    upper = shape.upper
    lower = shape.lower
    for x in range(x_min, x_max + 1):
        dx = math.fabs(x - x0) # find horizontal pixel boundary closest to x0
        dx = 0.0 if dx < 0.5 else dx - 0.5 # or dx = 0 if x0 is contained in pixel
        dy = (1.0 - dx / rx) * ry # corresponding dy given aspect ratio of lozenge
        upper[x] = int(math.floor(y0 - dy + 0.5))
        lower[x] = int(math.floor(y0 + dy + 0.5))
    shape.draw(x_min_shp, x_max_shp, mode) # so method knows whether to fill in left/right outline

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
    line_mode = fill if mode == outline else bg_fill if mode == bg_outline else mode
    vline(x0, x0, y0, y1, line_mode)
    if x0 < x1:
        vline(x1, x1, y0, y1, line_mode)
    if x0 + 1 < x1:
        hline(y0, x0 + 1, x1 - 1, line_mode)
        if y0 < y1:
            hline(y1, x0 + 1, x1 - 1, line_mode)

@micropython.native
def ellipse(x0: float, y0: float, rx: float, ry: float, mode: int):
    if rx <= 0.0 or ry <= 0.0:
        return
    ratio = ry / rx # ellipse eq: dx^2 + (dy / ratio)^2 = rx^2 = C
    C = rx * rx
    x_min_shp = int(math.floor(x0 - rx + 0.5)) # range of pixel coordinates to be drawn
    x_max_shp = int(math.ceil(x0 + rx - 0.5))
    x_min = x_min_shp if x_min_shp >= 0 else 0
    x_max = x_max_shp if x_max_shp < 72 else 0
    upper = shape.upper
    lower = shape.lower
    for x in range(x_min, x_max + 1):
        dx = math.fabs(x - x0) # find horizontal pixel boundary closest to x0
        dx = 0.0 if dx < 0.5 else dx - 0.5 # or dx = 0 if x0 is contained in pixel
        dy = ratio * math.sqrt(C - dx * dx) # solve implict equation for dy
        upper[x] = int(math.floor(y0 - dy + 0.5))
        lower[x] = int(math.floor(y0 + dy + 0.5))
    shape.draw(x_min_shp, x_max_shp, mode) # so method knows whether to fill in left/right outline
