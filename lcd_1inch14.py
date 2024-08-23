# ----------------------------------------------------------------------------
# TinyDrawer for Raspberry Pi Pico is licensed under the MLT License.
# Created by Saranomy 2024.
# ----------------------------------------------------------------------------

from machine import Pin, SPI
import framebuf

class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self, CS, RST, DC, MOSI, SCK, width: int = 240, height: int = 135, orientation: int = 0):
        self.width = width
        self.height = height
        
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)

        self.cs(1)
        self.spi = SPI(1, 31_250_000, polarity = 0, phase = 0, sck = Pin(SCK), mosi = Pin(MOSI), miso = None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display(orientation)
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self, orientation):
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        if orientation == 0:
            self.write_data(0x70)
        elif orientation == 1:
            self.write_data(0xC0)
        elif orientation == 2:
            self.write_data(0xA0)
        else:
            self.write_data(0x00)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)
        
    def show(self):
        if self.height > 135:
            end_col = self.width - 1
            end_page = self.height - 1

            self.write_cmd(0x2A)
            self.write_data((0x00))
            self.write_data(0x00)
            self.write_data((end_col >> 8) & 0xFF)
            self.write_data(end_col & 0xFF)

            self.write_cmd(0x2B)
            self.write_data((0x00))
            self.write_data(0x00)
            self.write_data((end_page >> 8) & 0xFF)
            self.write_data(end_page & 0xFF)
        else:
            self.write_cmd(0x2A)
            self.write_data(0)
            self.write_data(0x28)
            self.write_data(0x01)
            self.write_data(0x17)
            
            self.write_cmd(0x2B)
            self.write_data(0x00)
            self.write_data(0x35)
            self.write_data(0x00)
            self.write_data(0xBB)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
            
        self.spi.write(self.buffer)
        self.cs(1)