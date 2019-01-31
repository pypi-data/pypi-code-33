import math
from pyRoControl import command as command
from pyRoControl import _intercommunication
from pyRoControl._intercommunication import DESTINATION


class _Motion():
    def __init__(self, intercommon):
        self._intercommon = intercommon

    def move_body(self, relative_x=0, relative_y=0, relative_theta_degree=0,
                  speed_level=1, sync=True):
        des = DESTINATION["Coordinator"]
        cmd = command.MOVE_BODY
        data = {
            'iRelX': float(relative_x),
            'iRelY': float(relative_y),
            'iRelTheta': math.radians(relative_theta_degree),
            'time': int(speed_level),
            'mode': 2,
        }
        packet, serial = _intercommunication.get_packet(des, cmd, data)
        # print("packet", packet)
        self._intercommon.send_message(packet)
        return serial, None

    def move_head(self, yaw_degree=0, pitch_degree=0, speed_level=1,
                  sync=True):
        des = DESTINATION["Coordinator"]
        cmd = command.MOVE_HEAD
        data = {
            'yawAngle': math.radians(yaw_degree),
            'pitchAngle': math.radians(pitch_degree),
            'yawTime': speed_level,
            'pitchTime': speed_level,
            'mode': 2,
        }
        packet, serial = _intercommunication.get_packet(des, cmd, data)
        # print("packet", packet)
        self._intercommon.send_message(packet)
        return serial, None


class _DialogSystem():
    def __init__(self, intercommon):
        self._intercommon = intercommon

    def speak(self, sentence, wait=True):
        des = DESTINATION["Commander"]
        cmd = command.SPEAK
        data = {
            'tts': sentence,
            'type': 11,
            'speed': -1,
            'pitch': -1,
            'volume': -1,
            'waitFactor': -1,
            'readMode': -1,
            'languageId': -1,
            'alwaysListenState': -1,
        }
        packet, serial = _intercommunication.get_packet(des, cmd, data)
        # print("packet", packet)
        self._intercommon.send_message(packet)
        return serial, None

    def set_expression(self, facial, wait=True):
        des = DESTINATION["Commander"]
        cmd = command.SET_EXPRESSION
        data = {
            'face': facial,
            'type': 8,
            'speed': -1,
            'pitch': -1,
            'volume': -1,
            'waitFactor': -1,
            'readMode': -1,
            'languageId': -1,
            'alwaysListenState': -1,
        }
        packet, serial = _intercommunication.get_packet(des, cmd, data)
        # print("packet", packet)
        self._intercommon.send_message(packet)
        return serial, None


class Control():
    """ Zenbo SDK
    """

    def __init__(self, destination):
        self._intercommon = _intercommunication._intercomm(destination)
        self.motion = _Motion(self._intercommon)
        self.robot = _DialogSystem(self._intercommon)

    def release(self):
        self._intercommon.release()
        print('PyZenboSDK released')


def main():
    """
    """


if __name__ == '__main__':
    main()
