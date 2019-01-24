# Third party library imports
import psutil


class StateInterface:
    """
    This is the Interface for any new "Sate" object.
    The state objects are meant to describe some sort of current state/value of either the Computer as a whole, a sort
    of Process etc.
    A specific state object has a fixed set of values it represents. How these values are read from the system will be
    hardcoded into them. But the method, which starts this process of getting all the necessary values will have to be
    the same. "acquire" will update the object internal attributes of the object.
    The method "to_dict" will have to return a dictionary of all the values, that are represented by the state object.
    This is necessary to later publish them to their respective MQTT topics. The topic names (at least at the top level)
    will have the same names as the attributes of the state objects.

    CHANGELOG

    Added 28.12.2018
    """
    def acquire(self):
        """
        This method will get called to get the current(!) state of whatever value is being described by the specific
        state class/object and update all the attributes of the object.

        CHANGELOG

        Added 28.12.2018
        :return:
        """
        raise NotImplementedError()

    def to_dict(self):
        """
        This method will return a dictionary, whose keys are the names which the MQTT topics are supposed to have when
        publishing and the values are the values, which are supposed to be published to the MQTT system.

        This is not supposed to call the "acquire" method. This method will merely create a dict from whatever
        information about the values is currently at the disposal of the object.

        CHANGELOG

        Added 28.12.2018

        :return:
        """
        raise NotImplementedError()


class ComputingState(StateInterface):
    """
    This state represents the performance info about the machine on which the script is running. This included the
    percentage of CPU usage, the percentage of RAM usage and the current temperature in degrees celcius.
    All these values will give a slight indication of whether the machine is under an especially heavy load or not

    CHANGELOG

    Added 28.12.2018
    """
    def __init__(self):
        """
        The constructor.

        CHANGELOG

        Added 28.12.2018

        Changed 29.12.2018
        Added the 'temp' attribute which will store the processor temperature
        """
        self.attributes = {
            'cpu':  '0.0',
            'ram':  '0.0',
            'temp': '0.0'
        }

    def acquire(self):
        """
        This function will read all the values about the machine from the operating system and update the object
        attributes with the new values.

        The measurement of the CPU usage takes a second to complete. Please bare this on mind.

        CHANGELOG

        Added 28.12.2018

        Changed 29.12.2018
        Added the acquistion of the cpu temperature value

        :return:
        """
        # Getting the CPU usage as a percentage. The interval=1 makes a blocking call, that observes the CPU usage for
        # one second. The percpu=False makes it so
        # that only a single value is returned, which will be the average over all the cores.
        self.attributes['cpu'] = psutil.cpu_percent(interval=None, percpu=False)

        # Getting the memory stats of the machine. The function actually returns a whole bunch of info. But here we are
        # just using the percentage of used RAM as a indicator. This value is stored in the percent attribute of the
        # returned wrapper object.
        self.attributes['ram'] = psutil.virtual_memory().percent

        # 29.12.2018
        # Getting the temperature of the machine. The function returns a list with multiple values. one for each
        # individual core. We will be using the first value in the list, which will be a more general value for the
        # whole processor chip. And obviously we want the values to be in degrees celsius not fahrenheit. The current
        # attribute of the wrapper object in the list stores the actual sensor reading.
        try:
            self.attributes['temp'] = psutil.sensors_temperatures(fahrenheit=False)['coretemp'][0].current
        except:
            self.attributes['temp'] = '0.0'

    def to_dict(self):
        """
        Creates a dictionary with all the values based on the current attributes of the object

        CHANGELOG

        Added 28.12.2018

        Changed 29.12.2018
        Returning a copy of the internal dict to prevent side effects on the object.

        :return:
        """
        # 29.12.2018
        # We are returning a copy of the dict, because otherwise we would just be returning a reference to the actual
        # internal dict. And if that got modified, this object would be modified as well
        return self.attributes.copy()

    @property
    def cpu(self):
        """
        Property read access to the percentage of CPU usage

        CHANGELOG

        Added 28.12.2018

        :return:
        """
        return self.attributes['cpu']

    @property
    def ram(self):
        """
        Property read access to the percentage of the RAM usage

        CHANGELOG

        Added 28.12.2018

        :return:
        """
        return self.attributes['ram']

    @property
    def temp(self):
        """
        Property read access for the cpu temperature value

        CHANGELOG

        Added 29.12.2018

        :return:
        """
        return self.attributes['temp']


class NetworkState(StateInterface):
    """
    This state represents the network info about the system on which the program is running on.
    Currently this includes the total bytes sent since the start of the system(! not the program)

    CHANGELOG

    Added 28.12.2018
    """
    def __init__(self):
        """
        The constructor.

        CHANGELOG

        Added 28.12.2018
        """
        self.attributes = {
            'bytes_sent': '0',
            'bytes_recv': '0',
        }

    def acquire(self):
        """
        This method reads the values from the operating system and updates the object attributes with the new values.

        CHANGELOG

        Added 28.12.2018

        :return:
        """
        # This function will return the wrapper object which contains all the network statistics
        network_stats = psutil.net_io_counters()

        self.attributes['bytes_sent'] = network_stats.bytes_sent
        self.attributes['bytes_recv'] = network_stats.bytes_recv

    def to_dict(self):
        """
        Returns a dict, which contains all the values of the state, based on the current attributes of the object

        CHANGELOG

        Added 28.12.2018

        Changed 29.12.2018
        Returning a copy of the internal dict to prevent side effects on the object.

        :return:
        """
        # 29.12.2018
        # We are returning a copy of the dict, because otherwise we would just be returning a reference to the actual
        # internal dict. And if that got modified, this object would be modified as well
        return self.attributes.copy()

    @property
    def bytes_sent(self):
        """
        Property read access for the value of sent bytes

        CHANGELOG

        Added 28.12.2018

        :return:
        """
        return self.attributes['bytes_sent']

    @property
    def bytes_recv(self):
        """
        Property read access for the value of received bytes

        CHANGELOG

        Added 28.12.2018

        :return:
        """
        return self.attributes['bytes_recv']

