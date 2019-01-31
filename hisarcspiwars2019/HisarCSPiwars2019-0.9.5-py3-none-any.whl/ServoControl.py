from time import sleep, time
import RPi.GPIO as GPIO
from threading import Thread
import time

class ServoControl:
    
    def __init__(self, pin=35, GPIOSetup = GPIO.BOARD):
        GPIO.setmode(GPIOSetup)
        
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)
        self.pin = pin
        self.targetAngle = 90
        self.currentAngle = 90
        self.hasSlept = True
        self.isContinuous = False

    
    def setToContinuous(self):
        self.isContinuous = True
        GPIO.output(self.pin, True)
    
    def setToNotContinuous(self):
        self.isContinuous = False
        GPIO.output(self.pin, False)
    
    def __singleTurn__(self):
        signalLength = self.targetAngle / 18 + 2
        GPIO.output(self.pin, True)
        self.pwm.ChangeDutyCycle(signalLength)

        deltaAngle = abs(self.targetAngle - self.currentAngle)
        requiredSleep = deltaAngle / 150
        sleep(requiredSleep)  # experimental value
        GPIO.output(self.pin, False)
        self.pwm.ChangeDutyCycle(0)
        self.currentAngle = self.targetAngle
        self.hasSlept = True
    
    def __continuousTurn__(self):
        duty = self.targetAngle / 18 + 2
        self.pwm.ChangeDutyCycle(duty)
    
    def setAngle(self, angle):

        self.targetAngle = angle

        if self.isContinuous:
            self.__continuousTurn__()
        elif self.hasSlept and (self.currentAngle is not self.targetAngle):
            self.hasSlept = False
            
            Thread(target=self.__singleTurn__(), args=()).start()
