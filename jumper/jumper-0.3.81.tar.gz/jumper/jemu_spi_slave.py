class JemuSpiSlave(object):
    def __init__(self):
        pass

    def transmit(self, data):
        """
        Sends a byte string to the master. The function returns when all of the bytes were transmitted or when the
        slave select is deasserted.

        :param data: a byte-string of bytes to be sent.
        :return: The data received from the master as a byte string
        """
        pass
