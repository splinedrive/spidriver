#!/usr/bin/env python3
# coding=utf-8
# hack by Hirosh Dabui https://github.com/splinedrive
# mix of git@github.com:pimoroni/st7789-python.git and git@github.com:jamesbowman/spidriver.git 
# works only with fpga to have spimode 2. Quickhack to avoid reflashing the fm8 chip
# I have used blackicemx ice40 based fpga
import array
import getopt
import struct
import sys
import time
import numpy as np
import numbers

from PIL import Image
from spidriver import SPIDriver

ST7789_NOP = 0x00
ST7789_SWRESET = 0x01
ST7789_RDDID = 0x04
ST7789_RDDST = 0x09

ST7789_SLPIN = 0x10
ST7789_SLPOUT = 0x11
ST7789_PTLON = 0x12
ST7789_NORON = 0x13

# ILI9341_RDMODE = 0x0A
# ILI9341_RDMADCTL = 0x0B
# ILI9341_RDPIXFMT = 0x0C
# ILI9341_RDIMGFMT = 0x0A
# ILI9341_RDSELFDIAG = 0x0F

ST7789_INVOFF = 0x20
ST7789_INVON = 0x21
# ILI9341_GAMMASET = 0x26
ST7789_DISPOFF = 0x28
ST7789_DISPON = 0x29

ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C
ST7789_RAMRD = 0x2E

ST7789_PTLAR = 0x30
ST7789_MADCTL = 0x36
ST7789_COLMOD = 0x3A

ST7789_FRMCTR1 = 0xB1
ST7789_FRMCTR2 = 0xB2
ST7789_FRMCTR3 = 0xB3
ST7789_INVCTR = 0xB4
# ILI9341_DFUNCTR = 0xB6
ST7789_DISSET5 = 0xB6

ST7789_GCTRL = 0xB7
ST7789_GTADJ = 0xB8
ST7789_VCOMS = 0xBB

ST7789_LCMCTRL = 0xC0
ST7789_IDSET = 0xC1
ST7789_VDVVRHEN = 0xC2
ST7789_VRHS = 0xC3
ST7789_VDVS = 0xC4
ST7789_VMCTR1 = 0xC5
ST7789_FRCTRL2 = 0xC6
ST7789_CABCCTRL = 0xC7

ST7789_RDID1 = 0xDA
ST7789_RDID2 = 0xDB
ST7789_RDID3 = 0xDC
ST7789_RDID4 = 0xDD

ST7789_GMCTRP1 = 0xE0
ST7789_GMCTRN1 = 0xE1

ST7789_PWCTR6 = 0xFC

class ST7789:
    def __init__(self, sd):
        self.sd = sd
        self.sd.unsel()
        self._invert = True
        self._offset_top = 0
        self._offset_left = 0
        self._width = 240
        self._height = 240
        self._rotation = False

    def write(self, a, c):
        self.sd.seta(a)
        self.sd.sel()
        self.sd.write(c)
        self.sd.unsel()

    def writeCommand(self, cc):
        self.write(0, struct.pack("B", cc))

    def data(self, c):
        self.writeData1(c)

    def writeData(self, c):
        self.write(1, c)

    def writeData1(self, cc):
        self.writeData(struct.pack("B", cc))

    def cmd(self, cc, args=()):
        self.writeCommand(cc)
        n = len(args)
        if n != 0:
            self.writeData(struct.pack(str(n) + "B", *args))

    def command(self, c):
        self.cmd(c,())

    def rect(self, x, y, w, h, color):
        #self.setAddrWindow(x, y, x + w - 1, y + h - 1)
        self.set_window(x, y, x + w - 1, y + h - 1)
        self.writeData(w * h * struct.pack(">H", color))

    def start(self):
        self.sd.setb(1)
        time.sleep(.5)
        self.sd.setb(0)
        time.sleep(.5)
        self.sd.setb(1)
        time.sleep(.5)

#        self.cmd(SWRESET)   # Software reset, 0 args, w/delay
#        time.sleep(.180)
#        self.cmd(SLPOUT)    # Out of sleep mode, 0 args, w/delay
#        time.sleep(.255)
        # Initialize the display.

        self.command(ST7789_SWRESET)    # Software reset
        time.sleep(0.150)               # delay 150 ms

#        self.cmd(SLPOUT)    # Out of sleep mode, 0 args, w/delay
#        time.sleep(.255)

        self.command(ST7789_MADCTL)
        self.data(0x70)

        self.command(ST7789_FRMCTR2)    # Frame rate ctrl - idle mode
        self.data(0x0C)
        self.data(0x0C)
        self.data(0x00)
        self.data(0x33)
        self.data(0x33)

        self.command(ST7789_COLMOD)
        self.data(0x05)

        self.command(ST7789_GCTRL)
        self.data(0x14)

        self.command(ST7789_VCOMS)
        self.data(0x37)

        self.command(ST7789_LCMCTRL)    # Power control
        self.data(0x2C)

        self.command(ST7789_VDVVRHEN)   # Power control
        self.data(0x01)

        self.command(ST7789_VRHS)       # Power control
        self.data(0x12)

        self.command(ST7789_VDVS)       # Power control
        self.data(0x20)

        self.command(0xD0)
        self.data(0xA4)
        self.data(0xA1)

        self.command(ST7789_FRCTRL2)
        self.data(0x0F)

        self.command(ST7789_GMCTRP1)    # Set Gamma
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0D)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2B)
        self.data(0x3F)
        self.data(0x54)
        self.data(0x4C)
        self.data(0x18)
        self.data(0x0D)
        self.data(0x0B)
        self.data(0x1F)
        self.data(0x23)

        self.command(ST7789_GMCTRN1)    # Set Gamma
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0C)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2C)
        self.data(0x3F)
        self.data(0x44)
        self.data(0x51)
        self.data(0x2F)
        self.data(0x1F)
        self.data(0x1F)
        self.data(0x20)
        self.data(0x23)

        if self._invert:
            self.command(ST7789_INVON)   # Invert display
        else:
            self.command(ST7789_INVOFF)  # Don't invert display

        self.command(ST7789_SLPOUT)

#        self.command(ST7789_NORON)
        self.command(ST7789_DISPON)     # Display on
        time.sleep(0.100)               # 100 ms

    def clear(self):
        self.rect(0, 0, 240, 240, 0x0000)

    def loadimage(self, a):
        im = Image.open(a)
        if im.size[0] > im.size[1]:
            im = im.transpose(Image.ROTATE_90)
        w = 240 * im.size[0] // im.size[1]
        im = im.resize((w, 240), Image.ANTIALIAS)
        (w, h) = im.size
        if w > 240:
            im = im.crop((w // 2 - 64, 0, w // 2 + 64, 240))
        elif w < 240:
            c = Image.new("RGB", (240, 240))
            c.paste(im, (64 - w // 2, 0))
            im = c
        st.set_window(0, 0, 240, 240)
        st.writeData(as565(im.convert("RGB")))


    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to width-1,height-1.
        """
        if x1 is None:
            x1 = self._width - 1

        if y1 is None:
            y1 = self._height - 1

        y0 += self._offset_top
        y1 += self._offset_top

        x0 += self._offset_left
        x1 += self._offset_left

        self.command(ST7789_CASET)       # Column addr set
        self.data(x0 >> 8)
        self.data(x0 & 0xFF)             # XSTART
        self.data(x1 >> 8)
        self.data(x1 & 0xFF)             # XEND
        self.command(ST7789_RASET)       # Row addr set
        self.data(y0 >> 8)
        self.data(y0 & 0xFF)             # YSTART
        self.data(y1 >> 8)
        self.data(y1 & 0xFF)             # YEND
        self.command(ST7789_RAMWR)       # write to RAM

    def display(self, image):
        """Write the provided image to the hardware.

        :param image: Should be RGB format and the same dimensions as the display hardware.

        """
        # Set address bounds to entire display.
        self.set_window()
        # Convert image to array of 18bit 666 RGB data bytes.
        # Unfortunate that this copy has to occur, but the SPI byte writing
        # function needs to take an array of bytes and PIL doesn't natively
        # store images in 18-bit 666 RGB format.
        pixelbytes = list(self.image_to_data(image, self._rotation))
        # Write data to hardware.
        for i in range(0, len(pixelbytes), 4096):
            self.writeData(pixelbytes[i:i + 4096])
            #st.writeData(as565(im.convert("RGB")))

    def image_to_data(self, image, rotation=0):
        """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
        # NumPy is much faster at doing this. NumPy code provided by:
        # Keith (https://www.blogger.com/profile/02555547344016007163)
        pb = np.rot90(np.array(image.convert('RGB')), rotation // 90).astype('uint8')

        result = np.zeros((self._width, self._height, 2), dtype=np.uint8)
        result[..., [0]] = np.add(np.bitwise_and(pb[..., [0]], 0xF8), np.right_shift(pb[..., [1]], 5))
        result[..., [1]] = np.add(np.bitwise_and(np.left_shift(pb[..., [1]], 3), 0xE0), np.right_shift(pb[..., [2]], 3))
        return result.flatten().tolist()

if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "h:")
    except getopt.GetoptError as reason:
        print()
        print('usage: st7789 [ -h device ] image...')
        print()
        print()
        sys.exit(1)
    optdict = dict(optlist)

    st = ST7789(SPIDriver(optdict.get('-h', "/dev/ttyUSB0")))
    st.start()
    st.clear()
    for a in args:
      image = Image.open(a)
      image = image.resize((240, 240))
      st.display(image)
      time.sleep(3)
