import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Servo:

    # GPIO
    SERVO_1A = 11
    SERVO_2A = 5

    direction = 0

    def __init__(self):
        GPIO.setup(self.SERVO_1A, GPIO.OUT)
        GPIO.setup(self.SERVO_2A, GPIO.OUT)
        self.emergencyStop()

    def emergencyStop(self):
        self.setDirection(0)
        self.update()
    
    def setDirection(self, direction):
        self.direction = direction

    def update(self):
        if self.direction == 0:
            GPIO.output(self.SERVO_1A, False)
            GPIO.output(self.SERVO_2A, False)
        elif self.direction == 1:
            GPIO.output(self.SERVO_1A, True)
            GPIO.output(self.SERVO_2A, False)
        elif self.direction == -1:
            GPIO.output(self.SERVO_1A, False)
            GPIO.output(self.SERVO_2A, True)
        