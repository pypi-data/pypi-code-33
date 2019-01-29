"""
------------------------------------------------------------------------------
The MIT License (MIT)
Copyright (c) 2016 Newcastle University
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.import time
------------------------------------------------------------------------------
Author
Kenji Kawase, Artec Co., Ltd. 
We used the script below as reference
https://github.com/casnortheast/microbit_stub/
------------------------------------------------------------------------------
"""
from image import StuduinoBitImage as Image
from machine import Pin, Neopixel
import time
import _thread

""" ---------------------------------------------------------------------- """    
""" The LED display ------------------------------------------------------ """
class StuduinoBitDisplay:
    """Display class represents the 5x5 LED display. 
    
    There is a single display object that has an image.
    """
    
    __PIX_MAXCOLOR = 0xffffff
    __PIX_MIN = 0
    __PIX_SHIFT_R = 16
    __PIX_SHIFT_G = 8
    def __init__(self):
        """Initialise the display.
        """
        self.__last_image = Image(5,5)

        self.__powerPin = Pin(2, Pin.OUT)
        self.__controlPin = Pin(4, Pin.OUT)
        self.__np = Neopixel(self.__controlPin, 25, 0)
        self.__np.clear()
        self.__powerPin.value(True)
        self.__on = True
        
        self.__bgthid = -1

    def __print(self, image, color):
      """Output to the display.
      """
      self.__np.clear()
      #for x in range(5):
      #  for y in range(5):
      for x in range(image.width()):
        for y in range(image.height()):
          val = image.get_pixel_color(x,y, hex=True)
          if (val != 0) and (color is not None):
            val = color
          pos = abs(x-4) * 5 + y + 1
          self.__np.set(pos, val, update=False)
      self.__np.show()

    def get_pixel(self, x, y):
        """Gets the brightness of LED pixel (x,y).
    
        Brightness can be from 0 (LED is off) to 9 (maximum LED brightness).
        """
        pos = abs(x-4) * 5 + y + 1
        val = self.__np.get(pos)
        r = (val >> StuduinoBitDisplay.__PIX_SHIFT_R) & 0x000000ff
        g = (val >> StuduinoBitDisplay.__PIX_SHIFT_G) & 0x000000ff
        b = val & 0x000000ff
        return r,g,b
    
    def set_pixel(self, x, y, color):
        """Set the dsplay at LED pixel (x,y) to color. 
            """
        if (type(color) is tuple) or (type(color) is list):
          val = (color[0]<<StuduinoBitDisplay.__PIX_SHIFT_R)+(color[1]<<StuduinoBitDisplay.__PIX_SHIFT_G)+(color[2])
        elif (type(color) is int):
          val = color
        else:
          raise TypeError('color takes a (R,G,B) or [R,G,B] or #RGB')
        pos = abs(x-4) * 5 + y + 1
        self.__np.set(pos, val, update=True)
        time.sleep_ms(1)

    def clear(self):
        """Clear the display.
        """
        if self.__bgthid != -1:
          _thread.notify(self.__bgthid, _thread.SUSPEND)
          self.__bgthid = -1
  
        self.__last_image = Image(5,5)
        self.__np.clear()
       
    def show(self, iterable, delay=400, *, wait=True, loop=False, clear=False, color=None):
        """Show images or a string on the display.
        
        Shows the images an image at a time or a string a character at a time,
        with delay milliseconds between image/character.
        If loop is True, loop forever.
        If clear is True, clear the screen after showing.
        Usage:
        shows an image:
        display.show(image, delay=0, wait=True, loop=False, clear=False)
        show each image or letter in the iterable:
        display.show(iterable, delay=400, wait=True, loop=False, clear=False)
        """
        
        if iterable is None:
            raise TypeError('not iterable')
            
        if not iterable:
            return
            
        if isinstance(iterable, str):
            iterable = [Image(Image.CHARACTER_MAP.get(c, Image.CHARACTER_MAP.get('?')))
                        for c in iterable]
        
        if isinstance(iterable, Image):
            iterable = [iterable]
            
        for img in iterable:
#            if img != self.__last_image:
            self.__print(img, color)
            self.__last_image = img
            time.sleep_ms(delay)

        if loop:
            self.show(iterable, delay=delay, wait=wait, loop=loop, clear=clear, color=color)
        
        if clear:
            self.clear()
            
        
    def scroll(self, string, delay=150, *, wait=True, loop=False, monospace=False, color=None):
      if wait:
        self.__scroll_th(string, delay=delay, wait=wait, loop=loop, monospace=monospace, color=color)
      else:
        self.__bgthid = _thread.start_new_thread("display", self.__scroll_th, (string, delay), {'wait':wait, 'loop':loop, 'monospace':monospace, 'color':color})
        print(self.__bgthid)

#    def __scroll(self, string, delay=150, *, wait=True, loop=False, monospace=False):
#        """Scroll the string across the display with given delay.
#        
#        In this emulation this is the same as showing the string and clearing
#        the screen.
#        """
#        if not isinstance(string, str):
#            raise TypeError('can\'t convert ', type(string),  'to str implicitly')
#            
#        disp_string = ' ' + string + ' '
#        for i in range(len(disp_string)-1):
#          curr = Image(Image.CHARACTER_MAP.get(disp_string[i], Image(Image.CHARACTER_MAP.get('?'))))
#          next = Image(Image.CHARACTER_MAP.get(disp_string[i+1], Image(Image.CHARACTER_MAP.get('?'))))
#          for i in range(5):
#            time.sleep_ms(delay)
#            img = curr.shift_left(i) + next.shift_right(5-i)
#            self.__print(img)
#            time.sleep_ms(delay)
#            
#        if loop:
#            self.scroll(string, delay=delay, wait=wait, loop=loop, monospace=monospace)
#            
#        self.clear()

    def __scroll_th(self, string, delay=150, *, wait=True, loop=False, monospace=False, color=None):
        """Scroll the string across the display with given delay.
        
        In this emulation this is the same as showing the string and clearing
        the screen.
        """
        _thread.allowsuspend(True)
        
        if not isinstance(string, str):
            raise TypeError('can\'t convert ', type(string),  'to str implicitly')
            
        disp_string = ' ' + string + ' '
        for i in range(len(disp_string)-1):
          curr = Image(Image.CHARACTER_MAP.get(disp_string[i], Image(Image.CHARACTER_MAP.get('?'))))
          next = Image(Image.CHARACTER_MAP.get(disp_string[i+1], Image(Image.CHARACTER_MAP.get('?'))))
          for i in range(5):
            time.sleep_ms(delay)
            bc = curr.__get_base_color()
            img = curr.shift_left(i) + next.shift_right(5-i)
            img.set_base_color(bc)

            ntf = _thread.getnotification()
            if ntf:
              if ntf == _thread.EXIT:
                  # -------------------------------------------------
                  # Return from thread function terminates the thread
                  # -------------------------------------------------
                  #print("TH_FUNC: terminated")
                  return
              elif ntf == _thread.SUSPEND:
                  # -------------------------------------------------------------------
                  # The thread can be suspended using _thread.suspend(th_id) function,
                  # but sometimes it is more convenient to implement the "soft" suspend
                  # -------------------------------------------------------------------
                  #print("TH_FUNC: suspended")
                  # wait for RESUME notification indefinitely, some other thread must
                  # send the resume notification: _thread.notify(th_id, _thread.RESUME)
                  while _thread.wait() != _thread.RESUME:
                      pass
            else:
              self.__print(img, color)
                
            time.sleep_ms(delay)
            
        if loop:
            self.__scroll_th(string, delay=delay, wait=wait, loop=loop, monospace=monospace, color=color)
            
        self.clear()

    def on(self):
        if self.__on:
          return
        self.__on = True
        self.__powerPin.value(self.__on)
        self.show(self.__last_image)
        
    def off(self):
      for x in range(5):
        for y in range(5):
          val = self.get_pixel(x,y)
          self.__last_image.set_pixel_color(x,y,val)
        
      self.__on = False
      self.__powerPin.value(self.__on)
      
    def is_on(self):
        return self.__on
        
display = StuduinoBitDisplay()







