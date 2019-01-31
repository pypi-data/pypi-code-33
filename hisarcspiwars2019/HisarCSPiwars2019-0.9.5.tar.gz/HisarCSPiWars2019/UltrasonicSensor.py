from time import sleep, time
import RPi.GPIO as GPIO



class UltrasonicSensor:

  def __init__(self, echo, trig, setup=GPIO.BOARD):

    self.echo = echo
    self.trig = trig

    GPIO.setmode(setup)

    GPIO.setup(self.trig,GPIO.OUT)
    GPIO.setup(self.echo,GPIO.IN)

    GPIO.output(trig, False)


  def getDistance(self):

    GPIO.output(self.trig, True)
    sleep(0.0000001)

    signalStart = time()

    while GPIO.input(self.echo):
        sleep(0.0000001)
        signalEnd = time()

        totalTime = signalEnd - signalStart

    return totalTime * 17150
