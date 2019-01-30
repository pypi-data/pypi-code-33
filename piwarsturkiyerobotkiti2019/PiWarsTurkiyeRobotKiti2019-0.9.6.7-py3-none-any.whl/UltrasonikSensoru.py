from time import sleep, time
import RPi.GPIO as GPIO



class UltrasonikSensoru:

  def __init__(self, echo, trig, setup=GPIO.BOARD):

    self.echo = echo
    self.trig = trig

    self.sure = 0

    GPIO.setmode(setup)

    GPIO.setup(self.trig,GPIO.OUT)
    GPIO.setup(self.echo,GPIO.IN)

    GPIO.output(trig, False)


  def mesafeOlc(self):

    sinyal_bitis = 0
    sinyal_baslangic = 0

    GPIO.output(self.trig, True)
    sleep(0.00001)
    GPIO.output(self.trig, False)


    while GPIO.input(self.echo) == 0:
      sinyal_baslangic = time()

      # save time of arrival
    while GPIO.input(self.echo) == 1:
      sinyal_bitis = time()


    self.sure = sinyal_bitis - sinyal_baslangic

    return self.sure * 17150
