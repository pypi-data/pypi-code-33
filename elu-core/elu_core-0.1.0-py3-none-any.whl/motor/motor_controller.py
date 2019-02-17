from .motor import Motor
from .servo import Servo

class MotorController:

    m = ""
    s = ""

    # distance in cm
    maxDistance = 150
    minDistance = 30

    def __init__(self):
        self.m = Motor()
        self.s = Servo()

    def controll(self, ultrasonic, emergency, data):
        
        if emergency == True or data == "MOVE_STOP":
            self.m.emergencyStop()
            self.s.emergencyStop()
            return

        if (ultrasonic['Front_Left'] < self.minDistance or ultrasonic['Front_Right'] < self.minDistance) and (data == 'MOVE_FORWARD' or data == 'MOVE_FORWARD_LEFT' or data == 'MOVE_FORWARD_RIGHT'):
            self.s.emergencyStop()
            self.m.emergencyStop()
            return
        
        if (ultrasonic['Back_Left'] < self.minDistance or ultrasonic['Back_Right'] < self.minDistance) and (data == 'MOVE_BACKWARD' or data == 'MOVE_BACKWARD_LEFT' or data == 'MOVE_BACKWARD_RIGHT'):
            self.s.emergencyStop()
            self.m.emergencyStop()
            return

        if data == "MOVE_FORWARD_LEFT":
            self.m.setDirection(1)
            self.s.setDirection(1)
        elif data == "MOVE_FORWARD_RIGHT":
            self.m.setDirection(1)
            self.s.setDirection(-1)
        elif data == "MOVE_FORWARD":
            self.m.setDirection(1)
            self.s.setDirection(0)
        elif data == "MOVE_BACKWARD_LEFT":
            self.m.setDirection(-1)
            self.s.setDirection(1)
        elif data == "MOVE_BACKWARD_RIGHT":
            self.m.setDirection(-1)
            self.s.setDirection(-1)
        elif data == "MOVE_BACKWARD":
            self.m.setDirection(-1)
            self.s.setDirection(0)
        elif data == "MOVE_LEFT":
            self.s.setDirection(1)
        elif data == "MOVE_RIGHT":
            self.s.setDirection(-1)

        # scaledDistances = self.scaleDistance(ultrasonic)

        # self.calculateMotorSpeed(scaledDistances)

        self.s.update()
        self.m.update()

    # todo
    # For use with pwm
    def calculateMotorSpeed(self, scaledDistances):
        if self.m.getDirection() == 1:
            minScaledDistance = 0

            if scaledDistances['Front_Left'] < scaledDistances['Front_Right']:
                minScaledDistance = scaledDistances['Front_Left']
            else:
                minScaledDistance = scaledDistances['Front_Right']

            self.m.setSpeed(minScaledDistance)
        
        elif self.m.getDirection == -1:
            minScaledDistance = 0

            if scaledDistances['Back_Left'] < scaledDistances['Back_Right']:
                minScaledDistance = scaledDistances['Back_Left']
            else:
                minScaledDistance = scaledDistances['Back_Right']

            self.m.setSpeed(minScaledDistance)

    # todo
    # For use with pwm
    def scaleDistance(self, distances):
        
        for key in distances:
            # ScaledDistance = (actualDistance - MinDistance) / (MaxDistance - MinDistance)
            distances[key] = (distances[key] - self.minDistance) / (self.maxDistance - self.minDistance)
        
        return distances