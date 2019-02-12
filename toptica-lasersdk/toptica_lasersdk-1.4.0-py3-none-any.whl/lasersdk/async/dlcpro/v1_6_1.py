# Generated from 'v1_6_1.xml' on 2019-02-12 07:24:23.146809

from typing import Tuple

from toptica.lasersdk.async.client import AccessLevel
from toptica.lasersdk.async.client import Client

from toptica.lasersdk.async.client import DecofBoolean
from toptica.lasersdk.async.client import DecofInteger
from toptica.lasersdk.async.client import DecofReal
from toptica.lasersdk.async.client import DecofString
from toptica.lasersdk.async.client import DecofBinary

from toptica.lasersdk.async.client import MutableDecofBoolean
from toptica.lasersdk.async.client import MutableDecofInteger
from toptica.lasersdk.async.client import MutableDecofReal
from toptica.lasersdk.async.client import MutableDecofString
from toptica.lasersdk.async.client import MutableDecofBinary

from toptica.lasersdk.async.client import Connection
from toptica.lasersdk.async.client import NetworkConnection
from toptica.lasersdk.async.client import SerialConnection

from toptica.lasersdk.async.client import DecofError
from toptica.lasersdk.async.client import DeviceNotFoundError


class SystemMessages:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._count_new = DecofInteger(client, name + ':count-new')
        self._count = DecofInteger(client, name + ':count')
        self._latest_message = DecofString(client, name + ':latest-message')

    @property
    def count_new(self) -> 'DecofInteger':
        return self._count_new

    @property
    def count(self) -> 'DecofInteger':
        return self._count

    @property
    def latest_message(self) -> 'DecofString':
        return self._latest_message

    async def show_new(self) -> str:
        return await self.__client.exec(self.__name + ':show-new', input_stream=None, output_type=str, return_type=None)

    async def mark_as_read(self, ID: int) -> None:
        assert isinstance(ID, int), "expected type 'int' for parameter 'ID', got '{}'".format(type(ID))
        await self.__client.exec(self.__name + ':mark-as-read', ID, input_stream=None, output_type=None, return_type=None)

    async def show_all(self) -> str:
        return await self.__client.exec(self.__name + ':show-all', input_stream=None, output_type=str, return_type=None)

    async def show_persistent(self) -> str:
        return await self.__client.exec(self.__name + ':show-persistent', input_stream=None, output_type=str, return_type=None)

    async def show_log(self) -> str:
        return await self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)


class FwUpdate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    async def show_history(self) -> str:
        return await self.__client.exec(self.__name + ':show-history', input_stream=None, output_type=str, return_type=None)

    async def upload(self, stream_input: bytes, filename: str) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        assert isinstance(filename, str), "expected type 'str' for parameter 'filename', got '{}'".format(type(filename))
        await self.__client.exec(self.__name + ':upload', filename, input_stream=stream_input, output_type=None, return_type=None)

    async def show_log(self) -> str:
        return await self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)


class ServiceReport:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ready = DecofBoolean(client, name + ':ready')

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    async def service_report(self) -> bytes:
        return await self.__client.exec(self.__name + ':service-report', input_stream=None, output_type=bytes, return_type=None)

    async def request(self) -> None:
        await self.__client.exec(self.__name + ':request', input_stream=None, output_type=None, return_type=None)

    async def print(self) -> bytes:
        return await self.__client.exec(self.__name + ':print', input_stream=None, output_type=bytes, return_type=None)


class Licenses:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._installed_keys = DecofInteger(client, name + ':installed-keys')
        self._options = LicenseOptions(client, name + ':options')

    @property
    def installed_keys(self) -> 'DecofInteger':
        return self._installed_keys

    @property
    def options(self) -> 'LicenseOptions':
        return self._options

    async def install(self, licensekey: str) -> bool:
        assert isinstance(licensekey, str), "expected type 'str' for parameter 'licensekey', got '{}'".format(type(licensekey))
        return await self.__client.exec(self.__name + ':install', licensekey, input_stream=None, output_type=None, return_type=bool)

    async def get_key(self, key_number: int) -> str:
        assert isinstance(key_number, int), "expected type 'int' for parameter 'key_number', got '{}'".format(type(key_number))
        return await self.__client.exec(self.__name + ':get-key', key_number, input_stream=None, output_type=None, return_type=str)


class LicenseOptions:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._lock = LicenseOption(client, name + ':lock')

    @property
    def lock(self) -> 'LicenseOption':
        return self._lock


class LicenseOption:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._licensee = DecofString(client, name + ':licensee')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._valid_until = DecofString(client, name + ':valid-until')

    @property
    def licensee(self) -> 'DecofString':
        return self._licensee

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def valid_until(self) -> 'DecofString':
        return self._valid_until


class PcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel1 = PiezoDrv3(client, name + ':channel1')
        self._revision = DecofString(client, name + ':revision')
        self._status = DecofInteger(client, name + ':status')
        self._channel_count = DecofInteger(client, name + ':channel-count')
        self._channel2 = PiezoDrv3(client, name + ':channel2')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._slot = DecofString(client, name + ':slot')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._variant = DecofString(client, name + ':variant')
        self._serial_number = DecofString(client, name + ':serial-number')

    @property
    def channel1(self) -> 'PiezoDrv3':
        return self._channel1

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def channel_count(self) -> 'DecofInteger':
        return self._channel_count

    @property
    def channel2(self) -> 'PiezoDrv3':
        return self._channel2

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number


class PiezoDrv3:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._path = DecofString(client, name + ':path')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._external_input = ExtInput3(client, name + ':external-input')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._status = DecofInteger(client, name + ':status')
        self._output_filter = OutputFilter3(client, name + ':output-filter')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def external_input(self) -> 'ExtInput3':
        return self._external_input

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def output_filter(self) -> 'OutputFilter3':
        return self._output_filter

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class ExtInput3:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor


class OutputFilter3:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled


class Buzzer:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._welcome = MutableDecofString(client, name + ':welcome')

    @property
    def welcome(self) -> 'MutableDecofString':
        return self._welcome

    async def play_welcome(self) -> None:
        await self.__client.exec(self.__name + ':play-welcome', input_stream=None, output_type=None, return_type=None)

    async def play(self, melody: str) -> None:
        assert isinstance(melody, str), "expected type 'str' for parameter 'melody', got '{}'".format(type(melody))
        await self.__client.exec(self.__name + ':play', melody, input_stream=None, output_type=None, return_type=None)


class PowerSupply:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._voltage_15Vn = DecofReal(client, name + ':voltage-15Vn')
        self._load = DecofReal(client, name + ':load')
        self._type_ = DecofString(client, name + ':type')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_15V = DecofReal(client, name + ':voltage-15V')
        self._current_5V = DecofReal(client, name + ':current-5V')
        self._voltage_3V3 = DecofReal(client, name + ':voltage-3V3')
        self._voltage_5V = DecofReal(client, name + ':voltage-5V')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._revision = DecofString(client, name + ':revision')
        self._status = DecofInteger(client, name + ':status')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._current_15Vn = DecofReal(client, name + ':current-15Vn')
        self._current_15V = DecofReal(client, name + ':current-15V')

    @property
    def voltage_15Vn(self) -> 'DecofReal':
        return self._voltage_15Vn

    @property
    def load(self) -> 'DecofReal':
        return self._load

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_15V(self) -> 'DecofReal':
        return self._voltage_15V

    @property
    def current_5V(self) -> 'DecofReal':
        return self._current_5V

    @property
    def voltage_3V3(self) -> 'DecofReal':
        return self._voltage_3V3

    @property
    def voltage_5V(self) -> 'DecofReal':
        return self._voltage_5V

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def current_15Vn(self) -> 'DecofReal':
        return self._current_15Vn

    @property
    def current_15V(self) -> 'DecofReal':
        return self._current_15V


class Display:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._state = DecofInteger(client, name + ':state')
        self._auto_dark = MutableDecofBoolean(client, name + ':auto-dark')
        self._brightness = MutableDecofReal(client, name + ':brightness')
        self._idle_timeout = MutableDecofInteger(client, name + ':idle-timeout')

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def auto_dark(self) -> 'MutableDecofBoolean':
        return self._auto_dark

    @property
    def brightness(self) -> 'MutableDecofReal':
        return self._brightness

    @property
    def idle_timeout(self) -> 'MutableDecofInteger':
        return self._idle_timeout

    async def update_state(self, active: bool) -> None:
        assert isinstance(active, bool), "expected type 'bool' for parameter 'active', got '{}'".format(type(active))
        await self.__client.exec(self.__name + ':update-state', active, input_stream=None, output_type=None, return_type=None)


class McBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._revision = DecofString(client, name + ':revision')
        self._air_pressure = DecofReal(client, name + ':air-pressure')
        self._relative_humidity = DecofReal(client, name + ':relative-humidity')
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._serial_number = DecofString(client, name + ':serial-number')

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def air_pressure(self) -> 'DecofReal':
        return self._air_pressure

    @property
    def relative_humidity(self) -> 'DecofReal':
        return self._relative_humidity

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number


class TcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._revision = DecofString(client, name + ':revision')
        self._channel2 = TcChannel2(client, name + ':channel2')
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._slot = DecofString(client, name + ':slot')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._channel1 = TcChannel2(client, name + ':channel1')
        self._serial_number = DecofString(client, name + ':serial-number')

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def channel2(self) -> 'TcChannel2':
        return self._channel2

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def channel1(self) -> 'TcChannel2':
        return self._channel1

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number


class TcChannel2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._t_loop = TcChannelTLoop2(client, name + ':t-loop')
        self._ntc_parallel_resistance = DecofReal(client, name + ':ntc-parallel-resistance')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._drv_voltage = DecofReal(client, name + ':drv-voltage')
        self._path = DecofString(client, name + ':path')
        self._c_loop = TcChannelCLoop2(client, name + ':c-loop')
        self._ntc_series_resistance = DecofReal(client, name + ':ntc-series-resistance')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._temp_set_min = MutableDecofReal(client, name + ':temp-set-min')
        self._temp_set_max = MutableDecofReal(client, name + ':temp-set-max')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._current_set_max = MutableDecofReal(client, name + ':current-set-max')
        self._current_set_min = MutableDecofReal(client, name + ':current-set-min')
        self._fault = DecofBoolean(client, name + ':fault')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._power_source = DecofInteger(client, name + ':power-source')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._temp_reset = MutableDecofBoolean(client, name + ':temp-reset')
        self._limits = TcChannelCheck2(client, name + ':limits')
        self._resistance = DecofReal(client, name + ':resistance')
        self._ready = DecofBoolean(client, name + ':ready')
        self._status = DecofInteger(client, name + ':status')
        self._temp_act = DecofReal(client, name + ':temp-act')
        self._current_set = DecofReal(client, name + ':current-set')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def t_loop(self) -> 'TcChannelTLoop2':
        return self._t_loop

    @property
    def ntc_parallel_resistance(self) -> 'DecofReal':
        return self._ntc_parallel_resistance

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def drv_voltage(self) -> 'DecofReal':
        return self._drv_voltage

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def c_loop(self) -> 'TcChannelCLoop2':
        return self._c_loop

    @property
    def ntc_series_resistance(self) -> 'DecofReal':
        return self._ntc_series_resistance

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def temp_set_min(self) -> 'MutableDecofReal':
        return self._temp_set_min

    @property
    def temp_set_max(self) -> 'MutableDecofReal':
        return self._temp_set_max

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def current_set_max(self) -> 'MutableDecofReal':
        return self._current_set_max

    @property
    def current_set_min(self) -> 'MutableDecofReal':
        return self._current_set_min

    @property
    def fault(self) -> 'DecofBoolean':
        return self._fault

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def power_source(self) -> 'DecofInteger':
        return self._power_source

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def temp_reset(self) -> 'MutableDecofBoolean':
        return self._temp_reset

    @property
    def limits(self) -> 'TcChannelCheck2':
        return self._limits

    @property
    def resistance(self) -> 'DecofReal':
        return self._resistance

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def temp_act(self) -> 'DecofReal':
        return self._temp_act

    @property
    def current_set(self) -> 'DecofReal':
        return self._current_set

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    async def check_peltier(self) -> float:
        return await self.__client.exec(self.__name + ':check-peltier', input_stream=None, output_type=None, return_type=float)


class TcChannelTLoop2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._on = MutableDecofBoolean(client, name + ':on')

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def on(self) -> 'MutableDecofBoolean':
        return self._on


class TcChannelCLoop2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._on = MutableDecofBoolean(client, name + ':on')

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def on(self) -> 'MutableDecofBoolean':
        return self._on


class ExtInput2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor


class TcChannelCheck2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._timed_out = DecofBoolean(client, name + ':timed-out')
        self._out_of_range = DecofBoolean(client, name + ':out-of-range')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')
        self._timeout = MutableDecofInteger(client, name + ':timeout')

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def timed_out(self) -> 'DecofBoolean':
        return self._timed_out

    @property
    def out_of_range(self) -> 'DecofBoolean':
        return self._out_of_range

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout


class Cc5000Board:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel1 = Cc5000Drv(client, name + ':channel1')
        self._status = DecofInteger(client, name + ':status')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._regulator_temp = DecofReal(client, name + ':regulator-temp')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._variant = DecofString(client, name + ':variant')
        self._inverter_temp = DecofReal(client, name + ':inverter-temp')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._inverter_temp_fuse = DecofReal(client, name + ':inverter-temp-fuse')
        self._revision = DecofString(client, name + ':revision')
        self._regulator_temp_fuse = DecofReal(client, name + ':regulator-temp-fuse')
        self._slot = DecofString(client, name + ':slot')
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._power_15v = MutableDecofBoolean(client, name + ':power-15v')

    @property
    def channel1(self) -> 'Cc5000Drv':
        return self._channel1

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def regulator_temp(self) -> 'DecofReal':
        return self._regulator_temp

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def inverter_temp(self) -> 'DecofReal':
        return self._inverter_temp

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def inverter_temp_fuse(self) -> 'DecofReal':
        return self._inverter_temp_fuse

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def regulator_temp_fuse(self) -> 'DecofReal':
        return self._regulator_temp_fuse

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def power_15v(self) -> 'MutableDecofBoolean':
        return self._power_15v


class Cc5000Drv:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._aux = DecofReal(client, name + ':aux')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._path = DecofString(client, name + ':path')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._variant = DecofString(client, name + ':variant')
        self._emission = DecofBoolean(client, name + ':emission')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._voltage_out = DecofReal(client, name + ':voltage-out')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._status = DecofInteger(client, name + ':status')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def voltage_out(self) -> 'DecofReal':
        return self._voltage_out

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class OutputFilter2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled


class Standby:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._laser1 = StandbyLaser(client, name + ':laser1')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._state = DecofInteger(client, name + ':state')

    @property
    def laser1(self) -> 'StandbyLaser':
        return self._laser1

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def state(self) -> 'DecofInteger':
        return self._state


class StandbyLaser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._dl = StandbyDl(client, name + ':dl')
        self._amp = StandbyAmp(client, name + ':amp')
        self._nlo = StandbyShg(client, name + ':nlo')

    @property
    def dl(self) -> 'StandbyDl':
        return self._dl

    @property
    def amp(self) -> 'StandbyAmp':
        return self._amp

    @property
    def nlo(self) -> 'StandbyShg':
        return self._nlo


class StandbyDl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc


class StandbyAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc


class StandbyShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_servo_subsystem = MutableDecofBoolean(client, name + ':disable-servo-subsystem')
        self._disable_cavity_lock = MutableDecofBoolean(client, name + ':disable-cavity-lock')
        self._disable_power_stabilization = MutableDecofBoolean(client, name + ':disable-power-stabilization')

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_servo_subsystem(self) -> 'MutableDecofBoolean':
        return self._disable_servo_subsystem

    @property
    def disable_cavity_lock(self) -> 'MutableDecofBoolean':
        return self._disable_cavity_lock

    @property
    def disable_power_stabilization(self) -> 'MutableDecofBoolean':
        return self._disable_power_stabilization


class CcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status_txt = DecofString(client, name + ':status-txt')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._variant = DecofString(client, name + ':variant')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._revision = DecofString(client, name + ':revision')
        self._channel2 = CurrDrv2(client, name + ':channel2')
        self._status = DecofInteger(client, name + ':status')
        self._slot = DecofString(client, name + ':slot')
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._channel1 = CurrDrv2(client, name + ':channel1')

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def channel2(self) -> 'CurrDrv2':
        return self._channel2

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def channel1(self) -> 'CurrDrv2':
        return self._channel1


class CurrDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._aux = DecofReal(client, name + ':aux')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._path = DecofString(client, name + ':path')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')
        self._external_input = ExtInput3(client, name + ':external-input')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._variant = DecofString(client, name + ':variant')
        self._pd = DecofReal(client, name + ':pd')
        self._emission = DecofBoolean(client, name + ':emission')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._status = DecofInteger(client, name + ':status')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._output_filter = OutputFilter3(client, name + ':output-filter')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering

    @property
    def external_input(self) -> 'ExtInput3':
        return self._external_input

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def output_filter(self) -> 'OutputFilter3':
        return self._output_filter

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class IoBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._out_a = IoOutputChannel(client, name + ':out-a')
        self._digital_in3 = IoDigitalInput(client, name + ':digital-in3')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._digital_in2 = IoDigitalInput(client, name + ':digital-in2')
        self._digital_out2 = IoDigitalOutput(client, name + ':digital-out2')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._out_b = IoOutputChannel(client, name + ':out-b')
        self._digital_out3 = IoDigitalOutput(client, name + ':digital-out3')
        self._digital_in0 = IoDigitalInput(client, name + ':digital-in0')
        self._revision = DecofString(client, name + ':revision')
        self._digital_out0 = IoDigitalOutput(client, name + ':digital-out0')
        self._digital_in1 = IoDigitalInput(client, name + ':digital-in1')
        self._digital_out1 = IoDigitalOutput(client, name + ':digital-out1')

    @property
    def out_a(self) -> 'IoOutputChannel':
        return self._out_a

    @property
    def digital_in3(self) -> 'IoDigitalInput':
        return self._digital_in3

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def digital_in2(self) -> 'IoDigitalInput':
        return self._digital_in2

    @property
    def digital_out2(self) -> 'IoDigitalOutput':
        return self._digital_out2

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def out_b(self) -> 'IoOutputChannel':
        return self._out_b

    @property
    def digital_out3(self) -> 'IoDigitalOutput':
        return self._digital_out3

    @property
    def digital_in0(self) -> 'IoDigitalInput':
        return self._digital_in0

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def digital_out0(self) -> 'IoDigitalOutput':
        return self._digital_out0

    @property
    def digital_in1(self) -> 'IoDigitalInput':
        return self._digital_in1

    @property
    def digital_out1(self) -> 'IoDigitalOutput':
        return self._digital_out1


class IoOutputChannel:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._external_input = ExtInput2(client, name + ':external-input')
        self._linked_laser = MutableDecofInteger(client, name + ':linked-laser')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._voltage_offset = MutableDecofReal(client, name + ':voltage-offset')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def linked_laser(self) -> 'MutableDecofInteger':
        return self._linked_laser

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def voltage_offset(self) -> 'MutableDecofReal':
        return self._voltage_offset

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class IoDigitalInput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_act = DecofBoolean(client, name + ':value-act')

    @property
    def value_act(self) -> 'DecofBoolean':
        return self._value_act


class IoDigitalOutput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._invert = MutableDecofBoolean(client, name + ':invert')
        self._value_set = MutableDecofBoolean(client, name + ':value-set')
        self._mode = MutableDecofInteger(client, name + ':mode')
        self._value_act = DecofBoolean(client, name + ':value-act')

    @property
    def invert(self) -> 'MutableDecofBoolean':
        return self._invert

    @property
    def value_set(self) -> 'MutableDecofBoolean':
        return self._value_set

    @property
    def mode(self) -> 'MutableDecofInteger':
        return self._mode

    @property
    def value_act(self) -> 'DecofBoolean':
        return self._value_act


class UvShgLaser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')
        self._emission = DecofBoolean(client, name + ':emission')
        self._power_set = MutableDecofReal(client, name + ':power-set')
        self._status = DecofInteger(client, name + ':status')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._operation_time_pump = DecofReal(client, name + ':operation-time-pump')
        self._pump_power_margin = DecofReal(client, name + ':pump-power-margin')
        self._error_txt = DecofString(client, name + ':error-txt')
        self._operation_time_uv = DecofReal(client, name + ':operation-time-uv')
        self._error = DecofInteger(client, name + ':error')
        self._remaining_optics_spots = DecofInteger(client, name + ':remaining-optics-spots')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def power_set(self) -> 'MutableDecofReal':
        return self._power_set

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def operation_time_pump(self) -> 'DecofReal':
        return self._operation_time_pump

    @property
    def pump_power_margin(self) -> 'DecofReal':
        return self._pump_power_margin

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt

    @property
    def operation_time_uv(self) -> 'DecofReal':
        return self._operation_time_uv

    @property
    def error(self) -> 'DecofInteger':
        return self._error

    @property
    def remaining_optics_spots(self) -> 'DecofInteger':
        return self._remaining_optics_spots

    async def perform_optimization(self) -> None:
        await self.__client.exec(self.__name + ':perform-optimization', input_stream=None, output_type=None, return_type=None)

    async def clear_errors(self) -> None:
        await self.__client.exec(self.__name + ':clear-errors', input_stream=None, output_type=None, return_type=None)


class Laser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amp = LaserAmp(client, name + ':amp')
        self._product_name = DecofString(client, name + ':product-name')
        self._nlo = Nlo(client, name + ':nlo')
        self._dpss = Dpss2(client, name + ':dpss')
        self._health = DecofInteger(client, name + ':health')
        self._wide_scan = WideScan(client, name + ':wide-scan')
        self._recorder = Recorder(client, name + ':recorder')
        self._ctl = CtlT(client, name + ':ctl')
        self._pd_ext = PdExt(client, name + ':pd-ext')
        self._dl = LaserHead(client, name + ':dl')
        self._emission = DecofBoolean(client, name + ':emission')
        self._scan = ScanGenerator(client, name + ':scan')
        self._health_txt = DecofString(client, name + ':health-txt')
        self._uv = UvShg(client, name + ':uv')
        self._power_stabilization = PwrStab(client, name + ':power-stabilization')
        self._scope = ScopeT(client, name + ':scope')
        self._type_ = DecofString(client, name + ':type')

    @property
    def amp(self) -> 'LaserAmp':
        return self._amp

    @property
    def product_name(self) -> 'DecofString':
        return self._product_name

    @property
    def nlo(self) -> 'Nlo':
        return self._nlo

    @property
    def dpss(self) -> 'Dpss2':
        return self._dpss

    @property
    def health(self) -> 'DecofInteger':
        return self._health

    @property
    def wide_scan(self) -> 'WideScan':
        return self._wide_scan

    @property
    def recorder(self) -> 'Recorder':
        return self._recorder

    @property
    def ctl(self) -> 'CtlT':
        return self._ctl

    @property
    def pd_ext(self) -> 'PdExt':
        return self._pd_ext

    @property
    def dl(self) -> 'LaserHead':
        return self._dl

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def scan(self) -> 'ScanGenerator':
        return self._scan

    @property
    def health_txt(self) -> 'DecofString':
        return self._health_txt

    @property
    def uv(self) -> 'UvShg':
        return self._uv

    @property
    def power_stabilization(self) -> 'PwrStab':
        return self._power_stabilization

    @property
    def scope(self) -> 'ScopeT':
        return self._scope

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    async def save(self) -> None:
        await self.__client.exec(self.__name + ':save', input_stream=None, output_type=None, return_type=None)

    async def load(self) -> None:
        await self.__client.exec(self.__name + ':load', input_stream=None, output_type=None, return_type=None)


class LaserAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._seed_limits = AmpPower(client, name + ':seed-limits')
        self._seedonly_check = AmpSeedonlyCheck(client, name + ':seedonly-check')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._version = DecofString(client, name + ':version')
        self._factory_settings = AmpFactory(client, name + ':factory-settings')
        self._cc = Cc5000Drv(client, name + ':cc')
        self._output_limits = AmpPower(client, name + ':output-limits')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._type_ = DecofString(client, name + ':type')
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._tc = TcChannel2(client, name + ':tc')

    @property
    def seed_limits(self) -> 'AmpPower':
        return self._seed_limits

    @property
    def seedonly_check(self) -> 'AmpSeedonlyCheck':
        return self._seedonly_check

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def version(self) -> 'DecofString':
        return self._version

    @property
    def factory_settings(self) -> 'AmpFactory':
        return self._factory_settings

    @property
    def cc(self) -> 'Cc5000Drv':
        return self._cc

    @property
    def output_limits(self) -> 'AmpPower':
        return self._output_limits

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class AmpPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._status = DecofInteger(client, name + ':status')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._power = DecofReal(client, name + ':power')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power_max_warning_delay(self) -> 'MutableDecofReal':
        return self._power_max_warning_delay

    @property
    def power_min_warning_delay(self) -> 'MutableDecofReal':
        return self._power_min_warning_delay

    @property
    def power_min(self) -> 'MutableDecofReal':
        return self._power_min

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay


class AmpSeedonlyCheck:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pump = DecofBoolean(client, name + ':pump')
        self._seed = DecofBoolean(client, name + ':seed')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._status = DecofInteger(client, name + ':status')
        self._shutdown_delay = MutableDecofReal(client, name + ':shutdown-delay')
        self._warning_delay = MutableDecofReal(client, name + ':warning-delay')

    @property
    def pump(self) -> 'DecofBoolean':
        return self._pump

    @property
    def seed(self) -> 'DecofBoolean':
        return self._seed

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def shutdown_delay(self) -> 'MutableDecofReal':
        return self._shutdown_delay

    @property
    def warning_delay(self) -> 'MutableDecofReal':
        return self._warning_delay


class AmpFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._last_modified = DecofString(client, name + ':last-modified')
        self._cc = AmpFactoryCc(client, name + ':cc')
        self._seedonly_check = AmpFactorySeedonly(client, name + ':seedonly-check')
        self._seed_limits = AmpFactoryPower(client, name + ':seed-limits')
        self._power = MutableDecofReal(client, name + ':power')
        self._output_limits = AmpFactoryPower(client, name + ':output-limits')
        self._modified = DecofBoolean(client, name + ':modified')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._tc = TcFactorySettings(client, name + ':tc')

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def cc(self) -> 'AmpFactoryCc':
        return self._cc

    @property
    def seedonly_check(self) -> 'AmpFactorySeedonly':
        return self._seedonly_check

    @property
    def seed_limits(self) -> 'AmpFactoryPower':
        return self._seed_limits

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def output_limits(self) -> 'AmpFactoryPower':
        return self._output_limits

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

    @property
    def tc(self) -> 'TcFactorySettings':
        return self._tc

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class AmpFactoryCc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip


class AmpFactorySeedonly:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shutdown_delay = MutableDecofReal(client, name + ':shutdown-delay')
        self._warning_delay = MutableDecofReal(client, name + ':warning-delay')

    @property
    def shutdown_delay(self) -> 'MutableDecofReal':
        return self._shutdown_delay

    @property
    def warning_delay(self) -> 'MutableDecofReal':
        return self._warning_delay


class AmpFactoryPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power_min(self) -> 'MutableDecofReal':
        return self._power_min

    @property
    def power_max_warning_delay(self) -> 'MutableDecofReal':
        return self._power_max_warning_delay

    @property
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay

    @property
    def power_min_warning_delay(self) -> 'MutableDecofReal':
        return self._power_min_warning_delay


class TcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._ntc_parallel_resistance = MutableDecofReal(client, name + ':ntc-parallel-resistance')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._power_source = MutableDecofInteger(client, name + ':power-source')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def ntc_parallel_resistance(self) -> 'MutableDecofReal':
        return self._ntc_parallel_resistance

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max


class Nlo:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pd = NloLaserHeadPhotoDiodes(client, name + ':pd')
        self._power_optimization = NloLaserHeadPowerOptimization(client, name + ':power-optimization')
        self._servo = NloLaserHeadServos(client, name + ':servo')
        self._ssw_ver = DecofString(client, name + ':ssw-ver')
        self._shg = Shg(client, name + ':shg')
        self._fhg = Fhg(client, name + ':fhg')

    @property
    def pd(self) -> 'NloLaserHeadPhotoDiodes':
        return self._pd

    @property
    def power_optimization(self) -> 'NloLaserHeadPowerOptimization':
        return self._power_optimization

    @property
    def servo(self) -> 'NloLaserHeadServos':
        return self._servo

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def shg(self) -> 'Shg':
        return self._shg

    @property
    def fhg(self) -> 'Fhg':
        return self._fhg


class NloLaserHeadPhotoDiodes:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._dl = NloLaserHeadNloPhotodiode2(client, name + ':dl')
        self._amp = NloLaserHeadNloPhotodiode2(client, name + ':amp')
        self._fiber = NloLaserHeadNloPhotodiode2(client, name + ':fiber')
        self._fhg_int = NloLaserHeadNloDigilockPhotodiode2(client, name + ':fhg-int')
        self._shg_int = NloLaserHeadNloDigilockPhotodiode2(client, name + ':shg-int')
        self._shg = NloLaserHeadNloPhotodiode2(client, name + ':shg')
        self._fhg = NloLaserHeadNloPhotodiode2(client, name + ':fhg')
        self._fhg_pdh_dc = NloLaserHeadNloDigilockPhotodiode2(client, name + ':fhg-pdh-dc')
        self._shg_pdh_dc = NloLaserHeadNloDigilockPhotodiode2(client, name + ':shg-pdh-dc')
        self._fhg_pdh_rf = NloLaserHeadNloPdhPhotodiode2(client, name + ':fhg-pdh-rf')
        self._shg_pdh_rf = NloLaserHeadNloPdhPhotodiode2(client, name + ':shg-pdh-rf')

    @property
    def dl(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._dl

    @property
    def amp(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._amp

    @property
    def fiber(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._fiber

    @property
    def fhg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._fhg_int

    @property
    def shg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._shg_int

    @property
    def shg(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._shg

    @property
    def fhg(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._fhg

    @property
    def fhg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._fhg_pdh_dc

    @property
    def shg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._shg_pdh_dc

    @property
    def fhg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode2':
        return self._fhg_pdh_rf

    @property
    def shg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode2':
        return self._shg_pdh_rf


class NloLaserHeadNloPhotodiode2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power = DecofReal(client, name + ':power')

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power(self) -> 'DecofReal':
        return self._power


class NloLaserHeadNloDigilockPhotodiode2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadNloPdhPhotodiode2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._gain = MutableDecofReal(client, name + ':gain')

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def gain(self) -> 'MutableDecofReal':
        return self._gain


class NloLaserHeadPowerOptimization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress_data_shg = DecofBinary(client, name + ':progress-data-shg')
        self._ongoing = DecofBoolean(client, name + ':ongoing')
        self._shg_advanced = MutableDecofBoolean(client, name + ':shg-advanced')
        self._progress_data_fiber = DecofBinary(client, name + ':progress-data-fiber')
        self._progress = DecofInteger(client, name + ':progress')
        self._stage4 = NloLaserHeadStage2(client, name + ':stage4')
        self._abort = MutableDecofBoolean(client, name + ':abort')
        self._stage1 = NloLaserHeadStage2(client, name + ':stage1')
        self._stage5 = NloLaserHeadStage2(client, name + ':stage5')
        self._status_string = DecofString(client, name + ':status-string')
        self._progress_data_amp = DecofBinary(client, name + ':progress-data-amp')
        self._status = DecofInteger(client, name + ':status')
        self._stage3 = NloLaserHeadStage2(client, name + ':stage3')
        self._progress_data_fhg = DecofBinary(client, name + ':progress-data-fhg')
        self._stage2 = NloLaserHeadStage2(client, name + ':stage2')

    @property
    def progress_data_shg(self) -> 'DecofBinary':
        return self._progress_data_shg

    @property
    def ongoing(self) -> 'DecofBoolean':
        return self._ongoing

    @property
    def shg_advanced(self) -> 'MutableDecofBoolean':
        return self._shg_advanced

    @property
    def progress_data_fiber(self) -> 'DecofBinary':
        return self._progress_data_fiber

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def stage4(self) -> 'NloLaserHeadStage2':
        return self._stage4

    @property
    def abort(self) -> 'MutableDecofBoolean':
        return self._abort

    @property
    def stage1(self) -> 'NloLaserHeadStage2':
        return self._stage1

    @property
    def stage5(self) -> 'NloLaserHeadStage2':
        return self._stage5

    @property
    def status_string(self) -> 'DecofString':
        return self._status_string

    @property
    def progress_data_amp(self) -> 'DecofBinary':
        return self._progress_data_amp

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def stage3(self) -> 'NloLaserHeadStage2':
        return self._stage3

    @property
    def progress_data_fhg(self) -> 'DecofBinary':
        return self._progress_data_fhg

    @property
    def stage2(self) -> 'NloLaserHeadStage2':
        return self._stage2

    async def start_optimization_fhg(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-fhg', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_amp(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-amp', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_shg(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-shg', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_fiber(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-fiber', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_all(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-all', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadStage2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._restore_on_regress = MutableDecofBoolean(client, name + ':restore-on-regress')
        self._optimization_in_progress = DecofBoolean(client, name + ':optimization-in-progress')
        self._progress = DecofInteger(client, name + ':progress')
        self._restore_on_abort = MutableDecofBoolean(client, name + ':restore-on-abort')
        self._regress_tolerance = MutableDecofInteger(client, name + ':regress-tolerance')
        self._input = NloLaserHeadOptInput2(client, name + ':input')

    @property
    def restore_on_regress(self) -> 'MutableDecofBoolean':
        return self._restore_on_regress

    @property
    def optimization_in_progress(self) -> 'DecofBoolean':
        return self._optimization_in_progress

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def restore_on_abort(self) -> 'MutableDecofBoolean':
        return self._restore_on_abort

    @property
    def regress_tolerance(self) -> 'MutableDecofInteger':
        return self._regress_tolerance

    @property
    def input(self) -> 'NloLaserHeadOptInput2':
        return self._input

    async def start_optimization(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadOptInput2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_calibrated = DecofReal(client, name + ':value-calibrated')

    @property
    def value_calibrated(self) -> 'DecofReal':
        return self._value_calibrated


class NloLaserHeadServos:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg1_hor = NloLaserHeadServoPwm2(client, name + ':shg1-hor')
        self._fhg2_vert = NloLaserHeadServoPwm2(client, name + ':fhg2-vert')
        self._ta2_vert = NloLaserHeadServoPwm2(client, name + ':ta2-vert')
        self._uv_cryst = NloLaserHeadServoPwm2(client, name + ':uv-cryst')
        self._fiber1_hor = NloLaserHeadServoPwm2(client, name + ':fiber1-hor')
        self._ta1_vert = NloLaserHeadServoPwm2(client, name + ':ta1-vert')
        self._fiber2_vert = NloLaserHeadServoPwm2(client, name + ':fiber2-vert')
        self._fhg1_hor = NloLaserHeadServoPwm2(client, name + ':fhg1-hor')
        self._shg2_hor = NloLaserHeadServoPwm2(client, name + ':shg2-hor')
        self._fhg1_vert = NloLaserHeadServoPwm2(client, name + ':fhg1-vert')
        self._fiber2_hor = NloLaserHeadServoPwm2(client, name + ':fiber2-hor')
        self._fhg2_hor = NloLaserHeadServoPwm2(client, name + ':fhg2-hor')
        self._fiber1_vert = NloLaserHeadServoPwm2(client, name + ':fiber1-vert')
        self._shg1_vert = NloLaserHeadServoPwm2(client, name + ':shg1-vert')
        self._ta2_hor = NloLaserHeadServoPwm2(client, name + ':ta2-hor')
        self._ta1_hor = NloLaserHeadServoPwm2(client, name + ':ta1-hor')
        self._uv_outcpl = NloLaserHeadServoPwm2(client, name + ':uv-outcpl')
        self._shg2_vert = NloLaserHeadServoPwm2(client, name + ':shg2-vert')

    @property
    def shg1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._shg1_hor

    @property
    def fhg2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg2_vert

    @property
    def ta2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._ta2_vert

    @property
    def uv_cryst(self) -> 'NloLaserHeadServoPwm2':
        return self._uv_cryst

    @property
    def fiber1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber1_hor

    @property
    def ta1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._ta1_vert

    @property
    def fiber2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber2_vert

    @property
    def fhg1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg1_hor

    @property
    def shg2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._shg2_hor

    @property
    def fhg1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg1_vert

    @property
    def fiber2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber2_hor

    @property
    def fhg2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg2_hor

    @property
    def fiber1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber1_vert

    @property
    def shg1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._shg1_vert

    @property
    def ta2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._ta2_hor

    @property
    def ta1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._ta1_hor

    @property
    def uv_outcpl(self) -> 'NloLaserHeadServoPwm2':
        return self._uv_outcpl

    @property
    def shg2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._shg2_vert

    async def center_fhg_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-fhg-servos', input_stream=None, output_type=None, return_type=None)

    async def center_all_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-all-servos', input_stream=None, output_type=None, return_type=None)

    async def center_ta_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-ta-servos', input_stream=None, output_type=None, return_type=None)

    async def center_fiber_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-fiber-servos', input_stream=None, output_type=None, return_type=None)

    async def center_shg_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-shg-servos', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadServoPwm2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._display_name = DecofString(client, name + ':display-name')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._value = MutableDecofInteger(client, name + ':value')

    @property
    def display_name(self) -> 'DecofString':
        return self._display_name

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def value(self) -> 'MutableDecofInteger':
        return self._value

    async def center_servo(self) -> None:
        await self.__client.exec(self.__name + ':center-servo', input_stream=None, output_type=None, return_type=None)


class Shg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = NloLaserHeadSiggen2(client, name + ':scan')
        self._pc = PiezoDrv2(client, name + ':pc')
        self._lock = NloLaserHeadLockShg2(client, name + ':lock')
        self._tc = TcChannel2(client, name + ':tc')
        self._factory_settings = ShgFactorySettings(client, name + ':factory-settings')
        self._scope = NloLaserHeadScopeT2(client, name + ':scope')

    @property
    def scan(self) -> 'NloLaserHeadSiggen2':
        return self._scan

    @property
    def pc(self) -> 'PiezoDrv2':
        return self._pc

    @property
    def lock(self) -> 'NloLaserHeadLockShg2':
        return self._lock

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    @property
    def factory_settings(self) -> 'ShgFactorySettings':
        return self._factory_settings

    @property
    def scope(self) -> 'NloLaserHeadScopeT2':
        return self._scope

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadSiggen2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._offset = MutableDecofReal(client, name + ':offset')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset


class PiezoDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._path = DecofString(client, name + ':path')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._status = DecofInteger(client, name + ':status')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class NloLaserHeadLockShg2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')
        self._local_oscillator = NloLaserHeadLocalOscillatorShg2(client, name + ':local-oscillator')
        self._relock = NloLaserHeadRelock2(client, name + ':relock')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._window = NloLaserHeadWindow2(client, name + ':window')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._pid2 = NloLaserHeadPid2(client, name + ':pid2')
        self._analog_dl_gain = NloLaserHeadMinifalc2(client, name + ':analog-dl-gain')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._pid1 = NloLaserHeadPid2(client, name + ':pid1')
        self._state = DecofInteger(client, name + ':state')

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorShg2':
        return self._local_oscillator

    @property
    def relock(self) -> 'NloLaserHeadRelock2':
        return self._relock

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def window(self) -> 'NloLaserHeadWindow2':
        return self._window

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def pid2(self) -> 'NloLaserHeadPid2':
        return self._pid2

    @property
    def analog_dl_gain(self) -> 'NloLaserHeadMinifalc2':
        return self._analog_dl_gain

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def pid1(self) -> 'NloLaserHeadPid2':
        return self._pid1

    @property
    def state(self) -> 'DecofInteger':
        return self._state


class NloLaserHeadLocalOscillatorShg2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._use_external_oscillator = MutableDecofBoolean(client, name + ':use-external-oscillator')
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def use_external_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_external_oscillator

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    async def auto_pdh(self) -> None:
        await self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadRelock2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._delay = MutableDecofReal(client, name + ':delay')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class NloLaserHeadWindow2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._threshold = MutableDecofReal(client, name + ':threshold')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')

    @property
    def threshold(self) -> 'MutableDecofReal':
        return self._threshold

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel


class NloLaserHeadPid2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = NloLaserHeadGain2(client, name + ':gain')

    @property
    def gain(self) -> 'NloLaserHeadGain2':
        return self._gain


class NloLaserHeadGain2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i = MutableDecofReal(client, name + ':i')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._d = MutableDecofReal(client, name + ':d')
        self._p = MutableDecofReal(client, name + ':p')
        self._all = MutableDecofReal(client, name + ':all')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff


class NloLaserHeadMinifalc2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p_gain = MutableDecofReal(client, name + ':p-gain')

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain


class ShgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pd = NloLaserHeadShgPhotodiodesFactorySettings(client, name + ':pd')
        self._modified = DecofBoolean(client, name + ':modified')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')

    @property
    def pd(self) -> 'NloLaserHeadShgPhotodiodesFactorySettings':
        return self._pd

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadShgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg = NloLaserHeadPdFactorySettings(client, name + ':shg')
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')
        self._fiber = NloLaserHeadPdFactorySettings(client, name + ':fiber')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')

    @property
    def shg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._shg

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int

    @property
    def fiber(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fiber

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc


class NloLaserHeadPdFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadPdDigilockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadPdPdhFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = MutableDecofReal(client, name + ':gain')

    @property
    def gain(self) -> 'MutableDecofReal':
        return self._gain


class NloLaserHeadLockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._local_oscillator = NloLaserHeadLocalOscillatorFactorySettings(client, name + ':local-oscillator')
        self._relock = NloLaserHeadRelockFactorySettings(client, name + ':relock')
        self._window = NloLaserHeadLockWindowFactorySettings(client, name + ':window')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._analog_p_gain = MutableDecofReal(client, name + ':analog-p-gain')
        self._pid2_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid2-gain')
        self._pid1_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid1-gain')

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFactorySettings':
        return self._local_oscillator

    @property
    def relock(self) -> 'NloLaserHeadRelockFactorySettings':
        return self._relock

    @property
    def window(self) -> 'NloLaserHeadLockWindowFactorySettings':
        return self._window

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def analog_p_gain(self) -> 'MutableDecofReal':
        return self._analog_p_gain

    @property
    def pid2_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid2_gain

    @property
    def pid1_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid1_gain


class NloLaserHeadLocalOscillatorFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._attenuation_fhg_raw = MutableDecofInteger(client, name + ':attenuation-fhg-raw')
        self._attenuation_shg_raw = MutableDecofInteger(client, name + ':attenuation-shg-raw')
        self._phase_shift_shg = MutableDecofReal(client, name + ':phase-shift-shg')
        self._phase_shift_fhg = MutableDecofReal(client, name + ':phase-shift-fhg')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def attenuation_fhg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_fhg_raw

    @property
    def attenuation_shg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_shg_raw

    @property
    def phase_shift_shg(self) -> 'MutableDecofReal':
        return self._phase_shift_shg

    @property
    def phase_shift_fhg(self) -> 'MutableDecofReal':
        return self._phase_shift_fhg

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class NloLaserHeadRelockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._delay = MutableDecofReal(client, name + ':delay')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._frequency = MutableDecofReal(client, name + ':frequency')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency


class NloLaserHeadLockWindowFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._threshold = MutableDecofReal(client, name + ':threshold')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')

    @property
    def threshold(self) -> 'MutableDecofReal':
        return self._threshold

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel


class NloLaserHeadPidGainFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i = MutableDecofReal(client, name + ':i')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._d = MutableDecofReal(client, name + ':d')
        self._p = MutableDecofReal(client, name + ':p')
        self._all = MutableDecofReal(client, name + ':all')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff


class NloLaserHeadPcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan_frequency = MutableDecofReal(client, name + ':scan-frequency')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def scan_frequency(self) -> 'MutableDecofReal':
        return self._scan_frequency

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class NloLaserHeadTcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._power_source = MutableDecofInteger(client, name + ':power-source')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max


class NloLaserHeadScopeT2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channelx = NloLaserHeadScopeXAxisT2(client, name + ':channelx')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')
        self._data = DecofBinary(client, name + ':data')
        self._channel2 = NloLaserHeadScopeChannelT2(client, name + ':channel2')
        self._variant = MutableDecofInteger(client, name + ':variant')
        self._channel1 = NloLaserHeadScopeChannelT2(client, name + ':channel1')
        self._timescale = MutableDecofReal(client, name + ':timescale')

    @property
    def channelx(self) -> 'NloLaserHeadScopeXAxisT2':
        return self._channelx

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channel2(self) -> 'NloLaserHeadScopeChannelT2':
        return self._channel2

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant

    @property
    def channel1(self) -> 'NloLaserHeadScopeChannelT2':
        return self._channel1

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale


class NloLaserHeadScopeXAxisT2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')
        self._name = DecofString(client, name + ':name')
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._unit = DecofString(client, name + ':unit')

    @property
    def spectrum_range(self) -> 'MutableDecofReal':
        return self._spectrum_range

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def spectrum_omit_dc(self) -> 'MutableDecofBoolean':
        return self._spectrum_omit_dc

    @property
    def scope_timescale(self) -> 'MutableDecofReal':
        return self._scope_timescale

    @property
    def unit(self) -> 'DecofString':
        return self._unit


class NloLaserHeadScopeChannelT2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._name = DecofString(client, name + ':name')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Fhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = NloLaserHeadSiggen2(client, name + ':scan')
        self._pc = PiezoDrv2(client, name + ':pc')
        self._lock = NloLaserHeadLockFhg(client, name + ':lock')
        self._tc = TcChannel2(client, name + ':tc')
        self._factory_settings = FhgFactorySettings(client, name + ':factory-settings')
        self._scope = NloLaserHeadScopeT2(client, name + ':scope')

    @property
    def scan(self) -> 'NloLaserHeadSiggen2':
        return self._scan

    @property
    def pc(self) -> 'PiezoDrv2':
        return self._pc

    @property
    def lock(self) -> 'NloLaserHeadLockFhg':
        return self._lock

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    @property
    def factory_settings(self) -> 'FhgFactorySettings':
        return self._factory_settings

    @property
    def scope(self) -> 'NloLaserHeadScopeT2':
        return self._scope

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadLockFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')
        self._local_oscillator = NloLaserHeadLocalOscillatorFhg(client, name + ':local-oscillator')
        self._relock = NloLaserHeadRelock2(client, name + ':relock')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._window = NloLaserHeadWindow2(client, name + ':window')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._pid2 = NloLaserHeadPid2(client, name + ':pid2')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._pid1 = NloLaserHeadPid2(client, name + ':pid1')
        self._state = DecofInteger(client, name + ':state')

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFhg':
        return self._local_oscillator

    @property
    def relock(self) -> 'NloLaserHeadRelock2':
        return self._relock

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def window(self) -> 'NloLaserHeadWindow2':
        return self._window

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def pid2(self) -> 'NloLaserHeadPid2':
        return self._pid2

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def pid1(self) -> 'NloLaserHeadPid2':
        return self._pid1

    @property
    def state(self) -> 'DecofInteger':
        return self._state


class NloLaserHeadLocalOscillatorFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    async def auto_pdh(self) -> None:
        await self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class FhgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pd = NloLaserHeadFhgPhotodiodesFactorySettings(client, name + ':pd')
        self._modified = DecofBoolean(client, name + ':modified')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')

    @property
    def pd(self) -> 'NloLaserHeadFhgPhotodiodesFactorySettings':
        return self._pd

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadFhgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._fhg = NloLaserHeadPdFactorySettings(client, name + ':fhg')

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def fhg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fhg


class Dpss2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_max = DecofReal(client, name + ':current-max')
        self._tc_status_txt = DecofString(client, name + ':tc-status-txt')
        self._error_code = DecofInteger(client, name + ':error-code')
        self._power_margin = DecofReal(client, name + ':power-margin')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._operation_time = DecofReal(client, name + ':operation-time')
        self._power_act = DecofReal(client, name + ':power-act')
        self._status = DecofInteger(client, name + ':status')
        self._power_max = DecofReal(client, name + ':power-max')
        self._power_set = MutableDecofReal(client, name + ':power-set')
        self._error_txt = DecofString(client, name + ':error-txt')
        self._tc_status = DecofInteger(client, name + ':tc-status')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._current_act = DecofReal(client, name + ':current-act')

    @property
    def current_max(self) -> 'DecofReal':
        return self._current_max

    @property
    def tc_status_txt(self) -> 'DecofString':
        return self._tc_status_txt

    @property
    def error_code(self) -> 'DecofInteger':
        return self._error_code

    @property
    def power_margin(self) -> 'DecofReal':
        return self._power_margin

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def operation_time(self) -> 'DecofReal':
        return self._operation_time

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def power_max(self) -> 'DecofReal':
        return self._power_max

    @property
    def power_set(self) -> 'MutableDecofReal':
        return self._power_set

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt

    @property
    def tc_status(self) -> 'DecofInteger':
        return self._tc_status

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act


class WideScan:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._scan_end = MutableDecofReal(client, name + ':scan-end')
        self._duration = MutableDecofReal(client, name + ':duration')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._remaining_time = DecofInteger(client, name + ':remaining-time')
        self._offset = MutableDecofReal(client, name + ':offset')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._progress = DecofInteger(client, name + ':progress')
        self._state = DecofInteger(client, name + ':state')
        self._scan_begin = MutableDecofReal(client, name + ':scan-begin')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def scan_end(self) -> 'MutableDecofReal':
        return self._scan_end

    @property
    def duration(self) -> 'MutableDecofReal':
        return self._duration

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def remaining_time(self) -> 'DecofInteger':
        return self._remaining_time

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def scan_begin(self) -> 'MutableDecofReal':
        return self._scan_begin

    async def start(self) -> None:
        await self.__client.exec(self.__name + ':start', input_stream=None, output_type=None, return_type=None)

    async def stop(self) -> None:
        await self.__client.exec(self.__name + ':stop', input_stream=None, output_type=None, return_type=None)


class Recorder:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signals = RecorderInputs(client, name + ':signals')
        self._data = RecorderData(client, name + ':data')
        self._sample_count = DecofInteger(client, name + ':sample-count')
        self._sample_count_set = MutableDecofInteger(client, name + ':sample-count-set')
        self._recording_time = MutableDecofReal(client, name + ':recording-time')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._state = DecofInteger(client, name + ':state')
        self._sampling_interval = DecofReal(client, name + ':sampling-interval')

    @property
    def signals(self) -> 'RecorderInputs':
        return self._signals

    @property
    def data(self) -> 'RecorderData':
        return self._data

    @property
    def sample_count(self) -> 'DecofInteger':
        return self._sample_count

    @property
    def sample_count_set(self) -> 'MutableDecofInteger':
        return self._sample_count_set

    @property
    def recording_time(self) -> 'MutableDecofReal':
        return self._recording_time

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def sampling_interval(self) -> 'DecofReal':
        return self._sampling_interval


class RecorderInputs:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channelx = MutableDecofInteger(client, name + ':channelx')
        self._channel1 = MutableDecofInteger(client, name + ':channel1')
        self._channel2 = MutableDecofInteger(client, name + ':channel2')

    @property
    def channelx(self) -> 'MutableDecofInteger':
        return self._channelx

    @property
    def channel1(self) -> 'MutableDecofInteger':
        return self._channel1

    @property
    def channel2(self) -> 'MutableDecofInteger':
        return self._channel2


class RecorderData:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._zoom_data = DecofBinary(client, name + ':zoom-data')
        self._channelx = RecorderChannel(client, name + ':channelx')
        self._zoom_amplitude = MutableDecofReal(client, name + ':zoom-amplitude')
        self._channel2 = RecorderChannel(client, name + ':channel2')
        self._zoom_offset = MutableDecofReal(client, name + ':zoom-offset')
        self._channel1 = RecorderChannel(client, name + ':channel1')
        self._recorded_sample_count = DecofInteger(client, name + ':recorded-sample-count')

    @property
    def zoom_data(self) -> 'DecofBinary':
        return self._zoom_data

    @property
    def channelx(self) -> 'RecorderChannel':
        return self._channelx

    @property
    def zoom_amplitude(self) -> 'MutableDecofReal':
        return self._zoom_amplitude

    @property
    def channel2(self) -> 'RecorderChannel':
        return self._channel2

    @property
    def zoom_offset(self) -> 'MutableDecofReal':
        return self._zoom_offset

    @property
    def channel1(self) -> 'RecorderChannel':
        return self._channel1

    @property
    def recorded_sample_count(self) -> 'DecofInteger':
        return self._recorded_sample_count

    async def show_data(self, start_index: int, count: int) -> None:
        assert isinstance(start_index, int), "expected type 'int' for parameter 'start_index', got '{}'".format(type(start_index))
        assert isinstance(count, int), "expected type 'int' for parameter 'count', got '{}'".format(type(count))
        await self.__client.exec(self.__name + ':show-data', start_index, count, input_stream=None, output_type=None, return_type=None)

    async def zoom_out(self) -> None:
        await self.__client.exec(self.__name + ':zoom-out', input_stream=None, output_type=None, return_type=None)

    async def get_data(self, start_index: int, count: int) -> bytes:
        assert isinstance(start_index, int), "expected type 'int' for parameter 'start_index', got '{}'".format(type(start_index))
        assert isinstance(count, int), "expected type 'int' for parameter 'count', got '{}'".format(type(count))
        return await self.__client.exec(self.__name + ':get-data', start_index, count, input_stream=None, output_type=None, return_type=bytes)


class RecorderChannel:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._name = DecofString(client, name + ':name')
        self._signal = DecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def signal(self) -> 'DecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit


class CtlT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')
        self._remote_control = CtlRemoteControl(client, name + ':remote-control')
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._motor = CtlMotor(client, name + ':motor')
        self._mode_control = CtlModeControl(client, name + ':mode-control')
        self._factory_settings = CtlFactory(client, name + ':factory-settings')
        self._wavelength_set = MutableDecofReal(client, name + ':wavelength-set')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._optimization = CtlOptimizationT(client, name + ':optimization')
        self._scan = CtlScanT(client, name + ':scan')
        self._state = DecofInteger(client, name + ':state')
        self._power = CtlPower(client, name + ':power')
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._wavelength_act = DecofReal(client, name + ':wavelength-act')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')
        self._head_temperature = DecofReal(client, name + ':head-temperature')

    @property
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    @property
    def remote_control(self) -> 'CtlRemoteControl':
        return self._remote_control

    @property
    def tuning_power_min(self) -> 'DecofReal':
        return self._tuning_power_min

    @property
    def motor(self) -> 'CtlMotor':
        return self._motor

    @property
    def mode_control(self) -> 'CtlModeControl':
        return self._mode_control

    @property
    def factory_settings(self) -> 'CtlFactory':
        return self._factory_settings

    @property
    def wavelength_set(self) -> 'MutableDecofReal':
        return self._wavelength_set

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def optimization(self) -> 'CtlOptimizationT':
        return self._optimization

    @property
    def scan(self) -> 'CtlScanT':
        return self._scan

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def power(self) -> 'CtlPower':
        return self._power

    @property
    def tuning_current_min(self) -> 'DecofReal':
        return self._tuning_current_min

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def wavelength_act(self) -> 'DecofReal':
        return self._wavelength_act

    @property
    def wavelength_max(self) -> 'DecofReal':
        return self._wavelength_max

    @property
    def head_temperature(self) -> 'DecofReal':
        return self._head_temperature


class CtlRemoteControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor


class CtlMotor:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._position_accuracy_fullstep = MutableDecofInteger(client, name + ':position-accuracy-fullstep')
        self._position_hysteresis_microstep = MutableDecofInteger(client, name + ':position-hysteresis-microstep')
        self._position_hysteresis_fullstep = MutableDecofInteger(client, name + ':position-hysteresis-fullstep')
        self._position_accuracy_microstep = MutableDecofInteger(client, name + ':position-accuracy-microstep')
        self._power_save_disabled = MutableDecofBoolean(client, name + ':power-save-disabled')

    @property
    def position_accuracy_fullstep(self) -> 'MutableDecofInteger':
        return self._position_accuracy_fullstep

    @property
    def position_hysteresis_microstep(self) -> 'MutableDecofInteger':
        return self._position_hysteresis_microstep

    @property
    def position_hysteresis_fullstep(self) -> 'MutableDecofInteger':
        return self._position_hysteresis_fullstep

    @property
    def position_accuracy_microstep(self) -> 'MutableDecofInteger':
        return self._position_accuracy_microstep

    @property
    def power_save_disabled(self) -> 'MutableDecofBoolean':
        return self._power_save_disabled


class CtlModeControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._loop_enabled = MutableDecofBoolean(client, name + ':loop-enabled')

    @property
    def loop_enabled(self) -> 'MutableDecofBoolean':
        return self._loop_enabled


class CtlFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')

    @property
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    @property
    def tuning_power_min(self) -> 'DecofReal':
        return self._tuning_power_min

    @property
    def tuning_current_min(self) -> 'DecofReal':
        return self._tuning_current_min

    @property
    def wavelength_max(self) -> 'DecofReal':
        return self._wavelength_max

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class CtlOptimizationT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress = DecofInteger(client, name + ':progress')

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    async def flow(self) -> None:
        await self.__client.exec(self.__name + ':flow', input_stream=None, output_type=None, return_type=None)

    async def abort(self) -> None:
        await self.__client.exec(self.__name + ':abort', input_stream=None, output_type=None, return_type=None)

    async def smile(self) -> None:
        await self.__client.exec(self.__name + ':smile', input_stream=None, output_type=None, return_type=None)


class CtlScanT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._remaining_time = DecofInteger(client, name + ':remaining-time')
        self._shape = MutableDecofInteger(client, name + ':shape')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._trigger = CtlTriggerT(client, name + ':trigger')
        self._wavelength_begin = MutableDecofReal(client, name + ':wavelength-begin')
        self._microsteps = MutableDecofBoolean(client, name + ':microsteps')
        self._continuous_mode = MutableDecofBoolean(client, name + ':continuous-mode')
        self._progress = DecofInteger(client, name + ':progress')
        self._speed_max = DecofReal(client, name + ':speed-max')
        self._speed_min = DecofReal(client, name + ':speed-min')
        self._wavelength_end = MutableDecofReal(client, name + ':wavelength-end')

    @property
    def remaining_time(self) -> 'DecofInteger':
        return self._remaining_time

    @property
    def shape(self) -> 'MutableDecofInteger':
        return self._shape

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def trigger(self) -> 'CtlTriggerT':
        return self._trigger

    @property
    def wavelength_begin(self) -> 'MutableDecofReal':
        return self._wavelength_begin

    @property
    def microsteps(self) -> 'MutableDecofBoolean':
        return self._microsteps

    @property
    def continuous_mode(self) -> 'MutableDecofBoolean':
        return self._continuous_mode

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def speed_max(self) -> 'DecofReal':
        return self._speed_max

    @property
    def speed_min(self) -> 'DecofReal':
        return self._speed_min

    @property
    def wavelength_end(self) -> 'MutableDecofReal':
        return self._wavelength_end

    async def pause(self) -> None:
        await self.__client.exec(self.__name + ':pause', input_stream=None, output_type=None, return_type=None)

    async def start(self) -> None:
        await self.__client.exec(self.__name + ':start', input_stream=None, output_type=None, return_type=None)

    async def stop(self) -> None:
        await self.__client.exec(self.__name + ':stop', input_stream=None, output_type=None, return_type=None)

    async def continue_(self) -> None:
        await self.__client.exec(self.__name + ':continue', input_stream=None, output_type=None, return_type=None)


class CtlTriggerT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._output_enabled = MutableDecofBoolean(client, name + ':output-enabled')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._output_threshold = MutableDecofReal(client, name + ':output-threshold')
        self._input_enabled = MutableDecofBoolean(client, name + ':input-enabled')

    @property
    def output_enabled(self) -> 'MutableDecofBoolean':
        return self._output_enabled

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def output_threshold(self) -> 'MutableDecofReal':
        return self._output_threshold

    @property
    def input_enabled(self) -> 'MutableDecofBoolean':
        return self._input_enabled


class CtlPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act


class PdExt:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power = DecofReal(client, name + ':power')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class LaserHead:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._lock = Lock(client, name + ':lock')
        self._pc = PiezoDrv2(client, name + ':pc')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._pd = PdCal(client, name + ':pd')
        self._model = DecofString(client, name + ':model')
        self._pressure_compensation = PressureCompensation(client, name + ':pressure-compensation')
        self._version = DecofString(client, name + ':version')
        self._factory_settings = LhFactory(client, name + ':factory-settings')
        self._cc = CurrDrv1(client, name + ':cc')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._type_ = DecofString(client, name + ':type')
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._tc = TcChannel2(client, name + ':tc')

    @property
    def lock(self) -> 'Lock':
        return self._lock

    @property
    def pc(self) -> 'PiezoDrv2':
        return self._pc

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def pd(self) -> 'PdCal':
        return self._pd

    @property
    def model(self) -> 'DecofString':
        return self._model

    @property
    def pressure_compensation(self) -> 'PressureCompensation':
        return self._pressure_compensation

    @property
    def version(self) -> 'DecofString':
        return self._version

    @property
    def factory_settings(self) -> 'LhFactory':
        return self._factory_settings

    @property
    def cc(self) -> 'CurrDrv1':
        return self._cc

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class Lock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._candidate_filter = AlCandidateFilter(client, name + ':candidate-filter')
        self._spectrum_input_channel = MutableDecofInteger(client, name + ':spectrum-input-channel')
        self._lockin = Lockin(client, name + ':lockin')
        self._locking_delay = MutableDecofInteger(client, name + ':locking-delay')
        self._relock = AlRelock(client, name + ':relock')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._reset = AlReset(client, name + ':reset')
        self._candidates = DecofBinary(client, name + ':candidates')
        self._lock_tracking = Coordinate(client, name + ':lock-tracking')
        self._lockpoint = AlLockpoint(client, name + ':lockpoint')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._pid2 = Pid(client, name + ':pid2')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._window = AlWindow(client, name + ':window')
        self._lock_without_lockpoint = MutableDecofBoolean(client, name + ':lock-without-lockpoint')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._pid1 = Pid(client, name + ':pid1')
        self._type_ = MutableDecofInteger(client, name + ':type')
        self._state = DecofInteger(client, name + ':state')

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def candidate_filter(self) -> 'AlCandidateFilter':
        return self._candidate_filter

    @property
    def spectrum_input_channel(self) -> 'MutableDecofInteger':
        return self._spectrum_input_channel

    @property
    def lockin(self) -> 'Lockin':
        return self._lockin

    @property
    def locking_delay(self) -> 'MutableDecofInteger':
        return self._locking_delay

    @property
    def relock(self) -> 'AlRelock':
        return self._relock

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def reset(self) -> 'AlReset':
        return self._reset

    @property
    def candidates(self) -> 'DecofBinary':
        return self._candidates

    @property
    def lock_tracking(self) -> 'Coordinate':
        return self._lock_tracking

    @property
    def lockpoint(self) -> 'AlLockpoint':
        return self._lockpoint

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def pid2(self) -> 'Pid':
        return self._pid2

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def window(self) -> 'AlWindow':
        return self._window

    @property
    def lock_without_lockpoint(self) -> 'MutableDecofBoolean':
        return self._lock_without_lockpoint

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def pid1(self) -> 'Pid':
        return self._pid1

    @property
    def type_(self) -> 'MutableDecofInteger':
        return self._type_

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    async def find_candidates(self) -> None:
        await self.__client.exec(self.__name + ':find-candidates', input_stream=None, output_type=None, return_type=None)

    async def open(self) -> None:
        await self.__client.exec(self.__name + ':open', input_stream=None, output_type=None, return_type=None)

    async def close(self) -> None:
        await self.__client.exec(self.__name + ':close', input_stream=None, output_type=None, return_type=None)

    async def show_candidates(self) -> Tuple[str, int]:
        return await self.__client.exec(self.__name + ':show-candidates', input_stream=None, output_type=str, return_type=int)

    async def select_lockpoint(self, x: float, y: float, type_: int) -> None:
        assert isinstance(x, float), "expected type 'float' for parameter 'x', got '{}'".format(type(x))
        assert isinstance(y, float), "expected type 'float' for parameter 'y', got '{}'".format(type(y))
        assert isinstance(type_, int), "expected type 'int' for parameter 'type_', got '{}'".format(type(type_))
        await self.__client.exec(self.__name + ':select-lockpoint', x, y, type_, input_stream=None, output_type=None, return_type=None)


class AlCandidateFilter:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._edge_level = MutableDecofReal(client, name + ':edge-level')
        self._peak_noise_tolerance = MutableDecofReal(client, name + ':peak-noise-tolerance')
        self._bottom = MutableDecofBoolean(client, name + ':bottom')
        self._positive_edge = MutableDecofBoolean(client, name + ':positive-edge')
        self._edge_min_distance = MutableDecofInteger(client, name + ':edge-min-distance')
        self._negative_edge = MutableDecofBoolean(client, name + ':negative-edge')
        self._top = MutableDecofBoolean(client, name + ':top')

    @property
    def edge_level(self) -> 'MutableDecofReal':
        return self._edge_level

    @property
    def peak_noise_tolerance(self) -> 'MutableDecofReal':
        return self._peak_noise_tolerance

    @property
    def bottom(self) -> 'MutableDecofBoolean':
        return self._bottom

    @property
    def positive_edge(self) -> 'MutableDecofBoolean':
        return self._positive_edge

    @property
    def edge_min_distance(self) -> 'MutableDecofInteger':
        return self._edge_min_distance

    @property
    def negative_edge(self) -> 'MutableDecofBoolean':
        return self._negative_edge

    @property
    def top(self) -> 'MutableDecofBoolean':
        return self._top


class Lockin:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._modulation_enabled = MutableDecofBoolean(client, name + ':modulation-enabled')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._modulation_output_channel = MutableDecofInteger(client, name + ':modulation-output-channel')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._auto_lir = AutoLir(client, name + ':auto-lir')
        self._lock_level = MutableDecofReal(client, name + ':lock-level')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def modulation_enabled(self) -> 'MutableDecofBoolean':
        return self._modulation_enabled

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def modulation_output_channel(self) -> 'MutableDecofInteger':
        return self._modulation_output_channel

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def auto_lir(self) -> 'AutoLir':
        return self._auto_lir

    @property
    def lock_level(self) -> 'MutableDecofReal':
        return self._lock_level


class AutoLir:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress = DecofInteger(client, name + ':progress')

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    async def auto_lir(self) -> None:
        await self.__client.exec(self.__name + ':auto-lir', input_stream=None, output_type=None, return_type=None)


class AlRelock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._delay = MutableDecofReal(client, name + ':delay')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel


class AlReset:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Coordinate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    async def get(self) -> Tuple[float, float]:
        return await self.__client.get(self.__name)

    async def set(self, x: float, y: float) -> None:
        assert isinstance(x, float), "expected type 'float' for 'x', got '{}'".format(type(x))
        assert isinstance(y, float), "expected type 'float' for 'y', got '{}'".format(type(y))
        await self.__client.set(self.__name, x, y)


class AlLockpoint:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._type_ = DecofString(client, name + ':type')
        self._position = Coordinate(client, name + ':position')

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def position(self) -> 'Coordinate':
        return self._position


class Pid:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._outputlimit = Outputlimit(client, name + ':outputlimit')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._gain = Gain(client, name + ':gain')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._regulating_state = DecofBoolean(client, name + ':regulating-state')
        self._hold_state = DecofBoolean(client, name + ':hold-state')
        self._lock_state = DecofBoolean(client, name + ':lock-state')
        self._slope = MutableDecofBoolean(client, name + ':slope')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')

    @property
    def outputlimit(self) -> 'Outputlimit':
        return self._outputlimit

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def gain(self) -> 'Gain':
        return self._gain

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def regulating_state(self) -> 'DecofBoolean':
        return self._regulating_state

    @property
    def hold_state(self) -> 'DecofBoolean':
        return self._hold_state

    @property
    def lock_state(self) -> 'DecofBoolean':
        return self._lock_state

    @property
    def slope(self) -> 'MutableDecofBoolean':
        return self._slope

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel


class Outputlimit:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._max = MutableDecofReal(client, name + ':max')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def max(self) -> 'MutableDecofReal':
        return self._max


class Gain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fc_ip = DecofReal(client, name + ':fc-ip')
        self._i = MutableDecofReal(client, name + ':i')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._d = MutableDecofReal(client, name + ':d')
        self._p = MutableDecofReal(client, name + ':p')
        self._all = MutableDecofReal(client, name + ':all')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._fc_pd = DecofReal(client, name + ':fc-pd')

    @property
    def fc_ip(self) -> 'DecofReal':
        return self._fc_ip

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def fc_pd(self) -> 'DecofReal':
        return self._fc_pd


class AlWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._level_high = MutableDecofReal(client, name + ':level-high')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def level_high(self) -> 'MutableDecofReal':
        return self._level_high

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class PdCal:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power = DecofReal(client, name + ':power')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class PressureCompensation:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._offset = DecofReal(client, name + ':offset')
        self._compensation_voltage = DecofReal(client, name + ':compensation-voltage')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._air_pressure = DecofReal(client, name + ':air-pressure')
        self._factor = MutableDecofReal(client, name + ':factor')

    @property
    def offset(self) -> 'DecofReal':
        return self._offset

    @property
    def compensation_voltage(self) -> 'DecofReal':
        return self._compensation_voltage

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def air_pressure(self) -> 'DecofReal':
        return self._air_pressure

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor


class LhFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pd = LhFactoryPd(client, name + ':pd')
        self._cc = LhFactoryCc(client, name + ':cc')
        self._threshold_current = MutableDecofReal(client, name + ':threshold-current')
        self._pc = PcFactorySettings(client, name + ':pc')
        self._power = MutableDecofReal(client, name + ':power')
        self._last_modified = DecofString(client, name + ':last-modified')
        self._modified = DecofBoolean(client, name + ':modified')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._tc = TcFactorySettings(client, name + ':tc')

    @property
    def pd(self) -> 'LhFactoryPd':
        return self._pd

    @property
    def cc(self) -> 'LhFactoryCc':
        return self._cc

    @property
    def threshold_current(self) -> 'MutableDecofReal':
        return self._threshold_current

    @property
    def pc(self) -> 'PcFactorySettings':
        return self._pc

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

    @property
    def tc(self) -> 'TcFactorySettings':
        return self._tc

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class LhFactoryPd:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class LhFactoryCc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber


class PcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._pressure_compensation_factor = MutableDecofReal(client, name + ':pressure-compensation-factor')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def pressure_compensation_factor(self) -> 'MutableDecofReal':
        return self._pressure_compensation_factor

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class CurrDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._aux = DecofReal(client, name + ':aux')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._path = DecofString(client, name + ':path')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._variant = DecofString(client, name + ':variant')
        self._pd = DecofReal(client, name + ':pd')
        self._emission = DecofBoolean(client, name + ':emission')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._status = DecofInteger(client, name + ':status')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class ScanGenerator:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._end = MutableDecofReal(client, name + ':end')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._start = MutableDecofReal(client, name + ':start')
        self._unit = DecofString(client, name + ':unit')
        self._offset = MutableDecofReal(client, name + ':offset')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._signal_type = MutableDecofInteger(client, name + ':signal-type')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def end(self) -> 'MutableDecofReal':
        return self._end

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def start(self) -> 'MutableDecofReal':
        return self._start

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def signal_type(self) -> 'MutableDecofInteger':
        return self._signal_type

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel


class UvShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._error = DecofInteger(client, name + ':error')
        self._ssw_ver = DecofString(client, name + ':ssw-ver')
        self._operation_time = DecofReal(client, name + ':operation-time')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._crystal = UvCrystal(client, name + ':crystal')
        self._baseplate_temperature = DecofReal(client, name + ':baseplate-temperature')
        self._remaining_optics_spots = DecofInteger(client, name + ':remaining-optics-spots')
        self._power_optimization = UvShgPowerOptimization(client, name + ':power-optimization')
        self._status_parameters = UvStatusParameters(client, name + ':status-parameters')
        self._error_txt = DecofString(client, name + ':error-txt')
        self._eom = UvEom(client, name + ':eom')
        self._servo = NloLaserHeadUvServos(client, name + ':servo')
        self._pump = Dpss1(client, name + ':pump')
        self._lock = NloLaserHeadLockShg1(client, name + ':lock')
        self._power_margin = DecofReal(client, name + ':power-margin')
        self._scope = NloLaserHeadScopeT1(client, name + ':scope')
        self._pd = NloLaserHeadUvPhotoDiodes(client, name + ':pd')
        self._scan = NloLaserHeadSiggen1(client, name + ':scan')
        self._status = DecofInteger(client, name + ':status')
        self._cavity = UvCavity(client, name + ':cavity')
        self._power_stabilization = UvShgPowerStabilization(client, name + ':power-stabilization')
        self._factory_settings = UvFactorySettings(client, name + ':factory-settings')

    @property
    def error(self) -> 'DecofInteger':
        return self._error

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def operation_time(self) -> 'DecofReal':
        return self._operation_time

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def crystal(self) -> 'UvCrystal':
        return self._crystal

    @property
    def baseplate_temperature(self) -> 'DecofReal':
        return self._baseplate_temperature

    @property
    def remaining_optics_spots(self) -> 'DecofInteger':
        return self._remaining_optics_spots

    @property
    def power_optimization(self) -> 'UvShgPowerOptimization':
        return self._power_optimization

    @property
    def status_parameters(self) -> 'UvStatusParameters':
        return self._status_parameters

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt

    @property
    def eom(self) -> 'UvEom':
        return self._eom

    @property
    def servo(self) -> 'NloLaserHeadUvServos':
        return self._servo

    @property
    def pump(self) -> 'Dpss1':
        return self._pump

    @property
    def lock(self) -> 'NloLaserHeadLockShg1':
        return self._lock

    @property
    def power_margin(self) -> 'DecofReal':
        return self._power_margin

    @property
    def scope(self) -> 'NloLaserHeadScopeT1':
        return self._scope

    @property
    def pd(self) -> 'NloLaserHeadUvPhotoDiodes':
        return self._pd

    @property
    def scan(self) -> 'NloLaserHeadSiggen1':
        return self._scan

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def cavity(self) -> 'UvCavity':
        return self._cavity

    @property
    def power_stabilization(self) -> 'UvShgPowerStabilization':
        return self._power_stabilization

    @property
    def factory_settings(self) -> 'UvFactorySettings':
        return self._factory_settings

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def perform_optimization(self) -> None:
        await self.__client.exec(self.__name + ':perform-optimization', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    async def clear_errors(self) -> None:
        await self.__client.exec(self.__name + ':clear-errors', input_stream=None, output_type=None, return_type=None)


class UvCrystal:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._optics_shifters = NloLaserHeadUvCrystalSpots(client, name + ':optics-shifters')
        self._tc = TcChannel1(client, name + ':tc')

    @property
    def optics_shifters(self) -> 'NloLaserHeadUvCrystalSpots':
        return self._optics_shifters

    @property
    def tc(self) -> 'TcChannel1':
        return self._tc


class NloLaserHeadUvCrystalSpots:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_spot = DecofInteger(client, name + ':current-spot')
        self._remaining_spots = DecofInteger(client, name + ':remaining-spots')

    @property
    def current_spot(self) -> 'DecofInteger':
        return self._current_spot

    @property
    def remaining_spots(self) -> 'DecofInteger':
        return self._remaining_spots


class TcChannel1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._t_loop = TcChannelTLoop1(client, name + ':t-loop')
        self._ntc_parallel_resistance = DecofReal(client, name + ':ntc-parallel-resistance')
        self._temp_roc_enabled = DecofBoolean(client, name + ':temp-roc-enabled')
        self._drv_voltage = DecofReal(client, name + ':drv-voltage')
        self._path = DecofString(client, name + ':path')
        self._c_loop = TcChannelCLoop1(client, name + ':c-loop')
        self._ntc_series_resistance = DecofReal(client, name + ':ntc-series-resistance')
        self._temp_set = DecofReal(client, name + ':temp-set')
        self._temp_set_min = DecofReal(client, name + ':temp-set-min')
        self._temp_set_max = DecofReal(client, name + ':temp-set-max')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._current_set_max = DecofReal(client, name + ':current-set-max')
        self._current_set_min = DecofReal(client, name + ':current-set-min')
        self._fault = DecofBoolean(client, name + ':fault')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._power_source = DecofInteger(client, name + ':power-source')
        self._temp_roc_limit = DecofReal(client, name + ':temp-roc-limit')
        self._temp_reset = DecofBoolean(client, name + ':temp-reset')
        self._limits = TcChannelCheck1(client, name + ':limits')
        self._resistance = DecofReal(client, name + ':resistance')
        self._ready = DecofBoolean(client, name + ':ready')
        self._status = DecofInteger(client, name + ':status')
        self._temp_act = DecofReal(client, name + ':temp-act')
        self._current_set = DecofReal(client, name + ':current-set')
        self._enabled = DecofBoolean(client, name + ':enabled')

    @property
    def t_loop(self) -> 'TcChannelTLoop1':
        return self._t_loop

    @property
    def ntc_parallel_resistance(self) -> 'DecofReal':
        return self._ntc_parallel_resistance

    @property
    def temp_roc_enabled(self) -> 'DecofBoolean':
        return self._temp_roc_enabled

    @property
    def drv_voltage(self) -> 'DecofReal':
        return self._drv_voltage

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def c_loop(self) -> 'TcChannelCLoop1':
        return self._c_loop

    @property
    def ntc_series_resistance(self) -> 'DecofReal':
        return self._ntc_series_resistance

    @property
    def temp_set(self) -> 'DecofReal':
        return self._temp_set

    @property
    def temp_set_min(self) -> 'DecofReal':
        return self._temp_set_min

    @property
    def temp_set_max(self) -> 'DecofReal':
        return self._temp_set_max

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def current_set_max(self) -> 'DecofReal':
        return self._current_set_max

    @property
    def current_set_min(self) -> 'DecofReal':
        return self._current_set_min

    @property
    def fault(self) -> 'DecofBoolean':
        return self._fault

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def power_source(self) -> 'DecofInteger':
        return self._power_source

    @property
    def temp_roc_limit(self) -> 'DecofReal':
        return self._temp_roc_limit

    @property
    def temp_reset(self) -> 'DecofBoolean':
        return self._temp_reset

    @property
    def limits(self) -> 'TcChannelCheck1':
        return self._limits

    @property
    def resistance(self) -> 'DecofReal':
        return self._resistance

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def temp_act(self) -> 'DecofReal':
        return self._temp_act

    @property
    def current_set(self) -> 'DecofReal':
        return self._current_set

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled


class TcChannelTLoop1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ok_time = DecofReal(client, name + ':ok-time')
        self._p_gain = DecofReal(client, name + ':p-gain')
        self._d_gain = DecofReal(client, name + ':d-gain')
        self._i_gain = DecofReal(client, name + ':i-gain')
        self._ok_tolerance = DecofReal(client, name + ':ok-tolerance')
        self._on = DecofBoolean(client, name + ':on')

    @property
    def ok_time(self) -> 'DecofReal':
        return self._ok_time

    @property
    def p_gain(self) -> 'DecofReal':
        return self._p_gain

    @property
    def d_gain(self) -> 'DecofReal':
        return self._d_gain

    @property
    def i_gain(self) -> 'DecofReal':
        return self._i_gain

    @property
    def ok_tolerance(self) -> 'DecofReal':
        return self._ok_tolerance

    @property
    def on(self) -> 'DecofBoolean':
        return self._on


class TcChannelCLoop1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_gain = DecofReal(client, name + ':i-gain')
        self._on = DecofBoolean(client, name + ':on')

    @property
    def i_gain(self) -> 'DecofReal':
        return self._i_gain

    @property
    def on(self) -> 'DecofBoolean':
        return self._on


class ExtInput1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = DecofInteger(client, name + ':signal')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._factor = DecofReal(client, name + ':factor')

    @property
    def signal(self) -> 'DecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'DecofReal':
        return self._factor


class TcChannelCheck1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._temp_min = DecofReal(client, name + ':temp-min')
        self._timed_out = DecofBoolean(client, name + ':timed-out')
        self._out_of_range = DecofBoolean(client, name + ':out-of-range')
        self._temp_max = DecofReal(client, name + ':temp-max')
        self._timeout = DecofInteger(client, name + ':timeout')

    @property
    def temp_min(self) -> 'DecofReal':
        return self._temp_min

    @property
    def timed_out(self) -> 'DecofBoolean':
        return self._timed_out

    @property
    def out_of_range(self) -> 'DecofBoolean':
        return self._out_of_range

    @property
    def temp_max(self) -> 'DecofReal':
        return self._temp_max

    @property
    def timeout(self) -> 'DecofInteger':
        return self._timeout


class UvShgPowerOptimization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress_data = DecofBinary(client, name + ':progress-data')
        self._ongoing = DecofBoolean(client, name + ':ongoing')
        self._status_string = DecofString(client, name + ':status-string')
        self._status = DecofInteger(client, name + ':status')
        self._cavity = NloLaserHeadStage1(client, name + ':cavity')
        self._abort = DecofBoolean(client, name + ':abort')

    @property
    def progress_data(self) -> 'DecofBinary':
        return self._progress_data

    @property
    def ongoing(self) -> 'DecofBoolean':
        return self._ongoing

    @property
    def status_string(self) -> 'DecofString':
        return self._status_string

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def cavity(self) -> 'NloLaserHeadStage1':
        return self._cavity

    @property
    def abort(self) -> 'DecofBoolean':
        return self._abort


class NloLaserHeadStage1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._restore_on_regress = DecofBoolean(client, name + ':restore-on-regress')
        self._optimization_in_progress = DecofBoolean(client, name + ':optimization-in-progress')
        self._progress = DecofInteger(client, name + ':progress')
        self._restore_on_abort = DecofBoolean(client, name + ':restore-on-abort')
        self._regress_tolerance = DecofInteger(client, name + ':regress-tolerance')
        self._input = NloLaserHeadOptInput1(client, name + ':input')

    @property
    def restore_on_regress(self) -> 'DecofBoolean':
        return self._restore_on_regress

    @property
    def optimization_in_progress(self) -> 'DecofBoolean':
        return self._optimization_in_progress

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def restore_on_abort(self) -> 'DecofBoolean':
        return self._restore_on_abort

    @property
    def regress_tolerance(self) -> 'DecofInteger':
        return self._regress_tolerance

    @property
    def input(self) -> 'NloLaserHeadOptInput1':
        return self._input


class NloLaserHeadOptInput1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_calibrated = DecofReal(client, name + ':value-calibrated')

    @property
    def value_calibrated(self) -> 'DecofReal':
        return self._value_calibrated


class UvStatusParameters:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cavity_lock_settle_time = DecofInteger(client, name + ':cavity-lock-settle-time')
        self._power_stabilization_strategy = DecofInteger(client, name + ':power-stabilization-strategy')
        self._pump_lock_settle_time = DecofInteger(client, name + ':pump-lock-settle-time')
        self._power_output_relative_error_max = DecofReal(client, name + ':power-output-relative-error-max')
        self._power_output_relative_deviation_max = DecofReal(client, name + ':power-output-relative-deviation-max')
        self._power_margin_threshold = DecofReal(client, name + ':power-margin-threshold')
        self._operational_pump_power = DecofReal(client, name + ':operational-pump-power')
        self._cavity_lock_tolerance_factor = DecofInteger(client, name + ':cavity-lock-tolerance-factor')
        self._temperature_settle_time = DecofInteger(client, name + ':temperature-settle-time')
        self._settle_down_delay = DecofInteger(client, name + ':settle-down-delay')
        self._baseplate_temperature_limit = DecofReal(client, name + ':baseplate-temperature-limit')
        self._power_margin_tolerance_time = DecofInteger(client, name + ':power-margin-tolerance-time')
        self._power_lock_settle_time = DecofInteger(client, name + ':power-lock-settle-time')
        self._cavity_scan_duration = DecofInteger(client, name + ':cavity-scan-duration')

    @property
    def cavity_lock_settle_time(self) -> 'DecofInteger':
        return self._cavity_lock_settle_time

    @property
    def power_stabilization_strategy(self) -> 'DecofInteger':
        return self._power_stabilization_strategy

    @property
    def pump_lock_settle_time(self) -> 'DecofInteger':
        return self._pump_lock_settle_time

    @property
    def power_output_relative_error_max(self) -> 'DecofReal':
        return self._power_output_relative_error_max

    @property
    def power_output_relative_deviation_max(self) -> 'DecofReal':
        return self._power_output_relative_deviation_max

    @property
    def power_margin_threshold(self) -> 'DecofReal':
        return self._power_margin_threshold

    @property
    def operational_pump_power(self) -> 'DecofReal':
        return self._operational_pump_power

    @property
    def cavity_lock_tolerance_factor(self) -> 'DecofInteger':
        return self._cavity_lock_tolerance_factor

    @property
    def temperature_settle_time(self) -> 'DecofInteger':
        return self._temperature_settle_time

    @property
    def settle_down_delay(self) -> 'DecofInteger':
        return self._settle_down_delay

    @property
    def baseplate_temperature_limit(self) -> 'DecofReal':
        return self._baseplate_temperature_limit

    @property
    def power_margin_tolerance_time(self) -> 'DecofInteger':
        return self._power_margin_tolerance_time

    @property
    def power_lock_settle_time(self) -> 'DecofInteger':
        return self._power_lock_settle_time

    @property
    def cavity_scan_duration(self) -> 'DecofInteger':
        return self._cavity_scan_duration


class UvEom:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tc = TcChannel1(client, name + ':tc')

    @property
    def tc(self) -> 'TcChannel1':
        return self._tc


class NloLaserHeadUvServos:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg1_hor = NloLaserHeadServoPwm1(client, name + ':shg1-hor')
        self._hwp = NloLaserHeadServoPwm1(client, name + ':hwp')
        self._lens = NloLaserHeadServoPwm1(client, name + ':lens')
        self._outcpl = NloLaserHeadServoPwm1(client, name + ':outcpl')
        self._cryst = NloLaserHeadServoPwm1(client, name + ':cryst')
        self._comp_vert = NloLaserHeadServoPwm1(client, name + ':comp-vert')
        self._comp_hor = NloLaserHeadServoPwm1(client, name + ':comp-hor')
        self._shg2_hor = NloLaserHeadServoPwm1(client, name + ':shg2-hor')
        self._shg1_vert = NloLaserHeadServoPwm1(client, name + ':shg1-vert')
        self._shg2_vert = NloLaserHeadServoPwm1(client, name + ':shg2-vert')

    @property
    def shg1_hor(self) -> 'NloLaserHeadServoPwm1':
        return self._shg1_hor

    @property
    def hwp(self) -> 'NloLaserHeadServoPwm1':
        return self._hwp

    @property
    def lens(self) -> 'NloLaserHeadServoPwm1':
        return self._lens

    @property
    def outcpl(self) -> 'NloLaserHeadServoPwm1':
        return self._outcpl

    @property
    def cryst(self) -> 'NloLaserHeadServoPwm1':
        return self._cryst

    @property
    def comp_vert(self) -> 'NloLaserHeadServoPwm1':
        return self._comp_vert

    @property
    def comp_hor(self) -> 'NloLaserHeadServoPwm1':
        return self._comp_hor

    @property
    def shg2_hor(self) -> 'NloLaserHeadServoPwm1':
        return self._shg2_hor

    @property
    def shg1_vert(self) -> 'NloLaserHeadServoPwm1':
        return self._shg1_vert

    @property
    def shg2_vert(self) -> 'NloLaserHeadServoPwm1':
        return self._shg2_vert


class NloLaserHeadServoPwm1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._display_name = DecofString(client, name + ':display-name')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._value = DecofInteger(client, name + ':value')

    @property
    def display_name(self) -> 'DecofString':
        return self._display_name

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def value(self) -> 'DecofInteger':
        return self._value


class Dpss1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_max = DecofReal(client, name + ':current-max')
        self._tc_status_txt = DecofString(client, name + ':tc-status-txt')
        self._error_code = DecofInteger(client, name + ':error-code')
        self._power_margin = DecofReal(client, name + ':power-margin')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._operation_time = DecofReal(client, name + ':operation-time')
        self._power_act = DecofReal(client, name + ':power-act')
        self._status = DecofInteger(client, name + ':status')
        self._power_max = DecofReal(client, name + ':power-max')
        self._power_set = DecofReal(client, name + ':power-set')
        self._error_txt = DecofString(client, name + ':error-txt')
        self._tc_status = DecofInteger(client, name + ':tc-status')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._current_act = DecofReal(client, name + ':current-act')

    @property
    def current_max(self) -> 'DecofReal':
        return self._current_max

    @property
    def tc_status_txt(self) -> 'DecofString':
        return self._tc_status_txt

    @property
    def error_code(self) -> 'DecofInteger':
        return self._error_code

    @property
    def power_margin(self) -> 'DecofReal':
        return self._power_margin

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def operation_time(self) -> 'DecofReal':
        return self._operation_time

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def power_max(self) -> 'DecofReal':
        return self._power_max

    @property
    def power_set(self) -> 'DecofReal':
        return self._power_set

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt

    @property
    def tc_status(self) -> 'DecofInteger':
        return self._tc_status

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act


class NloLaserHeadLockShg1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._cavity_fast_pzt_voltage = DecofReal(client, name + ':cavity-fast-pzt-voltage')
        self._local_oscillator = NloLaserHeadLocalOscillatorShg1(client, name + ':local-oscillator')
        self._relock = NloLaserHeadRelock1(client, name + ':relock')
        self._lock_enabled = DecofBoolean(client, name + ':lock-enabled')
        self._window = NloLaserHeadWindow1(client, name + ':window')
        self._cavity_slow_pzt_voltage = DecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._pid_selection = DecofInteger(client, name + ':pid-selection')
        self._pid2 = NloLaserHeadPid1(client, name + ':pid2')
        self._analog_dl_gain = NloLaserHeadMinifalc1(client, name + ':analog-dl-gain')
        self._setpoint = DecofReal(client, name + ':setpoint')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._pid1 = NloLaserHeadPid1(client, name + ':pid1')
        self._state = DecofInteger(client, name + ':state')

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def cavity_fast_pzt_voltage(self) -> 'DecofReal':
        return self._cavity_fast_pzt_voltage

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorShg1':
        return self._local_oscillator

    @property
    def relock(self) -> 'NloLaserHeadRelock1':
        return self._relock

    @property
    def lock_enabled(self) -> 'DecofBoolean':
        return self._lock_enabled

    @property
    def window(self) -> 'NloLaserHeadWindow1':
        return self._window

    @property
    def cavity_slow_pzt_voltage(self) -> 'DecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def pid_selection(self) -> 'DecofInteger':
        return self._pid_selection

    @property
    def pid2(self) -> 'NloLaserHeadPid1':
        return self._pid2

    @property
    def analog_dl_gain(self) -> 'NloLaserHeadMinifalc1':
        return self._analog_dl_gain

    @property
    def setpoint(self) -> 'DecofReal':
        return self._setpoint

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def pid1(self) -> 'NloLaserHeadPid1':
        return self._pid1

    @property
    def state(self) -> 'DecofInteger':
        return self._state


class NloLaserHeadLocalOscillatorShg1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = DecofReal(client, name + ':amplitude')
        self._attenuation_raw = DecofInteger(client, name + ':attenuation-raw')
        self._coupled_modulation = DecofBoolean(client, name + ':coupled-modulation')
        self._phase_shift = DecofReal(client, name + ':phase-shift')
        self._use_external_oscillator = DecofBoolean(client, name + ':use-external-oscillator')
        self._use_fast_oscillator = DecofBoolean(client, name + ':use-fast-oscillator')
        self._enabled = DecofBoolean(client, name + ':enabled')

    @property
    def amplitude(self) -> 'DecofReal':
        return self._amplitude

    @property
    def attenuation_raw(self) -> 'DecofInteger':
        return self._attenuation_raw

    @property
    def coupled_modulation(self) -> 'DecofBoolean':
        return self._coupled_modulation

    @property
    def phase_shift(self) -> 'DecofReal':
        return self._phase_shift

    @property
    def use_external_oscillator(self) -> 'DecofBoolean':
        return self._use_external_oscillator

    @property
    def use_fast_oscillator(self) -> 'DecofBoolean':
        return self._use_fast_oscillator

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled


class NloLaserHeadRelock1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = DecofReal(client, name + ':amplitude')
        self._frequency = DecofReal(client, name + ':frequency')
        self._delay = DecofReal(client, name + ':delay')
        self._enabled = DecofBoolean(client, name + ':enabled')

    @property
    def amplitude(self) -> 'DecofReal':
        return self._amplitude

    @property
    def frequency(self) -> 'DecofReal':
        return self._frequency

    @property
    def delay(self) -> 'DecofReal':
        return self._delay

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled


class NloLaserHeadWindow1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._threshold = DecofReal(client, name + ':threshold')
        self._level_hysteresis = DecofReal(client, name + ':level-hysteresis')
        self._input_channel = DecofInteger(client, name + ':input-channel')

    @property
    def threshold(self) -> 'DecofReal':
        return self._threshold

    @property
    def level_hysteresis(self) -> 'DecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'DecofInteger':
        return self._input_channel


class NloLaserHeadPid1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = NloLaserHeadGain1(client, name + ':gain')

    @property
    def gain(self) -> 'NloLaserHeadGain1':
        return self._gain


class NloLaserHeadGain1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i = DecofReal(client, name + ':i')
        self._i_cutoff_enabled = DecofBoolean(client, name + ':i-cutoff-enabled')
        self._d = DecofReal(client, name + ':d')
        self._p = DecofReal(client, name + ':p')
        self._all = DecofReal(client, name + ':all')
        self._i_cutoff = DecofReal(client, name + ':i-cutoff')

    @property
    def i(self) -> 'DecofReal':
        return self._i

    @property
    def i_cutoff_enabled(self) -> 'DecofBoolean':
        return self._i_cutoff_enabled

    @property
    def d(self) -> 'DecofReal':
        return self._d

    @property
    def p(self) -> 'DecofReal':
        return self._p

    @property
    def all(self) -> 'DecofReal':
        return self._all

    @property
    def i_cutoff(self) -> 'DecofReal':
        return self._i_cutoff


class NloLaserHeadMinifalc1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p_gain = DecofReal(client, name + ':p-gain')

    @property
    def p_gain(self) -> 'DecofReal':
        return self._p_gain


class NloLaserHeadScopeT1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channelx = NloLaserHeadScopeXAxisT1(client, name + ':channelx')
        self._update_rate = DecofInteger(client, name + ':update-rate')
        self._data = DecofBinary(client, name + ':data')
        self._channel2 = NloLaserHeadScopeChannelT1(client, name + ':channel2')
        self._variant = DecofInteger(client, name + ':variant')
        self._channel1 = NloLaserHeadScopeChannelT1(client, name + ':channel1')
        self._timescale = DecofReal(client, name + ':timescale')

    @property
    def channelx(self) -> 'NloLaserHeadScopeXAxisT1':
        return self._channelx

    @property
    def update_rate(self) -> 'DecofInteger':
        return self._update_rate

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channel2(self) -> 'NloLaserHeadScopeChannelT1':
        return self._channel2

    @property
    def variant(self) -> 'DecofInteger':
        return self._variant

    @property
    def channel1(self) -> 'NloLaserHeadScopeChannelT1':
        return self._channel1

    @property
    def timescale(self) -> 'DecofReal':
        return self._timescale


class NloLaserHeadScopeXAxisT1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._spectrum_range = DecofReal(client, name + ':spectrum-range')
        self._xy_signal = DecofInteger(client, name + ':xy-signal')
        self._name = DecofString(client, name + ':name')
        self._spectrum_omit_dc = DecofBoolean(client, name + ':spectrum-omit-dc')
        self._scope_timescale = DecofReal(client, name + ':scope-timescale')
        self._unit = DecofString(client, name + ':unit')

    @property
    def spectrum_range(self) -> 'DecofReal':
        return self._spectrum_range

    @property
    def xy_signal(self) -> 'DecofInteger':
        return self._xy_signal

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def spectrum_omit_dc(self) -> 'DecofBoolean':
        return self._spectrum_omit_dc

    @property
    def scope_timescale(self) -> 'DecofReal':
        return self._scope_timescale

    @property
    def unit(self) -> 'DecofString':
        return self._unit


class NloLaserHeadScopeChannelT1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._name = DecofString(client, name + ':name')
        self._signal = DecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')
        self._enabled = DecofBoolean(client, name + ':enabled')

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def signal(self) -> 'DecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled


class NloLaserHeadUvPhotoDiodes:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg = NloLaserHeadNloPhotodiode1(client, name + ':shg')
        self._pdh_dc = NloLaserHeadNloDigilockPhotodiode1(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadNloPdhPhotodiode1(client, name + ':pdh-rf')

    @property
    def shg(self) -> 'NloLaserHeadNloPhotodiode1':
        return self._shg

    @property
    def pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode1':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode1':
        return self._pdh_rf


class NloLaserHeadNloPhotodiode1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = DecofReal(client, name + ':cal-factor')
        self._cal_offset = DecofReal(client, name + ':cal-offset')
        self._power = DecofReal(client, name + ':power')

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'DecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'DecofReal':
        return self._cal_offset

    @property
    def power(self) -> 'DecofReal':
        return self._power


class NloLaserHeadNloDigilockPhotodiode1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = DecofReal(client, name + ':cal-offset')

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'DecofReal':
        return self._cal_offset


class NloLaserHeadNloPdhPhotodiode1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._gain = DecofReal(client, name + ':gain')

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def gain(self) -> 'DecofReal':
        return self._gain


class NloLaserHeadSiggen1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = DecofReal(client, name + ':amplitude')
        self._frequency = DecofReal(client, name + ':frequency')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._offset = DecofReal(client, name + ':offset')

    @property
    def amplitude(self) -> 'DecofReal':
        return self._amplitude

    @property
    def frequency(self) -> 'DecofReal':
        return self._frequency

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def offset(self) -> 'DecofReal':
        return self._offset


class UvCavity:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pc = PiezoDrv1(client, name + ':pc')
        self._tc = TcChannel1(client, name + ':tc')

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def tc(self) -> 'TcChannel1':
        return self._tc


class PiezoDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._path = DecofString(client, name + ':path')
        self._voltage_max = DecofReal(client, name + ':voltage-max')
        self._voltage_min = DecofReal(client, name + ':voltage-min')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._voltage_set_dithering = DecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_set = DecofReal(client, name + ':voltage-set')
        self._feedforward_factor = DecofReal(client, name + ':feedforward-factor')
        self._status = DecofInteger(client, name + ':status')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._feedforward_master = DecofInteger(client, name + ':feedforward-master')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._feedforward_enabled = DecofBoolean(client, name + ':feedforward-enabled')

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def voltage_max(self) -> 'DecofReal':
        return self._voltage_max

    @property
    def voltage_min(self) -> 'DecofReal':
        return self._voltage_min

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def voltage_set_dithering(self) -> 'DecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_set(self) -> 'DecofReal':
        return self._voltage_set

    @property
    def feedforward_factor(self) -> 'DecofReal':
        return self._feedforward_factor

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def feedforward_master(self) -> 'DecofInteger':
        return self._feedforward_master

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def feedforward_enabled(self) -> 'DecofBoolean':
        return self._feedforward_enabled


class OutputFilter1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate = DecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')
        self._slew_rate_enabled = DecofBoolean(client, name + ':slew-rate-enabled')

    @property
    def slew_rate(self) -> 'DecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited

    @property
    def slew_rate_enabled(self) -> 'DecofBoolean':
        return self._slew_rate_enabled


class UvShgPowerStabilization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')
        self._power_set = DecofReal(client, name + ':power-set')
        self._power_max = DecofReal(client, name + ':power-max')
        self._power_min = DecofReal(client, name + ':power-min')
        self._gain = PwrStabGain1(client, name + ':gain')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._state = DecofInteger(client, name + ':state')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def power_set(self) -> 'DecofReal':
        return self._power_set

    @property
    def power_max(self) -> 'DecofReal':
        return self._power_max

    @property
    def power_min(self) -> 'DecofReal':
        return self._power_min

    @property
    def gain(self) -> 'PwrStabGain1':
        return self._gain

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def state(self) -> 'DecofInteger':
        return self._state


class PwrStabGain1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p = DecofReal(client, name + ':p')
        self._i = DecofReal(client, name + ':i')
        self._all = DecofReal(client, name + ':all')
        self._d = DecofReal(client, name + ':d')

    @property
    def p(self) -> 'DecofReal':
        return self._p

    @property
    def i(self) -> 'DecofReal':
        return self._i

    @property
    def all(self) -> 'DecofReal':
        return self._all

    @property
    def d(self) -> 'DecofReal':
        return self._d


class UvFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pd = NloLaserHeadUvPhotodiodesFactorySettings(client, name + ':pd')
        self._cavity_tc = NloLaserHeadTcFactorySettings(client, name + ':cavity-tc')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._eom_tc = NloLaserHeadTcFactorySettings(client, name + ':eom-tc')
        self._modified = DecofBoolean(client, name + ':modified')
        self._crystal_tc = NloLaserHeadTcFactorySettings(client, name + ':crystal-tc')

    @property
    def pd(self) -> 'NloLaserHeadUvPhotodiodesFactorySettings':
        return self._pd

    @property
    def cavity_tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._cavity_tc

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def eom_tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._eom_tc

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def crystal_tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._crystal_tc

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadUvPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg = NloLaserHeadPdFactorySettings(client, name + ':shg')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')

    @property
    def shg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._shg

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf


class PwrStab:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._output_channel = DecofInteger(client, name + ':output-channel')
        self._input_channel_value_act = DecofReal(client, name + ':input-channel-value-act')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._window = PwrStabWindow(client, name + ':window')
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._gain = PwrStabGain2(client, name + ':gain')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._state = DecofInteger(client, name + ':state')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')

    @property
    def output_channel(self) -> 'DecofInteger':
        return self._output_channel

    @property
    def input_channel_value_act(self) -> 'DecofReal':
        return self._input_channel_value_act

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def window(self) -> 'PwrStabWindow':
        return self._window

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def gain(self) -> 'PwrStabGain2':
        return self._gain

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled


class PwrStabWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class PwrStabGain2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p = MutableDecofReal(client, name + ':p')
        self._i = MutableDecofReal(client, name + ':i')
        self._all = MutableDecofReal(client, name + ':all')
        self._d = MutableDecofReal(client, name + ':d')

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d


class ScopeT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channelx = ScopeXAxisT(client, name + ':channelx')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')
        self._data = DecofBinary(client, name + ':data')
        self._channel2 = ScopeChannelT(client, name + ':channel2')
        self._variant = MutableDecofInteger(client, name + ':variant')
        self._channel1 = ScopeChannelT(client, name + ':channel1')
        self._timescale = MutableDecofReal(client, name + ':timescale')

    @property
    def channelx(self) -> 'ScopeXAxisT':
        return self._channelx

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channel2(self) -> 'ScopeChannelT':
        return self._channel2

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant

    @property
    def channel1(self) -> 'ScopeChannelT':
        return self._channel1

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale


class ScopeXAxisT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._name = DecofString(client, name + ':name')
        self._unit = DecofString(client, name + ':unit')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')

    @property
    def spectrum_range(self) -> 'MutableDecofReal':
        return self._spectrum_range

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def scope_timescale(self) -> 'MutableDecofReal':
        return self._scope_timescale

    @property
    def spectrum_omit_dc(self) -> 'MutableDecofBoolean':
        return self._spectrum_omit_dc

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal


class ScopeChannelT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._name = DecofString(client, name + ':name')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Ipconfig:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._net_mask = DecofString(client, name + ':net-mask')
        self._ip_addr = DecofString(client, name + ':ip-addr')
        self._cmd_port = DecofInteger(client, name + ':cmd-port')
        self._mac_addr = DecofString(client, name + ':mac-addr')
        self._mon_port = DecofInteger(client, name + ':mon-port')
        self._dhcp = DecofBoolean(client, name + ':dhcp')

    @property
    def net_mask(self) -> 'DecofString':
        return self._net_mask

    @property
    def ip_addr(self) -> 'DecofString':
        return self._ip_addr

    @property
    def cmd_port(self) -> 'DecofInteger':
        return self._cmd_port

    @property
    def mac_addr(self) -> 'DecofString':
        return self._mac_addr

    @property
    def mon_port(self) -> 'DecofInteger':
        return self._mon_port

    @property
    def dhcp(self) -> 'DecofBoolean':
        return self._dhcp

    async def set_ip(self, ip_addr: str, net_mask: str) -> None:
        assert isinstance(ip_addr, str), "expected type 'str' for parameter 'ip_addr', got '{}'".format(type(ip_addr))
        assert isinstance(net_mask, str), "expected type 'str' for parameter 'net_mask', got '{}'".format(type(net_mask))
        await self.__client.exec(self.__name + ':set-ip', ip_addr, net_mask, input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)

    async def set_dhcp(self) -> None:
        await self.__client.exec(self.__name + ':set-dhcp', input_stream=None, output_type=None, return_type=None)


class BuildInformation:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._build_node_name = DecofString(client, name + ':build-node-name')
        self._c_compiler_id = DecofString(client, name + ':c-compiler-id')
        self._build_tag = DecofString(client, name + ':build-tag')
        self._build_url = DecofString(client, name + ':build-url')
        self._cxx_compiler_id = DecofString(client, name + ':cxx-compiler-id')
        self._cxx_compiler_version = DecofString(client, name + ':cxx-compiler-version')
        self._job_name = DecofString(client, name + ':job-name')
        self._c_compiler_version = DecofString(client, name + ':c-compiler-version')
        self._build_number = DecofInteger(client, name + ':build-number')
        self._build_id = DecofString(client, name + ':build-id')

    @property
    def build_node_name(self) -> 'DecofString':
        return self._build_node_name

    @property
    def c_compiler_id(self) -> 'DecofString':
        return self._c_compiler_id

    @property
    def build_tag(self) -> 'DecofString':
        return self._build_tag

    @property
    def build_url(self) -> 'DecofString':
        return self._build_url

    @property
    def cxx_compiler_id(self) -> 'DecofString':
        return self._cxx_compiler_id

    @property
    def cxx_compiler_version(self) -> 'DecofString':
        return self._cxx_compiler_version

    @property
    def job_name(self) -> 'DecofString':
        return self._job_name

    @property
    def c_compiler_version(self) -> 'DecofString':
        return self._c_compiler_version

    @property
    def build_number(self) -> 'DecofInteger':
        return self._build_number

    @property
    def build_id(self) -> 'DecofString':
        return self._build_id


class DLCpro:
    def __init__(self, connection: Connection) -> None:
        self.__client = Client(connection)
        self._ul = MutableDecofInteger(self.__client, 'ul')
        self._system_messages = SystemMessages(self.__client, 'system-messages')
        self._fw_update = FwUpdate(self.__client, 'fw-update')
        self._tan = DecofInteger(self.__client, 'tan')
        self._time = MutableDecofString(self.__client, 'time')
        self._system_service_report = ServiceReport(self.__client, 'system-service-report')
        self._licenses = Licenses(self.__client, 'licenses')
        self._pc2 = PcBoard(self.__client, 'pc2')
        self._buzzer = Buzzer(self.__client, 'buzzer')
        self._system_health = DecofInteger(self.__client, 'system-health')
        self._power_supply = PowerSupply(self.__client, 'power-supply')
        self._display = Display(self.__client, 'display')
        self._pc1 = PcBoard(self.__client, 'pc1')
        self._pc3 = PcBoard(self.__client, 'pc3')
        self._frontkey_locked = DecofBoolean(self.__client, 'frontkey-locked')
        self._mc = McBoard(self.__client, 'mc')
        self._tc1 = TcBoard(self.__client, 'tc1')
        self._ampcc1 = Cc5000Board(self.__client, 'ampcc1')
        self._tc2 = TcBoard(self.__client, 'tc2')
        self._standby = Standby(self.__client, 'standby')
        self._cc2 = CcBoard(self.__client, 'cc2')
        self._system_health_txt = DecofString(self.__client, 'system-health-txt')
        self._io = IoBoard(self.__client, 'io')
        self._emission = DecofBoolean(self.__client, 'emission')
        self._uv = UvShgLaser(self.__client, 'uv')
        self._cc1 = CcBoard(self.__client, 'cc1')
        self._interlock_open = DecofBoolean(self.__client, 'interlock-open')
        self._laser1 = Laser(self.__client, 'laser1')
        self._ampcc2 = Cc5000Board(self.__client, 'ampcc2')
        self._net_conf = Ipconfig(self.__client, 'net-conf')
        self._svn_revision = DecofString(self.__client, 'svn-revision')
        self._fw_ver = DecofString(self.__client, 'fw-ver')
        self._ssw_ver = DecofString(self.__client, 'ssw-ver')
        self._uptime = DecofInteger(self.__client, 'uptime')
        self._decof_svn_revision = DecofString(self.__client, 'decof-svn-revision')
        self._serial_number = DecofString(self.__client, 'serial-number')
        self._uptime_txt = DecofString(self.__client, 'uptime-txt')
        self._echo = MutableDecofBoolean(self.__client, 'echo')
        self._build_information = BuildInformation(self.__client, 'build-information')
        self._decof_ver = DecofString(self.__client, 'decof-ver')
        self._system_label = MutableDecofString(self.__client, 'system-label')
        self._system_model = DecofString(self.__client, 'system-model')
        self._ssw_svn_revision = DecofString(self.__client, 'ssw-svn-revision')
        self._system_type = DecofString(self.__client, 'system-type')

    def __enter__(self):
        return self

    def __exit__(self):
        raise RuntimeError()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):
        await self.close()

    def __await__(self):
        return self.__aenter__().__await__()

    async def open(self) -> None:
        await self.__client.open()

    async def close(self) -> None:
        await self.__client.close()

    @property
    def ul(self) -> 'MutableDecofInteger':
        return self._ul

    @property
    def system_messages(self) -> 'SystemMessages':
        return self._system_messages

    @property
    def fw_update(self) -> 'FwUpdate':
        return self._fw_update

    @property
    def tan(self) -> 'DecofInteger':
        return self._tan

    @property
    def time(self) -> 'MutableDecofString':
        return self._time

    @property
    def system_service_report(self) -> 'ServiceReport':
        return self._system_service_report

    @property
    def licenses(self) -> 'Licenses':
        return self._licenses

    @property
    def pc2(self) -> 'PcBoard':
        return self._pc2

    @property
    def buzzer(self) -> 'Buzzer':
        return self._buzzer

    @property
    def system_health(self) -> 'DecofInteger':
        return self._system_health

    @property
    def power_supply(self) -> 'PowerSupply':
        return self._power_supply

    @property
    def display(self) -> 'Display':
        return self._display

    @property
    def pc1(self) -> 'PcBoard':
        return self._pc1

    @property
    def pc3(self) -> 'PcBoard':
        return self._pc3

    @property
    def frontkey_locked(self) -> 'DecofBoolean':
        return self._frontkey_locked

    @property
    def mc(self) -> 'McBoard':
        return self._mc

    @property
    def tc1(self) -> 'TcBoard':
        return self._tc1

    @property
    def ampcc1(self) -> 'Cc5000Board':
        return self._ampcc1

    @property
    def tc2(self) -> 'TcBoard':
        return self._tc2

    @property
    def standby(self) -> 'Standby':
        return self._standby

    @property
    def cc2(self) -> 'CcBoard':
        return self._cc2

    @property
    def system_health_txt(self) -> 'DecofString':
        return self._system_health_txt

    @property
    def io(self) -> 'IoBoard':
        return self._io

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def uv(self) -> 'UvShgLaser':
        return self._uv

    @property
    def cc1(self) -> 'CcBoard':
        return self._cc1

    @property
    def interlock_open(self) -> 'DecofBoolean':
        return self._interlock_open

    @property
    def laser1(self) -> 'Laser':
        return self._laser1

    @property
    def ampcc2(self) -> 'Cc5000Board':
        return self._ampcc2

    @property
    def net_conf(self) -> 'Ipconfig':
        return self._net_conf

    @property
    def svn_revision(self) -> 'DecofString':
        return self._svn_revision

    @property
    def fw_ver(self) -> 'DecofString':
        return self._fw_ver

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def uptime(self) -> 'DecofInteger':
        return self._uptime

    @property
    def decof_svn_revision(self) -> 'DecofString':
        return self._decof_svn_revision

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def uptime_txt(self) -> 'DecofString':
        return self._uptime_txt

    @property
    def echo(self) -> 'MutableDecofBoolean':
        return self._echo

    @property
    def build_information(self) -> 'BuildInformation':
        return self._build_information

    @property
    def decof_ver(self) -> 'DecofString':
        return self._decof_ver

    @property
    def system_label(self) -> 'MutableDecofString':
        return self._system_label

    @property
    def system_model(self) -> 'DecofString':
        return self._system_model

    @property
    def ssw_svn_revision(self) -> 'DecofString':
        return self._ssw_svn_revision

    @property
    def system_type(self) -> 'DecofString':
        return self._system_type

    async def change_password(self, password: str) -> None:
        assert isinstance(password, str), "expected type 'str' for parameter 'password', got '{}'".format(type(password))
        await self.__client.exec('change-password', password, input_stream=None, output_type=None, return_type=None)

    async def change_ul(self, ul: AccessLevel, passwd: str) -> int:
        assert isinstance(ul, AccessLevel), "expected type 'AccessLevel' for parameter 'ul', got '{}'".format(type(ul))
        assert isinstance(passwd, str), "expected type 'str' for parameter 'passwd', got '{}'".format(type(passwd))
        return await self.__client.change_ul(ul, passwd)

    async def service_script(self, stream_input: bytes) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        await self.__client.exec('service-script', input_stream=stream_input, output_type=None, return_type=None)

    async def service_report(self) -> bytes:
        return await self.__client.exec('service-report', input_stream=None, output_type=bytes, return_type=None)

    async def debug_log(self) -> str:
        return await self.__client.exec('debug-log', input_stream=None, output_type=str, return_type=None)

    async def system_connections(self) -> Tuple[str, int]:
        return await self.__client.exec('system-connections', input_stream=None, output_type=str, return_type=int)

    async def error_log(self) -> str:
        return await self.__client.exec('error-log', input_stream=None, output_type=str, return_type=None)

    async def service_log(self) -> str:
        return await self.__client.exec('service-log', input_stream=None, output_type=str, return_type=None)

    async def system_summary(self) -> str:
        return await self.__client.exec('system-summary', input_stream=None, output_type=str, return_type=None)

