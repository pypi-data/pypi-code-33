from collections import namedtuple
import time
import atexit
import pigpio

Reading =  namedtuple('Reading', 'temp rh')

class Sensor(object):
    def __init__(self, pi, gpio_pin, powered_by=None):
        """Create a new DHT sensor object that reads from a given GPIO pin.

        Parameters
        ----------
        gpio_pin : int
            GPIO pin to read from
        powered_by : int or None
            If not None, this GPIO pin is used to power the sensor
            Otherwise, sensor is powered by 3V3 or 5V pin

        """
        self.pi = pi
        self.data_gpio = gpio_pin
        self.power_gpio = powered_by
        self.data = []
        self.online = False if powered_by is not None else True

        self._rh = -999
        self._temp = -999
    
    def activate(self):
        if self.power_gpio is not None:
            self.pi.write(self.power_gpio, 1)
            self.online = True
    
    def deactivate(self):
        if self.power_gpio is not None:
            self.pi.write(self.power_gpio, 0)
            self.online = False
    
    def read(self, times=1, interval=3):
        """Measures temperature and humidity for a set number of times

        Parameters
        ----------
        times : int
            Number of times to read from the DHT11/22 sensor
        interval : int
            If reading more than 1 time, sets the time interval between reads.
            Minimum interval is 3 seconds for DHT22 and 2 seconds for DHT11.
            Shorter interval hangs the sensor.
        
        Returns
        -------
        list of Reading

        """
        if not self.online:
            raise ValueError('Sensor is not online')

        # Initialize values
        no_response = 0
        MAX_NO_RESPONSE = 2

        hH = 0
        hL = 0
        tH = 0
        tL = 0
        tov = None
        high_tick = 0
        bit = 40
        CS = 0
        def callback(gpio, level, tick):
            """Accumulate the 40 data bits.  Format into 5 bytes, humidity high,
            humidity low, temperature high, temperature low, checksum.
            """
            # access out of scope variables
            nonlocal bit, hH, hL, tH, tL, CS, high_tick, tov
            nonlocal no_response
            # Measure tick diff to get edge
            diff = pigpio.tickDiff(high_tick, tick)
            val = 0

            # Falling edge, high to low
            if level == 0:
                # Edge length determines if bit is 1 or 0.
                # 50 <= diff < 200, 1 bit
                # diff < 50, 0 bit
                # diff >= 200, bad bit
                if diff >= 50:
                    val = 1
                    if diff >= 200:  # Bad bit?
                        CS = 256  # Force bad checksum.
                else:
                    val = 0

                # Format bits into 5 bytes corresponding to 
                # hH : humidity high byte
                # hL : humidity low byte
                # tH : temp high byte
                # tL : temp low byte
                # CS : checksum byte

                if bit >= 40:  # Message complete.
                    bit = 40
                elif bit >= 32:  # In checksum byte.
                    CS = (CS<<1) + val

                    if bit == 39:
                        # 40th bit received.
                        self.pi.set_watchdog(gpio, 0)
                        no_response = 0
                        total = hH + hL + tH + tL

                        # Value of CS will be affected by a bad bit
                        # CS = 256
                        if (total & 255) == CS:  # Is checksum ok?
                            self._rh = ((hH<<8) + hL) * 0.1
                            if tH & 128:  # Negative temperature.
                                mult = -0.1
                                tH = tH & 127
                            else:
                                mult = 0.1
                            self._temp = ((tH<<8) + tL) * mult
                            tov = time.time()
                        else:
                            # BAD CHECKSUM
                            print('ERROR: Bad checksum')

                elif bit >=24:  # in temp low byte
                    # left shift by one and add bit
                    # for example
                    # a = 2  # 0010
                    # bit = 1
                    # a = (a<<1) + bit  # 0010 -> 0100 then add 1 -> 0101 = 5
                    tL = (tL<<1) + val  
                elif bit >=16:  # in temp high byte
                    tH = (tH<<1) + val
                elif bit >= 8:  # in humidity low byte
                    hL = (hL<<1) + val
                elif bit >= 0:  # in humidity high byte
                    hH = (hH<<1) + val
                else:  # header bits
                    pass
                # increment bit by 1
                bit += 1
            # Rising edge, low to high
            elif level == 1:
                high_tick = tick
                # If 0.25 s, then??
                if diff > 250000:
                    bit = -2
                    hH = 0
                    hL = 0
                    tH = 0
                    tL = 0
                    CS = 0
            # No change, watchdog timeout
            else:
                self.pi.set_watchdog(gpio, 0)
                # Too few data bits received.
                if bit < 8:
                    no_response += 1
                    print('ERROR: insufficient bits received ({} bits)'.format(bit))
                    if no_response > MAX_NO_RESPONSE:
                        no_response = 0
                        # Cycle power if sensor is powered by GPIO pin
                        if self.power_gpio is not None:
                            print('Cycling power at GPIO {}...'.format(self.power_gpio))
                            self.online = False
                            self.pi.write(self.power_gpio, 0)
                            time.sleep(2)
                            self.pi.write(self.power_gpio, 1)
                            time.sleep(2)
                            self.online = True
                            print('Done.')
                # Short message receieved.
                elif bit < 39:
                    no_response = 0
                    print('ERROR: message received is shorter than expected ({} bits)'.format(bit))
                # Full message received.
                else:                  
                    no_response = 0

        # def deactivate():
        #     """Deactivates the DHT11/22 sensor.
        #     """
        #     self.pi.set_watchdog(self.data_gpio, 0)
        #     if cb != None:
        #         cb.cancel()
        #     self.pi.stop()
        # atexit.register(deactivate)

        self.pi.set_pull_up_down(self.data_gpio, pigpio.PUD_OFF)
        self.pi.set_watchdog(self.data_gpio, 0) # Kill any watchdogs.

        cb = self.pi.callback(self.data_gpio, pigpio.EITHER_EDGE, callback)

        readings = []
        for _ in range(times):
            # Query the sensor
            if self.online:
                self.pi.write(self.data_gpio, pigpio.LOW)
                time.sleep(0.017) # 17 ms
            self.pi.set_mode(self.data_gpio, pigpio.INPUT)
            self.pi.set_watchdog(self.data_gpio, 200)  # in milliseconds
            time.sleep(0.2)

            readings.append(Reading(self._temp, self._rh))
            time.sleep(interval)

        # Cleanup
        self.pi.set_watchdog(self.data_gpio, 0)
        if cb != None:
            cb.cancel()

        return readings
    
    def read_once(self):
        """Measures temperature and humidity one time

        Returns
        -------
        float, float
            Returns the temperature in degrees Celsius and the humidity

        """
        return self.read()[0]
