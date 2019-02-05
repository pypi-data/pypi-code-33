import sys
import warnings
from typing import Iterator, List, TypeVar
import stringcoercion

from intermake.engine.abstract_command import Command
from intermake.engine.async_result import Result
import intermake.helpers.printing as pr
from intermake.helpers.printing import StdOutWrapper
from intermake.extensions import coercion_extensions
from mhelper import ArgsKwargs, abstract, virtual, Logger


_LOG = Logger( "user_interface_manager", False )

T = TypeVar( "T" )
__author__ = "Martin Rusilowicz"


class TaskCancelledError( Exception ):
    """
    Can raise this error when the plugin tries to send a progress update (stdout), if it determines
    the user has chosen to cancel the operation.
    
    Note that this is distinct from the `KeyboardInterrupt` issued by the CLI and is handled separately.
    """
    
    
    def __init__( self, message = None ):
        super().__init__( message or "Task cancelled by user." )


class _GeneralUiSettings:
    """
    :ivar number_of_results_to_keep: Number of results to keep in history
    """
    KEY = "general_ui_settings"
    
    
    def __init__( self ):
        self.number_of_results_to_keep = 10


class EImRunMode:
    """
    Modes - which controller to create and in which configuration.
    
    * These are the modes supported by Intermake.
      The application may accept further options.
    * These modes can also be prefixed `intermake_`, which requests the Intermake-defined GUI to be
      used, ignoring any custom modifications of the derived application.
    * `ARG`, `CLI`, `PYI`, `PYS`, `JUP` all create `ConsoleController` by default, whilst `GUI`
      creates `GuiController`.
    
    :cvar ARG: Parses command line arguments
    :cvar CLI: Console-based host with a command-line-interactive frontend.
    :cvar PYI: Console-based host with a Python-interactive frontend. For interactive sessions, this imports the commands into locals.
    :cvar PYS: Console-based host without a frontend. For your own Python scripts, this does not modify the environment.
    :cvar GUI: Graphical host with a graphical frontend.
    :cvar JUP: Console-based host without a frontend. For Jupyter notebook, this imports the commands into locals.
    """
    ARG = "arg"
    CLI = "cli"
    PYI = "pyi"
    IPYI = "ipyi"
    PYS = "pys"
    GUI = "gui"
    JUP = "jup"
    
    names = { ARG: "command line argument parsing",
              CLI: "command line interactive",
              PYI: "Python interactive",
              PYS: "Python library",
              GUI: "graphical user interface",
              JUP: "Jupyter notebook" }
    
    
    @classmethod
    def is_console( cls, x: str ):
        return x in (cls.ARG, cls.CLI, cls.PYI, cls.JUP, cls.PYS, cls.IPYI)
    
    
    @classmethod
    def is_gui( cls, x: str ):
        return x == cls.GUI
    
    
    @classmethod
    def get_name( cls, x: str ):
        return cls.names.get( x, x )


class ResultCollection:
    """
    Maintains a collection of results.
    Items are added to the back, thus [-1] is the most recent result.
    The size of the list is constrained by `_GeneralUiSettings.number_of_results_to_keep`.
    """
    
    
    def __init__( self, owner: "Controller" ) -> None:
        self.__data: List[Result] = []
        self.__owner: Controller = owner
    
    
    def __str__( self ):
        return "{} results".format( len( self ) )
    
    
    def append( self, result: Result ) -> None:
        self.__data.append( result )
        
        while len( self ) > self.__owner.general_ui_settings.number_of_results_to_keep:
            self.__data.pop( 0 )
    
    
    def __len__( self ) -> int:
        return len( self.__data )
    
    
    def __bool__( self ) -> bool:
        return bool( self.__data )
    
    
    def __getitem__( self, item ) -> Result:
        return self.__data[item]
    
    
    def __iter__( self ) -> Iterator[Result]:
        return iter( self.__data )


@abstract
class Controller:
    """
    The `Controller` runs commands according to the current user interface (CLI, python, jupyter, GUI, etc.)
    
    All virtual methods that should be overridden in the derived classes begin with `on_`.
    
    Life cycle:
    
       on_run
         ↓         
       on_pause ↔ on_resume
         ↓
       on_stop
       
    """
    ACTIVE: "Controller" = None
    
    
    def __init__( self, app, mode: str ):
        """
        CONSTRUCTOR
        
        :param app:     The application for which this controller is running.
                        This is the `self` argument when `Application.on_create_controller` is
                        called. 
        :param mode:    The mode name identifying this controller.
                        This is the `mode` argument when `Application.on_create_controller` is
                        called. 
        """
        from intermake import Application
        
        self.app: Application = app
        self.mode: str = mode
        self.general_ui_settings: _GeneralUiSettings = app.local_data.retrieve( _GeneralUiSettings.KEY, _GeneralUiSettings() )
        self.result_history = ResultCollection( self )
        self._previous_ui_controller: Controller = None
        self.__awaiting_stop = False
        self.__previous_stdout = None
        self.__previous_showwarning = None
        
        # Specify the coercers
        # This isn't actually used by this class, but all the currently derived classes use it so
        # it's just done once here for convenience
        self.coercers: stringcoercion.CoercerCollection = stringcoercion.create_default()
        coercion_extensions.init( self.coercers )
    
    
    def acquire( self, command, *args, **kwargs ) -> "_CommandAcquisition":
        """
        Acquires an object capable of running a command.
        
        usage::
        ```
            host.acquire( my_command ).run( args )
        ```
        
        :param command:     Either an `Command` instance to run
                            OR a `function` previously bound to a `BasicCommand`.
        :param kwargs:      Any host specific parameters dictating _how_ to run the command.
        :return:            An object upon which `run` may be called to invoke the command.
                            See `__Runner.run`. 
        """
        if not isinstance( command, Command ):
            from intermake.framework import BasicCommand
            command: Command = BasicCommand.retrieve( command )
        
        return _CommandAcquisition( self, command, ArgsKwargs( *args, **kwargs ) )
    
    
    @abstract
    def on_execute( self, args: Result ) -> None:
        """
        The derived should respond by running the command (`xargs.command`) in the appropriate
        manner.
        
            1. Ensuring `Streaming.INSTANCE.set_target()` is called to send output to an
               appropriate destination.
            2. Calling `xargs.execute()` to perform the actual routine.
            3. Calling `xargs.set_result()` or `xargs.set_error()` with the result of the execution.
            
        These steps may be performed asynchronously:
        **This call should not block.**
        """
        raise NotImplementedError( "Abstract" )
    
    
    @virtual
    def on_executed( self, args: Result ):
        """
        The derived class should perform any response to a command having
        completed and should then call `result.complete_command`.
        """
        pass
    
    
    def start( self ):
        """
        Starts this interface controller running. 
        """
        
        #
        # Pause previous
        #
        if Controller.ACTIVE is not None:
            Controller.ACTIVE.__pause()
        
        self._previous_ui_controller = Controller.ACTIVE
        Controller.ACTIVE = self
        
        #
        # Call derived class and handle errors 
        #
        try:
            Controller.ACTIVE.__resume()
            _LOG( "START {}: controller is starting for the first time", self )
            asynchronous = Controller.ACTIVE.on_start()
        except ExitUiError as ex:
            # Causes the UI to exit
            _LOG( "CLOSE {}: controller is closing due to {}", self, ex )
            asynchronous = False
        except ExitError as ex:
            # Causes everything to exit
            _LOG( "EXIT {}: all controllers are closing due to {}", self, ex )
            
            if self._previous_ui_controller is None:
                return
            
            raise
        except Exception as ex:
            pr.pr_traceback( ex )
            raise ValueError( "Error running UI «{}».".format( Controller.ACTIVE ) ) from ex
        else:
            if asynchronous:
                self.__awaiting_stop = True
                _LOG( "PERSIST {}: controller is asynchronous", self )
            else:
                _LOG( "EOL {}: controller has ended its synchronous loop", self )
                
                #
        # Stop if synchronous
        #
        if not asynchronous:
            self.__awaiting_stop = True
            self.stop()
    
    
    def stop( self ):
        """
        Stop a running user interface controller.
        
        The previous controller, if any, is now active.
         
        :return: Nothing is returned.
        """
        #
        # Check state
        #
        if not self.__awaiting_stop:
            raise ValueError( "Attempt to exit a UI controller «{}», but this controller is not running asynchronously. Did you mean to raise `ExitUiError` instead?".format( self ) )
        
        if self is not Controller.ACTIVE:
            raise ValueError( "Attempt to exit a UI controller «{}», but this UI controller is not the active one «{}».".format( self, Controller.ACTIVE ) )
        
        previous = self._previous_ui_controller
        
        #
        # Call derived class
        #
        self.__pause()
        
        _LOG( "STOP {}: controller is stopping", self )
        self.on_stop()
        
        #
        # Resume previous class (if present)
        #
        Controller.ACTIVE = previous
        
        if previous is None:
            from intermake.helpers.printing import pr_verbose
            pr_verbose( "Application exited." )
            _LOG( "HALT {}: There is no previous controller to resume. The application will probably exit.", self )
        else:
            previous.__resume()
    
    
    def __pause( self ):
        """
        Pauses the controller. 
        """
        # Call derived class
        _LOG( "PAUSE {}: controller is entering a paused state", self )
        self.on_pause()
    
    
    def __resume( self ):
        """
        Resumes the controller.
        """
        # Call derived class
        _LOG( "RESUME {}: controller is entering a running state", self )
        self.on_resume()
    
    
    @virtual
    def on_start( self ) -> bool:
        """
        The derived class should run the UI controller's main loop.
        
        :return: Returning `True` indicates that the controller runs asynchronously - `self._stop` must then
                 be called manually in this case.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def on_pause( self ) -> None:
        """
        The derived class should perform any "pause" handling.
        This is called prior to the controller seceding control to another's `on_start`, as well as before `on_stop` is called.
        """
        return
    
    
    @virtual
    def on_resume( self ) -> None:
        """
        The derived class should perform any "resume" handling.
        This is called prior to the controller resuming control after another's `on_stop`, as well as before `on_start` is called.
        """
        return
    
    
    @virtual
    def on_stop( self ) -> None:
        """
        The derived class should implement any necessary response to shut down the host.
        This is called when `on_start` exits synchronously, or when `self._stop()` is called to terminate an asynchronous `on_start`.
        """
        return


class _CommandAcquisition:
    """
    Presents a `run` function that runs the command in the specified user-interface.
    
    Use `intermake.acquire` to obtain this class.
    """
    
    
    def __init__( self, controller: Controller, command: Command, ui_args: ArgsKwargs ):
        self.controller = controller
        self.controller_args = ui_args
        self.command = command
    
    
    def run( self, *args, **kwargs ) -> Result:
        """
        Runs the command.
        
        :param args:        Passed to command. 
        :param kwargs:      Passed to command.
        :return:            The `Result` object.
        """
        # Construct the argument wrapper
        args_ = ArgsKwargs( *args, **kwargs )
        exec_args = Result( command = self.command,
                            args = args_,
                            controller_args = self.controller_args,
                            controller = self.controller )
        
        # Redirect streams to collect output
        previous_stdout = sys.stdout
        sys.stdout = StdOutWrapper.INSTANCE
        previous_showwarning = sys.stdout
        warnings.showwarning = pr.pr_warning
        
        try:
            # Ask the controller to execute the command
            self.controller.on_execute( exec_args )
        finally:
            # Restore streams
            sys.stdout = previous_stdout
            warnings.showwarning = previous_showwarning
        
        # Return the result placeholder
        return exec_args


class ExitError( BaseException ):
    """
    Used as a special error to indicate the application should exit.
    Raised, for instance, when the command line arguments have all been parsed and there is nothing
    left to do.
    """
    pass


class ExitUiError( BaseException ):
    """
    Used as a special error to indicate the current UI should exit.
    Raised, for instance, via the "exit" command or "CTRL+C".
    """
    pass
