"""Python wrapper over Dynamixel API.

The parameters used here are taken from the python example at
https://github.com/ROBOTIS-GIT/DynamixelSDK/blob/master/python/tests/protocol_combined.py

"""

import logging
import dynamixel_sdk as dxl

# Control table address for Dynamixel MX
ADDR_MX_TORQUE_ENABLE = 64  # Control table address is different in Dynamixel model
ADDR_MX_GOAL_POSITION = 116
ADDR_MX_PRESENT_POSITION = 132

# Control table address for Dynamixel PRO
ADDR_PRO_TORQUE_ENABLE = 64
ADDR_PRO_GOAL_POSITION = 116
ADDR_PRO_PRESENT_POSITION = 132

TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque

# Servo config dictionary contains individual per-servo information
DEFAULT_CONFIG = {
    'test_servo': {
        'id': 1,  # Servo ID
        'model': 'mx',  # Servo model tag, one of 'MX' or 'PRO'
        'min': 0,  # Minimum position (MX servos go from 0 to 4095)
        'max': 4095,  # Maximum position
    },
}


def _parse_config_dict(config):
    """Parse, verify, and return a servo config dictionary."""
    assert isinstance(config, dict), "Servo configuration dictionary must be a dictionary."
    for key, value in config.items():
        assert isinstance(key, str), "Keys in servo configuration dictionary must be strings."
        assert isinstance(value, dict), "Values in servo configuration dictionary must be dictionaries."
        assert 'id' in value.keys(), "Individual servo configuration must contain the 'id' field."
        assert isinstance(value['id'], int), "Servo id must be an integer."
        assert 'min' in value.keys(), "Individual servo configuration must contain the 'min' field."
        assert 'max' in value.keys(), "Individual servo configuration must contain the 'max' field."
        assert isinstance(value['min'], int), "Servo 'min' must be an integer."
        assert isinstance(value['max'], int), "Servo 'max' must be an integer."
        assert value['min'] < value['max'], "max must be > min"
        value.update({'range': value['max'] - value['min']})
        assert 'model' in value.keys(), "Individual servo configuration must contain the 'model' field."
        if value['model'] == 'mx':
            value.update({'addr_torque_enable': ADDR_MX_TORQUE_ENABLE})
            value.update({'addr_goal_position': ADDR_MX_GOAL_POSITION})
            value.update({'addr_present_position': ADDR_MX_PRESENT_POSITION})
        elif value['model'] == 'pro':
            value.update({'addr_torque_enable': ADDR_PRO_TORQUE_ENABLE})
            value.update({'addr_goal_position': ADDR_PRO_GOAL_POSITION})
            value.update({'addr_present_position': ADDR_PRO_PRESENT_POSITION})
        else:
            raise AssertionError("Unknown servo model %s " % value['model'])
    return config


class Servos(object):
    """Object wraps functionality of Dynamixel API."""

    def __init__(self,
                 device_name='/dev/ttyUSB0',
                 baudrate=1000000,
                 protocol_version=2.0,
                 action_bounds=[-1.0, 1.0],
                 config=DEFAULT_CONFIG,
                 ):
        """ Initialize, creates port handler to device.

        Args:
            device_name: (str) Device name, should be set to "/dev/dynamixel" if using udev rules script.
            baudrate: (int) Baudrate for communicating with the servos.
            protocol_version: (int) Dynamixel API Protocol version.
            action_bounds: [float, float] [min, max] range for commanded actions.
            config: (dict) Servo configuration dictionary, see DEFAULT_CONFIG as an example
        """
        assert isinstance(action_bounds, list), "Action range must be list of floats."
        assert all([isinstance(_, float) for _ in action_bounds]), "Action range must be list of floats."
        assert action_bounds[0] < action_bounds[1], "Action range must be [min, max]."
        self.action_bounds = action_bounds
        self.action_range = action_bounds[1] - action_bounds[0]
        # Validate and process servo config
        self.config = _parse_config_dict(config)
        self.all_servo_names = [*self.config.keys()]
        # Open port to communicate with U2D2 Device
        self.device_name = device_name
        self.port_handler = dxl.PortHandler(device_name)
        if not self.port_handler.openPort():
            raise IOError('Failed to open device at %s' % device_name)
        logging.info('Opened device at %s' % device_name)
        # Set the baud rate for the device
        self.baudrate = baudrate
        if not self.port_handler.setBaudRate(baudrate):
            raise IOError('Failed to set baudrate %s for device %s' % (baudrate, device_name))
        logging.debug('Set baudrate to %s' % baudrate)
        # Protocol version determines the packet handler used
        self.protocol_version = protocol_version
        self.packet_handler = dxl.PacketHandler(protocol_version)

    def engage(self, servo_names=None, engage=True):
        """Engage or disengage servos.

        Args:
            servo_names: [int] List of integer servo names to (dis)engage.
            engage: (bool) Engage (True) or Disengage (False).
        """
        servo_names = servo_names or self.all_servo_names
        assert isinstance(servo_names, list), "servo_names must be a list."
        # Different commands for enabling and disabling servos
        if engage:
            logging.debug('Enabling torque for servos %s' % servo_names)
            engage_command = TORQUE_ENABLE
        else:
            logging.debug('Disabling torque for servos %s' % servo_names)
            engage_command = TORQUE_DISABLE
        for name in servo_names:
            assert isinstance(name, str), "servo name must be string."
            assert name in self.all_servo_names, "No matching config found for servo name %s." % name
            config = self.config[name]
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler,
                                                                            config['id'],
                                                                            config['addr_torque_enable'],
                                                                            engage_command)
            if dxl_comm_result != dxl.COMM_SUCCESS:
                logging.debug("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                logging.error("%s" % self.packet_handler.getRxPacketError(dxl_error))
            else:
                logging.debug("Dynamixel - %s has been successfully connected" % name)

    def set(self, servo_pos_dict):
        """Set servo positions.

        Args:
            servo_pos_dict: (dict) Dictionary of servo_names to commanded position.
        """
        assert isinstance(servo_pos_dict, dict), "servo_pos_dict must be a dict."
        for name, pos_value in servo_pos_dict.items():
            assert isinstance(name, str), "servo name must be string."
            assert name in self.all_servo_names, "No matching config found for servo name %s." % name
            config = self.config[name]
            assert self.action_bounds[0] <= pos_value <= self.action_bounds[
                1], "Commanded pos must be within action bounds."
            # Clip to action range boundary and scale for the specific servo
            clipped_pos_value = max(self.action_bounds[0], min(pos_value, self.action_bounds[1]))
            scaled_pos_value = (clipped_pos_value - self.action_bounds[0]) * \
                               (config['range'] / self.action_range) + config['min']
            logging.debug('Commanding position %.2f (val %s) for servo %s' % (pos_value, scaled_pos_value, name))
            dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(self.port_handler,
                                                                            config['id'],
                                                                            config['addr_goal_position'],
                                                                            int(scaled_pos_value))
            if dxl_comm_result != dxl.COMM_SUCCESS:
                logging.debug("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                logging.error("%s" % self.packet_handler.getRxPacketError(dxl_error))

    def get(self, servo_names=None):
        """Read position of servos.

        Args:
            servo_names: [int] List of integer servo ids to read position of.
        """
        servo_names = servo_names or self.all_servo_names
        assert isinstance(servo_names, list), "servo_names must be a list."
        positions = []
        for name in servo_names:
            assert isinstance(name, str), "servo name must be string."
            assert name in self.all_servo_names, "No matching config found for servo name %s." % name
            config = self.config[name]
            raw_position, dxl_comm_result, dxl_error = self.packet_handler.read4ByteTxRx(self.port_handler,
                                                                                         config['id'],
                                                                                         config[
                                                                                             'addr_present_position'])
            if dxl_comm_result != dxl.COMM_SUCCESS:
                logging.debug("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                logging.error("%s" % self.packet_handler.getRxPacketError(dxl_error))
            position = (raw_position - config['min']) * (self.action_range / config['range']) + self.action_bounds[0]
            logging.debug('Received position %.2f (val %s) for servo %s' % (position, raw_position, name))
            positions.append(position)
        return positions

    def __del__(self):
        """Disengage servos and close port."""
        self.engage(engage=False)
        self.port_handler.closePort()
