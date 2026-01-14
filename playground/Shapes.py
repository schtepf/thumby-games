import thumby
import math
import shapes
import textmode
from fps import FPS

fps = FPS()
thumby.display.setFPS(0)
fps.tock()

shp = shapes.Shape()

page = 0 # 0 = start page, 1 = shapes, 2 = twister, 3 = parallax, 4 = polygons
drawmode = shapes.fill
shape = 1 # 0 = none, 1 = rect, 2 = ellipse, 3 = lozenge, 4 = rect_outline
speed = 3
wavelen2 = wavelen = 40.0
phase = 0.0

# mountain-style parallax layers, each exactly one screen wide and cyclic (first entry at x=0 ~ last entry at x=72)
# y-coordinates start at 0 and increase to the top (adjusted in the program code)
parallax = [
    [(0., 5.), (10., 20.), (14., 10.), (20., 16.), (26, 2.), (34., 12.), (40., 0.), (45., 15.), (50., 8.), (53., 24.), (60., 5.), (66., 12.), (72., 5.)],
    [(0., 5.), (20., 20.), (23.5, 18.), (27., 20.), (40., 4.), (45., 12.), (47., 10.), (49., 12.), (60., 0.), (65., 10.), (72., 5.)],
    [(0, 2.), (10, 8.), (20, 0.), (28., 10.), (40., 5.), (50., 14.), (60., 0.), (66., 10.), (72., 2.)]
]
offsets = [0., 0., 0.] # corresponding horizontal offsets
pspeed = 1.0   # scrolling speed
pheight = 2.0  # view height (determines offsets btw layers)

@micropython.native
def morphing_polygon(n: float, r: float = 20.0, obj: shapes.ConvexPoly = None) -> shapes.ConvexPoly:
    n = n if n >= 3. else 3.
    n_pts = int(math.ceil(n))
    phi = [2. * math.pi * i / n for i in range(n_pts)]
    x = [math.cos(t) * r for t in phi]
    y = [math.sin(t) * r for t in phi]
    if obj is None:
        obj = shapes.ConvexPoly(x=x, y=y)
    else:
        obj.change(x=x, y=y)
    return obj

mode_tick = 0.0
angle = 0.0
n_poly = 3.0
poly = morphing_polygon(n_poly)

@micropython.viper
def draw_sky(lines: int):
    scr = ptr8(thumby.display.display.buffer)
    if lines >= 1:
        for i in range(72):
            scr[i] = 0b00101011
    if lines >= 2:
        for i in range(72, 2 * 72):
            scr[i] = 0b10001001
    if lines >= 3:
        for i in range(2 * 72, 3 * 72):
            scr[i] = 0b00001000
    if lines >= 4:
        for i in range(3 * 72, 4 * 72):
            scr[i] = 0b01000001

while not thumby.buttonB.pressed():
    if thumby.buttonA.justPressed():
        page += 1
        if page > 4:
            page = 0
        fps.tock() # timing relative to page
    elif thumby.buttonL.justPressed():
        if speed > 0:
            speed -= 1
    elif thumby.buttonR.justPressed():
        if speed < 10:
            speed += 1

    dt = fps.frame_time()
    fps.tick()
    phase += speed * 0.5 * dt
    if phase > 2.0 * math.pi:
        phase -= 2.0 * math.pi # keep phase accurate in long-running demo

    if page == 0:
        thumby.display.fill(0)
        textmode.print_text(0, 0,
            "@ cycle\n  pages\n\n% exit", 
            textmode.block)
        
    elif page == 1:
        if thumby.buttonU.justPressed():
            drawmode += 1
            if drawmode > shapes.xor:
                drawmode = shapes.fill
        if thumby.buttonD.justPressed():
            shape += 1
            if shape > 4:
                shape = 0

        thumby.display.fill(0)
        for x in range(5, 72, 10):
            shapes.vline(x, x, 0, 39, shapes.fill)
        for y in range(5, 40, 10):
            shapes.hline(y, 0, 71, shapes.xor)
        
        size1 = 50 * math.fabs(math.sin(phase))
        size1_1 = int(size1)
        size1_2 = int(size1 / 2)
        size1_4 = int(size1 / 4)
        size2 = 50 * math.fabs(math.cos(phase))
        size2_1 = int(size2)
        size2_2 = int(size2 / 2)
        size2_4 = int(size2 / 4)
        
        if shape == 0:
            pass
        elif shape == 1:
            shapes.rect(15 - size1_2, 19 - size1_4, 15 + size1_2, 19 + size1_4, drawmode)
            shapes.rect(35 - size2_2, 19 - size2_2, 35 + size2_2, 19 + size2_2, drawmode)
            shapes.rect(55 - size1_4, 19 - size1_2, 55 + size1_4, 19 + size1_2, drawmode)
        elif shape == 2:
            shapes.ellipse(15, 19, size1_2, size1_4, drawmode)
            shapes.ellipse(35, 19, size2_2, size2_2, drawmode)
            shapes.ellipse(55, 19, size1_4, size1_2, drawmode)
        elif shape == 3:
            shapes.lozenge(15, 19, size1_2, size1_4, drawmode)
            shapes.lozenge(35, 19, size2_2, size2_2, drawmode)
            shapes.lozenge(55, 19, size1_4, size1_1, drawmode)
        elif shape == 4:
            shapes.rect_outline(15 - size1_2, 19 - size1_4, 15 + size1_2, 19 + size1_4, drawmode)
            shapes.rect_outline(35 - size2_2, 19 - size2_2, 35 + size2_2, 19 + size2_2, drawmode)
            shapes.rect_outline(55 - size1_4, 19 - size1_2, 55 + size1_4, 19 + size1_2, drawmode)
        else:
            raise Exception("INTERNAL ERROR")

        cur_fps = fps.fps()
        if fps.tock_time() < 4:
            textmode.print_text(0, 0, 
                "1=shapes\n\n^ drawmode\n_ shape\n[]speed", textmode.block)
        else:
            textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)

    elif page == 2:
        if thumby.buttonU.pressed():
            if wavelen > 18.0:
                wavelen -= 0.5
        elif thumby.buttonD.pressed():
            wavelen += 0.5
        wavelen2 += 0.2 * dt * (wavelen - wavelen2)
        
        thumby.display.fill(0)
        for x in range(5, 72, 10):
            shapes.vline(x, x, 0, 39, shapes.fill)
        for y in range(5, 40, 10):
            shapes.hline(y, 0, 71, shapes.xor)

        phase += speed * 1.0 * dt
        if phase > 2.0 * math.pi:
            phase -= 2.0 * math.pi # keep phase accurate in long-running demo
        shapes.twister(phase=phase, wavelen1=wavelen, wavelen2=wavelen2)
        
        cur_fps = fps.fps()
        if fps.tock_time() < 4:
            textmode.print_text(0, 0, 
                "2=twister\n\n^ tighten\n_ loosen\n[]speed", textmode.block)
        else:
            textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)
    
    elif page == 3:
        if thumby.buttonL.pressed():
            if pspeed > 0.1:
                pspeed -= 0.02
        elif thumby.buttonR.pressed():
            pspeed += 0.02
        elif thumby.buttonU.pressed():
            pheight += 0.1
        elif thumby.buttonD.pressed():
            if pheight > 0.0:
                pheight -= 0.1

        thumby.display.fill(0)
        draw_sky(2)
        l = 0
        for layer in parallax:
            offset = offsets[l]
            offsets[l] -= pspeed * (l + 1)
            while offsets[l] < 0.:
                offsets[l] += 72.
            l += 1
            height = 20. + pheight * l * l
            n = len(layer)
            shp.reset(lower=int(height + 10.))
            x1 = layer[0][0]
            y1 = layer[0][1]
            for i in range(1, n):
                x0, y0 = x1, y1 # shift to next pair of points
                x1 = layer[i][0]
                y1 = layer[i][1]
                shp.line_segment(x0 + offset, height - y0, x1 + offset, height - y1, upper=True)
                if (x1 + offset) >= 72.:
                    offset -= 72. # wrap shape around to left side of screen and redraw this line segment
                    shp.line_segment(x0 + offset, height - y0, x1 + offset, height - y1, upper=True)
            shp.draw(-1, 72, shapes.outline)

        cur_fps = fps.fps()
        if fps.tock_time() < 4:
            textmode.print_text(0, 0, 
                "3=parallax\n\n\n^_ up/down\n[]speed", textmode.block)
        else:
            textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)

    elif page == 4:
        if thumby.buttonU.pressed():
            n_poly += dt # increase/decrease by 1 corner per second
            poly = morphing_polygon(n_poly, obj=poly)
        elif thumby.buttonD.pressed():
            n_poly -= dt
            if n_poly < 3.0:
                n_poly = 3.0
            poly = morphing_polygon(n_poly, obj=poly)

        angle += 6. * (speed + 10.) * dt
        if angle >= 360.:
            angle -= 360.
        sizeA = 25 + 10. * math.sin(phase)
        sizeB = 15. + 15. * math.cos(phase)
        dx = 5. * math.sin(phase * 2)
        
        mode_tick += dt
        if mode_tick >= 4.0:
            mode_tick -= 4.0
            drawmode += 1
            if drawmode > shapes.xor:
                drawmode = shapes.fill
        
        thumby.display.fill(0)
        draw_sky(4)
        poly.draw(24 - dx, 20, drawmode, sx=sizeA / 20., sy=sizeA / 20., angle=angle)
        poly.draw(48 + dx, 20, drawmode, sx=sizeB / 20., sy=sizeB / 20., angle=30 - angle)

        cur_fps = fps.fps()
        if fps.tock_time() < 4:
            textmode.print_text(0, 0, 
                "4=polygons\n\n^ more\n_ fewer\n[]speed", textmode.block)
        else:
            textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)


    else:
        raise Exception("INTERNAL ERROR")

    thumby.display.update()
