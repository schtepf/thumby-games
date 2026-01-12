# SHAPES draws simple geometric shapes by rendering vertical lines,
# which can be optimised well because of VRAM layout on the Thumby.
# This approach implies some limitations, though. In particular,
# shapes must be convex along the y-axis, i.e. every vertical section
# of the shape must be a single unbroken line. Only filled shapes
# are supported, but they can additionally have a single-pixel outline,
# which adds a considerable amount of complexity to the code. Keep in
# mind that the library is designed for drawing large shapes efficiently.
# It will be faster to render e.g. many small triangles by plotting
# individual pixels.
#
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
#
# shapes.rect(x0, y0, x1, y1, mode)
#  - draw filled rectangle from top left (x0, y0) to bottom right (x1, y1)
#  - according to mode, and automatically clipped to screen
# 
# shapes.rect_outline(x0, y0, x1, y1, mode)
#  - draw rectangle outline (1px width) according to mode (fill, bg_fill, xor)
#  - from top left (x0, y0) to bottom right (x1, y1), automatically clipped to screen
#  - aims to be as fast as possible (unlike thumby.display.drawRectangle())
#
# shapes.ellipse(x0, y0, rx, ry, mode)
#  - draw filled ellipse around (x0, y0) with radii rx and ry
#  - according to mode, and automatically clipped to screen
#
# shapes.lozenge(x0, y0, rx, ry, mode)
#  - draw filled rombus shape centered at (x0, y0) with half-diametres rx and ry
#  - according to mode, and automatically clipped to screen
#
# shapes.twister(phase, wavelen1, wavelen2, x1=-1, x2=72, y0=19.5, ry=19)
#  - draws a horizontal twisting spiral with given phase (at x=0.0) and wavelength (in pixels)
#  - x0, x1 is an integer range of pixel coordinates to draw (terminating shape at end)
#  - spiral can be tightened or loosened by setting wavelen2 (at x2) different from wavelen1 (at x1)
#  - the spiral is centered vertically at y0 and extends for ry above and below
#
#
# shp = shapes.Shape() creates an object for rendering arbitrary shapes,
# which must be convex along the y-axis. The shape is defined by setting
# the start and end of the vertical line to be drawn at each x-coordinate
# in internal arrays shp.upper[] and shp.lower[]. Only the part of the arrays
# actually rendered to screen needs to be updated.
#
# shapes.shape is a globally allocated scratch object, which all drawing functions
# in the module share for rendering objects.
#
# shp.draw(x1, x2, mode)
#  - draw shape by rendering vertical lines for x-coordinates from x1 to x2 
#  - x1 < 0 and x2 >= 72 are allowed, indicating that border is outside screen
#    (relevant for outline and bg_outline modes, to determine if border is drawn)
#  - shp.upper[] and shp.lower[] can also be out of screen range
#    (relevant for outline and bg_outline modes, to determine if border is drawn)
#  - no vlines are drawn for x with shp.lower[x] < shp.upper[x]
#  - in outline modes, upper[] and lower[] specify the outer boundary of the shape,
#    i.e. an inner outline is drawn with upperl[x] <= y <= lower[x]
#  - the outline will be incomplete at the left and right borders of the screen
#    because we would need to known upper[-1], lower[-1], upper[72], and lower[72]
#    for correct rendering; this is accepted to keep array offsets simple
#  
# shp.reset(x1=0, x2=71, upper=40, lower=-1)
#  - reset internal arrays shp.upper[] and shp.lower[] for defensive programming
#  - default sets upper[x]=40 and lower[x]=-1, so no line will be drawn unless both are updated
#
# shp.line_segment(x0, y0, x1, y1, upper, fine=False):
#  - utility function for creating polygonal shapes to be rendered with shp.draw
#  - draws line segment from (x0, y0) to (x1, y1), automatically clipped as needed
#  - all coordinates are floating-point for precise position
#  - draw upper boundary if upper=True, lower boundary if upper=False
#  - if fine=True, take care to include all pixels that overlap with polygon
#  - only extends shape upwards (for upper=True) or downwards (for upper=False),
#    so multiple line segments can easily be combined into consistent polygon
#  - recommendation: call shp.reset() before drawing polygon outline
#
#
# poly = shapes.ConvexPoly(x, y, unit=1) creates a convex polygon that can be
# scaled, rotated and then rendered at any position on the screen. The polygon is
# specified by listing the coordinates of vertices in counter-clockwise order. The 
# reference point for positioning and rotation is always (0, 0). We do not check
# correctness of the specification or whether the polygon is really convex. This can
# be abused to render some y-convex shapes as long as they are not rotated too far.
#  - x, y are lists of the same length specifying the coordinates of the vertices
#    of a convex polygon in counter-clockwise order (otherwise: undefined behaviour)
#  - if unit != 1, all coordinates specified in the constructor are divided by unit,
#    which can be used to simplify coordinates, e.g. point (1, 2) with unit=3
#
# poly.draw(x0, y0, mode, angle=0, sx=1, sy=1):
#  - draw convex polygon with origin shifted to coordinates (x, y)
#  - angle != 0 rotates polygon counter-clockwise by specified degrees
#  - sx, sy are scaling factors in x and y dimension (before rotation)
#
# The internal rendering functions can also be called directly for maximal flexibility:
#
# shapes.vline(x1, x2, y1, y2, mode)
#  - draw vertical line from (x, y1) to (x, y2) inclusive with call shapes.vline(x, x, y1, y2, mode)
#  - specify x2 > x1 to draw wide line (x2 - x1 + 1 pixels) efficiently (used e.g. by rect())
#  - automatically clipped to screen, no line is drawn if y2 < y1 or x2 < x1
#  - draws line according to mode (fill, bg_fill, xor), with single-pixel outline (for outline and bg_outline)
#
# shapes.hline(y, x1, x2, mode)
#  - draw horizontal line from (x1, y) to (x2, y) inclusive
#  - automatically clipped to screen, no line is drawn if x1 < x2
#  - draws line according to mode (fill, bg_fill, xor), outline modes are ignored
#  - this function is useful for drawing a horizontal outline or grid, but inefficient for shapes
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

    @micropython.native
    def reset(self, x1: int = 0, x2: int = 71, upper: int = 40, lower: int = -1):
        x1 = 0 if x1 < 0 else x1
        x2 = 71 if x2 > 71 else x2
        upper_data = self.upper
        lower_data = self.lower
        for x in range(x1, x2 + 1):
            upper_data[x] = upper
            lower_data[x] = lower

    @micropython.native
    def line_segment(self, x0: float, y0: float, x1: float, y1: float, upper: bool, fine: bool = False):
        px0 = int(math.floor(x0 + 0.5))
        px1 = int(math.floor(x1 + 0.5))
        py0 = int(math.floor(y0 + 0.5))
        py1 = int(math.floor(y1 + 0.5))
        if px0 > px1 or px0 >= 72 or px1 < 0:
            return # completely outside screen
        bdry = self.upper if upper else self.lower # boundary data to write to
        # extend boundary for (x0, y0) and (x1, y1), upwards (upper=True) or downwards (upper=False)
        if upper:
            if px0 >= 0 and py0 < bdry[px0]: # px0 < 72 ensured above
                bdry[px0] = py0
            if px1 < 72 and py1 < bdry[px1]: # px1 >= 0 ensured above
                bdry[px1] = py1
        else:
            if px0 >= 0 and py0 > bdry[px0]:
                bdry[px0] = py0
            if px1 < 72 and py1 > bdry[px1]:
                bdry[px1] = py1
        # extend boundary for inner points of the line segment
        if fine:
            # if fine=True, maximise the range of pixels covered by evaluating line coordinates either
            # at the left or the right boundary of each pixel (depending on slope and upper/lower boundary);
            # we also include px0 or px1 if the line might touch an additional pixel there 
            left_align = (upper and (y1 < y0)) or ((not upper) and (y1 > y0))
            if left_align:
                px0 += 1 # left align: draw points px0 + 1 .. px1 (because left bdry of px1 is further outside than y1)
                px1 += 1 # right align: draw points px0 .. px1 - 1 (because right bdry of px0 is further outside than y0)
        else:
            px0 += 1 # only fill in coordinates between the end points
        px0 = px0 if px0 >= 0 else 0   # clamp to valid range
        px1 = px1 if px1 <= 72 else 72
        if px1 > px0:
            slope = (y1 - y0) / (x1 - x0)
            # determine whether we determine line coordinates at left or right boundary of pixel,
            # chosen to maximise the range of pixels covered by the shape
            for px in range (px0, px1):
                if fine:
                    x = px - 0.5 if left_align else px + 0.5 # evaluate line at pixel boundary
                else:
                    x = float(px) # evaluate line at centre
                y = y0 + slope * (x - x0)
                py = int(math.floor(y + 0.5))
                if upper:
                    if py < bdry[px]:
                        bdry[px] = py
                else:
                    if py > bdry[px]:
                        bdry[px] = py

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
                    else:
                        y1_bdry = y2_ # right neigbour empty -> close outline
                if x > x1_:
                    y1_nb = upper[x - 1]
                    y2_nb = lower[x - 1]
                    if y1_nb <= y2_nb:
                        if y1_nb > y1_bdry:
                            y1_bdry = y1_nb
                        if y2_nb < y2_bdry:
                            y2_bdry = y2_nb
                    else:
                        y1_bdry = y2_ # left neigbour empty -> close outline
                if y1_bdry - 1 > y1_:
                    vline(x, x, y1_ + 1, y1_bdry - 1, bdry_mode)
                if y2_bdry + 1 < y2_:
                    vline(x, x, y2_bdry + 1, y2_ - 1, bdry_mode)


shape = Shape() # shared by drawing functions

class ConvexPoly:
    def __init__(self, x: list[float], y: list[float], scale: float = 1.0):
        n_x = length(x)
        n_y = length(y)
        if (n_x != n_y or n_x < 3):
            raise Exception("x and y must be lists of the same length, with a least 3 elements")
        self.x = [float(_x) / scale for _x in x]
        self.y = [float(_y) / scale for _y in y]

    @micropython.native
    def draw(self, x0: float, y0: float, mode: int, angle: float = 0.0, sx: float = 1.0, sy: float = 1.0):
        x = self.x # vertex coordinates after transformation
        y = self.y
        idx_L = x.index(min(x))   # treating x, y as circular buffers, idx_L .. idx_R gives the lower boundary 
        idx_R = x.index(max(x))   # left-to-right, and the opposite direction gives the upper boundary left-to-right
        xL = int(math.floor(x[idx_L] + 0.5)) # pixel range that needs to be drawn
        xR = int(math.floor(x[idx_R] + 0.5))
        shape.reset(xL, xR)
        i = idx_L

            

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

@micropython.native
def twister(phase: float, wavelen1: float, wavelen2: float, x1: int = -1, x2: int = 72, y0: float = 19.5, ry: float = 18.0):
    x1_ = x1 if x1 >= 0 else 0
    x2_ = x2 if x2 < 72 else 71
    omega = 2.0 * math.pi / wavelen1 # angular speed of spiral at x1
    omega2 = 2.0 * math.pi / wavelen2 # desired angular speed at x2 
    alpha = (omega2 - omega) / (x2 - x1) # angular accel to achieve tightening over [x1, x2]
    upper = shape.upper
    lower = shape.lower
    for x in range(x1_, x2_ + 1):
        dx = x - x1
        phi = phase + omega * dx + 0.5 * alpha * dx * dx
        dy = ry * math.sin(phi)
        upper[x] = int(math.floor(y0 - dy - 0.0)) # shift upper/lower by 0.5 px away from y0
        lower[x] = int(math.floor(y0 + dy + 1.0))
    shape.draw(x1, x2, outline)
    shape.upper, shape.lower = shape.lower, shape.upper # flip arrays to draw backsides
    shape.draw(x1, x2, bg_outline)
    shape.upper, shape.lower = shape.lower, shape.upper

