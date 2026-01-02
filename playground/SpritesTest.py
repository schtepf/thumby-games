import thumby
import math
import sprites
import shapes
import textmode
from fps import FPS

balloon_fg = bytearray([240,152,12,228,246,254,254,254,252,252,248,224,3,15,31,63,127,255,191,223,103,59,12,7,0,0,0,0,12,147,97,0,0,0,0,0])
balloon_mask = bytearray([248,252,254,254,255,255,255,255,254,254,252,248,15,31,63,127,255,255,255,255,255,127,63,15,0,0,0,0,31,191,99,1,0,0,0,0])

balloon = sprites.Sprite(12, 24, balloon_fg, balloon_mask)
bobj = sprites.SpriteObj(frames=[balloon])

fps = FPS()
thumby.display.setFPS(0)
fps.tock()

x0 = 0
y0 = 0
invert = False
bobj.friction(1.0, 1.0)

while not thumby.buttonB.pressed():
    dt = fps.frame_time()
    fps.tick()

    if thumby.buttonR.pressed():
        bobj.accel(4, 0)
    elif thumby.buttonL.pressed():
        bobj.accel(-4, 0)
    elif thumby.buttonU.pressed():
        bobj.accel(0, -2)
    elif thumby.buttonD.pressed():
        bobj.accel(0, 2)
    else:
        bobj.accel(0, 0)
    if thumby.buttonA.justPressed():
        invert = not invert

    out_x, out_y = bobj.onscreen()
    if out_x:
        bobj.speed(-bobj.vx, bobj.vy)
    if out_y:
        bobj.speed(bobj.vx, -bobj.vy)

    thumby.display.fill(0)
    for x in range(5, 72, 10):
        shapes.vline(x, x, 0, 39, shapes.fill)
    for y in range(5, 40, 10):
        shapes.hline(y, 0, 71, shapes.xor)

    bobj.update(dt)    
    bobj.draw(invert)

    cur_fps = fps.fps()
    textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)

    thumby.display.update()
