import random
import time

import board
import displayio
import framebufferio
import rgbmatrix

displayio.release_displays()

def apply_life_rule(old, new):
    width = old.width
    height = old.height
    for y in range(height):
        yyy = y * width
        ym1 = ((y + height - 1) % height) * width
        yp1 = ((y + 1) % height) * width
        xm1 = width - 1
        for x in range(width):
            xp1 = (x + 1) % width
            neighbors = (
                old[xm1 + ym1] + old[xm1 + yyy] + old[xm1 + yp1] +
                old[x   + ym1] +                  old[x   + yp1] +
                old[xp1 + ym1] + old[xp1 + yyy] + old[xp1 + yp1])
            new[x+yyy] = neighbors == 3 or (neighbors == 2 and old[x+yyy])
            xm1 = x

def randomize(output, fraction=0.50):
    for i in range(output.height * output.width):
        output[i] = random.random() < fraction

# after xkcd's tribute to John Conway (1937-2020) https://xkcd.com/2293/
conway_data = [
    b'  +++   ',
    b'  + +   ',
    b'  + +   ',
    b'   +    ',
    b'+ +++   ',
    b' + + +  ',
    b'   +  + ',
    b'  + +   ',
    b'  + +   ',
]

def conway(output):
    for i in range(output.height * output.width):
        output[i] = 0
    for i, si in enumerate(conway_data):
        y = output.height - len(conway_data) - 2 + i
        for j, cj in enumerate(si):
            output[(output.width - 8)//2 + j, y] = cj & 1

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)
SCALE = 1
b1 = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 2)
b2 = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 2)
palette = displayio.Palette(2)
tg1 = displayio.TileGrid(b1, pixel_shader=palette)
tg2 = displayio.TileGrid(b2, pixel_shader=palette)
g1 = displayio.Group(max_size=3, scale=SCALE)
g1.append(tg1)
display.show(g1)
g2 = displayio.Group(max_size=3, scale=SCALE)
g2.append(tg2)

palette[1] = 0xffffff
conway(b1)
display.auto_refresh = True
time.sleep(3)
n = 40

while True:
    for _ in range(n):
        display.show(g1)
        apply_life_rule(b1, b2)
        display.show(g2)
        apply_life_rule(b2, b1)

    randomize(b1)
    palette[0] = 0
    palette[1] = (
        (0x0000ff if random.random() > .33 else 0) |
        (0x00ff00 if random.random() > .33 else 0) |
        (0xff0000 if random.random() > .33 else 0)) or 0xffffff
    n = 200