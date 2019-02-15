from .Raspi_PWM_Servo_Driver import PWM

pwm = 0
start = False
def startServo(address):
    global pwm,start
    try:
        pwm = PWM(address)
        pwm.setPWMFreq(50)
        start = True
    except:
        raise BaseException("Bad I2C address")

def setServoPulse(channel, pulse):
    global pwm,start
    if start == False:raise BaseException("please using startServo to set Servo's I2C address")
    pulseLength = 1000000                   # 1,000,000 us per second
    pulseLength /= 50                       # 50 Hz
    pulseLength /= 4096                     # 12 bits of resolution
    pulse /= pulseLength
    pwm.setPWM(channel, 0, int(pulse))