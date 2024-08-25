# ----------------------------------------------------------------------------
# TinyDrawer for Raspberry Pi Pico is licensed under the MLT License.
# Created by Saranomy 2024.
# ----------------------------------------------------------------------------

import framebuf

class TinyDrawer:
    def __init__(self, hex_string: str, buffer_w: int = 8, buffer_h: int = 4, display_w: int = 240, display_h: int = 135, zoom: int = 5):
        """
        Create TinyDrawer object and the buffer that stores sprites. 
        Default buffer is 8 columns by 4 rows where each sprite is 8 by 8 pixels

        Args:
            hex_string (string): A string representation of the sprite buffer, length must be a multiple of 64
            buffer_w (int): A number of sprites the buffer can store horizontally
            buffer_h (int): A number of sprites the buffer can store vertically
            display_w (int): Width of the display in pixels
            display_h (int): Height of the display in pixels
            zoom (int): Scale of the pixels
        """
        if not self.set_buffer_hex(hex_string, buffer_w, buffer_h):
            return
        self.display_w = display_w
        self.display_h = display_h
        self.zoom = zoom
        self.pal_dict = {}
        self.colors = [
            # RGB333 [0-7] to RGB8 [0, 36, 73, 109, 146, 182, 219, 255]
            self.c333_565(0, 0, 0), # 0 black
            self.c333_565(1, 1, 2), # 1 dark-blue
            self.c333_565(3, 1, 2), # 2 dark-purple
            self.c333_565(0, 4, 2), # 3 dark-green
            self.c333_565(5, 2, 1), # 4 brown
            self.c333_565(3, 2, 2), # 5 dark-grey
            self.c333_565(5, 5, 5), # 6 light-grey
            self.c333_565(7, 7, 7), # 7 white
            self.c333_565(7, 0, 2), # 8 red
            self.c333_565(7, 4, 0), # 9 orange
            self.c333_565(7, 6, 1), # 10 yellow
            self.c333_565(0, 7, 1), # 11 green
            self.c333_565(1, 5, 7), # 12 blue
            self.c333_565(4, 3, 4), # 13 lavender
            self.c333_565(7, 3, 5), # 14 pink
            self.c333_565(7, 6, 5), # 15 light-peach
        ]
        
    def set_buffer_hex(self, hex_string: str, buffer_w: int = 8, buffer_h: int = 4) -> bool:
        """
        Set the sprite buffer using string containing hexadecimal numbers (1 character = 1-byte color)
        
        Args:
            hex_string (string): A string representation of the buffer, length must be a multiple of 64
            buffer_w (int): A number of sprites the buffer can store horizontally
            buffer_h (int): A number of sprites the buffer can store vertically
            
        Returns:
            bool: True if buffer is set successfully
        """
        hex_string = hex_string.replace("\n", "").strip().lower()
        buffer = bytes(bytearray(int(char, 16) for char in hex_string))
        if buffer_w < 0 or buffer_h < 0 or len(buffer) != 64 * buffer_w * buffer_h:
            return False
        self.buffer_w = buffer_w
        self.buffer_h = buffer_h
        self.buffer = buffer
        return True
    
    def spr(self, fb: framebuf.FrameBuffer, n: int, x: int, y: int, w: int = 1, h: int = 1, flip_x: bool = False, flip_y: bool = False): 
        """
        Draw the n sprite at x,y position
        
        Args:
            fb (framebuf.FrameBuffer): The frame buffer that stores actual display data
            n (int): The sprite index starting at 0
            x (int): The x position on the actual display
            y (int): The x position on the actual display
            w (int): Width of the sprite (1 = 8 pixels)
            h (int): Height of the sprite (1 = 8 pixels)
            flip_x (bool): True to flip the sprite horizontally when drawing
            flip_y (bool): True to flip the sprite vertically when drawing
        """
        w8, h8 = w * 8, h * 8
        bx0 = (n % self.buffer_w) * 8
        bx1 = bx0 + w8
        if n == 0:
            by0, by1 = 0, h8
        else:
            by0 = (n // self.buffer_w) * 8
            by1 = by0 + h8
        if flip_x:
            h_add = -self.zoom
            x += w8 * self.zoom
        else:
            h_add = self.zoom
        if flip_y:
            v_add = -self.zoom
            y += (h8 - 1) * self.zoom
        else:
            v_add = self.zoom
        dy = y
        for by in range(by0, by1):
            dx = x
            for bx in range(bx0, bx1):
                c = self.buffer[by * self.buffer_w * 8 + bx]
                c_pal = c in self.pal_dict
                if c_pal or c != 0:
                    if c_pal:
                        c = self.pal_dict[c]
                    fb.fill_rect(dx, dy, self.zoom, self.zoom, self.colors[c])
                dx += h_add
            dy += v_add
            
    def pal(self, c0: int = None, c1: int = None):
        """
        Change the colors when drawing, replace c0 with c1. Call pal() to reset
        
        Args:
            c0 (int): The original color to replace
            c1 (int): The new color to use instead
        """
        if isinstance(c0, int) and isinstance(c1, int):
            self.pal_dict[c0] = c1
        else:
            self.pal_dict = {}
            
    def color(self, c: int) -> int:
        """
        Get RGB565 color from tiny_drawer's color index
        
        Args:
            c (int): The color index [0,15] including the end points
            
        Returns:
            int: The color integer in RGB565 format, or the black color if the index is not found
        """
        if c < 0 or c > len(self.colors):
            return self.colors[0]
        return self.colors[c]
    
    def c333_565(self, r: int, g: int, b: int) -> int:
        """
        Convert RGB333 (each color is 3 bits) to RGB565 with 0b_LLL_Bbb_LL_Rrr_LL_Ggg format
        
        Args:
            r (int): The red color index [0-7] including the end points
            g (int): The green color index [0-7] including the end points
            b (int): The blue color index [0-7] including the end points
            
        Returns:
            int: The color integer in RGB565 format
        """
        if r | g | b == 0: return 0
        return 0b111_000_11_000_11_000 | (g & 7) | (r & 7) << 5 | ((b & 7) << 10)

