"""
controller.py - Defines controller classes.

Every controller class has a function 'control()' that causes some influence
on the forked process. The effect the function creates vary by controller
classes, and so users may choose one controller class they want to use through
the command line argument of the coy program.

[For developer] All controller classes must inherit the base class 'Controller'
and override 'control()' method with their own functionalities implemented.
The method must implement the same interface, meaning that it takes the same
arguments and returns a boolean. The method is called by coy with an argument
of integer which is the return value of 'watch()' function. You may change the
behavior of the method based on the integer argument.
     If a class requires additional modules, the modules must be imported
inside the class declaration so that users can make use of the coy tool with
the minimum set of the prerequisite libraries.

Copyright 2018 coronocoya.net <nshou@coronocoya.net>
This code can be distributed under the terms of MIT License. Please see the
file COPYING for the license description.

"""

# Register the names of class here to activate.
ALL = ['DebuggingController', 'StopContController']


class Controller:
    """
    A base class of all controller classes.

    It does nothing and must not be instantiated.

    Args & attributes:
      proc (subprocess.Popen): Forked process.

    """
    def __init__(self, proc=None):
        self.proc = proc

    def control(self, state, *args, **kwargs):
        """
        Does nothing and immediately returns True.

        Args:
          state (int): State value returned by the last 'watch()'.

        Returns:
          bool: Always True.

        """
        return True

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


class DebuggingController(Controller):
    """
    A controller class only for test use.

    It prints out the PID of the forked process and state, then returns.

    """
    def control(self, state, *args, **kwargs):
        """
        Just prints out the PID of the forked process and state.

        Args:
          state (int): State value returned by the last 'watch()'.

        Returns:
          bool: Always True.

        """
        print(self.proc.pid, state)
        return True


class StopContController(Controller):
    """
    Controls processes using SIGSTOP and SIGCONT.

    This controller enables the forked process (self.proc) to completely yield
    up its CPU usage quota to the other processes when triggered.

    """
    def control(self, state, *args, **kwargs):
        """
        Sends a SIGSTOP/SIGCONT signal based on the 'state' argument.

        The method is stateless, meaning that it does not store any variables
        with regard to the state of the forked process. It sends a signal based
        only on the 'state' no matter whether the process is already stopped or
        still running. This is reasonable because the behavior of processes
        against SIGSTOP and SIGCONT is idempotent in most systems.

        Args:
          state (int): 1 to SIGSTOP, 0 to SIGCONT.

        Returns:
          bool: True if successful, False otherwise.

        """
        import signal

        if state == 1:
            self.proc.send_signal(signal.SIGSTOP)
            return True
        if state == 0:
            self.proc.send_signal(signal.SIGCONT)
            return True

        return False
        # TODO: error handling, process existence check.
