# coding=utf-8
# Copyright 2018 Hugo Ponte.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
DEFAULT_SERVO_CONFIG = {
    1: {
        'id': 1,  # Servo ID
        'model': 'mx',  # Servo model tag, one of 'MX' or 'PRO'
        'min_pos_val': 0,
        'max_pos_val': 4095,
    },
}


def _parse_servo_config_dict(servo_config):
    """Parse, verify, and return a servo config dictionary."""
    assert isinstance(servo_config, dict), "Servo configuration dictionary must be a dictionary."
    for key, value in servo_config.items():
        assert isinstance(key, int), "Keys in servo configuration dictionary must be integers."
        assert isinstance(value, dict), "Values in servo configuration dictionary must be dictionaries."
        assert 'id' in value.keys(), "Individual servo configuration must contain the 'id' field."
        assert isinstance(value['id'], int), "Servo id must be an integer."
        assert 'min_pos_val' in value.keys(), "Individual servo configuration must contain the 'min_pos_val' field."
        assert 'max_pos_val' in value.keys(), "Individual servo configuration must contain the 'max_pos_val' field."
        assert isinstance(value['min_pos_val'], int), "Servo 'min_pos_val' must be an integer."
        assert isinstance(value['max_pos_val'], int), "Servo 'max_pos_val' must be an integer."
        assert value['min_pos_val'] < value['max_pos_val'], "max_pos_val must be > min_pos_val"
        value.update({'range': value['max_pos_val'] - value['min_pos_val']})
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
    return servo_config


class DXLPy(object):
    """Object wraps functionality of Dynamixel API."""

    def __init__(self,
                 device_name='/dev/ttyUSB0',
                 baudrate=1000000,
                 protocol_version=2.0,
                 action_range=[-1.0, 1.0],
                 servo_config=DEFAULT_SERVO_CONFIG,
                 ):
        """ Initialize, creates port handler to device.

        Args:
            device_name: (str) Device name, should be set to "/dev/dynamixel" if using udev rules script.
            baudrate: (int) Baudrate for communicating with the servos.
            protocol_version: (int) Dynamixel API Protocol version.
            action_range: [float, float] [min, max] range for commanded actions.
            servo_config: (dict) Servo configuration dictionary, see DEFAULT_SERVO_CONFIG as an example
        """
        assert isinstance(action_range, list), "Action range must be list of floats."
        assert all([isinstance(_, float) for _ in action_range]), "Action range must be list of floats."
        assert action_range[0] < action_range[1], "Action range must be [min, max]."
        self.action_range = action_range
        self.action_range_range = action_range[1] - action_range[0]
        # Validate and process servo config
        self.servo_config = _parse_servo_config_dict(servo_config)
        # List of servo_ids
        self.servo_ids = [servo['id'] for servo in self.servo_config.values()]
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
        logging.info('Set baudrate to %s' % baudrate)
        # Protocol version determines the packet handler used
        self.protocol_version = protocol_version
        self.packet_handler = dxl.PacketHandler(protocol_version)

    def engage(self, servo_ids=None, engage=True):
        """Engage or disengage servos.

        Args:
            servo_ids: [int] List of integer servo ids to (dis)engage.
            engage: (bool) Engage (True) or Disengage (False).
        """
        servo_ids = servo_ids or self.servo_ids
        assert isinstance(servo_ids, list), "servo_ids must be a list."
        # Different commands for enabling and disabling servos
        if engage:
            logging.info('Enabling torque for servos %s' % servo_ids)
            engage_command = TORQUE_ENABLE
        else:
            logging.info('Disabling torque for servos %s' % servo_ids)
            engage_command = TORQUE_DISABLE
        for servo_id in servo_ids:
            assert isinstance(servo_id, int), "servo_id must be integers."
            assert servo_id in self.servo_ids, "No matching config found for some servo_id %s." % servo_id
            servo_config = self.servo_config[servo_id]
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler,
                                                                            servo_id,
                                                                            servo_config['addr_torque_enable'],
                                                                            engage_command)
            if dxl_comm_result != dxl.COMM_SUCCESS:
                logging.info("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                logging.error("%s" % self.packet_handler.getRxPacketError(dxl_error))
            else:
                logging.info("Dynamixel - %s has been successfully connected" % servo_id)

    def set(self, servo_pos_dict):
        """Set servo positions.

        Args:
            servo_pos_dict: (dict) Dictionary of servo_ids to commanded position.
        """
        assert isinstance(servo_pos_dict, dict), "servo_pos_dict must be a dict."
        for servo_id, pos_value in servo_pos_dict.items():
            assert isinstance(servo_id, int), "servo_id must be integers."
            assert servo_id in self.servo_ids, "No matching config found for some servo_id %s." % servo_id
            servo_config = self.servo_config[servo_id]
            assert self.action_range[0] < pos_value < self.action_range[1], "Commanded pos must be within action_range."
            # Clip to action range boundary and scale for the specific servo
            clipped_pos_value = max(self.action_range[0], min(pos_value, self.action_range[1]))
            scaled_pos_value = clipped_pos_value * (servo_config['range'] / self.action_range_range) + servo_config[
                'min_pos_val']
            logging.info('Commanding position (val) %s for servo %s' % (pos_value, servo_id))
            dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(self.port_handler,
                                                                            servo_id,
                                                                            servo_config['addr_goal_position'],
                                                                            int(scaled_pos_value))
            if dxl_comm_result != dxl.COMM_SUCCESS:
                logging.info("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                logging.error("%s" % self.packet_handler.getRxPacketError(dxl_error))

    def get(self, servo_ids=None):
        """Read position of servos.

        Args:
            servo_ids: [int] List of integer servo ids to read position of.
        """
        servo_ids = servo_ids or self.servo_ids
        assert isinstance(servo_ids, list), "servo_ids must be a list."
        for servo_id in servo_ids:
            assert isinstance(servo_id, int), "servo_id must be integers."
            assert servo_id in self.servo_ids, "No matching config found for some servo_id %s." % servo_id
            servo_config = self.servo_config[servo_id]
            raw_position, dxl_comm_result, dxl_error = self.packet_handler.read4ByteTxRx(self.port_handler,
                                                                                         servo_id,
                                                                                         servo_config[
                                                                                             'addr_present_position'])
            if dxl_comm_result != dxl.COMM_SUCCESS:
                logging.info("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                logging.error("%s" % self.packet_handler.getRxPacketError(dxl_error))
            position = (raw_position - servo_config['min_pos_val']) * (self.action_range_range / servo_config['range'])
            logging.info('Received position %.2f (val %s) for servo %s' % (position, raw_position, servo_id))
        return position
