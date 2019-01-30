from gpiozero import CamJamKitRobot
from typing import Optional


class Motors():
    def __init__(self):
        self._m0 = 0
        self._m1 = 0
        self._cam_jam_robot = CamJamKitRobot()

    @property
    def m0(self) -> int:
        '''
        Gets the value of Motor 0
        :returns: returns value of Motor 0
        '''
        return self._m0

    @m0.setter
    def m0(self, power: int) -> None:
        '''
        Sets the value of Motor 0
        :param power: Power as a percent
        '''
        self._m0 = power
        self._update_power(m0=power, m1=self._m1)

    @property
    def m1(self) -> int:
        '''
        Gets the value of Motor 1
        :returns: returns value of Motor 1
        '''
        return self._m1

    @m1.setter
    def m1(self, power: int) -> None:
        '''
        Sets the value of Motor 1
        :param power: Power as a percent
        '''
        self._m1 = power
        self._update_power(m0=self._m0, m1=power)

    def _update_power(self, m0: int, m1: int):
        '''
        Sets the power of the motors
        :param m0: Power of motor 0
        :param m1: Power of motor 1
        '''
        normalised_m0 = self._normalise_power(m0)
        normalised_m1 = self._normalise_power(m1)
        self._cam_jam_robot.value = (normalised_m0, normalised_m1)

    @staticmethod
    def _normalise_power(power: int):
        return power/100.0