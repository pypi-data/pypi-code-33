# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import numbers
import time
import numpy as np
import atexit

import spidev
import RPi.GPIO as GPIO

from PIL import Image
from PIL import ImageDraw

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

SPI_CLOCK_HZ = 16000000 # 4 MHz

# Constants for interacting with display registers.
ST7735_TFTWIDTH    = 160
ST7735_TFTHEIGHT   = 80

ST7735_NOP         = 0x00
ST7735_SWRESET     = 0x01
ST7735_RDDID       = 0x04
ST7735_RDDST       = 0x09

ST7735_SLPIN       = 0x10
ST7735_SLPOUT      = 0x11
ST7735_PTLON       = 0x12
ST7735_NORON       = 0x13

# ILI9341_RDMODE      = 0x0A
# ILI9341_RDMADCTL    = 0x0B
# ILI9341_RDPIXFMT    = 0x0C
# ILI9341_RDIMGFMT    = 0x0A
# ILI9341_RDSELFDIAG  = 0x0F

ST7735_INVOFF      = 0x20
ST7735_INVON       = 0x21
# ILI9341_GAMMASET    = 0x26
ST7735_DISPOFF     = 0x28
ST7735_DISPON      = 0x29

ST7735_CASET       = 0x2A
ST7735_RASET       = 0x2B
ST7735_RAMWR       = 0x2C
ST7735_RAMRD       = 0x2E

ST7735_PTLAR       = 0x30
ST7735_MADCTL      = 0x36
# ST7735_PIXFMT      = 0x3A
ST7735_COLMOD       = 0x3A

ST7735_FRMCTR1     = 0xB1
ST7735_FRMCTR2     = 0xB2
ST7735_FRMCTR3     = 0xB3
ST7735_INVCTR      = 0xB4
# ILI9341_DFUNCTR     = 0xB6
ST7735_DISSET5      = 0xB6


ST7735_PWCTR1      = 0xC0
ST7735_PWCTR2      = 0xC1
ST7735_PWCTR3      = 0xC2
ST7735_PWCTR4      = 0xC3
ST7735_PWCTR5      = 0xC4
ST7735_VMCTR1      = 0xC5
# ILI9341_VMCTR2      = 0xC7

ST7735_RDID1       = 0xDA
ST7735_RDID2       = 0xDB
ST7735_RDID3       = 0xDC
ST7735_RDID4       = 0xDD

ST7735_GMCTRP1     = 0xE0
ST7735_GMCTRN1     = 0xE1

ST7735_PWCTR6      = 0xFC

# Colours for convenience
ST7735_BLACK       = 0x0000 # 0b 00000 000000 00000
ST7735_BLUE        = 0x001F # 0b 00000 000000 11111
ST7735_GREEN       = 0x07E0 # 0b 00000 111111 00000
ST7735_RED         = 0xF800 # 0b 11111 000000 00000
ST7735_CYAN        = 0x07FF # 0b 00000 111111 11111
ST7735_MAGENTA     = 0xF81F # 0b 11111 000000 11111
ST7735_YELLOW      = 0xFFE0 # 0b 11111 111111 00000
ST7735_WHITE       = 0xFFFF # 0b 11111 111111 11111


def color565(r, g, b):
    """Convert red, green, blue components to a 16-bit 565 RGB value. Components
    should be values 0 to 255.
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def image_to_data(image):
    """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
    # NumPy is much faster at doing this. NumPy code provided by:
    # Keith (https://www.blogger.com/profile/02555547344016007163)
    pb = np.rot90(np.array(image.convert('RGB')), 1).astype('uint16')
    color = ((pb[:,:,0] & 0xF8) << 8) | ((pb[:,:,1] & 0xFC) << 3) | (pb[:,:,2] >> 3)
    return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()

class ST7735(object):
    """Representation of an ST7735 TFT LCD."""

    def __init__(self, port, cs, dc, backlight=None, rst=None, width=ST7735_TFTWIDTH,
        height=ST7735_TFTHEIGHT, spi_speed_hz=4000000):
        """Create an instance of the display using SPI communication.  Must
        provide the GPIO pin number for the D/C pin and the SPI driver.  Can
        optionally provide the GPIO pin number for the reset pin as the rst
        parameter.

        :param port: SPI port number
        :param cs: SPI CS number (0 or 1 for BCM
        """
        self._spi = spidev.SpiDev(port, cs)
        self._spi.mode = 0
        self._spi.lsbfirst = False
        self._spi.max_speed_hz = spi_speed_hz

        self._dc = dc
        self._rst = rst
        self.width = width
        self.height = height

        # Set DC as output.
        GPIO.setup(dc, GPIO.OUT)

        # Setup backlight as output (if provided).
        if backlight is not None:
            GPIO.setup(backlight, GPIO.OUT)

        # Setup reset as output (if provided).
        if rst is not None:
            GPIO.setup(rst, GPIO.OUT)

        # Create an image buffer.
        self.buffer = Image.new('RGB', (width, height))

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or command
        data (False).  Chunk_size is an optional size of bytes to write in a
        single SPI transaction, with a default of 4096.
        """
        # Set DC low for command, high for data.
        GPIO.output(self._dc, is_data)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start+chunk_size, len(data))
            self._spi.xfer(data[start:end])

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            GPIO.output(self._rst, 1)
            time.sleep(0.500)
            GPIO.output(self._rst, 0)
            time.sleep(0.500)
            GPIO.output(self._rst, 1)
            time.sleep(0.500)

    def _init(self):
        # Initialize the display.  Broken out as a separate function so it can
        # be overridden by other displays in the future.
        
        self.command(ST7735_SWRESET)    # Software reset
        time.sleep(0.150)               # delay 150 ms
        
        self.command(ST7735_SLPOUT)     # Out of sleep mode
        time.sleep(0.500)               # delay 500 ms
        
        self.command(ST7735_FRMCTR1)    # Frame rate ctrl - normal mode
        self.data(0x01)                 # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        self.data(0x2C)
        self.data(0x2D)
        
        self.command(ST7735_FRMCTR2)    # Frame rate ctrl - idle mode
        self.data(0x01)                 # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        self.data(0x2C)
        self.data(0x2D)
        
        self.command(ST7735_FRMCTR3)    # Frame rate ctrl - partial mode
        self.data(0x01)                 # Dot inversion mode
        self.data(0x2C)
        self.data(0x2D)
        self.data(0x01)                 # Line inversion mode
        self.data(0x2C)
        self.data(0x2D)
        
        self.command(ST7735_INVCTR)     # Display inversion ctrl
        self.data(0x07)                 # No inversion
        
        self.command(ST7735_PWCTR1)     # Power control
        self.data(0xA2)
        self.data(0x02)                 # -4.6V
        self.data(0x84)                 # auto mode
        
        self.command(ST7735_PWCTR2)     # Power control
        self.data(0x0A)                 # Opamp current small
        self.data(0x00)                 # Boost frequency
        
        self.command(ST7735_PWCTR4)     # Power control
        self.data(0x8A)                 # BCLK/2, Opamp current small & Medium low
        self.data(0x2A)
        
        self.command(ST7735_PWCTR5)     # Power control
        self.data(0x8A)
        self.data(0xEE)
        
        self.command(ST7735_VMCTR1)     # Power control
        self.data(0x0E)
        
        self.command(ST7735_INVON)      # Don't invert display
        
        self.command(ST7735_MADCTL)     # Memory access control (directions)
        self.data(0xC8)                 # row addr/col addr, bottom to top refresh
        
        self.command(ST7735_COLMOD)     # set color mode
        self.data(0x05)                 # 16-bit color
        
        
        self.command(ST7735_CASET)      # Column addr set
        self.data(0x00)                 # XSTART = 0
        self.data(132 - ST7735_TFTHEIGHT)
        self.data(0x00)                 # XEND = 127
        self.data(ST7735_TFTHEIGHT - 1)
        
        self.command(ST7735_RASET)      # Row addr set
        self.data(0x00)                 # XSTART = 0
        self.data(161 - ST7735_TFTWIDTH)
        self.data(0x00)                 # XEND = 159
        self.data(ST7735_TFTWIDTH - 1)
        
        
        self.command(ST7735_GMCTRP1)    # Set Gamma
        self.data(0x02)
        self.data(0x1c)
        self.data(0x07)
        self.data(0x12)
        self.data(0x37)
        self.data(0x32)
        self.data(0x29)
        self.data(0x2d)
        self.data(0x29)
        self.data(0x25)
        self.data(0x2B)
        self.data(0x39)
        self.data(0x00)
        self.data(0x01)
        self.data(0x03)
        self.data(0x10)
        
        self.command(ST7735_GMCTRN1)    # Set Gamma
        self.data(0x03)
        self.data(0x1d)
        self.data(0x07)
        self.data(0x06)
        self.data(0x2E)
        self.data(0x2C)
        self.data(0x29)
        self.data(0x2D)
        self.data(0x2E)
        self.data(0x2E)
        self.data(0x37)
        self.data(0x3F)
        self.data(0x00)
        self.data(0x00)
        self.data(0x02)
        self.data(0x10)
        
        self.command(ST7735_NORON)      # Normal display on
        time.sleep(0.10)                # 10 ms
        
        self.command(ST7735_DISPON)     # Display on
        time.sleep(0.100)               # 100 ms

    def begin(self):
        """Initialize the display.  Should be called once before other calls that
        interact with the display are called.
        """
        self.reset()
        self._init()
        atexit.register(self.clear_on_exit)

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to width-1,height-1.
        """
        if x1 is None:
            x1 = self.width-1

        if y1 is None:
            y1 = self.height-1

        y0 += 26
        y1 += 26

        x0 += 1
        x1 += 1

        self.command(ST7735_CASET)       # Column addr set
        self.data(y0 >> 8)
        self.data(y0)                    # XSTART
        self.data(y1 >> 8)
        self.data(y1)                    # XEND
        self.command(ST7735_RASET)       # Row addr set
        self.data(x0 >> 8)
        self.data(x0)                    # YSTART
        self.data(x1 >> 8)
        self.data(x1)                    # YEND
        self.command(ST7735_RAMWR)       # write to RAM

    def display(self, image=None):
        """Write the display buffer or provided image to the hardware.  If no
        image parameter is provided the display buffer will be written to the
        hardware.  If an image is provided, it should be RGB format and the
        same dimensions as the display hardware.
        """
        # By default write the internal buffer to the display.
        if image is None:
            image = self.buffer
        # Set address bounds to entire display.
        self.set_window()
        # Convert image to array of 16bit 565 RGB data bytes.
        # Unfortunate that this copy has to occur, but the SPI byte writing
        # function needs to take an array of bytes and PIL doesn't natively
        # store images in 16-bit 565 RGB format.
        pixelbytes = list(image_to_data(image))
        # Write data to hardware.
        self.data(pixelbytes)

    def clear(self, color=(0,0,0)):
        """Clear the image buffer to the specified RGB color (default black)."""
        width, height = self.buffer.size
        self.buffer.putdata([color]*(width*height))

    def draw(self):
        """Return a PIL ImageDraw instance for 2D drawing on the image buffer."""
        return ImageDraw.Draw(self.buffer)

    def clear_on_exit(self):
        self.clear()
        self.display()


