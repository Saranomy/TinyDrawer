# ----------------------------------------------------------------------------
# TinyDrawer for Raspberry Pi Pico is licensed under the MLT License.
# Created by Saranomy 2024.
# ----------------------------------------------------------------------------

from machine import Pin, SPI, PWM
import framebuf, time, random, micropython, math
from lcd_1inch14 import LCD_1inch14
from tinydrawer import TinyDrawer

# setup for lcd_1inch14.py

BL = 13   # blacklight/BLK pin
DC = 8    # data/command pin
RST = 12  # reset/RES pin
MOSI = 11 # serial data line/SDA pin
SCK = 10  # serial clock line/SDL pin
CS = 9    # chip select pin

# input pins

PIN_A = 15
PIN_B = 17
PIN_UP = 2
PIN_CTRL = 3
PIN_LEFT = 16
PIN_DOWN = 18
PIN_RIGHT = 20

# static variables

FPS = 30
SHOW_FPS = True
display_w = 240
display_h = 135

td = TinyDrawer(display_w = display_w, display_h = display_h)

class Coin:
    def __init__(self, x, y, fb):
        self.x, self.y = x, y
        self.count = 0
    def draw(self):
        self.count += 1
        if self.count > 10:
            n = 4
        else:
            n = 3
        if self.count > 20:
            self.count = 0
        td.spr(fb, n, self.x, self.y)

class Player:
    def __init__(self, x, y, fb):
        self.x, self.y = x, y
        self.y_floor = self.y
        self.vy = 0
        self.facing_left = False
        self.fb = fb
        self.autoplay = True
        self.is_luigi = False
        self.next_move = 0
        self.countdown = 0
    def move(self, dx):
        self.facing_left = dx < 0
        self.x += dx * td.zoom
        if self.x < -8 * td.zoom:
            self.x = td.display_w
        elif self.x > td.display_w:
            self.x = -8 * td.zoom
    def draw(self):
        self.y += self.vy
        if self.y < self.y_floor:
            self.vy += td.zoom
        else:
            self.y = self.y_floor
            self.vy = 0
        if self.y == self.y_floor:
            n = 0
        else:
            n = 8
        if self.autoplay:
            if self.countdown == 0:
                self.countdown = random.randint(3, 30)
                self.next_move = random.randint(-1, 1)
            self.countdown -= 1
            self.move(self.next_move)
            if not self.next_move == 0 and random.randint(0, 6) == 0:
                self.jump()
        if self.is_luigi:
            td.pal(8, 11)
        td.spr(fb, n, self.x, self.y, flip_x=self.facing_left)
        td.pal()

    def jump(self):
        if self.vy == 0 and self.y == self.y_floor:
            self.vy = -td.zoom * 4

if __name__=='__main__':
        
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(65535) # brightness [0-32768-65535]

    fb = LCD_1inch14(CS, RST, DC, MOSI, SCK, width=display_w, height=display_h)
    
    td.zoom = 4
    step = 8 * td.zoom
    td.set_buffer_hex("000877004fff94ff000000000000000000000000000000000000000000000000008888804f9994f9000000000000000000000000000000000000000000000000004f5f004999949900000000000aa000000aa00000000000000000000000000000fffff0449994440008880000aa9a00000aa000000000000000000000000000000f44004f494ff90088788000aa9a00000aa000000000000000000000000000008c8c8049f4f9990078887000aa9a00000aa000000000000000000000000000007aca70499499990000f000000aa000000aa0000000000000000000000000000004040049949999000fff00000000000000000000000000000000000000000000087780949994990007770000000000000000000000000000000000000000000088880044444444007787700000000000000000000000000000000000000000004f5f009994999400877780000000000000000000000000000000000000000000fffff0444444440000f0000000000000000000000000000000000000000000000f440094999499000fff000000000000000000000000000000000000000000008c8c874444444400fcccf00000000000000000000000000000000000000000070aca009994999400077700000000000000000000000000000000000000000000040400444444440004040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
    
    player = Player(2 * step, display_h - 2 * step, fb)
    coin = Coin(step, display_h - 4 * step, fb)
    
    keyA = Pin(PIN_A, Pin.IN, Pin.PULL_UP)
    keyB = Pin(PIN_B, Pin.IN, Pin.PULL_UP)
    
    key2 = Pin(PIN_UP, Pin.IN, Pin.PULL_UP)
    key3 = Pin(PIN_CTRL, Pin.IN, Pin.PULL_UP)
    key4 = Pin(PIN_LEFT, Pin.IN, Pin.PULL_UP)
    key5 = Pin(PIN_DOWN, Pin.IN, Pin.PULL_UP)
    key6 = Pin(PIN_RIGHT, Pin.IN, Pin.PULL_UP)
    
    elapsed_time = 1000
    f = FPS
    
    tiles = [
        [-1,9,-1,-1,-1,11,-1], # top row
        [-1,-1,-1,-1,-1,2,10], # bottom row
    ]
    
    # clear the entire screen
    fb.fill(td.color(1))
    
    # paint the area that won't be updated
    for i in range(0, math.ceil(display_w/step)):
        td.spr(fb, 1, i * step, display_h - step)
        
    # report stat before entering draw loop
    micropython.mem_info()
    
    while(1):
        start_time = time.ticks_ms()
        
        # clear 3 rows above the ground
        fb.fill_rect(0, display_h - 4 * step, display_w, 3 * step, td.color(1))
            
        if SHOW_FPS:
            fb.text(f"{f} fps", int(display_w / 2), display_h - 4 * step, td.color(7))
        
        if(keyA.value() == 0): # a
            player.jump()
        if(keyB.value() == 0): # b
            player.autoplay = not player.autoplay
        if(key2.value() == 0): # up
            player.move(0)
        if(key3.value() == 0): # ctrl
            player.move(0)
        if(key4.value() == 0): # left
            player.move(-1)
        if(key5.value() == 0): # down
            player.move(0)
        if(key6.value() == 0): # right
            player.move(1)
        
        # draw tiles
        for y in range(len(tiles)):
            for x in range(len(tiles[0])):
                if tiles[y][x] >= 0:
                    td.spr(fb, tiles[y][x], x * 8 * td.zoom, display_h - 8 * td.zoom * 2 * len(tiles) + (y + 1) * 8 * td.zoom)
        coin.draw()
        player.draw()
        
        # ship the frame
        fb.show()
        
        # update fps
        end_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(end_time, start_time)
        frame_time = 1000 / FPS
        if elapsed_time < frame_time:
            time.sleep((frame_time - elapsed_time) / 1000)
            f = FPS
        elif SHOW_FPS:
            f = "{:.1f}".format(1000 / elapsed_time)