# Generated from 'v1_4_0.xml' on 2019-02-12 07:24:19.423638

from typing import Tuple

from toptica.lasersdk.client import AccessLevel
from toptica.lasersdk.client import Client

from toptica.lasersdk.client import DecofBoolean
from toptica.lasersdk.client import DecofInteger
from toptica.lasersdk.client import DecofReal
from toptica.lasersdk.client import DecofString
from toptica.lasersdk.client import DecofBinary

from toptica.lasersdk.client import MutableDecofBoolean
from toptica.lasersdk.client import MutableDecofInteger
from toptica.lasersdk.client import MutableDecofReal
from toptica.lasersdk.client import MutableDecofString
from toptica.lasersdk.client import MutableDecofBinary

from toptica.lasersdk.client import Connection
from toptica.lasersdk.client import NetworkConnection
from toptica.lasersdk.client import SerialConnection

from toptica.lasersdk.client import DecofError
from toptica.lasersdk.client import DeviceNotFoundError


class PcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._channel1 = PiezoDrv2(client, name + ':channel1')
        self._status = DecofInteger(client, name + ':status')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._slot = DecofString(client, name + ':slot')
        self._revision = DecofString(client, name + ':revision')

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def channel1(self) -> 'PiezoDrv2':
        return self._channel1

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def revision(self) -> 'DecofString':
        return self._revision


class PiezoDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._status = DecofInteger(client, name + ':status')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._path = DecofString(client, name + ':path')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master


class ExtInput2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')
        self._signal = MutableDecofInteger(client, name + ':signal')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal


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


class Cc5000Board:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._regulator_temp = DecofReal(client, name + ':regulator-temp')
        self._revision = DecofString(client, name + ':revision')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._variant = DecofString(client, name + ':variant')
        self._inverter_temp = DecofReal(client, name + ':inverter-temp')
        self._slot = DecofString(client, name + ':slot')
        self._status = DecofInteger(client, name + ':status')
        self._inverter_temp_fuse = DecofReal(client, name + ':inverter-temp-fuse')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._channel1 = Cc5000Drv(client, name + ':channel1')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._power_15v = MutableDecofBoolean(client, name + ':power-15v')
        self._regulator_temp_fuse = DecofReal(client, name + ':regulator-temp-fuse')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def regulator_temp(self) -> 'DecofReal':
        return self._regulator_temp

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def inverter_temp(self) -> 'DecofReal':
        return self._inverter_temp

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def inverter_temp_fuse(self) -> 'DecofReal':
        return self._inverter_temp_fuse

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def channel1(self) -> 'Cc5000Drv':
        return self._channel1

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def power_15v(self) -> 'MutableDecofBoolean':
        return self._power_15v

    @property
    def regulator_temp_fuse(self) -> 'DecofReal':
        return self._regulator_temp_fuse

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver


class Cc5000Drv:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._voltage_out = DecofReal(client, name + ':voltage-out')
        self._emission = DecofBoolean(client, name + ':emission')
        self._path = DecofString(client, name + ':path')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._status = DecofInteger(client, name + ':status')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._variant = DecofString(client, name + ':variant')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._aux = DecofReal(client, name + ':aux')
        self._current_act = DecofReal(client, name + ':current-act')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def voltage_out(self) -> 'DecofReal':
        return self._voltage_out

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip


class OutputFilter1:
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


class CcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel2 = CurrDrv2(client, name + ':channel2')
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._revision = DecofString(client, name + ':revision')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._variant = DecofString(client, name + ':variant')
        self._slot = DecofString(client, name + ':slot')
        self._status = DecofInteger(client, name + ':status')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._channel1 = CurrDrv2(client, name + ':channel1')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')

    @property
    def channel2(self) -> 'CurrDrv2':
        return self._channel2

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def channel1(self) -> 'CurrDrv2':
        return self._channel1

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver


class CurrDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._pd = DecofReal(client, name + ':pd')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')
        self._status = DecofInteger(client, name + ':status')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._emission = DecofBoolean(client, name + ':emission')
        self._path = DecofString(client, name + ':path')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._variant = DecofString(client, name + ':variant')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._aux = DecofReal(client, name + ':aux')
        self._current_act = DecofReal(client, name + ':current-act')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip


class Display:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._brightness = MutableDecofReal(client, name + ':brightness')
        self._state = DecofInteger(client, name + ':state')
        self._idle_timeout = MutableDecofInteger(client, name + ':idle-timeout')
        self._auto_dark = MutableDecofBoolean(client, name + ':auto-dark')

    @property
    def brightness(self) -> 'MutableDecofReal':
        return self._brightness

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def idle_timeout(self) -> 'MutableDecofInteger':
        return self._idle_timeout

    @property
    def auto_dark(self) -> 'MutableDecofBoolean':
        return self._auto_dark

    def update_state(self, active: bool) -> None:
        assert isinstance(active, bool), "expected type 'bool' for parameter 'active', got '{}'".format(type(active))
        self.__client.exec(self.__name + ':update-state', active, input_stream=None, output_type=None, return_type=None)


class TcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel2 = TcChannel(client, name + ':channel2')
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._channel1 = TcChannel(client, name + ':channel1')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._slot = DecofString(client, name + ':slot')
        self._revision = DecofString(client, name + ':revision')

    @property
    def channel2(self) -> 'TcChannel':
        return self._channel2

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def channel1(self) -> 'TcChannel':
        return self._channel1

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def revision(self) -> 'DecofString':
        return self._revision


class TcChannel:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_set = DecofReal(client, name + ':current-set')
        self._ready = DecofBoolean(client, name + ':ready')
        self._c_loop = TcChannelCLoop(client, name + ':c-loop')
        self._limits = TcChannelCheck(client, name + ':limits')
        self._temp_set_max = MutableDecofReal(client, name + ':temp-set-max')
        self._status = DecofInteger(client, name + ':status')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._disabled_preset = TcDisabledPreset(client, name + ':disabled-preset')
        self._power_source = DecofInteger(client, name + ':power-source')
        self._path = DecofString(client, name + ':path')
        self._t_loop = TcChannelTLoop(client, name + ':t-loop')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._resistance = DecofReal(client, name + ':resistance')
        self._current_set_min = MutableDecofReal(client, name + ':current-set-min')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._temp_set_min = MutableDecofReal(client, name + ':temp-set-min')
        self._current_act = DecofReal(client, name + ':current-act')
        self._temp_act = DecofReal(client, name + ':temp-act')
        self._temp_reset = MutableDecofBoolean(client, name + ':temp-reset')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._fault = DecofBoolean(client, name + ':fault')
        self._drv_voltage = DecofReal(client, name + ':drv-voltage')
        self._ntc_series_resistance = DecofReal(client, name + ':ntc-series-resistance')
        self._current_set_max = MutableDecofReal(client, name + ':current-set-max')

    @property
    def current_set(self) -> 'DecofReal':
        return self._current_set

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    @property
    def c_loop(self) -> 'TcChannelCLoop':
        return self._c_loop

    @property
    def limits(self) -> 'TcChannelCheck':
        return self._limits

    @property
    def temp_set_max(self) -> 'MutableDecofReal':
        return self._temp_set_max

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def disabled_preset(self) -> 'TcDisabledPreset':
        return self._disabled_preset

    @property
    def power_source(self) -> 'DecofInteger':
        return self._power_source

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def t_loop(self) -> 'TcChannelTLoop':
        return self._t_loop

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def resistance(self) -> 'DecofReal':
        return self._resistance

    @property
    def current_set_min(self) -> 'MutableDecofReal':
        return self._current_set_min

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def temp_set_min(self) -> 'MutableDecofReal':
        return self._temp_set_min

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def temp_act(self) -> 'DecofReal':
        return self._temp_act

    @property
    def temp_reset(self) -> 'MutableDecofBoolean':
        return self._temp_reset

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def fault(self) -> 'DecofBoolean':
        return self._fault

    @property
    def drv_voltage(self) -> 'DecofReal':
        return self._drv_voltage

    @property
    def ntc_series_resistance(self) -> 'DecofReal':
        return self._ntc_series_resistance

    @property
    def current_set_max(self) -> 'MutableDecofReal':
        return self._current_set_max

    def check_peltier(self) -> float:
        return self.__client.exec(self.__name + ':check-peltier', input_stream=None, output_type=None, return_type=float)


class TcChannelCLoop:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._on = MutableDecofBoolean(client, name + ':on')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')

    @property
    def on(self) -> 'MutableDecofBoolean':
        return self._on

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain


class TcChannelCheck:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._timed_out = DecofBoolean(client, name + ':timed-out')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._out_of_range = DecofBoolean(client, name + ':out-of-range')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')

    @property
    def timed_out(self) -> 'DecofBoolean':
        return self._timed_out

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def out_of_range(self) -> 'DecofBoolean':
        return self._out_of_range

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min


class TcDisabledPreset:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name


class TcChannelTLoop:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._on = MutableDecofBoolean(client, name + ':on')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def on(self) -> 'MutableDecofBoolean':
        return self._on

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain


class Standby:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._state = DecofInteger(client, name + ':state')
        self._laser1 = StandbyLaser(client, name + ':laser1')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def laser1(self) -> 'StandbyLaser':
        return self._laser1


class StandbyLaser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amp = StandbyAmp(client, name + ':amp')
        self._nlo = StandbyShg(client, name + ':nlo')
        self._dl = StandbyDl(client, name + ':dl')

    @property
    def amp(self) -> 'StandbyAmp':
        return self._amp

    @property
    def nlo(self) -> 'StandbyShg':
        return self._nlo

    @property
    def dl(self) -> 'StandbyDl':
        return self._dl


class StandbyAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc


class StandbyShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')
        self._disable_power_stabilization = MutableDecofBoolean(client, name + ':disable-power-stabilization')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_servo_subsystem = MutableDecofBoolean(client, name + ':disable-servo-subsystem')
        self._disable_cavity_lock = MutableDecofBoolean(client, name + ':disable-cavity-lock')

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc

    @property
    def disable_power_stabilization(self) -> 'MutableDecofBoolean':
        return self._disable_power_stabilization

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_servo_subsystem(self) -> 'MutableDecofBoolean':
        return self._disable_servo_subsystem

    @property
    def disable_cavity_lock(self) -> 'MutableDecofBoolean':
        return self._disable_cavity_lock


class StandbyDl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc


class Buzzer:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._welcome = MutableDecofString(client, name + ':welcome')

    @property
    def welcome(self) -> 'MutableDecofString':
        return self._welcome

    def play_welcome(self) -> None:
        self.__client.exec(self.__name + ':play-welcome', input_stream=None, output_type=None, return_type=None)

    def play(self, melody: str) -> None:
        assert isinstance(melody, str), "expected type 'str' for parameter 'melody', got '{}'".format(type(melody))
        self.__client.exec(self.__name + ':play', melody, input_stream=None, output_type=None, return_type=None)


class PowerSupply:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_15Vn = DecofReal(client, name + ':voltage-15Vn')
        self._current_15Vn = DecofReal(client, name + ':current-15Vn')
        self._current_15V = DecofReal(client, name + ':current-15V')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._voltage_5V = DecofReal(client, name + ':voltage-5V')
        self._revision = DecofString(client, name + ':revision')
        self._current_5V = DecofReal(client, name + ':current-5V')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._load = DecofReal(client, name + ':load')
        self._voltage_15V = DecofReal(client, name + ':voltage-15V')
        self._status = DecofInteger(client, name + ':status')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._voltage_3V3 = DecofReal(client, name + ':voltage-3V3')

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_15Vn(self) -> 'DecofReal':
        return self._voltage_15Vn

    @property
    def current_15Vn(self) -> 'DecofReal':
        return self._current_15Vn

    @property
    def current_15V(self) -> 'DecofReal':
        return self._current_15V

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def voltage_5V(self) -> 'DecofReal':
        return self._voltage_5V

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def current_5V(self) -> 'DecofReal':
        return self._current_5V

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def load(self) -> 'DecofReal':
        return self._load

    @property
    def voltage_15V(self) -> 'DecofReal':
        return self._voltage_15V

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def voltage_3V3(self) -> 'DecofReal':
        return self._voltage_3V3


class McBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._air_pressure = DecofReal(client, name + ':air-pressure')
        self._relative_humidity = DecofReal(client, name + ':relative-humidity')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._revision = DecofString(client, name + ':revision')

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def air_pressure(self) -> 'DecofReal':
        return self._air_pressure

    @property
    def relative_humidity(self) -> 'DecofReal':
        return self._relative_humidity

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def revision(self) -> 'DecofString':
        return self._revision


class IoBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._digital_out0 = IoDigitalOutput(client, name + ':digital-out0')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._revision = DecofString(client, name + ':revision')
        self._digital_out1 = IoDigitalOutput(client, name + ':digital-out1')
        self._digital_out2 = IoDigitalOutput(client, name + ':digital-out2')
        self._out_b = IoOutputChannel(client, name + ':out-b')
        self._digital_out3 = IoDigitalOutput(client, name + ':digital-out3')
        self._digital_in2 = IoDigitalInput(client, name + ':digital-in2')
        self._digital_in0 = IoDigitalInput(client, name + ':digital-in0')
        self._digital_in3 = IoDigitalInput(client, name + ':digital-in3')
        self._out_a = IoOutputChannel(client, name + ':out-a')
        self._digital_in1 = IoDigitalInput(client, name + ':digital-in1')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')

    @property
    def digital_out0(self) -> 'IoDigitalOutput':
        return self._digital_out0

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def digital_out1(self) -> 'IoDigitalOutput':
        return self._digital_out1

    @property
    def digital_out2(self) -> 'IoDigitalOutput':
        return self._digital_out2

    @property
    def out_b(self) -> 'IoOutputChannel':
        return self._out_b

    @property
    def digital_out3(self) -> 'IoDigitalOutput':
        return self._digital_out3

    @property
    def digital_in2(self) -> 'IoDigitalInput':
        return self._digital_in2

    @property
    def digital_in0(self) -> 'IoDigitalInput':
        return self._digital_in0

    @property
    def digital_in3(self) -> 'IoDigitalInput':
        return self._digital_in3

    @property
    def out_a(self) -> 'IoOutputChannel':
        return self._out_a

    @property
    def digital_in1(self) -> 'IoDigitalInput':
        return self._digital_in1

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver


class IoDigitalOutput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_act = DecofBoolean(client, name + ':value-act')
        self._value_set = MutableDecofBoolean(client, name + ':value-set')
        self._mode = MutableDecofInteger(client, name + ':mode')
        self._invert = MutableDecofBoolean(client, name + ':invert')

    @property
    def value_act(self) -> 'DecofBoolean':
        return self._value_act

    @property
    def value_set(self) -> 'MutableDecofBoolean':
        return self._value_set

    @property
    def mode(self) -> 'MutableDecofInteger':
        return self._mode

    @property
    def invert(self) -> 'MutableDecofBoolean':
        return self._invert


class IoOutputChannel:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._voltage_offset = MutableDecofReal(client, name + ':voltage-offset')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def voltage_offset(self) -> 'MutableDecofReal':
        return self._voltage_offset

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master


class ExtInput1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')
        self._signal = MutableDecofInteger(client, name + ':signal')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal


class IoDigitalInput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_act = DecofBoolean(client, name + ':value-act')

    @property
    def value_act(self) -> 'DecofBoolean':
        return self._value_act


class Laser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = Siggen(client, name + ':scan')
        self._ctl = CtlT(client, name + ':ctl')
        self._scope = ScopeT(client, name + ':scope')
        self._power_stabilization = PwrStab(client, name + ':power-stabilization')
        self._type_ = DecofString(client, name + ':type')
        self._nlo = Nlo(client, name + ':nlo')
        self._dl = LaserHead(client, name + ':dl')
        self._emission = DecofBoolean(client, name + ':emission')
        self._pd_ext = PdExt(client, name + ':pd-ext')
        self._amp = LaserAmp(client, name + ':amp')
        self._product_name = DecofString(client, name + ':product-name')
        self._health = DecofInteger(client, name + ':health')
        self._health_txt = DecofString(client, name + ':health-txt')

    @property
    def scan(self) -> 'Siggen':
        return self._scan

    @property
    def ctl(self) -> 'CtlT':
        return self._ctl

    @property
    def scope(self) -> 'ScopeT':
        return self._scope

    @property
    def power_stabilization(self) -> 'PwrStab':
        return self._power_stabilization

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def nlo(self) -> 'Nlo':
        return self._nlo

    @property
    def dl(self) -> 'LaserHead':
        return self._dl

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def pd_ext(self) -> 'PdExt':
        return self._pd_ext

    @property
    def amp(self) -> 'LaserAmp':
        return self._amp

    @property
    def product_name(self) -> 'DecofString':
        return self._product_name

    @property
    def health(self) -> 'DecofInteger':
        return self._health

    @property
    def health_txt(self) -> 'DecofString':
        return self._health_txt

    def load(self) -> None:
        self.__client.exec(self.__name + ':load', input_stream=None, output_type=None, return_type=None)

    def save(self) -> None:
        self.__client.exec(self.__name + ':save', input_stream=None, output_type=None, return_type=None)

    def detect(self) -> None:
        self.__client.exec(self.__name + ':detect', input_stream=None, output_type=None, return_type=None)


class Siggen:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal_type = MutableDecofInteger(client, name + ':signal-type')
        self._start = MutableDecofReal(client, name + ':start')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._unit = DecofString(client, name + ':unit')
        self._end = MutableDecofReal(client, name + ':end')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._offset = MutableDecofReal(client, name + ':offset')

    @property
    def signal_type(self) -> 'MutableDecofInteger':
        return self._signal_type

    @property
    def start(self) -> 'MutableDecofReal':
        return self._start

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def end(self) -> 'MutableDecofReal':
        return self._end

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset


class CtlT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._optimization = CtlOptimizationT(client, name + ':optimization')
        self._state = DecofInteger(client, name + ':state')
        self._scan = CtlScanT(client, name + ':scan')
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')
        self._wavelength_act = DecofReal(client, name + ':wavelength-act')
        self._head_temperature = DecofReal(client, name + ':head-temperature')
        self._mode_control = CtlModeControl(client, name + ':mode-control')
        self._remote_control = CtlRemoteControl(client, name + ':remote-control')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')
        self._factory_settings = CtlFactory(client, name + ':factory-settings')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._power = CtlPower(client, name + ':power')
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._wavelength_set = MutableDecofReal(client, name + ':wavelength-set')
        self._motor = CtlMotor(client, name + ':motor')
        self._state_txt = DecofString(client, name + ':state-txt')

    @property
    def tuning_power_min(self) -> 'DecofReal':
        return self._tuning_power_min

    @property
    def optimization(self) -> 'CtlOptimizationT':
        return self._optimization

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def scan(self) -> 'CtlScanT':
        return self._scan

    @property
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    @property
    def wavelength_act(self) -> 'DecofReal':
        return self._wavelength_act

    @property
    def head_temperature(self) -> 'DecofReal':
        return self._head_temperature

    @property
    def mode_control(self) -> 'CtlModeControl':
        return self._mode_control

    @property
    def remote_control(self) -> 'CtlRemoteControl':
        return self._remote_control

    @property
    def wavelength_max(self) -> 'DecofReal':
        return self._wavelength_max

    @property
    def factory_settings(self) -> 'CtlFactory':
        return self._factory_settings

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def power(self) -> 'CtlPower':
        return self._power

    @property
    def tuning_current_min(self) -> 'DecofReal':
        return self._tuning_current_min

    @property
    def wavelength_set(self) -> 'MutableDecofReal':
        return self._wavelength_set

    @property
    def motor(self) -> 'CtlMotor':
        return self._motor

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt


class CtlOptimizationT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress = DecofInteger(client, name + ':progress')

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    def flow(self) -> None:
        self.__client.exec(self.__name + ':flow', input_stream=None, output_type=None, return_type=None)

    def abort(self) -> None:
        self.__client.exec(self.__name + ':abort', input_stream=None, output_type=None, return_type=None)

    def smile(self) -> None:
        self.__client.exec(self.__name + ':smile', input_stream=None, output_type=None, return_type=None)


class CtlScanT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._speed_max = DecofReal(client, name + ':speed-max')
        self._wavelength_end = MutableDecofReal(client, name + ':wavelength-end')
        self._trigger = CtlTriggerT(client, name + ':trigger')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._continuous_mode = MutableDecofBoolean(client, name + ':continuous-mode')
        self._wavelength_begin = MutableDecofReal(client, name + ':wavelength-begin')
        self._microsteps = MutableDecofBoolean(client, name + ':microsteps')
        self._progress = DecofInteger(client, name + ':progress')
        self._shape = MutableDecofInteger(client, name + ':shape')
        self._remaining_time = DecofInteger(client, name + ':remaining-time')
        self._speed_min = DecofReal(client, name + ':speed-min')

    @property
    def speed_max(self) -> 'DecofReal':
        return self._speed_max

    @property
    def wavelength_end(self) -> 'MutableDecofReal':
        return self._wavelength_end

    @property
    def trigger(self) -> 'CtlTriggerT':
        return self._trigger

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def continuous_mode(self) -> 'MutableDecofBoolean':
        return self._continuous_mode

    @property
    def wavelength_begin(self) -> 'MutableDecofReal':
        return self._wavelength_begin

    @property
    def microsteps(self) -> 'MutableDecofBoolean':
        return self._microsteps

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def shape(self) -> 'MutableDecofInteger':
        return self._shape

    @property
    def remaining_time(self) -> 'DecofInteger':
        return self._remaining_time

    @property
    def speed_min(self) -> 'DecofReal':
        return self._speed_min

    def continue_(self) -> None:
        self.__client.exec(self.__name + ':continue', input_stream=None, output_type=None, return_type=None)

    def start(self) -> None:
        self.__client.exec(self.__name + ':start', input_stream=None, output_type=None, return_type=None)

    def stop(self) -> None:
        self.__client.exec(self.__name + ':stop', input_stream=None, output_type=None, return_type=None)

    def pause(self) -> None:
        self.__client.exec(self.__name + ':pause', input_stream=None, output_type=None, return_type=None)


class CtlTriggerT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._output_enabled = MutableDecofBoolean(client, name + ':output-enabled')
        self._input_enabled = MutableDecofBoolean(client, name + ':input-enabled')
        self._output_threshold = MutableDecofReal(client, name + ':output-threshold')

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def output_enabled(self) -> 'MutableDecofBoolean':
        return self._output_enabled

    @property
    def input_enabled(self) -> 'MutableDecofBoolean':
        return self._input_enabled

    @property
    def output_threshold(self) -> 'MutableDecofReal':
        return self._output_threshold


class CtlModeControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._loop_enabled = MutableDecofBoolean(client, name + ':loop-enabled')

    @property
    def loop_enabled(self) -> 'MutableDecofBoolean':
        return self._loop_enabled


class CtlRemoteControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._speed = MutableDecofReal(client, name + ':speed')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed


class CtlFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')

    @property
    def tuning_power_min(self) -> 'DecofReal':
        return self._tuning_power_min

    @property
    def wavelength_max(self) -> 'DecofReal':
        return self._wavelength_max

    @property
    def tuning_current_min(self) -> 'DecofReal':
        return self._tuning_current_min

    @property
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    def apply(self) -> None:
        self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class CtlPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act


class CtlMotor:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_save_disabled = MutableDecofBoolean(client, name + ':power-save-disabled')
        self._position_accuracy = MutableDecofInteger(client, name + ':position-accuracy')
        self._position_hysteresis = MutableDecofInteger(client, name + ':position-hysteresis')

    @property
    def power_save_disabled(self) -> 'MutableDecofBoolean':
        return self._power_save_disabled

    @property
    def position_accuracy(self) -> 'MutableDecofInteger':
        return self._position_accuracy

    @property
    def position_hysteresis(self) -> 'MutableDecofInteger':
        return self._position_hysteresis


class ScopeT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel2 = ScopeChannelT(client, name + ':channel2')
        self._timescale = MutableDecofReal(client, name + ':timescale')
        self._data = DecofBinary(client, name + ':data')
        self._channelx = ScopeXAxisT(client, name + ':channelx')
        self._variant = MutableDecofInteger(client, name + ':variant')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')
        self._channel1 = ScopeChannelT(client, name + ':channel1')

    @property
    def channel2(self) -> 'ScopeChannelT':
        return self._channel2

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channelx(self) -> 'ScopeXAxisT':
        return self._channelx

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate

    @property
    def channel1(self) -> 'ScopeChannelT':
        return self._channel1


class ScopeChannelT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._name = DecofString(client, name + ':name')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit


class ScopeXAxisT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._name = DecofString(client, name + ':name')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._unit = DecofString(client, name + ':unit')
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal

    @property
    def spectrum_range(self) -> 'MutableDecofReal':
        return self._spectrum_range

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def scope_timescale(self) -> 'MutableDecofReal':
        return self._scope_timescale

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def spectrum_omit_dc(self) -> 'MutableDecofBoolean':
        return self._spectrum_omit_dc


class PwrStab:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._output_channel = DecofInteger(client, name + ':output-channel')
        self._gain = PwrStabGain(client, name + ':gain')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._input_channel_value_act = DecofReal(client, name + ':input-channel-value-act')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._window = PwrStabWindow(client, name + ':window')
        self._state = DecofInteger(client, name + ':state')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def output_channel(self) -> 'DecofInteger':
        return self._output_channel

    @property
    def gain(self) -> 'PwrStabGain':
        return self._gain

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def input_channel_value_act(self) -> 'DecofReal':
        return self._input_channel_value_act

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def window(self) -> 'PwrStabWindow':
        return self._window

    @property
    def state(self) -> 'DecofInteger':
        return self._state


class PwrStabGain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._all = MutableDecofReal(client, name + ':all')
        self._d = MutableDecofReal(client, name + ':d')
        self._i = MutableDecofReal(client, name + ':i')
        self._p = MutableDecofReal(client, name + ':p')

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p


class PwrStabWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Nlo:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fhg = Fhg(client, name + ':fhg')
        self._shg = Shg(client, name + ':shg')
        self._pd = NloLaserHeadPhotoDiodes(client, name + ':pd')
        self._ssw_ver = DecofString(client, name + ':ssw-ver')
        self._servo = NloLaserHeadServos(client, name + ':servo')
        self._power_optimization = NloLaserHeadPowerOptimization(client, name + ':power-optimization')

    @property
    def fhg(self) -> 'Fhg':
        return self._fhg

    @property
    def shg(self) -> 'Shg':
        return self._shg

    @property
    def pd(self) -> 'NloLaserHeadPhotoDiodes':
        return self._pd

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def servo(self) -> 'NloLaserHeadServos':
        return self._servo

    @property
    def power_optimization(self) -> 'NloLaserHeadPowerOptimization':
        return self._power_optimization


class Fhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tc = TcChannel(client, name + ':tc')
        self._scope = NloLaserHeadScopeT(client, name + ':scope')
        self._scan = NloLaserHeadSiggen(client, name + ':scan')
        self._pc = PiezoDrv1(client, name + ':pc')
        self._factory_settings = FhgFactorySettings(client, name + ':factory-settings')
        self._lock = NloLaserHeadLockFhg(client, name + ':lock')

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    @property
    def scope(self) -> 'NloLaserHeadScopeT':
        return self._scope

    @property
    def scan(self) -> 'NloLaserHeadSiggen':
        return self._scan

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def factory_settings(self) -> 'FhgFactorySettings':
        return self._factory_settings

    @property
    def lock(self) -> 'NloLaserHeadLockFhg':
        return self._lock

    def store(self) -> None:
        self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    def restore(self) -> None:
        self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadScopeT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel2 = NloLaserHeadScopeChannelT(client, name + ':channel2')
        self._timescale = MutableDecofReal(client, name + ':timescale')
        self._data = DecofBinary(client, name + ':data')
        self._channelx = NloLaserHeadScopeXAxisT(client, name + ':channelx')
        self._variant = MutableDecofInteger(client, name + ':variant')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')
        self._channel1 = NloLaserHeadScopeChannelT(client, name + ':channel1')

    @property
    def channel2(self) -> 'NloLaserHeadScopeChannelT':
        return self._channel2

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channelx(self) -> 'NloLaserHeadScopeXAxisT':
        return self._channelx

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate

    @property
    def channel1(self) -> 'NloLaserHeadScopeChannelT':
        return self._channel1


class NloLaserHeadScopeChannelT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._name = DecofString(client, name + ':name')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit


class NloLaserHeadScopeXAxisT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._name = DecofString(client, name + ':name')
        self._unit = DecofString(client, name + ':unit')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal

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


class NloLaserHeadSiggen:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._offset = MutableDecofReal(client, name + ':offset')

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset


class PiezoDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._status = DecofInteger(client, name + ':status')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._path = DecofString(client, name + ':path')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master


class FhgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')
        self._modified = DecofBoolean(client, name + ':modified')
        self._pd = NloLaserHeadFhgPhotodiodesFactorySettings(client, name + ':pd')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def pd(self) -> 'NloLaserHeadFhgPhotodiodesFactorySettings':
        return self._pd

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    def apply(self) -> None:
        self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)

    def retrieve_now(self) -> None:
        self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadPcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._scan_frequency = MutableDecofReal(client, name + ':scan-frequency')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def scan_frequency(self) -> 'MutableDecofReal':
        return self._scan_frequency

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min


class NloLaserHeadTcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._power_source = MutableDecofInteger(client, name + ':power-source')

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source


class NloLaserHeadFhgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fhg = NloLaserHeadPdFactorySettings(client, name + ':fhg')
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')

    @property
    def fhg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fhg

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf


class NloLaserHeadPdFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor


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
        self._pid2_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid2-gain')
        self._relock = NloLaserHeadRelockFactorySettings(client, name + ':relock')
        self._pid1_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid1-gain')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._window = NloLaserHeadLockWindowFactorySettings(client, name + ':window')
        self._analog_p_gain = MutableDecofReal(client, name + ':analog-p-gain')
        self._local_oscillator = NloLaserHeadLocalOscillatorFactorySettings(client, name + ':local-oscillator')

    @property
    def pid2_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid2_gain

    @property
    def relock(self) -> 'NloLaserHeadRelockFactorySettings':
        return self._relock

    @property
    def pid1_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid1_gain

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def window(self) -> 'NloLaserHeadLockWindowFactorySettings':
        return self._window

    @property
    def analog_p_gain(self) -> 'MutableDecofReal':
        return self._analog_p_gain

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFactorySettings':
        return self._local_oscillator


class NloLaserHeadPidGainFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._i = MutableDecofReal(client, name + ':i')
        self._p = MutableDecofReal(client, name + ':p')
        self._all = MutableDecofReal(client, name + ':all')
        self._d = MutableDecofReal(client, name + ':d')

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d


class NloLaserHeadRelockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._delay = MutableDecofReal(client, name + ':delay')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')

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
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude


class NloLaserHeadLockWindowFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._threshold = MutableDecofReal(client, name + ':threshold')

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def threshold(self) -> 'MutableDecofReal':
        return self._threshold


class NloLaserHeadLocalOscillatorFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._attenuation_shg_raw = MutableDecofInteger(client, name + ':attenuation-shg-raw')
        self._phase_shift_shg = MutableDecofReal(client, name + ':phase-shift-shg')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._attenuation_fhg_raw = MutableDecofInteger(client, name + ':attenuation-fhg-raw')
        self._phase_shift_fhg = MutableDecofReal(client, name + ':phase-shift-fhg')

    @property
    def attenuation_shg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_shg_raw

    @property
    def phase_shift_shg(self) -> 'MutableDecofReal':
        return self._phase_shift_shg

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def attenuation_fhg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_fhg_raw

    @property
    def phase_shift_fhg(self) -> 'MutableDecofReal':
        return self._phase_shift_fhg


class NloLaserHeadLockFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')
        self._relock = NloLaserHeadRelock(client, name + ':relock')
        self._state = MutableDecofInteger(client, name + ':state')
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._window = NloLaserHeadWindow(client, name + ':window')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._local_oscillator = NloLaserHeadLocalOscillatorFhg(client, name + ':local-oscillator')
        self._pid1 = NloLaserHeadPid(client, name + ':pid1')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._pid2 = NloLaserHeadPid(client, name + ':pid2')

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage

    @property
    def relock(self) -> 'NloLaserHeadRelock':
        return self._relock

    @property
    def state(self) -> 'MutableDecofInteger':
        return self._state

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def window(self) -> 'NloLaserHeadWindow':
        return self._window

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFhg':
        return self._local_oscillator

    @property
    def pid1(self) -> 'NloLaserHeadPid':
        return self._pid1

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def pid2(self) -> 'NloLaserHeadPid':
        return self._pid2


class NloLaserHeadRelock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._delay = MutableDecofReal(client, name + ':delay')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class NloLaserHeadWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._threshold = MutableDecofReal(client, name + ':threshold')

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def threshold(self) -> 'MutableDecofReal':
        return self._threshold


class NloLaserHeadLocalOscillatorFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._use_external_oscillator = MutableDecofBoolean(client, name + ':use-external-oscillator')

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def use_external_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_external_oscillator

    def auto_pdh(self) -> None:
        self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadPid:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = NloLaserHeadGain(client, name + ':gain')

    @property
    def gain(self) -> 'NloLaserHeadGain':
        return self._gain


class NloLaserHeadGain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._p = MutableDecofReal(client, name + ':p')
        self._d = MutableDecofReal(client, name + ':d')
        self._i = MutableDecofReal(client, name + ':i')
        self._all = MutableDecofReal(client, name + ':all')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled


class Shg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tc = TcChannel(client, name + ':tc')
        self._scope = NloLaserHeadScopeT(client, name + ':scope')
        self._scan = NloLaserHeadSiggen(client, name + ':scan')
        self._pc = PiezoDrv1(client, name + ':pc')
        self._factory_settings = ShgFactorySettings(client, name + ':factory-settings')
        self._lock = NloLaserHeadLockShg(client, name + ':lock')

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    @property
    def scope(self) -> 'NloLaserHeadScopeT':
        return self._scope

    @property
    def scan(self) -> 'NloLaserHeadSiggen':
        return self._scan

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def factory_settings(self) -> 'ShgFactorySettings':
        return self._factory_settings

    @property
    def lock(self) -> 'NloLaserHeadLockShg':
        return self._lock

    def store(self) -> None:
        self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    def restore(self) -> None:
        self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class ShgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')
        self._modified = DecofBoolean(client, name + ':modified')
        self._pd = NloLaserHeadShgPhotodiodesFactorySettings(client, name + ':pd')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def pd(self) -> 'NloLaserHeadShgPhotodiodesFactorySettings':
        return self._pd

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    def apply(self) -> None:
        self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)

    def retrieve_now(self) -> None:
        self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadShgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg = NloLaserHeadPdFactorySettings(client, name + ':shg')
        self._dl = NloLaserHeadPdFactorySettings(client, name + ':dl')
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')
        self._fiber = NloLaserHeadPdFactorySettings(client, name + ':fiber')
        self._amp = NloLaserHeadPdFactorySettings(client, name + ':amp')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')

    @property
    def shg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._shg

    @property
    def dl(self) -> 'NloLaserHeadPdFactorySettings':
        return self._dl

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int

    @property
    def fiber(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fiber

    @property
    def amp(self) -> 'NloLaserHeadPdFactorySettings':
        return self._amp

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc


class NloLaserHeadLockShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')
        self._relock = NloLaserHeadRelock(client, name + ':relock')
        self._state = MutableDecofInteger(client, name + ':state')
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._analog_dl_gain = NloLaserHeadMinifalc(client, name + ':analog-dl-gain')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._window = NloLaserHeadWindow(client, name + ':window')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._local_oscillator = NloLaserHeadLocalOscillatorShg(client, name + ':local-oscillator')
        self._pid1 = NloLaserHeadPid(client, name + ':pid1')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._pid2 = NloLaserHeadPid(client, name + ':pid2')

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage

    @property
    def relock(self) -> 'NloLaserHeadRelock':
        return self._relock

    @property
    def state(self) -> 'MutableDecofInteger':
        return self._state

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def analog_dl_gain(self) -> 'NloLaserHeadMinifalc':
        return self._analog_dl_gain

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def window(self) -> 'NloLaserHeadWindow':
        return self._window

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorShg':
        return self._local_oscillator

    @property
    def pid1(self) -> 'NloLaserHeadPid':
        return self._pid1

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def pid2(self) -> 'NloLaserHeadPid':
        return self._pid2


class NloLaserHeadMinifalc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p_gain = MutableDecofReal(client, name + ':p-gain')

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain


class NloLaserHeadLocalOscillatorShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._use_external_oscillator = MutableDecofBoolean(client, name + ':use-external-oscillator')

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def use_external_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_external_oscillator

    def auto_pdh(self) -> None:
        self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadPhotoDiodes:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fhg_int = NloLaserHeadNloDigilockPhotodiode(client, name + ':fhg-int')
        self._fhg = NloLaserHeadNloPhotodiode(client, name + ':fhg')
        self._shg = NloLaserHeadNloPhotodiode(client, name + ':shg')
        self._dl = NloLaserHeadNloPhotodiode(client, name + ':dl')
        self._fhg_pdh_dc = NloLaserHeadNloDigilockPhotodiode(client, name + ':fhg-pdh-dc')
        self._fiber = NloLaserHeadNloPhotodiode(client, name + ':fiber')
        self._shg_pdh_dc = NloLaserHeadNloDigilockPhotodiode(client, name + ':shg-pdh-dc')
        self._amp = NloLaserHeadNloPhotodiode(client, name + ':amp')
        self._fhg_pdh_rf = NloLaserHeadNloPdhPhotodiode(client, name + ':fhg-pdh-rf')
        self._shg_int = NloLaserHeadNloDigilockPhotodiode(client, name + ':shg-int')
        self._shg_pdh_rf = NloLaserHeadNloPdhPhotodiode(client, name + ':shg-pdh-rf')

    @property
    def fhg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._fhg_int

    @property
    def fhg(self) -> 'NloLaserHeadNloPhotodiode':
        return self._fhg

    @property
    def shg(self) -> 'NloLaserHeadNloPhotodiode':
        return self._shg

    @property
    def dl(self) -> 'NloLaserHeadNloPhotodiode':
        return self._dl

    @property
    def fhg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._fhg_pdh_dc

    @property
    def fiber(self) -> 'NloLaserHeadNloPhotodiode':
        return self._fiber

    @property
    def shg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._shg_pdh_dc

    @property
    def amp(self) -> 'NloLaserHeadNloPhotodiode':
        return self._amp

    @property
    def fhg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode':
        return self._fhg_pdh_rf

    @property
    def shg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._shg_int

    @property
    def shg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode':
        return self._shg_pdh_rf


class NloLaserHeadNloDigilockPhotodiode:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class NloLaserHeadNloPhotodiode:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power = DecofReal(client, name + ':power')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor


class NloLaserHeadNloPdhPhotodiode:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = MutableDecofReal(client, name + ':gain')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def gain(self) -> 'MutableDecofReal':
        return self._gain

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class NloLaserHeadServos:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._uv_cryst = NloLaserHeadServoPwm(client, name + ':uv-cryst')
        self._ta2_hor = NloLaserHeadServoPwm(client, name + ':ta2-hor')
        self._fhg1_hor = NloLaserHeadServoPwm(client, name + ':fhg1-hor')
        self._fiber1_vert = NloLaserHeadServoPwm(client, name + ':fiber1-vert')
        self._shg1_vert = NloLaserHeadServoPwm(client, name + ':shg1-vert')
        self._fhg2_vert = NloLaserHeadServoPwm(client, name + ':fhg2-vert')
        self._fiber2_vert = NloLaserHeadServoPwm(client, name + ':fiber2-vert')
        self._ta1_vert = NloLaserHeadServoPwm(client, name + ':ta1-vert')
        self._fhg1_vert = NloLaserHeadServoPwm(client, name + ':fhg1-vert')
        self._shg2_hor = NloLaserHeadServoPwm(client, name + ':shg2-hor')
        self._shg1_hor = NloLaserHeadServoPwm(client, name + ':shg1-hor')
        self._fhg2_hor = NloLaserHeadServoPwm(client, name + ':fhg2-hor')
        self._uv_outcpl = NloLaserHeadServoPwm(client, name + ':uv-outcpl')
        self._ta1_hor = NloLaserHeadServoPwm(client, name + ':ta1-hor')
        self._fiber2_hor = NloLaserHeadServoPwm(client, name + ':fiber2-hor')
        self._ta2_vert = NloLaserHeadServoPwm(client, name + ':ta2-vert')
        self._fiber1_hor = NloLaserHeadServoPwm(client, name + ':fiber1-hor')
        self._shg2_vert = NloLaserHeadServoPwm(client, name + ':shg2-vert')

    @property
    def uv_cryst(self) -> 'NloLaserHeadServoPwm':
        return self._uv_cryst

    @property
    def ta2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._ta2_hor

    @property
    def fhg1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fhg1_hor

    @property
    def fiber1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fiber1_vert

    @property
    def shg1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._shg1_vert

    @property
    def fhg2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fhg2_vert

    @property
    def fiber2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fiber2_vert

    @property
    def ta1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._ta1_vert

    @property
    def fhg1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fhg1_vert

    @property
    def shg2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._shg2_hor

    @property
    def shg1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._shg1_hor

    @property
    def fhg2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fhg2_hor

    @property
    def uv_outcpl(self) -> 'NloLaserHeadServoPwm':
        return self._uv_outcpl

    @property
    def ta1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._ta1_hor

    @property
    def fiber2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fiber2_hor

    @property
    def ta2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._ta2_vert

    @property
    def fiber1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fiber1_hor

    @property
    def shg2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._shg2_vert

    def center_all_servos(self) -> None:
        self.__client.exec(self.__name + ':center-all-servos', input_stream=None, output_type=None, return_type=None)

    def center_fhg_servos(self) -> None:
        self.__client.exec(self.__name + ':center-fhg-servos', input_stream=None, output_type=None, return_type=None)

    def center_ta_servos(self) -> None:
        self.__client.exec(self.__name + ':center-ta-servos', input_stream=None, output_type=None, return_type=None)

    def center_fiber_servos(self) -> None:
        self.__client.exec(self.__name + ':center-fiber-servos', input_stream=None, output_type=None, return_type=None)

    def center_shg_servos(self) -> None:
        self.__client.exec(self.__name + ':center-shg-servos', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadServoPwm:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._value = MutableDecofInteger(client, name + ':value')
        self._display_name = DecofString(client, name + ':display-name')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def value(self) -> 'MutableDecofInteger':
        return self._value

    @property
    def display_name(self) -> 'DecofString':
        return self._display_name

    def center_servo(self) -> None:
        self.__client.exec(self.__name + ':center-servo', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadPowerOptimization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ongoing = DecofBoolean(client, name + ':ongoing')
        self._stage5 = NloLaserHeadStage(client, name + ':stage5')
        self._shg_advanced = MutableDecofBoolean(client, name + ':shg-advanced')
        self._abort = MutableDecofBoolean(client, name + ':abort')
        self._progress_data_shg = DecofBinary(client, name + ':progress-data-shg')
        self._stage4 = NloLaserHeadStage(client, name + ':stage4')
        self._stage2 = NloLaserHeadStage(client, name + ':stage2')
        self._status = DecofInteger(client, name + ':status')
        self._progress_data_fhg = DecofBinary(client, name + ':progress-data-fhg')
        self._stage1 = NloLaserHeadStage(client, name + ':stage1')
        self._stage3 = NloLaserHeadStage(client, name + ':stage3')
        self._progress_data_amp = DecofBinary(client, name + ':progress-data-amp')
        self._status_string = DecofString(client, name + ':status-string')
        self._progress_data_fiber = DecofBinary(client, name + ':progress-data-fiber')
        self._progress = DecofInteger(client, name + ':progress')

    @property
    def ongoing(self) -> 'DecofBoolean':
        return self._ongoing

    @property
    def stage5(self) -> 'NloLaserHeadStage':
        return self._stage5

    @property
    def shg_advanced(self) -> 'MutableDecofBoolean':
        return self._shg_advanced

    @property
    def abort(self) -> 'MutableDecofBoolean':
        return self._abort

    @property
    def progress_data_shg(self) -> 'DecofBinary':
        return self._progress_data_shg

    @property
    def stage4(self) -> 'NloLaserHeadStage':
        return self._stage4

    @property
    def stage2(self) -> 'NloLaserHeadStage':
        return self._stage2

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def progress_data_fhg(self) -> 'DecofBinary':
        return self._progress_data_fhg

    @property
    def stage1(self) -> 'NloLaserHeadStage':
        return self._stage1

    @property
    def stage3(self) -> 'NloLaserHeadStage':
        return self._stage3

    @property
    def progress_data_amp(self) -> 'DecofBinary':
        return self._progress_data_amp

    @property
    def status_string(self) -> 'DecofString':
        return self._status_string

    @property
    def progress_data_fiber(self) -> 'DecofBinary':
        return self._progress_data_fiber

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    def start_optimization_all(self) -> int:
        return self.__client.exec(self.__name + ':start-optimization-all', input_stream=None, output_type=None, return_type=int)

    def start_optimization_fiber(self) -> int:
        return self.__client.exec(self.__name + ':start-optimization-fiber', input_stream=None, output_type=None, return_type=int)

    def start_optimization_shg(self) -> int:
        return self.__client.exec(self.__name + ':start-optimization-shg', input_stream=None, output_type=None, return_type=int)

    def start_optimization_fhg(self) -> int:
        return self.__client.exec(self.__name + ':start-optimization-fhg', input_stream=None, output_type=None, return_type=int)

    def start_optimization_amp(self) -> int:
        return self.__client.exec(self.__name + ':start-optimization-amp', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadStage:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._input = NloLaserHeadOptInput(client, name + ':input')
        self._progress = DecofInteger(client, name + ':progress')
        self._regress_tolerance = MutableDecofInteger(client, name + ':regress-tolerance')
        self._restore_on_regress = MutableDecofBoolean(client, name + ':restore-on-regress')
        self._optimization_in_progress = DecofBoolean(client, name + ':optimization-in-progress')
        self._restore_on_abort = MutableDecofBoolean(client, name + ':restore-on-abort')

    @property
    def input(self) -> 'NloLaserHeadOptInput':
        return self._input

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def regress_tolerance(self) -> 'MutableDecofInteger':
        return self._regress_tolerance

    @property
    def restore_on_regress(self) -> 'MutableDecofBoolean':
        return self._restore_on_regress

    @property
    def optimization_in_progress(self) -> 'DecofBoolean':
        return self._optimization_in_progress

    @property
    def restore_on_abort(self) -> 'MutableDecofBoolean':
        return self._restore_on_abort

    def start_optimization(self) -> int:
        return self.__client.exec(self.__name + ':start-optimization', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadOptInput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_calibrated = DecofReal(client, name + ':value-calibrated')

    @property
    def value_calibrated(self) -> 'DecofReal':
        return self._value_calibrated


class LaserHead:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._factory_settings = LhFactory(client, name + ':factory-settings')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._type_ = DecofString(client, name + ':type')
        self._tc = TcChannel(client, name + ':tc')
        self._version = DecofString(client, name + ':version')
        self._pc = PiezoDrv1(client, name + ':pc')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._cc = CurrDrv1(client, name + ':cc')
        self._lock = Lock(client, name + ':lock')

    @property
    def factory_settings(self) -> 'LhFactory':
        return self._factory_settings

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    @property
    def version(self) -> 'DecofString':
        return self._version

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def cc(self) -> 'CurrDrv1':
        return self._cc

    @property
    def lock(self) -> 'Lock':
        return self._lock

    def store(self) -> None:
        self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    def restore(self) -> None:
        self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class LhFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tc = TcFactorySettings(client, name + ':tc')
        self._last_modified = DecofString(client, name + ':last-modified')
        self._power = MutableDecofReal(client, name + ':power')
        self._pc = PcFactorySettings(client, name + ':pc')
        self._modified = DecofBoolean(client, name + ':modified')
        self._threshold_current = MutableDecofReal(client, name + ':threshold-current')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._cc = LhFactoryCc(client, name + ':cc')

    @property
    def tc(self) -> 'TcFactorySettings':
        return self._tc

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def pc(self) -> 'PcFactorySettings':
        return self._pc

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def threshold_current(self) -> 'MutableDecofReal':
        return self._threshold_current

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

    @property
    def cc(self) -> 'LhFactoryCc':
        return self._cc

    def apply(self) -> None:
        self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)

    def retrieve_now(self) -> None:
        self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)


class TcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._power_source = MutableDecofInteger(client, name + ':power-source')

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source


class PcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min


class LhFactoryCc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber


class CurrDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._pd = DecofReal(client, name + ':pd')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')
        self._status = DecofInteger(client, name + ':status')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._emission = DecofBoolean(client, name + ':emission')
        self._path = DecofString(client, name + ':path')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._variant = DecofString(client, name + ':variant')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._aux = DecofReal(client, name + ':aux')
        self._current_act = DecofReal(client, name + ':current-act')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip


class Lock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._candidates = DecofBinary(client, name + ':candidates')
        self._spectrum_input_channel = MutableDecofInteger(client, name + ':spectrum-input-channel')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._state = DecofInteger(client, name + ':state')
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._lockin = Lockin(client, name + ':lockin')
        self._window = AlWindow(client, name + ':window')
        self._lockpoint = AlLockpoint(client, name + ':lockpoint')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._type_ = MutableDecofInteger(client, name + ':type')
        self._reset = AlReset(client, name + ':reset')
        self._pid2 = Pid(client, name + ':pid2')
        self._locking_delay = MutableDecofInteger(client, name + ':locking-delay')
        self._pid1 = Pid(client, name + ':pid1')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._relock = AlRelock(client, name + ':relock')
        self._candidate_filter = AlCandidateFilter(client, name + ':candidate-filter')

    @property
    def candidates(self) -> 'DecofBinary':
        return self._candidates

    @property
    def spectrum_input_channel(self) -> 'MutableDecofInteger':
        return self._spectrum_input_channel

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def lockin(self) -> 'Lockin':
        return self._lockin

    @property
    def window(self) -> 'AlWindow':
        return self._window

    @property
    def lockpoint(self) -> 'AlLockpoint':
        return self._lockpoint

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def type_(self) -> 'MutableDecofInteger':
        return self._type_

    @property
    def reset(self) -> 'AlReset':
        return self._reset

    @property
    def pid2(self) -> 'Pid':
        return self._pid2

    @property
    def locking_delay(self) -> 'MutableDecofInteger':
        return self._locking_delay

    @property
    def pid1(self) -> 'Pid':
        return self._pid1

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def relock(self) -> 'AlRelock':
        return self._relock

    @property
    def candidate_filter(self) -> 'AlCandidateFilter':
        return self._candidate_filter

    def show_candidates(self) -> Tuple[str, int]:
        return self.__client.exec(self.__name + ':show-candidates', input_stream=None, output_type=str, return_type=int)

    def select_lockpoint(self, x: float, y: float, type_: int) -> None:
        assert isinstance(x, float), "expected type 'float' for parameter 'x', got '{}'".format(type(x))
        assert isinstance(y, float), "expected type 'float' for parameter 'y', got '{}'".format(type(y))
        assert isinstance(type_, int), "expected type 'int' for parameter 'type_', got '{}'".format(type(type_))
        self.__client.exec(self.__name + ':select-lockpoint', x, y, type_, input_stream=None, output_type=None, return_type=None)

    def stop_scan(self) -> None:
        self.__client.exec(self.__name + ':stop-scan', input_stream=None, output_type=None, return_type=None)

    def start_scan(self) -> None:
        self.__client.exec(self.__name + ':start-scan', input_stream=None, output_type=None, return_type=None)

    def close(self) -> None:
        self.__client.exec(self.__name + ':close', input_stream=None, output_type=None, return_type=None)

    def open(self) -> None:
        self.__client.exec(self.__name + ':open', input_stream=None, output_type=None, return_type=None)

    def find_candidates(self) -> None:
        self.__client.exec(self.__name + ':find-candidates', input_stream=None, output_type=None, return_type=None)


class Lockin:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._lock_level = MutableDecofReal(client, name + ':lock-level')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._modulation_enabled = MutableDecofBoolean(client, name + ':modulation-enabled')
        self._modulation_output_channel = MutableDecofInteger(client, name + ':modulation-output-channel')

    @property
    def lock_level(self) -> 'MutableDecofReal':
        return self._lock_level

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def modulation_enabled(self) -> 'MutableDecofBoolean':
        return self._modulation_enabled

    @property
    def modulation_output_channel(self) -> 'MutableDecofInteger':
        return self._modulation_output_channel


class AlWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._level_high = MutableDecofReal(client, name + ':level-high')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def level_high(self) -> 'MutableDecofReal':
        return self._level_high

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis


class AlLockpoint:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._position = Coordinate(client, name + ':position')
        self._type_ = DecofString(client, name + ':type')

    @property
    def position(self) -> 'Coordinate':
        return self._position

    @property
    def type_(self) -> 'DecofString':
        return self._type_


class Coordinate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    def get(self) -> Tuple[float, float]:
        return self.__client.get(self.__name)

    def set(self, y: float, x: float) -> None:
        assert isinstance(y, float), "expected type 'float' for 'y', got '{}'".format(type(y))
        assert isinstance(x, float), "expected type 'float' for 'x', got '{}'".format(type(x))
        self.__client.set(self.__name, y, x)


class AlReset:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Pid:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._hold_state = DecofBoolean(client, name + ':hold-state')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')
        self._gain = Gain(client, name + ':gain')
        self._lock_state = DecofBoolean(client, name + ':lock-state')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._outputlimit = Outputlimit(client, name + ':outputlimit')
        self._regulating_state = DecofBoolean(client, name + ':regulating-state')
        self._slope = MutableDecofBoolean(client, name + ':slope')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def hold_state(self) -> 'DecofBoolean':
        return self._hold_state

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock

    @property
    def gain(self) -> 'Gain':
        return self._gain

    @property
    def lock_state(self) -> 'DecofBoolean':
        return self._lock_state

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def outputlimit(self) -> 'Outputlimit':
        return self._outputlimit

    @property
    def regulating_state(self) -> 'DecofBoolean':
        return self._regulating_state

    @property
    def slope(self) -> 'MutableDecofBoolean':
        return self._slope


class Gain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._i = MutableDecofReal(client, name + ':i')
        self._p = MutableDecofReal(client, name + ':p')
        self._fc_ip = DecofReal(client, name + ':fc-ip')
        self._all = MutableDecofReal(client, name + ':all')
        self._d = MutableDecofReal(client, name + ':d')
        self._fc_pd = DecofReal(client, name + ':fc-pd')

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def fc_ip(self) -> 'DecofReal':
        return self._fc_ip

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def fc_pd(self) -> 'DecofReal':
        return self._fc_pd


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


class AlRelock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._delay = MutableDecofReal(client, name + ':delay')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')

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

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude


class AlCandidateFilter:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._positive_edge = MutableDecofBoolean(client, name + ':positive-edge')
        self._edge_level = MutableDecofReal(client, name + ':edge-level')
        self._peak_noise_tolerance = MutableDecofReal(client, name + ':peak-noise-tolerance')
        self._edge_min_distance = MutableDecofInteger(client, name + ':edge-min-distance')
        self._bottom = MutableDecofBoolean(client, name + ':bottom')
        self._top = MutableDecofBoolean(client, name + ':top')
        self._negative_edge = MutableDecofBoolean(client, name + ':negative-edge')

    @property
    def positive_edge(self) -> 'MutableDecofBoolean':
        return self._positive_edge

    @property
    def edge_level(self) -> 'MutableDecofReal':
        return self._edge_level

    @property
    def peak_noise_tolerance(self) -> 'MutableDecofReal':
        return self._peak_noise_tolerance

    @property
    def edge_min_distance(self) -> 'MutableDecofInteger':
        return self._edge_min_distance

    @property
    def bottom(self) -> 'MutableDecofBoolean':
        return self._bottom

    @property
    def top(self) -> 'MutableDecofBoolean':
        return self._top

    @property
    def negative_edge(self) -> 'MutableDecofBoolean':
        return self._negative_edge


class PdExt:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power = DecofReal(client, name + ':power')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor


class LaserAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._output_limits = AmpPower(client, name + ':output-limits')
        self._factory_settings = AmpFactory(client, name + ':factory-settings')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._type_ = DecofString(client, name + ':type')
        self._tc = TcChannel(client, name + ':tc')
        self._version = DecofString(client, name + ':version')
        self._seed_limits = AmpPower(client, name + ':seed-limits')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._cc = Cc5000Drv(client, name + ':cc')
        self._seedonly_check = AmpSeedonlyCheck(client, name + ':seedonly-check')

    @property
    def output_limits(self) -> 'AmpPower':
        return self._output_limits

    @property
    def factory_settings(self) -> 'AmpFactory':
        return self._factory_settings

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    @property
    def version(self) -> 'DecofString':
        return self._version

    @property
    def seed_limits(self) -> 'AmpPower':
        return self._seed_limits

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def cc(self) -> 'Cc5000Drv':
        return self._cc

    @property
    def seedonly_check(self) -> 'AmpSeedonlyCheck':
        return self._seedonly_check

    def store(self) -> None:
        self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    def restore(self) -> None:
        self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class AmpPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')
        self._power = DecofReal(client, name + ':power')
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._status = DecofInteger(client, name + ':status')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def power_max_warning_delay(self) -> 'MutableDecofReal':
        return self._power_max_warning_delay

    @property
    def power_min(self) -> 'MutableDecofReal':
        return self._power_min

    @property
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def power_min_warning_delay(self) -> 'MutableDecofReal':
        return self._power_min_warning_delay

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor


class AmpFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tc = TcFactorySettings(client, name + ':tc')
        self._last_modified = DecofString(client, name + ':last-modified')
        self._modified = DecofBoolean(client, name + ':modified')
        self._power = MutableDecofReal(client, name + ':power')
        self._seed_limits = AmpFactoryPower(client, name + ':seed-limits')
        self._output_limits = AmpFactoryPower(client, name + ':output-limits')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._cc = AmpFactoryCc(client, name + ':cc')
        self._seedonly_check = AmpFactorySeedonly(client, name + ':seedonly-check')

    @property
    def tc(self) -> 'TcFactorySettings':
        return self._tc

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def seed_limits(self) -> 'AmpFactoryPower':
        return self._seed_limits

    @property
    def output_limits(self) -> 'AmpFactoryPower':
        return self._output_limits

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

    @property
    def cc(self) -> 'AmpFactoryCc':
        return self._cc

    @property
    def seedonly_check(self) -> 'AmpFactorySeedonly':
        return self._seedonly_check

    def apply(self) -> None:
        self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)

    def retrieve_now(self) -> None:
        self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)


class AmpFactoryPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay

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
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor


class AmpFactoryCc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified


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


class AmpSeedonlyCheck:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pump = DecofBoolean(client, name + ':pump')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._seed = DecofBoolean(client, name + ':seed')
        self._shutdown_delay = MutableDecofReal(client, name + ':shutdown-delay')
        self._warning_delay = MutableDecofReal(client, name + ':warning-delay')
        self._status = DecofInteger(client, name + ':status')

    @property
    def pump(self) -> 'DecofBoolean':
        return self._pump

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def seed(self) -> 'DecofBoolean':
        return self._seed

    @property
    def shutdown_delay(self) -> 'MutableDecofReal':
        return self._shutdown_delay

    @property
    def warning_delay(self) -> 'MutableDecofReal':
        return self._warning_delay

    @property
    def status(self) -> 'DecofInteger':
        return self._status


class SystemMessages:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._count = DecofInteger(client, name + ':count')
        self._latest_message = DecofString(client, name + ':latest-message')
        self._count_new = DecofInteger(client, name + ':count-new')

    @property
    def count(self) -> 'DecofInteger':
        return self._count

    @property
    def latest_message(self) -> 'DecofString':
        return self._latest_message

    @property
    def count_new(self) -> 'DecofInteger':
        return self._count_new

    def show_log(self) -> str:
        return self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)

    def show_all(self) -> str:
        return self.__client.exec(self.__name + ':show-all', input_stream=None, output_type=str, return_type=None)

    def show_persistent(self) -> str:
        return self.__client.exec(self.__name + ':show-persistent', input_stream=None, output_type=str, return_type=None)

    def mark_as_read(self, ID: int) -> None:
        assert isinstance(ID, int), "expected type 'int' for parameter 'ID', got '{}'".format(type(ID))
        self.__client.exec(self.__name + ':mark-as-read', ID, input_stream=None, output_type=None, return_type=None)

    def show_new(self) -> str:
        return self.__client.exec(self.__name + ':show-new', input_stream=None, output_type=str, return_type=None)


class ServiceReport:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ready = DecofBoolean(client, name + ':ready')

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    def service_report(self) -> bytes:
        return self.__client.exec(self.__name + ':service-report', input_stream=None, output_type=bytes, return_type=None)

    def print(self) -> bytes:
        return self.__client.exec(self.__name + ':print', input_stream=None, output_type=bytes, return_type=None)

    def request(self) -> None:
        self.__client.exec(self.__name + ':request', input_stream=None, output_type=None, return_type=None)


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

    def get_key(self, key_number: int) -> str:
        assert isinstance(key_number, int), "expected type 'int' for parameter 'key_number', got '{}'".format(type(key_number))
        return self.__client.exec(self.__name + ':get-key', key_number, input_stream=None, output_type=None, return_type=str)

    def install(self, licensekey: str) -> bool:
        assert isinstance(licensekey, str), "expected type 'str' for parameter 'licensekey', got '{}'".format(type(licensekey))
        return self.__client.exec(self.__name + ':install', licensekey, input_stream=None, output_type=None, return_type=bool)


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
        self._valid_until = DecofString(client, name + ':valid-until')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._licensee = DecofString(client, name + ':licensee')

    @property
    def valid_until(self) -> 'DecofString':
        return self._valid_until

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def licensee(self) -> 'DecofString':
        return self._licensee


class FwUpdate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    def upload(self, stream_input: bytes, filename: str) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        assert isinstance(filename, str), "expected type 'str' for parameter 'filename', got '{}'".format(type(filename))
        self.__client.exec(self.__name + ':upload', filename, input_stream=stream_input, output_type=None, return_type=None)

    def show_log(self) -> str:
        return self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)

    def show_history(self) -> str:
        return self.__client.exec(self.__name + ':show-history', input_stream=None, output_type=str, return_type=None)


class BuildInformation:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._build_id = DecofString(client, name + ':build-id')
        self._build_tag = DecofString(client, name + ':build-tag')
        self._job_name = DecofString(client, name + ':job-name')
        self._build_url = DecofString(client, name + ':build-url')
        self._c_compiler_version = DecofString(client, name + ':c-compiler-version')
        self._build_node_name = DecofString(client, name + ':build-node-name')
        self._build_number = DecofInteger(client, name + ':build-number')
        self._cxx_compiler_version = DecofString(client, name + ':cxx-compiler-version')
        self._c_compiler_id = DecofString(client, name + ':c-compiler-id')
        self._cxx_compiler_id = DecofString(client, name + ':cxx-compiler-id')

    @property
    def build_id(self) -> 'DecofString':
        return self._build_id

    @property
    def build_tag(self) -> 'DecofString':
        return self._build_tag

    @property
    def job_name(self) -> 'DecofString':
        return self._job_name

    @property
    def build_url(self) -> 'DecofString':
        return self._build_url

    @property
    def c_compiler_version(self) -> 'DecofString':
        return self._c_compiler_version

    @property
    def build_node_name(self) -> 'DecofString':
        return self._build_node_name

    @property
    def build_number(self) -> 'DecofInteger':
        return self._build_number

    @property
    def cxx_compiler_version(self) -> 'DecofString':
        return self._cxx_compiler_version

    @property
    def c_compiler_id(self) -> 'DecofString':
        return self._c_compiler_id

    @property
    def cxx_compiler_id(self) -> 'DecofString':
        return self._cxx_compiler_id


class Ipconfig:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._mon_port = DecofInteger(client, name + ':mon-port')
        self._net_mask = DecofString(client, name + ':net-mask')
        self._ip_addr = DecofString(client, name + ':ip-addr')
        self._cmd_port = DecofInteger(client, name + ':cmd-port')
        self._dhcp = DecofBoolean(client, name + ':dhcp')
        self._mac_addr = DecofString(client, name + ':mac-addr')

    @property
    def mon_port(self) -> 'DecofInteger':
        return self._mon_port

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
    def dhcp(self) -> 'DecofBoolean':
        return self._dhcp

    @property
    def mac_addr(self) -> 'DecofString':
        return self._mac_addr

    def set_dhcp(self) -> None:
        self.__client.exec(self.__name + ':set-dhcp', input_stream=None, output_type=None, return_type=None)

    def set_ip(self, ip_addr: str, net_mask: str) -> None:
        assert isinstance(ip_addr, str), "expected type 'str' for parameter 'ip_addr', got '{}'".format(type(ip_addr))
        assert isinstance(net_mask, str), "expected type 'str' for parameter 'net_mask', got '{}'".format(type(net_mask))
        self.__client.exec(self.__name + ':set-ip', ip_addr, net_mask, input_stream=None, output_type=None, return_type=None)

    def apply(self) -> None:
        self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class DLCpro:
    def __init__(self, connection: Connection) -> None:
        self.__client = Client(connection)
        self._system_health = DecofInteger(self.__client, 'system-health')
        self._pc2 = PcBoard(self.__client, 'pc2')
        self._ampcc1 = Cc5000Board(self.__client, 'ampcc1')
        self._cc1 = CcBoard(self.__client, 'cc1')
        self._emission = DecofBoolean(self.__client, 'emission')
        self._display = Display(self.__client, 'display')
        self._tc2 = TcBoard(self.__client, 'tc2')
        self._standby = Standby(self.__client, 'standby')
        self._buzzer = Buzzer(self.__client, 'buzzer')
        self._tc1 = TcBoard(self.__client, 'tc1')
        self._pc3 = PcBoard(self.__client, 'pc3')
        self._pc1 = PcBoard(self.__client, 'pc1')
        self._interlock_open = DecofBoolean(self.__client, 'interlock-open')
        self._ampcc2 = Cc5000Board(self.__client, 'ampcc2')
        self._power_supply = PowerSupply(self.__client, 'power-supply')
        self._mc = McBoard(self.__client, 'mc')
        self._io = IoBoard(self.__client, 'io')
        self._laser1 = Laser(self.__client, 'laser1')
        self._system_health_txt = DecofString(self.__client, 'system-health-txt')
        self._frontkey_locked = DecofBoolean(self.__client, 'frontkey-locked')
        self._system_messages = SystemMessages(self.__client, 'system-messages')
        self._system_service_report = ServiceReport(self.__client, 'system-service-report')
        self._licenses = Licenses(self.__client, 'licenses')
        self._tan = DecofInteger(self.__client, 'tan')
        self._time = MutableDecofString(self.__client, 'time')
        self._fw_update = FwUpdate(self.__client, 'fw-update')
        self._fw_ver = DecofString(self.__client, 'fw-ver')
        self._ssw_svn_revision = DecofString(self.__client, 'ssw-svn-revision')
        self._svn_revision = DecofString(self.__client, 'svn-revision')
        self._ssw_ver = DecofString(self.__client, 'ssw-ver')
        self._uptime_txt = DecofString(self.__client, 'uptime-txt')
        self._system_type = DecofString(self.__client, 'system-type')
        self._serial_number = DecofString(self.__client, 'serial-number')
        self._build_information = BuildInformation(self.__client, 'build-information')
        self._uptime = DecofInteger(self.__client, 'uptime')
        self._decof_svn_revision = DecofString(self.__client, 'decof-svn-revision')
        self._system_label = MutableDecofString(self.__client, 'system-label')
        self._system_model = DecofString(self.__client, 'system-model')
        self._echo = MutableDecofBoolean(self.__client, 'echo')
        self._decof_ver = DecofString(self.__client, 'decof-ver')
        self._ul = MutableDecofInteger(self.__client, 'ul')
        self._net_conf = Ipconfig(self.__client, 'net-conf')

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def open(self) -> None:
        self.__client.open()

    def close(self) -> None:
        self.__client.close()

    def run(self) -> None:
        self.__client.run()

    def stop(self) -> None:
        self.__client.stop()

    def poll(self) -> None:
        self.__client.poll()

    @property
    def system_health(self) -> 'DecofInteger':
        return self._system_health

    @property
    def pc2(self) -> 'PcBoard':
        return self._pc2

    @property
    def ampcc1(self) -> 'Cc5000Board':
        return self._ampcc1

    @property
    def cc1(self) -> 'CcBoard':
        return self._cc1

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def display(self) -> 'Display':
        return self._display

    @property
    def tc2(self) -> 'TcBoard':
        return self._tc2

    @property
    def standby(self) -> 'Standby':
        return self._standby

    @property
    def buzzer(self) -> 'Buzzer':
        return self._buzzer

    @property
    def tc1(self) -> 'TcBoard':
        return self._tc1

    @property
    def pc3(self) -> 'PcBoard':
        return self._pc3

    @property
    def pc1(self) -> 'PcBoard':
        return self._pc1

    @property
    def interlock_open(self) -> 'DecofBoolean':
        return self._interlock_open

    @property
    def ampcc2(self) -> 'Cc5000Board':
        return self._ampcc2

    @property
    def power_supply(self) -> 'PowerSupply':
        return self._power_supply

    @property
    def mc(self) -> 'McBoard':
        return self._mc

    @property
    def io(self) -> 'IoBoard':
        return self._io

    @property
    def laser1(self) -> 'Laser':
        return self._laser1

    @property
    def system_health_txt(self) -> 'DecofString':
        return self._system_health_txt

    @property
    def frontkey_locked(self) -> 'DecofBoolean':
        return self._frontkey_locked

    @property
    def system_messages(self) -> 'SystemMessages':
        return self._system_messages

    @property
    def system_service_report(self) -> 'ServiceReport':
        return self._system_service_report

    @property
    def licenses(self) -> 'Licenses':
        return self._licenses

    @property
    def tan(self) -> 'DecofInteger':
        return self._tan

    @property
    def time(self) -> 'MutableDecofString':
        return self._time

    @property
    def fw_update(self) -> 'FwUpdate':
        return self._fw_update

    @property
    def fw_ver(self) -> 'DecofString':
        return self._fw_ver

    @property
    def ssw_svn_revision(self) -> 'DecofString':
        return self._ssw_svn_revision

    @property
    def svn_revision(self) -> 'DecofString':
        return self._svn_revision

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def uptime_txt(self) -> 'DecofString':
        return self._uptime_txt

    @property
    def system_type(self) -> 'DecofString':
        return self._system_type

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def build_information(self) -> 'BuildInformation':
        return self._build_information

    @property
    def uptime(self) -> 'DecofInteger':
        return self._uptime

    @property
    def decof_svn_revision(self) -> 'DecofString':
        return self._decof_svn_revision

    @property
    def system_label(self) -> 'MutableDecofString':
        return self._system_label

    @property
    def system_model(self) -> 'DecofString':
        return self._system_model

    @property
    def echo(self) -> 'MutableDecofBoolean':
        return self._echo

    @property
    def decof_ver(self) -> 'DecofString':
        return self._decof_ver

    @property
    def ul(self) -> 'MutableDecofInteger':
        return self._ul

    @property
    def net_conf(self) -> 'Ipconfig':
        return self._net_conf

    def service_report(self) -> bytes:
        return self.__client.exec('service-report', input_stream=None, output_type=bytes, return_type=None)

    def system_connections(self) -> Tuple[str, int]:
        return self.__client.exec('system-connections', input_stream=None, output_type=str, return_type=int)

    def debug_log(self) -> str:
        return self.__client.exec('debug-log', input_stream=None, output_type=str, return_type=None)

    def error_log(self) -> str:
        return self.__client.exec('error-log', input_stream=None, output_type=str, return_type=None)

    def service_script(self, stream_input: bytes) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        self.__client.exec('service-script', input_stream=stream_input, output_type=None, return_type=None)

    def service_log(self) -> str:
        return self.__client.exec('service-log', input_stream=None, output_type=str, return_type=None)

    def system_summary(self) -> str:
        return self.__client.exec('system-summary', input_stream=None, output_type=str, return_type=None)

    def change_ul(self, ul: AccessLevel, passwd: str) -> int:
        assert isinstance(ul, AccessLevel), "expected type 'AccessLevel' for parameter 'ul', got '{}'".format(type(ul))
        assert isinstance(passwd, str), "expected type 'str' for parameter 'passwd', got '{}'".format(type(passwd))
        return self.__client.change_ul(ul, passwd)

    def change_password(self, password: str) -> None:
        assert isinstance(password, str), "expected type 'str' for parameter 'password', got '{}'".format(type(password))
        self.__client.exec('change-password', password, input_stream=None, output_type=None, return_type=None)

