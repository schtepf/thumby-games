import thumby
import textmode
from fps import FPS

thumby.display.setFPS(60)
fps = FPS()

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

scrolltext = "&&& See how 'textmode' renders [ scrolling [ text [ rows [ !!!"
scroll_min_x = -7 * len(scrolltext)
scroll_x = 72
      
shift = 0
while not thumby.buttonB.justPressed():
    mode = textmode.block
    if thumby.buttonU.pressed():
        mode = textmode.outline
    elif thumby.buttonL.pressed():
        mode = textmode.overlay
    elif thumby.buttonR.pressed():
        mode = textmode.overlay_outline
    elif thumby.buttonD.pressed():
        mode = textmode.inverted

    thumby.display.fill(0)
    for i in range(0, 12, 3):
        thumby.display.drawRectangle(i, i, 72 - 2*i, 40 - 2*i, 1)
    thumby.display.drawFilledRectangle(12, 12, 72 - 2*12, 40 - 2*12, 1)
        
    for l in range(4):
        textmode.print_text(0, l+1, lines[(l + shift) % len(lines)], mode)
    if (fps.frame() % 20) == 0:
        shift += 1 # scroll up text lines every 20 frames

    textmode.scroll_text(scroll_x, 0, scrolltext, mode)
    scroll_x -= 1
    if scroll_x < scroll_min_x:
        scroll_x = 72

    fps.tick()
    cur_fps = fps.fps()
    textmode.print_text(4, 4, f"{cur_fps:4.1f}/s", textmode.inverted)

    thumby.display.update()
