import thumby
import math
import random
import sprites
import shapes
import textmode
from fps import FPS

balloon_fg = bytearray([0,240,152,12,228,246,254,254,254,252,252,248,224,0,0,3,15,31,63,127,255,191,223,103,59,12,7,0,0,0,0,0,0,12,147,97,0,0,0,0,0,0])
balloon_mask = bytearray([240,248,252,254,254,255,255,255,255,254,254,252,248,224,3,15,31,63,127,255,255,255,255,255,127,63,15,7,0,0,0,0,12,31,191,115,1,0,0,0,0,0])

balloon_spr = sprites.Sprite(14, 24, balloon_fg, balloon_mask)

max_sprites = 42
balloons = [sprites.SpriteObj(frames=[balloon_spr], visible=False) for _ in range(max_sprites)]

def random_init(obj: sprites.SpriteObj):
    x = random.uniform(-8.0, 64.0)
    y = random.uniform(40.0, 60.0)
    obj.move(x, y)
    vy = random.uniform(-40.0, -10.0)
    vx = random.uniform(-15.0, 15.0)
    obj.speed(vx, vy)
    obj.accel(0.0, -5.0)
    obj.friction(0.5, 0.0)
    obj.visible(True)

fps = FPS()
thumby.display.setFPS(0)
fps.tock()

invert = False  # toggle inverse display with A button
wind = 0.0      # additional horizontal acceleration from wind (with L, R buttons)
n_sprites = 13  # number of sprites rendered (adjust with U, D buttons)

for i in range(n_sprites):
    random_init(balloons[i])
    balloons[i].update(0)

while not thumby.buttonB.pressed():
    dt = fps.frame_time()
    fps.tick()

    if thumby.buttonU.justPressed():
        if n_sprites < max_sprites:
            n_sprites += 1
            random_init(balloons[n_sprites - 1])
    elif thumby.buttonD.justPressed():
        if n_sprites > 1:
            balloons[n_sprites - 1].visible(False)
            n_sprites -= 1
    elif thumby.buttonA.justPressed():
        invert = not invert

    if thumby.buttonL.pressed():
        wind = -20.0
    elif thumby.buttonR.pressed():
        wind = 20.0
    else:
        wind = 0.0

    thumby.display.fill(0)
    
    if not invert:
        # background grid show only in normal mode
        for x in range(5, 72, 10):
            shapes.vline(x, x, 0, 39, shapes.fill)
        for y in range(5, 40, 10):
            shapes.hline(y, 0, 71, shapes.fill)

    for i in range(n_sprites):
        out_x, out_y = balloons[i].onscreen()
        if out_x or out_y < 0:
            random_init(balloons[i])
        balloons[i].update(dt, ax=wind)
        balloons[i].draw(invert)

    cur_fps = fps.fps()
    if fps.tock_time() < 4:
        textmode.print_text(0, 0, 
            "^ more\n_ fewer\n[] wind\n@ invert\n% exit", textmode.block)
    else:
        textmode.print_text(0, 0, f"n={n_sprites}", textmode.overlay)
        textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)

    thumby.display.update()

    