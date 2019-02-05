from queue import Empty, Queue
from threading import Event, Thread
from typing import Callable, IO, List, Union, Sequence

import os
import subprocess
import warnings

from mhelper import ansi, exception_helper


_DOnOutput = Callable[[str], None]


class AsyncSubprocess:
    """
    Runs a process asynchronously.
    
    The virtual methods should be overridden to control behaviour. 
    """
    
    
    def __init__( self,
                  *,
                  command: List[str],
                  directory: str = None,
                  send: str = None ) -> None:
        """
        CONSTRUCTOR
        
        :param command:         Command to execute 
        :param directory:       Directory to execute command within 
        :param send:            Standard input to send
        
        """
        self.command = command
        self.directory = directory
        self.send = send
        
        self.process: subprocess.Popen = None
    
    
    def on_stdout_received( self, line ):
        """
        VIRTUAL THREAD_UNSAFE
        
        Called when a line of stdout is received, runs in its own thread.
        
        The base implementation calls `on_output_received`.
        """
        self.on_output_received( line )
    
    
    def on_stderr_received( self, line ):
        """
        VIRTUAL THREAD_UNSAFE
        
        Called when a line of stderr is received, runs in its own thread.
        
        The base implementation calls `on_output_received`.
        """
        self.on_output_received( line )
    
    
    def on_output_received( self, line ):
        """
        VIRTUAL THREAD_UNSAFE
        
        Called when a line of stdout or stderr is received, runs in its own thread.
        """
        pass
    
    
    def on_process_exit( self ):
        """
        VIRTUAL THREAD_UNSAFE
        
        Called when the process exits, runs in its own thread.
        """
        pass
    
    
    def run( self ):
        """
        Starts the subprocess.
        """
        
        if self.directory is not None:
            if not os.path.isdir( self.directory ):
                raise FileNotFoundError( "Not a directory: " + self.directory )
            
            cwd = os.getcwd()
            os.chdir( self.directory )
        else:
            cwd = None
        
        self.process = subprocess.Popen( self.command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE )
        
        if self.directory is not None:
            os.chdir( cwd )
        
        # Stdin argument?
        if self.send is not None:
            self.process.stdin.write( self.send.encode( "UTF-8" ) )
        
        self.process.stdin.close()
        
        # Read asynchronously
        thread_1 = Thread( target = self.__stream_watching_thread, args = (self.process.stdout, self.on_stdout_received) )
        thread_1.name = "async_run.stdout_thread(" + " ".join( self.command ) + ")"
        thread_1.daemon = True
        thread_1.start()
        
        thread_2 = Thread( target = self.__stream_watching_thread, args = (self.process.stderr, self.on_stderr_received) )
        thread_2.name = "async_run.stderr_thread(" + " ".join( self.command ) + ")"
        thread_2.daemon = True
        thread_2.start()
        
        thread_3 = Thread( target = self.__exit_watching_thread, args = () )
        thread_2.name = "async_run.exit_thread(" + " ".join( self.command ) + ")"
        thread_3.daemon = True
        thread_3.start()
    
    
    def __stream_watching_thread( self, out: IO, call ) -> None:
        for line in out:
            line = line.decode()
            if line.endswith( "\n" ):
                line = line[:-1]
            call( line )
        
        out.close()
    
    
    def __exit_watching_thread( self ) -> None:
        self.process.wait()
        self.on_process_exit()


class SafeAsyncSubprocess( AsyncSubprocess ):
    """
    A variation of `AsyncSubprocess` that ensures the callbacks are to the main thread.
    
    The virtual methods should be overridden to control behaviour.
    """
    
    
    def __init__( self,
                  *,
                  command: List[str],
                  directory: str = None,
                  send: str = None,
                  event: Event = None ):
        """
        CONSTRUCTOR
        
        :param command: 
        :param directory: 
        :param send: 
        :param event:           The wait `Event` to fire when messages are received or the
                                subprocess exits. If this is `None` a new `Event` is set on
                                `self.event`. 
        """
        super().__init__( command = command,
                          directory = directory,
                          send = send )
        
        self.event = event if event is not None else Event()
        self.stdout_queue = Queue()
        self.stderr_queue = Queue()
    
    
    def on_stdout_received( self, line ):
        self.stdout_queue.put( line )
        self.event.set()
    
    
    def on_stderr_received( self, line ):
        self.stderr_queue.put( line )
        self.event.set()
    
    
    def on_process_exit( self ):
        self.event.set()
    
    
    def on_stdout( self, line ):
        """
        VIRTUAL
        
        Called when a line of stdout is received. Runs in the main thread. 
        """
        pass
    
    
    def on_stderr( self, line ):
        """
        VIRTUAL
        
        Called when a line of stderr is received. Runs in the main thread.
        """
        pass
    
    
    def wait( self ):
        """
        Waits for the `event` then calls `process_queue` to call the callbacks
        in the main thread.
        
        :return: True unless the process has exited.
        """
        self.event.wait()
        self.event.clear()
        return self.process_queue()
    
    
    def process_queue( self ):
        """
        Sends any standard outputs to the designated functions.
        
        Unlike `wait` the wait `Event` is not required to process the queue, so
        the function exits immediately. This can be called if multiple
        `SafeAsyncSubprocess` share the same event.
        """
        used = True
        while used:
            used = False
            
            try:
                line = self.stdout_queue.get_nowait()
            except Empty:
                pass
            else:
                self.on_stdout( line )
                used = True
            
            try:
                line = self.stderr_queue.get_nowait()
            except Empty:
                pass
            else:
                self.on_stderr( line )
                used = True
        return self.process.returncode is None
    
    
    def wait_for_exit( self ):
        """
        Repeatedly calls `wait` until the subprocess exits.
        :return: 
        """
        while self.wait():
            pass
    
    
    def raise_any_error( self ):
        """
        If the process has exited with a non-zero return, raises a
        `SubprocessError`.
        """
        if self.process.returncode:
            raise exception_helper.SubprocessError(
                    "SubprocessError 2. The command «{}» exited with error code «{}». "
                    "If available, checking the output may provide more details."
                        .format( " ".join( '"{}"'.format( x ) for x in self.command ),
                                 self.process.returncode ),
                    return_code = self.process.returncode )


def execute( command: List[str],
             *,
             dir: str = None,
             on_stdout: _DOnOutput = None,
             on_stderr: _DOnOutput = None,
             echo: bool = False,
             err: bool = False,
             tx: str = None,
             keep_lines: bool = False,
             rx_stdout: bool = False,
             rx_stderr: bool = False,
             rx_out: bool = False,
             rx_code: bool = False ) -> Union[str, int, list, tuple]:
    """
    Executes an external command.
    
    This function blocks until it completes, but the command is executed in its
    own thread to allow output to be diverted to the provided functions.
    
    :param command:             Command sequence to run.
                                See `Popen`. 
    :param dir:                 Working directory.
                                The original is restored after execution.
                                `None`: Do not change
    :param on_stdout:           Callable that receives lines (`str`) from stdout. 
    :param on_stderr:           Callable that receives lines (`str`) from stderr.
    :param echo:                When `True`, the command line, stdout and stderr are printed. 
    :param err:                 When `True`, a non-zero return code raises a `SubprocessError`. 
    :param tx:                  Input to send to `stdin`.
                                `None`: Send nothing 
    :param rx_stdout:           When `True`, stdout is buffered and returned.
    :param rx_stderr:           When `True`, stderr is buffered and returned. 
    :param rx_out:              When `True`, a common stdout and stderr buffer is created and
                                returned.
    :param keep_lines:          When `True`, buffers are returned as lists.
    :param rx_code:             When `True`, the exit code is returned.
                                This is implicit if no other `rx_` arguments are passed.
    :return: Either a single value, or a tuple if multiple collect statements are specified.
             In this case the following order is used: out, stdout, stderr, code.
    """
    # Stream arguments?
    if on_stdout is None:
        on_stdout = __ignore
    
    if on_stderr is None:
        on_stderr = __ignore
    
    # Collect arguments?
    common_array = []
    stdout_array = []
    stderr_array = []
    
    if rx_out:
        on_stdout = __Collect( common_array, on_stdout )
        on_stderr = __Collect( common_array, on_stderr )
    
    if rx_stdout:
        on_stdout = __Collect( stdout_array, on_stdout )
    
    if rx_stderr:
        on_stderr = __Collect( stderr_array, on_stderr )
    
    # Echo argument?
    if echo:
        print( ansi.FORE_YELLOW + "{}".format( command ) + ansi.RESET )
        on_stdout = __PrintStdOut( "O>" + ansi.DIM + ansi.FORE_GREEN, on_stdout )
        on_stderr = __PrintStdOut( "E>" + ansi.DIM + ansi.FORE_RED, on_stderr )
    
    ex = SafeAsyncSubprocess( command = command,
                              directory = dir,
                              send = tx )
    
    ex.on_stdout = on_stdout
    ex.on_stderr = on_stderr
    
    ex.run()
    ex.wait_for_exit()
    
    if err:
        ex.raise_any_error()
    
    r = []
    
    if rx_out:
        r.append( __as( keep_lines, common_array ) )
    
    if rx_stdout:
        r.append( __as( keep_lines, stdout_array ) )
    
    if rx_stderr:
        r.append( __as( keep_lines, stderr_array ) )
    
    if rx_code or not r:
        r.append( ex.process.returncode )
    
    if len( r ) == 1:
        return r[0]
    else:
        return tuple( r )


class __PrintStdOut:
    def __init__( self, pfx, orig ):
        self.pfx = pfx
        self.orig = orig
    
    
    def __call__( self, line ):
        print( self.pfx + line + ansi.RESET )
        self.orig( line )


class __Collect:
    def __init__( self, arr, orig ):
        self.arr = arr
        self.orig = orig
    
    
    def __call__( self, line ):
        self.arr.append( line )
        self.orig( line )


def __ignore( _ ):
    pass


def __as( keep_lines, array ):
    if keep_lines:
        return array
    else:
        return "\n".join( array )


# region Deprecated
def run( wd: str, cmd: Union[str, Sequence[str]], *, echo = False ):
    warnings.warn( "Deprecated - use execute", DeprecationWarning )
    if isinstance( cmd, str ):
        cmd = cmd.split( " " )
    return execute( dir = wd,
                    command = cmd,
                    echo = echo,
                    rx_stdout = True )


def run_subprocess( wd: str, cmd: Union[str, Sequence[str]], *, echo = False ) -> str:
    warnings.warn( "Deprecated - use execute", DeprecationWarning )
    if isinstance( cmd, str ):
        cmd = cmd.split( " " )
    return execute( dir = wd,
                    command = cmd,
                    echo = echo,
                    rx_stdout = True )
# endregion
