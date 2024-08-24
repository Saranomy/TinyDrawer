# ----------------------------------------------------------------------------
# TinyDrawer for Raspberry Pi Pico is licensed under the MLT License.
# Created by Saranomy 2024.
# ----------------------------------------------------------------------------

from machine import Pin, SPI, PWM
import framebuf, time, random, micropython, tiny_drawer, math
from lcd_1inch14 import LCD_1inch14

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

FPS = 8
SHOW_FPS = False
display_w = 240
display_h = 135

td = tiny_drawer.TinyDrawer(display_w = display_w, display_h = display_h)
td.zoom = 1
step = 8 * td.zoom

# how many blocks for snake to move
bar_h = 8 * (td.zoom + 1) # increase the zoom level for drawing sprites on the bottom bar
nx = display_w // step
ny = (display_h - bar_h) // step
start_x = display_w - nx * step
start_y = display_h - bar_h - ny * step
score = 0
alive = True
    
class Apple:
    def __init__(self, fb):
        self.reposition()
        
    def draw(self):
        td.spr(fb, 0, self.x, self.y)
        
    def reposition(self):
        self.x = start_x + random.randint(0, nx - 1) * step
        self.y = start_y + random.randint(0, ny - 1) * step
        
class Snake:
    def __init__(self, fb):
        self.x0 = start_x + (nx // 2) * step
        self.y0 = start_y + (ny // 2) * step
        self.x, self.y = self.x0, self.y0
        self.fb = fb
        self.di = -1
        alive = True
        self.tails = [[self.x, self.y]]
        self.tail_max = 4
    
    def change_direction(self, di):
        global alive, score
        if not alive:
            alive = True
            self.di = -1
            self.x, self.y = self.x0, self.y0
            self.tails = [[self.x, self.y]]
            self.tail_max = 4
            apple.reposition()
            score = 0
        if (di == 0 and self.di != 2) or (di == 1 and self.di != 3) or (di == 2 and self.di != 0) or (di == 3 and self.di != 1):
            self.di = di
            
    def draw(self, apple):
        global score, alive
        if alive:
            # update tails
            if len(self.tails) >= self.tail_max:
                self.tails.pop(0)
            if self.di >= 0:
                self.tails.append([self.x, self.y])
            # update position
            if self.di == 0: # up
                self.y -= step
            elif self.di == 1: # right
                self.x += step
            elif self.di == 2: # down
                self.y += step
            elif self.di == 3 : # left
                self.x -= step
            # handle out of bounds
            if self.di == 3 and self.x < start_x:
                self.x = start_x + (nx - 1) * step
            elif self.di == 1 and self.x > start_x + (nx - 1) * step:
                self.x = start_x
            elif self.di == 0 and self.y < start_y:
                self.y = start_y + (ny - 1) * step
            elif self.di == 2 and self.y > start_y + (ny - 1) * step:
                self.y = start_y
            # eat apple
            if self.x == apple.x and self.y == apple.y:
                apple.reposition()
                score += 1
                self.tail_max += 1
    
        for idx, t in enumerate(self.tails):
            n = 2
            if idx == len(self.tails) - 1:
                n = 1
            elif self.x == t[0] and self.y == t[1]:
                # hit its tail
                alive = False
            # draw its head and tails
            td.spr(self.fb, n, t[0], t[1])

if __name__=='__main__':
        
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(65535) # brightness [0-32768-65535]

    fb = LCD_1inch14(CS, RST, DC, MOSI, SCK, width=display_w, height=display_h)
    
    ret = td.set_buffer_hex("00000000003333000033330000000000000000000000000000000000000000000003030003333330033333300000000000000000000000000000000000000000000330003333333333333333000000000000000000000000000000000000000000888800377337733333333300000000000000000000000000000000000000000878888037133173333333330000000000000000000000000000000000000000088888803333333333333333000000000000000000000000000000000000000008888880033333300333333000000000000000000000000000000000000000000088880000333300003333000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000777700000770000077770000777700077007700777770000777700077777700777777000777000077007700770077007700770077777700770077007777770077007700007700000000770000007700770077007700000077000000000077007700770000770000007770000777700077777700777770007777700000077000770077000077000007700000000077000777770000007700770077000077000077777700007700007700000077007700000077007700770077007700007700000777700007777000777777000777700000007700077770000777700000770000000000000000000000000000000000000000000000000000000000000000000007777000077770000777700077770007700770077777000000000000000000007700770077007700777777077007707777777707777700000000000000000000770077007700770077000007700770770770770770000000000000000000000007777000077777007707770777777077077077077777000000000000000000007700770000007700770077077007707707707707700000000000000000000000770077007700770077777707700770770770770777770000000000000000000007777000077770000777700770077077077077077777000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000777700770077077777077777000000000000000000000000000000000000000777777077007707777707700770000000000000000000000000000000000000077007707700770770000770077000000000000000000000000000000000000007700770770077077777077777700000000000000000000000000000000000000770077077007707700007777700000000000000000000000000000000000000077777700777700777770770077000000000000000000000000000000000000000777700007700077777077007700000000000000000000")
    print(f"Buffer set: {ret}")
    
    apple = Apple(fb)
    snake = Snake(fb)
    
    keyA = Pin(PIN_A, Pin.IN, Pin.PULL_UP)
    keyB = Pin(PIN_B, Pin.IN, Pin.PULL_UP)
    
    key2 = Pin(PIN_UP, Pin.IN, Pin.PULL_UP)
    key3 = Pin(PIN_CTRL, Pin.IN, Pin.PULL_UP)
    key4 = Pin(PIN_LEFT, Pin.IN, Pin.PULL_UP)
    key5 = Pin(PIN_DOWN, Pin.IN, Pin.PULL_UP)
    key6 = Pin(PIN_RIGHT, Pin.IN, Pin.PULL_UP)
    
    elapsed_time = 1000
    f = FPS
    
    # clear the entire screen
    fb.fill(td.color(0))
        
    # report stat before entering draw loop
    micropython.mem_info()
    
    bar_step = 8 * (td.zoom + 1)
    
    while(1):
        start_time = time.ticks_ms()
        if(keyB.value() == 0): # b
            score += 1
        if(key2.value() == 0): # up
            snake.change_direction(0)
        if(key4.value() == 0): # left
            snake.change_direction(3)
        if(key5.value() == 0): # down
            snake.change_direction(2)
        if(key6.value() == 0): # right
            snake.change_direction(1)
        
        # clear the pixels inside the snake area
        fb.fill_rect(start_x, start_y, nx * step, ny * step, td.color(1))
        
        # draw actors
        apple.draw()
        snake.draw(apple)
                
        # increase the zoom level to draw score
        td.zoom += 1
        fb.fill_rect(0, display_h - bar_step, bar_step * 3, bar_step, td.color(0))
        td.spr(fb, 0, 0, display_h - bar_step)
        td.spr(fb, 8 + (score // 10) % 10, bar_step, display_h - bar_step)
        td.spr(fb, 8 + score % 10, bar_step * 2, display_h - bar_step)
        if not alive:
            # draw game over
            td.spr(fb, 18, (display_w - bar_step * 4) // 2, (display_h - bar_step * 2) // 2, w = 4, h = 2)
        td.zoom -= 1
        
        if SHOW_FPS:
            fb.text(f"{f} fps", start_x, start_y, td.color(7))
        
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
