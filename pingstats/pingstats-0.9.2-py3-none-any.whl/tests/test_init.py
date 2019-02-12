# Please note, these tests **REQUIRE** pytest

# Due to a limitation in using ``stty`` with ``pytest``, any display functions
# using the scaling feature set will not work.

# Due to the method of which ``hipsterplot`` is implemented, testing the output
# of ``hipsterplot.plot`` becomes very difficult to do with pytest.
# TODO Fix tests using ``hipsterplot.plot``

# import pytest
from inspect import getargspec
from random import randint
from os import name

import pingstats


def test_globals_present():
    assert dir(pingstats).count('X_COLUMN_SCALE' and 'Y_ROW_SCALE')
    assert dir(pingstats).count('__version__')
    assert dir(pingstats).count('parser')
    assert dir(pingstats).count('plot_pings')
    assert dir(pingstats).count('get_pings')  # DEBUG api changing
    assert dir(pingstats).count('Pings')


def test_global_values():
    assert pingstats.X_COLUMN_SCALE == 11 if name != 'nt' else 13
    assert pingstats.Y_ROW_SCALE == 0


def test_plot_pings(capsys):  # Superficial tests only, hipsterplot requires terminal
    argspec = getargspec(pingstats.plot_pings)
    assert len(argspec[0]) == 3
    assert argspec[0].count('pings' and 'columns' and 'rows')
    assert argspec[0][0] == 'pings'
    assert argspec[0][1] == 'columns'
    assert argspec[0][2] == 'rows'


class TestPings:
    def test_init(self):
        test_address, test_max = 'test', 45
        test_list = [randint(0, 100) for i in range(100)]
        test_pings = pingstats.Pings(address=test_address,
                                     realtime_data=test_list,
                                     average_data=test_list,
                                     realtime_data_length=test_max,
                                     average_data_length=test_max)

        assert test_address == test_pings.address
        assert test_list == test_pings.realtime_data and test_pings.average_data
        assert test_max == test_pings._realtime_data_length and test_pings._average_data_length

    def test_decode_line(self):
        pingstats.name = 'posix'  # force posix functionality
        assert pingstats.name == 'posix'

        # test gets correct time
        test_line = 'ttl time=2'
        test_float = float(test_line.split('time=')[1].split(' ')[0])
        result = pingstats.Pings('test')._decode_line(test_line)
        assert result == test_float

        # test gets -1 on failed ping
        test_line = '0 received'
        test_float = -1
        result = pingstats.Pings('test')._decode_line(test_line)
        assert result == test_float

        pingstats.name = 'nt'  # force nt functionality
        assert pingstats.name == 'nt'

        # test gets correct time
        test_line = 'ttl time=2ms'
        result = pingstats.Pings('test')._decode_line(test_line)
        test_float = float(test_line.split('time=')[1].split(' ')[0].strip('ms'))
        assert result == test_float

        # test gets correct time as 1ms when ping is under 1ms
        test_line = 'ttl time<1ms'
        test_float = float(test_line.split('time<')[1].split(' ')[0].strip('<ms'))
        result = pingstats.Pings('test')._decode_line(test_line)
        assert result == test_float

        # test gets -1 on failed ping
        test_line = '100% loss'
        test_float = -1
        result = pingstats.Pings('test')._decode_line(test_line)
        assert result == test_float

        # test raises if no data found in ping
        # with pytest.raises(ValueError):
        #     test_line = ''
        #     result = pingstats.Pings()._decode_line(test_line)

        pingstats.name = name  # DEBUG resets tampering with os name

    def test_run_subprocess(self):
        assert pingstats.name == name
        test_address = '127.0.0.1'
        test_result = pingstats.Pings('test')._run_subprocess(test_address)

        test_single_string = ''

        for line in test_result:
            test_single_string += line + '\n'

        print(test_result)
        print(test_single_string)

        assert type(test_result) == list
        assert len(test_result) > 0
        assert test_single_string.count(test_address)

        if name == 'nt':
            assert test_single_string.count('Received = 1')
            assert test_single_string.count('TTL' and 'time')
        else:
            assert test_single_string.count('1 received')
            assert test_single_string.count('tt' and 'time' and 'icmp')

    def test_iter(self):
        test_address, test_max = '127.0.0.1', 22
        test_pings = pingstats.Pings(address=test_address,
                                     realtime_data_length=test_max,
                                     average_data_length=test_max)

        for i, ping in enumerate(test_pings):
            assert type(ping) is float
            assert ping != 0
            assert test_pings.realtime_data[-1] == ping
            assert test_pings.average_data[-1] == sum(test_pings.realtime_data) / len(test_pings.realtime_data)

            assert len(test_pings.realtime_data) == len(test_pings.average_data)
            assert len(test_pings.realtime_data) <= test_max
            assert len(test_pings.average_data) <= test_max

            if i == 30:
                break

    def test_iter_timeout(self):
        # Reset data lists
        address = "172.16.1.255"
        for i, pings in enumerate(pingstats.Pings(address)):
            assert pings == -1

            break
