import thumby
import math
import shapes
import textmode
from fps import FPS


fps = FPS()
thumby.display.setFPS(10)

while fps.time() < 2.0:
    thumby.display.fill(0)
    fps.tick()
    textmode.print_text(0, 0,
        "@ cycle\n  modes\n\n% exit", textmode.block)
    thumby.display.update()

thumby.display.setFPS(0)
fps.tock()
mode = 1

size = 20

while not thumby.buttonB.justPressed():
    if thumby.buttonA.justPressed():
        mode += 1
        if mode > 1:
            mode = 1
        # optional mode init code
        fps.tock()

    thumby.display.fill(0)
    fps.tick()

    if mode == 1:
        if thumby.buttonU.pressed():
            size += 1
        elif thumby.buttonD.pressed():
            if size > 1:
                size -= 1

        op = shapes.xor
        if thumby.buttonL.pressed():
            op = shapes.outline
        elif thumby.buttonR.pressed():
            op = shapes.bg_outline

        shapes.ellipse(35, 19, size, size, shapes.bg_outline)
        shapes.lozenge(35, 19, size, shapes.fill)
        shapes.ellipse(15, 19, size // 4, 15, op)
        shapes.rect(41, 10, 66, 30, op)
    
        cur_fps = fps.fps()
        textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)
        textmode.print_text(0, 0, f"{size:3d} px", textmode.overlay)
        if fps.tock_time() < 4:
            textmode.print_text(0, 0, 
                "mode 1\n\n^/_ size  \n[ outline \n] inverted", textmode.block)

    else:
        raise Exception("FUCK")

    thumby.display.update()
