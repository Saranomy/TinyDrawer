# TinyDrawer

Install [TinyDrawer](https://pypi.org/project/tinydrawer) package on [Thonny](https://thonny.org)

- [Features](#features)
- [Get Started](#get_started)
- [Limitations](#limitations)
- [License](#license)

## 2D Games for Pi Pico
A collection of drawing methods inspired by [PICO-8 game engine](https://www.lexaloffle.com/pico-8.php) built for [Raspberry Pi Pico devices](https://www.raspberrypi.com/products/raspberry-pi-pico) written in [MicroPython](https://micropython.org). These methods handle drawing on the high-level while pushing pixels to the RGB565 [framebuf.FrameBuffer](https://docs.micropython.org/en/latest/library/framebuf.html).

| [Waveshare's Pico LCD 1.14](https://www.waveshare.com/wiki/Pico-LCD-1.14) | [ZhongJungYuan's 1.69 TFT LCD](https://www.aliexpress.com/i/1005004721706705.html) |
| - | - |
| ![waveshare screen](./images/waveshare_pico_lcd_1_14.gif) | ![zhongjungyuan screen](./images/zjy169s0800tg01.gif) |

<a name="features"></a>

## Features

#### Sprite Buffer
Just like PICO-8, TinyDrawer comes with the sprite buffer that can store 32 sprites (8 columns and 4 rows, and each sprite is 8x8 pixels) by default. Design your sprites using [TinyDrawer Sprite Buffer Editor](https://html-preview.github.io/?url=https://github.com/saranomy/tinydrawer/blob/master/editor.html)

![alt text](./images/editor.png)

At the bottom, copy the Hex String, and initialize the TinyDrawer to load this sprite buffer to your program.

#### TinyDrawer

Call `TinyDrawer(hex_string, buffer_w, buffer_h, display_w, display_h, zoom)` to create the TinyDrawer object

```python
import tinydrawer

# Initialize TinyDrawer with the hex string from the Editor
td = TinyDrawer("000877004fff94ff...") # <- arg: your hex string
```

You can change the zoom level and display's width and height

```python
td = TinyDrawer("000877004fff94ff...", display_w = 240, display_h = 135, zoom = 5)
```

You can later change the sprite buffer size by calling `set_buffer_hex(hex_string, buffer_w, buffer_h)`.

```python
# change buffer size to 12 x 2
td.set_buffer_hex("000877004fff94ff...", buffer_w = 12, buffer_h = 2)
```

#### Sprite Index

The sprite index `n` indicates which sprite from the Sprite Buffer should be drawn. The top-left sprite has an index of `n = 0`, while the first sprite in the second row has an index of `n = 8`.

![sprite position](./images/sprites.png)

#### Draw Sprite

Use `spr(fb, n, x, y)` to draw a sprite at index `n` to the framebuf.FrameBuffer `fb` at `x`, `y` position.

```python
# spr(fb, n, x, y, w = 1, h = 1, flip_x = False, flip_y = False)

# draw a 8x8 sprite 0 at (20, 10)
td.spr(fb, 0, 20, 10)

# draw a 16x16 sprite 1 at (120, 30)
td.spr(fb, 1, 120, 30, w = 2, h = 2)

# draw a 8x8 sprite 8 but flipping the sprite horizontally
td.spr(fb, 8, 0, 0, flip_x = True)
```

#### Color
TinyDrawer comes with 16 colors:

| Index | Name | Hex |
| - | - | - |
| 0 | Black | ![#000000](https://via.placeholder.com/15/000000/000000?text=+) `#000000` |
| 1 | Dark Blue | ![#242449](https://via.placeholder.com/15/242449/000000?text=+) `#242449` |
| 2 | Dark Purple | ![#6D2449](https://via.placeholder.com/15/6D2449/000000?text=+) `#6D2449` |
| 3 | Dark Green | ![#009249](https://via.placeholder.com/15/009249/000000?text=+) `#009249` |
| 4 | Brown | ![#B64924](https://via.placeholder.com/15/B64924/000000?text=+) `#B64924` |
| 5 | Dark Grey | ![#6D6D49](https://via.placeholder.com/15/6D6D49/000000?text=+) `#6D6D49` |
| 6 | Light Grey | ![#B6B6B6](https://via.placeholder.com/15/B6B6B6/000000?text=+) `#B6B6B6` |
| 7 | White | ![#FFFFFF](https://via.placeholder.com/15/FFFFFF/000000?text=+) `#FFFFFF` |
| 8 | Red | ![#FF0048](https://via.placeholder.com/15/FF0048/000000?text=+) `#FF0048` |
| 9 | Orange | ![#FF9200](https://via.placeholder.com/15/FF9200/000000?text=+) `#FF9200` |
| 10 | Yellow | ![#FFDB24](https://via.placeholder.com/15/FFDB24/000000?text=+) `#FFDB24` |
| 11 | Green | ![#00FF24](https://via.placeholder.com/15/00FF24/000000?text=+) `#00FF24` |
| 12 | Blue | ![#24B6FF](https://via.placeholder.com/15/24B6FF/000000?text=+) `#24B6FF` |
| 13 | Lavender | ![#926d92](https://via.placeholder.com/15/926d92/000000?text=+) `#926d92` |
| 14 | Pink | ![#6D2449](https://via.placeholder.com/15/6D2449/000000?text=+) `#FF4992` |
| 15 | Light Peach | ![#ffDBB6](https://via.placeholder.com/15/ffDBB6/000000?text=+) `#FFDBB6` |

To use a color on the framebuf, call `color(index)` to get the int number in RGB565 color format.

```python
# fill the entire display with black color
fbuff.fill(td.color(0))

# draw an orange rectangle
fbuff.fill_rect(0, 0, 240, 100, td.color(9))
```

#### Replace Color

By default, the black color `0` on the Sprite Buffer is considered as a transparent color when drawing. Use `pal(c0, c1)` to swap colors before drawing.

For example, to draw the black color pixels on the framebuf:
1. On the [Editor](https://html-preview.github.io/?url=https://github.com/saranomy/tinydrawer/blob/master/editor.html), replace black color with white color `0` or any other color
2. Optional: Call `pal()` to reset the palette
3. Call `pal(7, 0)` to replace white `7` with black `0` when drawing
4. Call `str(fb, n, x, y)` to draw
5. Optional: Call `pal()` to clear the color replacement

Another example, we can turn Mario into Luigi by swapping colors at sprite index `0`

```python
# replace any red with green
td.pal(8, 11) 

# draw mario sprite
td.spr(fb, 0, 100, 100)

# reset the color replacement
td.pal()
```

<a name="get_started"></a>

## Get Started

#### Hardware Requirement
In this demo, we will use [Pi Pico W](https://www.pishop.ca/product/raspberry-pi-pico-w/) and [Waveshare's Pico LCD 1.14](https://www.pishop.ca/product/1-14inch-lcd-display-module-for-raspberry-pi-pico-65k-colors-240-135-spi/) which has joystick controller and buttons. We will run *example_mario.py* on the Pico. You can use any device and any display screen as long as they meet the following requirements
- Have a [Raspberry Pi Pico device](https://www.raspberrypi.com/products/raspberry-pi-pico) or Pico compatible device
- Have a SPI [ST7789](https://newhavendisplay.com/content/datasheets/ST7789V.pdf) display connected to Pi Pico
- Make sure the display color format is set to RGB565
- Have a code that can send [framebuf.FrameBuffer](https://docs.micropython.org/en/latest/library/framebuf.html) to the display


#### Install

1. Complete the Get Started guide with the [Pi Pico](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico)
2. Open [Thonny](https://thonny.org), and connect to the Pi Pico

![thonny](./images/thonny.png)

3. Go to Tools -> Manage Packages. Then search for [tinydrawer](https://pypi.org/project/tinydrawer/) and install it to the Pi Pico

![search tinydrawer](./images/tinydrawer.png)

4. Upload `lc_1inch14.py` to the Pi Pico. This is a demo file from [Waveshare's Pico LCD 1.14](https://www.waveshare.com/wiki/Pico-LCD-1.14) tutorial. We modified it to be used on different screen sizes and orientations. If you use a different display, use the demo file from your manufacturer, make sure that the class is a child of `framebuf.FrameBuffer`

```python
class LCD_1inch14(framebuf.FrameBuffer):
    ...
```

4. Upload `example_mario.py` to the Pi Pico
5. Open `example_mario.py` on Thonny, and check the parameters on the TinyDrawer

```python
display_w = 240
display_h = 135

td = TinyDrawer("000877004fff94ff...", display_w = display_w, display_h = display_h)
...
```

6. Run the `example_mario.py` on the Pi Pico. On [Waveshare's Pico LCD 1.14](https://www.waveshare.com/wiki/Pico-LCD-1.14), press the B button to turn off the Mario's autorun mode. Then you can move the player using left stick, right stick and the A button.

#### Next Step
Upload `example_snake.py` and run it

![waveshare snake](./images/snake_on_lcd_1_14.gif)


<a name="license"></a>

## Limitations

Updating more pixels means a drop in framerate since we have to constantly run `spr()`. 

Comment on the `example_mario.py`
- Since the camera does not move, the floor of the level and the background above the coin are drawn before entering the game loop. It won't send the updated pixels to the framebuf to save the computation time.

We will keep optimizing the drawing functions. Feel free to contribute to the project.

<a name="license"></a>

## License

The source code for the site is licensed under the MIT license, which you can find in the LICENSE file.

All graphical assets are licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0).
