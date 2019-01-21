"""
watcher.py - Defines watcher classes.

Every watcher class has a function 'watch()' that monitors some resource and
returns when it detects the state is changed. The target resources monitored
and their reaction vary by watcher classes, and users may choose one watcher
class they want to use through the command line argument of the coy program.

[For developer] All watcher classes must inherit the base class 'Watcher' and
override 'watch()' method with their own functionalities implemented. The
method must implement the same interface, meaning that it takes the same
arguments and returns an integer. The method should alleviate bursty changes
and small oscillation near a threshold in the monitored resource using, for
example, multi-stage thresholds, counters, and some other statistical methods.
If the method takes a long time to process, it should utilize 'proc.poll()' to
check to see if the target process dies during the processing, in which case
the result of the method is no longer needed and so the method may exit.
     If a class requires additional modules, the modules must be imported
inside the class declaration so that users can make use of the coy tool with
the minimum set of the prerequisite libraries.

Copyright 2018 coronocoya.net <nshou@coronocoya.net>
This code can be distributed under the terms of MIT License. Please see the
file COPYING for the license description.

"""

# Register the names of class here to activate.
ALL = ['DebuggingWatcher', 'CPUUsageWatcher']


class Watcher:
    """
    A base class of all watcher classes.

    It does nothing and must not be instantiated.

    Args & attributes:
      proc (subprocess.Popen): Forked process.

    """
    def __init__(self, proc=None):
        self.proc = proc

    def watch(self, *args, **kwargs):
        """
        Does nothing and immediately returns 0.

        Returns:
          int: Always 0.

        """
        return 0

    def set_proc(self, proc):
        """
        Stores a Popen object.

        Args:
          proc (subprocess.Popen): Forked process.

        Returns:
          subprocess.Popen: A Popen object previously set.

        """
        prev = self.proc
        self.proc = proc
        return prev


class DebuggingWatcher(Watcher):
    """
    A watcher class only for test use.

    It reads from stdin and returns the input as an integer.

    """
    def watch(self, *args, **kwargs):
        """
        Waits for input from stdin and returns it as an integer.

        Returns:
          int: Value provided by stdin

        """
        try:
            i = int(input('[DebuggingWatcher] '))
        except ValueError:
            i = 0

        return i


class CPUUsageWatcher(Watcher):
    """
    Watches if the other process begins a high-load task on CPU.

    CPUUsageWatcher monitors the system-wide CPU utilization as a percentage
    regularly (every 1/3 seconds by default) and calculates its EWMA. The other
    processes' load (OPL) is defined by subtracting the utilization of the
    target process alone (self.proc) from the EWMA. The function 'watch()'
    returns when OPL crosses the thresholds.
         EWMA is calculated by 'EWMA_n = a * U + (1 - a) * EWMA_n-1' where 'a'
    is 0.35 by default, 'U' is the last sample value of CPU usage.
         The watcher has 4 thresholds, th_max, th_high, th_low, and th_min. The
    default values of th_max and th_min are 50 and 25 respectively. Th_high is
    defined by 0.9 * th_max and th_low is 1.2 * th_min. If the OPL exceeds
    th_max or is less than th_min, 'watch()' immediately returns indicating so.
    It also returns when the OPL is 'th_max > OPL > th_high' for several times
    (2 * 'reciprocal for the sampling frequency') or 'th_low > OPL > th_min'
    for a certain times (1 * 'reciprocal for the sampling frequency'.)

    """
    def __init__(self, proc=None):
        super(CPUUsageWatcher, self).__init__(proc)
        self.interval = 1 / 3
        self.alpha = 0.35
        self.th_max = 50
        self.th_min = 25
        self.th_high = 0.9 * self.th_max
        self.th_low = 1.2 * self.th_min
        self.cnt_high = int(2 / self.interval)
        self.cnt_low = int(1 / self.interval)
        self.lastreport = 0 # 0:idle, 1:busy
        # TODO: Config parsing
        # TODO: Handle errors
        #   psutil import error check, config parse error, exceptions raised by
        #   psutil.Process, errors on unacceptable value range, etc..
        # TODO: Documentation on exceptions

    def watch(self, *args, **kwargs):
        """
        Monitors the CPU utilization and detects the state change of whether
        the system is busy or idle.

        Returns:
          int: 1 if the system turns busy from being idle, or 0 on the other
               way around.

        """
        import psutil
        counter_high = 0
        counter_low = 0
        targetp = psutil.Process(self.proc.pid)
        ncores = psutil.cpu_count()
        targetp.cpu_percent() # Ignore the first call

        ewma = psutil.cpu_percent(interval=self.interval) # EWMA_0
        while self.proc.poll() is None:
            opl = ewma - targetp.cpu_percent() / ncores

            if opl >= self.th_max:
                counter_high += 1
                counter_low = 0
                if self.lastreport == 0:
                    self.lastreport = 1
                    return 1 # idle -> busy

            elif self.th_max > opl >= self.th_high:
                counter_high += 1
                counter_low = 0
                if self.lastreport == 0 and counter_high >= self.cnt_high:
                    self.lastreport = 1
                    return 1 # idle -> busy

            elif self.th_low >= opl > self.th_min:
                counter_high = 0
                counter_low += 1
                if self.lastreport == 1 and counter_low >= self.cnt_low:
                    self.lastreport = 0
                    return 0 # busy -> idle

            elif self.th_min >= opl:
                counter_high = 0
                counter_low += 1
                if self.lastreport == 1:
                    self.lastreport = 0
                    return 0 # busy -> idle

            ewma = self.alpha * psutil.cpu_percent(interval=self.interval) + (1 - self.alpha) * ewma

        return 0 # Target process terminated or some error occurred.
        # TODO: catch exceptions raised by psutil
