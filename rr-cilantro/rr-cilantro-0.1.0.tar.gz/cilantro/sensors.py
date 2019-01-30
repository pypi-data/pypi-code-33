from gpiozero import DistanceSensor, LineSensor as CamJamLineSensor


class UltrasoundSensor():
    def __init__(self, trigger: int, echo: int) -> None:
        self.sensor = DistanceSensor(trigger=trigger, echo=echo)

    def get_distance(self) -> float:
        '''
        Gets the distance of an object from the sensor in cm
        '''
        distance_in_cm = self.sensor.distance * 100
        return distance_in_cm

class LineSensor():
    def __init__(self, pin: int) -> None:
        self.line_sensor = CamJamLineSensor(pin)
        self.on_line = False
        self.line_sensor.when_no_line = self._line_not_seen
        self.line_sensor.when_line = self._line_seen

    def _line_not_seen(self):
        self.on_line = True
    
    def _line_seen(self):
        self.on_line = False