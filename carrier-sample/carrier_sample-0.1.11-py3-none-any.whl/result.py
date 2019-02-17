import numpy as np


class Result:
    ErrorMessageMapper = {
        "success": "成功",
        "command_not_found": "命令不存在",
        "sampler_not_found": "采样器不存在",
        "in_measuring": "正在测量中",
        "voltage_not_enough": "电压不足",
        "real_sampler_error": "采样器出错",
        "wave_not_found": "未找到波形",
        "appropriate_percent_wave_not_found": "未找到正确波形"
    }

    def __init__(self):
        self.init_value()

    def process(self):
        self.wave = np.array(self.wave)
        self.wave = self.wave[self.wave != 0]
        self.voltage_amplitude = np.max(self.wave)
        self.time_line = np.array([self.sampling_interval * i for i in range(len(self.wave))])

    def init_value(self):
        self.error = False
        self.message = ''

        self.sampler_name = ''
        self.measuring = False
        self.success = False

        self.max_voltage = 0.0
        self.min_voltage = 0.0
        self.sampling_interval = 0.0  # us
        self.wave = np.array([])
        self.time_line = np.array([])
        self.tau = 0.0
        self.voltage_amplitude = 0.0

    def update_value(self, other):
        self.error = other.error
        self.message = other.message

        self.sampler_name = other.sampler_name
        self.measuring = other.measuring
        self.success = other.success

        self.max_voltage = other.max_voltage
        self.min_voltage = other.min_voltage
        self.sampling_interval = other.sampling_interval
        self.wave = other.wave
        self.time_line = other.time_line
        self.tau = other.tau
        self.voltage_amplitude = other.voltage_amplitude

    @property
    def chinese_message(self) -> str:
        return self.ErrorMessageMapper[self.message]
