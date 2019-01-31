class JemuMemory(object):
    def __init__(self):
        pass

    def set(self, address, value, force=False):
        """
        Sets data in the memory

        :param address: address to write the data to
        :param data: Byte string to be written to memory.
        :param force: If True, will write to read only registers as well.
        """
        pass

    def get(self, address, length):
        """
        Reads data from the memory

        :param address: address of the data
        :param length: number of byrtes to be read
        :return: A byte array of the data.
        """
        pass
