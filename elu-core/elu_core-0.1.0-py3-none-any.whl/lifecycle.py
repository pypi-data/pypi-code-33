from .communication.communication import Communication
from .motor.motor_controller import MotorController
from .sensoric.ultrasonic.ultrasonic import Ultrasonic
from .sensoric.emergency_stop.emergency_stop import EmergencyStop

class LifeCycle:

  uss = ""
  emergencyStopComponent = ""
  communication = ""
  motorController = ""
  doPostAfterCycles = 30
  currentCycles = 0
  command = ""
  emergencyStop = False

  def __init__(self):

    self.uss = Ultrasonic()
    self.emergencyStopComponent = EmergencyStop()
    self.communication = Communication('localhost',8080)
    self.motorController = MotorController()

  def run(self):

    while(True):

      # Ultrasonic data
      self.uss.readData()

      # Emergencystop data
      isEmergencyPressed = self.emergencyStopComponent.isPressed()
      
      if not self.emergencyStop:
        self.motorController.controll(self.uss.getData(), isEmergencyPressed, self.command)

      # Motor Should stop and then the emergencystop
      # should block in the next cylce the motorcontroller
      if isEmergencyPressed:
        self.emergencyStop = isEmergencyPressed

      # Communication handling
      self.command = self.communication.pull()

      # Post data to server
      if self.currentCycles >= self.doPostAfterCycles:

        self.currentCycles = 0

        self.communication.send(self.uss.getData())
      
      else:

        self.currentCycles += 1

      # Reset Emergency Stop
      if self.emergencyStop:
        if self.command == 'MOVE_STOP':
          self.emergencyStop = False