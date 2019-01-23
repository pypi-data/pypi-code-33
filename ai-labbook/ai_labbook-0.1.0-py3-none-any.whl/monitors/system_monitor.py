import GPUtil
import psutil
import os

from labbook.monitors import Monitor
from labbook import ExpEvents

class SystemMonitor(Monitor):
    def __init__(self, sample_rate=32, experiment=None):
        super(SystemMonitor, self).__init__("SystemMonitor", events=[ExpEvents.STEP], experiment=experiment)

        self.pid = os.getpid()
        self.process = psutil.Process(self.pid)
        self.sample_rate = sample_rate

    def __call__(self, event, new_value, **kwargs):
        if event == ExpEvent.STEP and new_value % self.sample_rate == 0:
            with self.experiment.namespace("system"):
                # Make these all into a single group as a % of total (Memory group, CPU ground,GPU grop)
                self.experiment.log_metric("cpu_count", psutil.cpu_count())
                self.experiment.log_metric("cpu_perc", self.process.cpu_percent())
                self.experiment.log_metric("ram_usage", self.process.memory_percent())
                self.experiment.log_metric("swap_usage", self.process.swap_memory()/self.process.swap_memory())

                for gpu in GPUtil.getGPUs():
                    self.experiment.log_metric(f"gpu_mem.{gpu.id}", gpu.memoryUtil())
                    self.experiment.log_metric(f"gpu_load.{gpu.id}", gpu.load())
