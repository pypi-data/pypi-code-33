class JemuCpu(object):
    def __init__(self):
        pass

    def set_core_register(self, register, value):
        """
        Sets the value on a core register

        :param register: Can be either a register number or a string (i.e. "PC, "R15", "LR", etc.)
        :param value:
        """
        pass

    def get_core_register(self, register):
        """
        Gets the value of a core register

        :param register: Can be either a register number or a string (i.e. "PC, "R15", "LR", etc.)
        :return the current value in the register
        """
        pass
