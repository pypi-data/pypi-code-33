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

    GPIO.output(self.trig, True)
    sleep(0.0000001)
    GPIO.output(self.trig, False)

    sinyal_baslangic = time()
    sinyal_bitis = 0
    while True:
      if GPIO.input(self.echo):
        sinyal_bitis = time()
        break
      if ( abs(time() - sinyal_baslangic) > 1):
        break



    self.sure = sinyal_bitis - sinyal_baslangic

    return self.sure * 17150
