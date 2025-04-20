import thumby
import textmode
from fps import FPS

thumby.display.setFPS(2)
fps = FPS(5)

lines = [
    "This is a",
    "sample of",
    "text we can",
    "display!",
    "  score:42",
    "+ - * / =",
    ".!?.:;\"()",
    "   ____",
    " ] good [",
    "   ^^^^",
    ",sweet' &",
    "",
]
      
shift = 0
while not thumby.buttonB.justPressed():
    mode = textmode.block
    if thumby.buttonU.pressed():
        mode = textmode.outline
    elif thumby.buttonL.pressed():
        mode = textmode.overlay
    elif thumby.buttonR.pressed():
        mode = textmode.overlay_outline

    thumby.display.fill(0)
    for i in range(0, 12, 3):
        thumby.display.drawRectangle(i, i, 72 - 2*i, 40 - 2*i, 1)
    thumby.display.drawFilledRectangle(12, 12, 72 - 2*12, 40 - 2*12, 1)
        
    for l in range(5):
        textmode.print_text(0, l, lines[(l + shift) % len(lines)], mode)

    fps.tick()
    cur_fps = fps.fps()
    textmode.print_text(3, 4, f"{cur_fps:3.0f} fps", textmode.inverted)

    shift += 1
    thumby.display.update()
