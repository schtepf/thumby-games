import thumby
import math
import shapes
import textmode
from fps import FPS

fps = FPS()
thumby.display.setFPS(0)
fps.tock()

shp = shapes.Shape()

page = 0 # 0 = start page, 1 = shapes, 2 = twister
drawmode = shapes.fill
shape = 1 # 0 = none, 1 = rect, 2 = ellipse, 3 = lozenge, 4 = rect_outline
speed = 3
wavelen2 = wavelen = 40.0
phase = 0.0

while not thumby.buttonB.pressed():
    if thumby.buttonA.justPressed():
        page += 1
        if page > 2:
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
        
        phase += speed * 0.5 * dt
        if phase > 2.0 * math.pi:
            phase -= 2.0 * math.pi # keep phase accurate in long-running demo
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
        

    else:
        raise Exception("INTERNAL ERROR")

    thumby.display.update()
