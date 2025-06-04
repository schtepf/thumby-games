import thumby
import textmode
import shapes
from fps import FPS

fps = FPS()
thumby.display.setFPS(10)

while fps.time() < 3.0:
    thumby.display.fill(0)
    fps.tick()
    textmode.print_text(0, 0,
        "@ screens\n% exit\n\n^ modes\n_ bg on/off", textmode.block)
    thumby.display.update()

thumby.display.setFPS(60)
fps.tock()
screen = 1
show_bg = True
use_shapes = False

modes = [
    textmode.block, 
    textmode.outline, 
    textmode.overlay, 
    textmode.overlay_outline, 
    textmode.inverted
]
mode = 0

lines = [
    "This is a",
    "sample of",
    "text we can",
    "display!",
    "  score:42",
    "+ - * / =",
    ".!?.:;\"()",
    "#66 $A % @",
    "   ____",
    " ] good [",
    "   ^^^^",
    ",sweet' &",
    "",
]
shift = 0

scrolltext = "&&& See how nicely 'textmode' renders [ scrolling [ text [ rows [ !!!"
scroll_min_x = -7 * len(scrolltext)
scroll_x = [72.0] * 5
scroll_speed = [0.2, 0.1, 0.6, 1.0, 0.4]

while not thumby.buttonB.justPressed():
    if thumby.buttonA.justPressed():
        screen += 1
        if screen > 3:
            screen = 1
        if screen == 1:
            thumby.display.setFPS(60)
        else:
            thumby.display.setFPS(0)
        fps.tock()
    
    if thumby.buttonD.justPressed():
        show_bg = not show_bg
    if thumby.buttonL.justPressed():
        use_shapes = not use_shapes
    if thumby.buttonU.justPressed():
        mode += 1
        if mode >= len(modes):
            mode = 0
    dpy_mode = modes[mode]

    thumby.display.fill(0)
    if screen == 1 or screen == 2:
        if show_bg:
            if use_shapes:
                for i in range(0, 12, 3):
                    shapes.rect_outline(i, i, 71 - i, 39 - i, 1)
                shapes.rect(12, 12, 71 - 12, 39 - 12, shapes.fill)
            else:
                for i in range(0, 12, 3):
                    thumby.display.drawRectangle(i, i, 72 - 2*i, 40 - 2*i, 1)
                thumby.display.drawFilledRectangle(12, 12, 72 - 2*12, 40 - 2*12, 1)
        for l in range(5):
            textmode.print_text(0, l, lines[(l + shift) % len(lines)], dpy_mode)
        if (fps.frame() % 20) == 0:
            shift += 1 # scroll up text lines every 20 frames

    elif screen == 3:
        if show_bg:
            if use_shapes:
                shapes.rect(12, 8, 59, 31, shapes.fill)
            else:
                thumby.display.drawFilledRectangle(12, 8, 60 - 12, 32 - 8, 1)
        for i in range(5):
            scroll_x[i] -= scroll_speed[i]
            if scroll_x[i] < scroll_min_x:
                scroll_x[i] = 72.0
            textmode.scroll_text(int(scroll_x[i]), i, scrolltext, dpy_mode)
    else:
        raise BaseException("NYI")

    fps.tick()
    cur_fps = fps.fps()
    if screen != 1:
        textmode.print_text(3, 4, f"{cur_fps:5.1f}/s", textmode.overlay)

    thumby.display.update()
