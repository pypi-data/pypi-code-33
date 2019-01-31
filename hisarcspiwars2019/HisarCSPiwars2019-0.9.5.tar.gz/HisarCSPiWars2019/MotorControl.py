from pololu_drv8835_rpi import motors
import math



class MotorControl:

    def __init__(self):
        self.rightSpeed = 0
        self.leftSpeed = 0

    def setSpeeds(self, rightSpeed, leftSpeed):

        self.rightSpeed = rightSpeed
        self.leftSpeed = leftSpeed

        480 if rightSpeed>480 else rightSpeed
        -480 if rightSpeed < -480 else rightSpeed

        480 if leftSpeed > 480 else leftSpeed
        -480 if leftSpeed < -480 else leftSpeed



        motors.setSpeeds(rightSpeed, leftSpeed)

    def controllerDataToMotorSpeed(self, x, y, t):
        if (t):
            if (math.copysign(1, x) != math.copysign(1, y)):
                return (int)((-y + x) * 240)
            else:
                return (int)((-y + x) * 480)
        else:
            if (math.copysign(1, x) == math.copysign(1, y)):
                return (int)((-y - x) * 240)
            else:
                return (int)((-y - x) * 480)
