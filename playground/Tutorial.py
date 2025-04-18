import time
import thumby
import math

# BITMAP: width: 32, height: 32
bitmap0 = bytearray([0,0,0,0,0,0,0,0,248,8,232,40,40,40,40,40,40,40,40,40,40,232,8,248,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,255,0,63,32,32,32,32,32,32,32,32,32,32,63,0,255,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,255,0,12,12,63,63,12,12,0,0,24,24,3,3,0,255,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,31,16,16,16,16,20,18,16,20,18,16,16,16,16,16,31,0,0,0,0,0,0,0,0])

# Make a sprite object using bytearray (a path to binary file from 'IMPORT SPRITE' is also valid)
thumbySprite = thumby.Sprite(32, 32, bitmap0, key=0)

# Set the FPS (without this call, the default fps is 30)
thumby.display.setFPS(0) # see how fast this can go

bobRate = 250 # Set arbitrary bob rate (higher is slower)
bobRange = 5  # How many pixels to move the sprite up/down (-5px ~ 5px)
barSep = 8 # how far bars are separated
barSpeed = 100 # speed of bars (ms between steps)

def mk_pattern(n):
    pattern = 0
    i = 0
    while (i < 32):
        pattern |= (1 << i)
        i += barSep
    return pattern

@micropython.viper
def fill_pattern(buffer, pattern:int, phase:int, barSep:int):
    buf = ptr8(buffer)
    for x in range(72):
        phi = phase + x
        for ybyte in range(5):
            buf[x + 72 * ybyte] = (pattern >> (phi % barSep))
            phi += 8
            ybyte += 1
        x += 1

t1 = t0 = time.ticks_ms()   # Get time (ms)
dt = 0
phase = 0
ticks_list = [100] * 20
ticks_idx = 0
while not thumby.buttonB.pressed():
    t2 = time.ticks_ms()
    t = time.ticks_diff(t2, t0)
    dt += time.ticks_diff(t2, t1)
    while dt >= barSpeed:
        dt -= barSpeed
        phase += 1
    ticks_list[ticks_idx] = time.ticks_diff(t2, t1)
    ticks_idx = (ticks_idx + 1) % len(ticks_list)
    fps = len(ticks_list) * 1000 / sum(ticks_list)
    t1 = t2

    if thumby.buttonU.justPressed() and barSpeed > 10:
        barSpeed = int(barSpeed / 1.3)
    if thumby.buttonD.justPressed() and barSpeed < 200:
        barSpeed = int(barSpeed * 1.3)
    if thumby.buttonR.justPressed() and barSep < 31:
        barSep += 1
        phase += 1
    if thumby.buttonL.justPressed() and barSep > 2:
        barSep -= 1
        phase -= 1
    if phase >= barSep or phase < 0:
        phase = 0
        
    thumby.display.fill(0) # Fill canvas to black
    
    buf = thumby.display.display.buffer
    pattern = mk_pattern(barSep)
    fill_pattern(buf, pattern, phase, barSep)
    
    if not thumby.buttonA.pressed():
        thumby.display.drawRectangle(0, 0, 72, 40, 1)
        thumby.display.drawFilledRectangle(12, 8, 48, 24, 0)
        thumby.display.drawRectangle(12, 8, 48, 24, 1)

    # Calculate number of pixels to offset sprite for bob animation
    bobOffset = math.sin(t / bobRate) * bobRange
    # Center the sprite using screen and bitmap dimensions and apply bob offset
    thumbySprite.x = 24 - 32//2
    thumbySprite.y = int(round((thumby.display.height/2) - (32/2) + bobOffset))
    # Display the bitmap using bitmap data, position, and bitmap dimensions
    thumby.display.drawSprite(thumbySprite)
    
    thumby.display.drawText(f"{fps:3.0f}", 60 - 3*6 - 2, 32 - 2*10, 1)
    thumby.display.drawText("fps", 60 - 3*6 - 2, 32 - 10, 1)
    
    thumby.display.update()
    