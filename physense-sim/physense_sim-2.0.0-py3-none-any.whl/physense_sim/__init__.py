from guizero import App, Text, PushButton, Picture, Slider, MenuBar
import socket
from threading import Thread
import pygame
from os import path

here = path.abspath(path.dirname(__file__))

# create socket object
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(.1)
host = socket.gethostname()
port = 12345

s.bind((host,port))


r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rport = 6666

pygame.mixer.init()
pygame.mixer.music.load(here + '/buzzer.wav')

# flag for btn push
VAL = 0
light = 1
btn1Val = 0
btn2Val = 0
btn3Val = 0
btn4Val = 0


def lightSense():
   global light
   if (light == 1):
       light = 0
       btnLight.image = here + "/moon.png"
   else:
       light = 1
       btnLight.image = here + "/sun.png"


def tempSense():
   temp = tempSlide.value

   if temp > 99:
       return temp
   elif temp > 9:
       return str(0) + str(temp)
   elif temp >= 0:
       return str("00") + str(temp)
   elif temp < -9:
       return temp
   else:
       return " " + str(temp)


def playBuzzer():
   pygame.mixer.music.play()


def btn1Push():
   global btn1Val

   btn1Val = 1


def btn2Push():
   global btn2Val

   btn2Val = 1


def btn3Push():
   global btn3Val

   btn3Val = 1


def btn4Push():
   global btn4Val

   btn4Val = 1


def readServerValues():
   # obtains values from the server
       try:
           temp, a = s.recvfrom(1024)  # once it receives this value that's it. so store in variable

       except socket.timeout:
               temp = b'test'
               pass


       temp = str(temp)

       temp = temp.strip('b')
       temp = temp.strip('\'')
       temp = temp.strip('\'')
       temp = temp.split(',')

       if (temp[0] == "rled" and temp[1] == "on"):
           ledRPIC.value = here + "/rLedOn.png"

       elif (temp[0] == "rled" and temp[1] == "off"):
           ledRPIC.value = here + "/rLedOff.png"

       elif (temp[0] == "yled" and temp[1] == "on"):
           ledYPIC.value = here + "/yLedOn.png"
       elif (temp[0] == "yled" and temp[1] == "off"):
           ledYPIC.value = here + "/yLedOff.png"

       elif (temp[0] == "gled" and temp[1] == "on"):
           ledGPIC.value = here + "/gLedOn.png"

       elif (temp[0] == "gled" and temp[1] == "off"):
           ledGPIC.value = here + "/gLedOff.png"

       elif (temp[0] == "bled" and temp[1] == "on"):
           ledBPIC.value = here + "/bLedOn.png"
       elif (temp[0] == "bled" and temp[1] == "off"):
           ledBPIC.value = here + "/bLedOff.png"

       elif (temp[0] == "buzz" and temp[1] == "play"):
           playBuzzer()



def sendServerValues():
   global btn1Val, btn2Val, btn3Val, btn4Val

   strTemp = str(light) + str(tempSense()) + str(btn1Val) + str(btn2Val) + str(btn3Val) + str(btn4Val)

   r.sendto(strTemp.encode('utf-8'),(host, rport))  # send as a list and then parse out the two values on the other end

   btn1Val = 0
   btn2Val = 0
   btn3Val = 0
   btn4Val = 0
   # obtains values from the server


myApp = App(title="Physical Programming Simulator", layout="grid", bg='tan', height=575, width=410)

# Define Pictures for LEDs
Text(myApp, text="LED's", size=12, grid=[0, 0])

Text(myApp, text="rled", align="bottom", color="red", size=12, grid=[0, 1])
ledRPIC = Picture(myApp, image=here + "/rLedOff.png", grid=[0, 2])

Text(myApp, text="yled", align="bottom", color="yellow", size=12, grid=[0, 3])
ledYPIC = Picture(myApp, image=here + "/yLedOff.png", grid=[0, 4])

Text(myApp, text="gled", align="bottom", color="green", size=12, grid=[0, 5])
ledGPIC = Picture(myApp, image=here + "/gLedOff.png", grid=[0, 6])

Text(myApp, text="bled", align="bottom", color="blue", size=12, grid=[0, 7])
ledBPIC = Picture(myApp, image=here + "/bLedOff.png", grid=[0, 8])

Text(myApp, text="Push Buttons", size=12, grid=[1, 0])
btn1 = PushButton(myApp, text="Button_1", command=btn1Push, grid=[1, 2])
btn2 = PushButton(myApp, text="Button_2", command=btn2Push, grid=[1, 3])
btn3 = PushButton(myApp, text="Button_3", command=btn3Push, grid=[1, 4])
btn4 = PushButton(myApp, text="Button_4", command=btn4Push, grid=[1, 5])

Text(myApp, text="Light Sensor", size=12, grid=[5, 0])
Text(myApp, text="light", size=12, grid=[5, 1])
btnLight = PushButton(myApp, image=here + "/sun.png", command=lightSense, grid=[5, 2])

Text(myApp, text="Temperature Sensor", size=12, grid=[6, 0])
Text(myApp, text="temp", size=12, grid=[6, 1])
tempSlide = Slider(myApp, start=150, end=-50, horizontal=False, grid=[6, 2, 1, 4])
tempSlide.width = 50
tempSlide.height = 150

Text(myApp, text="Speaker", align="bottom", size=12, grid=[5, 4])
Text(myApp, text="buzz", align="bottom", size=12, grid=[5, 5])
buzzerPIC = Picture(myApp, image=here + "/speaker.png", grid=[5, 6])

Thread(target=myApp.repeat(500, readServerValues)).start()  # originally 500 miliseconds
Thread(target=myApp.repeat(500, sendServerValues)).start()

myApp.display()
