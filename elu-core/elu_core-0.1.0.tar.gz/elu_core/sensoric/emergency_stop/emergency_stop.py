import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class EmergencyStop:

  # Button input GPIO's
  EMERGENCY_STOP_FRONT = 6
  EMERGENCY_STOP_BACK = 13
  EMERGENCY_STOP_LEFT = 19
  EMERGENCY_STOP_RIGHT = 26
  EMERGENCY_STOP = 4 # NOT IMPLEMENTET

  def __init__(self):
    GPIO.setup(self.EMERGENCY_STOP_FRONT, GPIO.IN)
    GPIO.setup(self.EMERGENCY_STOP_BACK, GPIO.IN)
    GPIO.setup(self.EMERGENCY_STOP_LEFT, GPIO.IN)
    GPIO.setup(self.EMERGENCY_STOP_RIGHT, GPIO.IN)
    GPIO.setup(self.EMERGENCY_STOP, GPIO.IN)

  def isPressed(self):
    isEmergencyPressed = False

    if GPIO.input(self.EMERGENCY_STOP_FRONT) == 1:
      isEmergencyPressed = True
    
    if GPIO.input(self.EMERGENCY_STOP_BACK) == 1:
      isEmergencyPressed = True
    
    if GPIO.input(self.EMERGENCY_STOP_LEFT) == 1:
      isEmergencyPressed = True
    
    if GPIO.input(self.EMERGENCY_STOP_RIGHT) == 1:
      isEmergencyPressed = True

    if GPIO.input(self.EMERGENCY_STOP) == 1:
      isEmergencyPressed = True

    return isEmergencyPressed
    
  def getData(self):
    data = {"Stop": self.EMERGENCY_STOP, "Stop_Front": self.EMERGENCY_STOP_FRONT, "Stop_Back": self.EMERGENCY_STOP_BACK, "Stop_Left": self.EMERGENCY_STOP_LEFT, "Stop_Right": self.EMERGENCY_STOP_RIGHT}
    return data