import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Motor:

    speed = 0
    direction = 0 # 0 stop, -1 backwards, 1 forwards

    # GPIO's
    M1_1A = 10
    M1_2A = 9
    # M2_3A = 5 # Not in prototype
    # M2_4A = 11 # Not in prototype

    def __init__(self):
        GPIO.setup(self.M1_1A, GPIO.OUT)
        GPIO.setup(self.M1_2A, GPIO.OUT)
        self.emergencyStop()

    def setSpeed(self, speed):
        self.speed = speed

    def getSpeed(self):
        return self.speed
    
    def setDirection(self, direction):
        self.direction = direction

    def getDirection(self):
        return self.direction

    def emergencyStop(self):
        self.setSpeed(0)
        self.setDirection(0)
        self.update()

    def update(self):
        # TODO Add pwm control

        if self.direction == 0:
            GPIO.output(self.M1_1A, False)
            GPIO.output(self.M1_2A, False)
        elif self.direction == 1:
            GPIO.output(self.M1_1A, True)
            GPIO.output(self.M1_2A, False)
        elif self.direction == -1:
            GPIO.output(self.M1_1A, False)
            GPIO.output(self.M1_2A, True)

        