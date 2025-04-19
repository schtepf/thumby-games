import thumby

## TODO: documentation

# bitmap data for 7x8 font: 64 codepoints with 7px x 8px each (= 7 bytes)
font78_fg = bytearray([0,0,0,0,0,0,0,0,0,46,6,0,0,0,0,0,14,0,14,0,0,0,42,20,42,20,42,0,0,42,20,42,20,42,0,0,42,20,42,20,42,0,0,12,30,60,30,12,0,0,0,0,6,8,0,0,0,0,28,62,34,0,0,0,0,34,62,28,0,0,0,20,8,62,8,20,0,0,8,8,62,8,8,0,0,0,64,48,0,0,0,0,8,8,8,8,8,0,0,0,32,0,0,0,0,0,48,56,28,14,6,0,0,28,62,34,34,28,0,0,32,36,62,62,32,0,0,36,50,58,42,36,0,0,34,42,42,62,20,0,0,12,10,8,62,62,0,0,38,46,42,58,18,0,0,28,62,42,42,24,0,0,2,34,50,10,6,0,0,20,62,42,42,20,0,0,4,42,42,62,28,0,0,0,36,0,0,0,0,0,0,68,52,0,0,0,0,0,8,28,54,34,0,0,0,52,52,52,0,0,0,34,54,28,8,0,0,0,4,34,14,4,0,0,0,42,20,42,20,42,0,0,60,62,10,10,60,0,0,62,62,42,42,20,0,0,28,62,34,34,38,0,0,62,62,34,34,28,0,0,62,62,42,42,34,0,0,62,62,10,10,2,0,0,28,62,34,42,58,0,0,62,62,8,8,62,0,0,34,62,62,34,34,0,0,18,34,62,30,2,0,0,62,62,8,20,34,0,0,62,62,32,32,32,0,0,62,6,28,6,62,0,0,62,6,8,48,62,0,0,28,62,34,34,28,0,0,62,62,18,18,12,0,0,28,62,34,50,44,0,0,62,62,18,18,44,0,0,36,46,42,58,18,0,0,2,62,62,2,2,0,0,30,62,32,32,30,0,0,14,30,32,16,14,0,0,30,48,28,48,30,0,0,34,54,8,20,34,0,0,6,62,56,8,6,0,0,38,50,42,38,50,0,8,20,34,8,12,12,0,0,42,20,42,20,42,0,0,24,24,8,34,20,8,0,8,4,114,100,8,0,0,16,38,78,32,16,0])
font78_bg = bytearray([0,0,0,0,0,0,0,0,127,127,127,15,0,0,0,31,31,31,31,31,0,127,127,127,127,127,127,127,127,127,127,127,127,127,127,127,127,127,127,127,127,127,30,63,127,127,127,63,30,0,0,15,31,31,28,0,0,62,127,127,127,119,0,0,119,127,127,127,62,0,62,62,127,127,127,62,62,28,28,127,127,127,28,28,0,224,248,248,120,0,0,28,28,28,28,28,28,28,0,112,112,112,0,0,0,120,124,126,127,63,31,15,63,127,127,127,127,127,62,112,126,127,127,127,127,112,126,127,127,127,127,127,126,127,127,127,127,127,127,62,30,31,31,127,127,127,127,127,127,127,127,127,127,63,62,127,127,127,127,127,62,7,119,127,127,127,31,15,62,127,127,127,127,127,62,14,127,127,127,127,127,62,0,126,126,126,0,0,0,0,238,254,254,126,0,0,0,28,62,127,127,127,119,0,126,126,126,126,126,0,119,127,127,127,62,28,0,14,127,127,127,31,14,0,127,127,127,127,127,127,127,126,127,127,127,127,127,126,127,127,127,127,127,127,62,62,127,127,127,127,127,127,127,127,127,127,127,127,62,127,127,127,127,127,127,119,127,127,127,127,31,31,7,62,127,127,127,127,127,127,127,127,127,127,127,127,127,119,127,127,127,127,119,119,63,127,127,127,127,63,7,127,127,127,127,127,127,119,127,127,127,127,112,112,112,127,127,127,63,127,127,127,127,127,127,127,127,127,127,62,127,127,127,127,127,62,127,127,127,127,63,63,30,62,127,127,127,127,127,126,127,127,127,127,127,127,126,126,127,127,127,127,127,63,7,127,127,127,127,7,7,63,127,127,127,127,127,63,31,63,127,127,127,63,31,63,127,127,126,127,127,63,119,127,127,127,127,127,119,15,127,127,127,127,31,15,127,127,127,127,127,127,127,62,127,127,127,30,30,30,127,127,127,127,127,127,127,60,60,60,127,127,127,62,28,30,255,255,255,254,28,56,127,255,255,255,120,56])

block = const(1)
outline = const(2)
overlay = const(3)
overlay_outline = const(4)

@micropython.viper
def print_text(x: int, y: int, text, mode: int):
    buf = ptr8(thumby.display.display.buffer)
    fg = ptr8(font78_fg)
    bg = ptr8(font78_bg)
    if not(0 <= y < 5):
        return
    for char in text.upper():
        code = int(ord(char)) - 32
        if not(0 <= code <= 63):
            code = 60 # invalid codepoint
        if not(0 <= x < 10):
            continue
        buf_offset = y * 72 + x * 7 + 1
        font_offset = code * 7
        for i in range(7):
            fg_byte = fg[font_offset + i]
            bg_byte = bg[font_offset + i]
            buf_byte = buf[buf_offset + i]
            if mode == block:
                buf[buf_offset + i] = fg_byte
            elif mode == outline:
                buf[buf_offset + i] = bg_byte ^ fg_byte
            elif mode == overlay:
                buf[buf_offset + i] = (buf_byte & (0xff ^ bg_byte)) | fg_byte
            elif mode == overlay_outline:
                buf[buf_offset + i] = (buf_byte | bg_byte) ^ fg_byte
        x += 1
