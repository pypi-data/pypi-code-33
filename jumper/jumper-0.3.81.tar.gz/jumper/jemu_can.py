class JemuCan(object):
    def __init__(self):
        pass

    def send_base_frame(self, identifier, data, rtr=False, crc=None):
        """
        Sends a base frame to the CAN bus

        :param identifier: 11 bits identifier
        :param data: Byte string of 0-8 bytes.
        :param rtr: If True, RTR bit will be on
        :param crc: Defaults to the actual CRC of the packet. Can be overridden by setting it to any other value than None.
        """
        pass

    def send_extended_frame(self, identifier, data, rtr=False, crc=None):
        """
        Sends a base frame to the CAN bus

        :param identifier: 29 bits identifier
        :param data: Byte string of 0-8 bytes.
        :param rtr: If True, RTR bit will be on
        :param crc: Defaults to the actual CRC of the packet. Can be overridden by setting it to any other value than None.
        """
        pass

    def on_packet(self, callback):
        """
        Registers a callback to be called each time a packet is sent over the bus

        :param callback: A callback function that will be called with the following arguments (identifier, data, rtr, crc, is_extended)
        """
        pass
