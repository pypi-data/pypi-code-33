import time
import board
import neopixel

class AdafruitLed():
    def __init__(self,num_pixels):
        self.nowColor = (0,0,0)
        self.transferColor = [(5,0,0),(0,5,0),(-5,0,0),(0,0,5),(0,-5,0),(5,0,0),(0,0,-5),(-5,0,0)]
        self.num_pixels = num_pixels
        self.pixels = neopixel.NeoPixel(board.D18, num_pixels)
    
    def flow(self):
        self.nowColor = (0,0,0)
        for i in self.transferColor:
            for j in range(10):
                self.nowColor += i
                for k in range(self.num_pixels):
                    self.pixels[k] = self.nowColor
                    time.sleep(.3)
    
    def changeAll(self,color):
        for i in range(20):
            self.pixels.fill(self.nowColor - self.nowColor * i / 19)
            time.sleep(.1)
        for i in range(20):
            self.pixels.fill(color * i / 19)
            time.sleep(.1)
        self.nowColor = color
    
    def flowAll(self):
        self.nowColor = (0,0,0)
        for i in self.transferColor:
            for j in range(10):
                self.nowColor += i
                for k in range(self.num_pixels):
                    self.pixels[k] = self.nowColor
                time.sleep(.3)