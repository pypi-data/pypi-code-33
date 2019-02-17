import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Ultrasonic:

    # Pin declaration for Raspberry Pi 3b+
    GPIO_ULTRASONIC_FRONT_LEFT = 4
    GPIO_ULTRASONIC_FRONT_RIGHT = 17
    GPIO_ULTRASONIC_BACK_LEFT = 27
    GPIO_ULTRASONIC_BACK_RIGHT = 22
    GPIO_ULTRASONIC_FRONT_LEFT_ECHO = 23
    GPIO_ULTRASONIC_FRONT_RIGHT_ECHO = 24
    GPIO_ULTRASONIC_BACK_LEFT_ECHO = 25
    GPIO_ULTRASONIC_BACK_RIGHT_ECHO = 18

    SPEED_OF_SOUND = 34300

    # The distance for each sensor
    distanceFrontLeft = 0
    distanceFrontRight = 0
    distanceBackLeft = 0
    distanceBackRight = 0

    def __init__(self):
        GPIO.setup(self.GPIO_ULTRASONIC_FRONT_LEFT, GPIO.OUT)
        GPIO.setup(self.GPIO_ULTRASONIC_FRONT_RIGHT, GPIO.OUT)
        GPIO.setup(self.GPIO_ULTRASONIC_BACK_LEFT, GPIO.OUT)
        GPIO.setup(self.GPIO_ULTRASONIC_BACK_RIGHT, GPIO.OUT)
        GPIO.setup(self.GPIO_ULTRASONIC_FRONT_LEFT_ECHO, GPIO.IN)
        GPIO.setup(self.GPIO_ULTRASONIC_FRONT_RIGHT_ECHO, GPIO.IN)
        GPIO.setup(self.GPIO_ULTRASONIC_BACK_LEFT_ECHO, GPIO.IN)
        GPIO.setup(self.GPIO_ULTRASONIC_BACK_RIGHT_ECHO, GPIO.IN)
        time.sleep(1)
        GPIO.output(self.GPIO_ULTRASONIC_FRONT_LEFT, False)
        GPIO.output(self.GPIO_ULTRASONIC_FRONT_RIGHT, False)
        GPIO.output(self.GPIO_ULTRASONIC_BACK_LEFT, False)
        GPIO.output(self.GPIO_ULTRASONIC_BACK_RIGHT, False)

    def getDistance(self, ultrasonic_gpio, echo_gpio):
        GPIO.setup(ultrasonic_gpio, GPIO.OUT)
        GPIO.output(ultrasonic_gpio, True)
        time.sleep(0.00001)
        GPIO.output(ultrasonic_gpio, False)

        starttime = time.time()
        stopp = starttime
        start = starttime

        while  GPIO.input(echo_gpio) == 0:
            start = time.time()
            
        while  GPIO.input(echo_gpio) == 1:
            stopp = time.time()
            
        delta = stopp - start         
        distance = (delta * self.SPEED_OF_SOUND) / 2

        return distance

    def readData(self):

        self.distanceFrontLeft = self.getDistance(self.GPIO_ULTRASONIC_FRONT_LEFT, self.GPIO_ULTRASONIC_FRONT_LEFT_ECHO)
        self.distanceFrontRight = self.getDistance(self.GPIO_ULTRASONIC_FRONT_RIGHT, self.GPIO_ULTRASONIC_FRONT_RIGHT_ECHO)
        self.distanceBackLeft = self.getDistance(self.GPIO_ULTRASONIC_BACK_LEFT, self.GPIO_ULTRASONIC_BACK_LEFT_ECHO)
        self.distanceBackRight = self.getDistance(self.GPIO_ULTRASONIC_BACK_RIGHT, self.GPIO_ULTRASONIC_BACK_RIGHT_ECHO)

    def getData(self):
        data = {"Front_Left": self.distanceFrontLeft, "Front_Right": self.distanceFrontRight, "Back_Left": self.distanceBackLeft, "Back_Right": self.distanceBackRight}
        dataMOCK = {"Front_Left": 10, "Front_Right": 10, "Back_Left": 10, "Back_Right": 10}
        return data