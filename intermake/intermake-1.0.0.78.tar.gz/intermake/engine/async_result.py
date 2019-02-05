import warnings
from typing import List, Optional, Callable

from intermake.engine.abstract_command import Command
from mhelper import MEnum, ArgsKwargs, ArgValueCollection


__author__ = "Martin Rusilowicz"


class _EResultState( MEnum ):
    PENDING = 0
    SUCCESS = 1
    FAILURE = 2


class Result:
    """
    Intermake asynchronous result container and command executor.
    
    .. note::
    
        * Receiving:
            * All callbacks will be made in the primary thread, i.e. the
              same thread that requested the result.
        * Calling:
            * The `Result` class is not itself thread safe - it is up to
              the host to ensure that `set_result` or `set_error` is
              called in the main thread.
          
    :cvar __INDEX:          Tally on result count.  
    :ivar state:            State of result (pending, success, failure)
    :ivar ui_controller:             Executing host
    :ivar result:           Result (on success)
    :ivar exception:        Exception (on failure)
    :ivar traceback:        Exception traceback (on failure)
    :ivar messages:         Messages (on success or failure)
    :ivar index:            Index of result (arbitrary)
    :ivar __callbacks:      Result listeners (when pending)
    """
    __INDEX = 0
    
    
    def __init__( self,
                  *,
                  command: Command,
                  args: ArgsKwargs,
                  controller_args: ArgsKwargs,
                  controller ) -> None:
        """
        Constructs a `Result` in the `PENDING` state.
        """
        from intermake.engine.abstract_controller import Controller
        assert isinstance( controller, Controller )
        
        Result.__INDEX += 1
        
        self.command: Command = command
        self.args: ArgsKwargs = args
        self.ui_args: ArgsKwargs = controller_args
        self.state = _EResultState.PENDING
        self.ui_controller: Controller = controller
        self.result: Optional[object] = None
        self.exception: Exception = None
        self.traceback: str = None
        self.messages: Optional[List[str]] = None
        
        self.index = Result.__INDEX
        self.__callbacks: List[Callable[[Result], None]] = []
    
    
    def execute( self ) -> object:
        """
        Runs the command.
        This action can be performed in *any thread*.
        """
        # Check the argument types are correct
        ArgValueCollection( self.command.args, read = self.args )
        
        return self.command.on_run( *self.args.args, **self.args.kwargs )
    
    
    @property
    def title( self ):
        """
        The title of this Result.
        """
        warnings.warn( "Deprecated - use `command.name`", DeprecationWarning )
        return self.command.name
    
    
    def set_result( self,
                    result: Optional[object],
                    messages: Optional[List[str]] ):
        """
        Sets the result on this object and calls the callbacks.
        This action should be performed in the *main thread*.
        """
        assert self.state == _EResultState.PENDING, self.state
        self.state = _EResultState.SUCCESS
        self.result = result
        self.messages = messages
        self.__callback()
    
    
    def set_error( self,
                   exception: Optional[BaseException],
                   stacktrace: Optional[str],
                   messages: Optional[List[str]] ):
        """
        Sets the result on this object and calls the callbacks.
        This action should be performed in the *main thread*.
        """
        assert self.state == _EResultState.PENDING, self.state
        self.state = _EResultState.FAILURE
        self.exception = exception
        self.traceback = stacktrace
        self.messages = messages
        self.__callback()
    
    
    def listen( self, callback: Callable[["Result"], None] ):
        """
        Adds a callback.
        
        This function calls `callback` if the result has completed, otherwise
        `callback` is called when the result completes.
        """
        if self.is_pending:
            self.__callbacks.append( callback )
        else:
            callback( self )
    
    
    def __callback( self ):
        """
        Calls the callbacks, including the host itself.
        """
        
        # Call any global callbacks
        self.ui_controller.app.on_executed( self )
        self.ui_controller.result_history.append( self )
        self.ui_controller.on_executed( self )
        
        for callback in self.__callbacks:
            callback( self )
        
        self.__callbacks = None
    
    
    def raise_exception( self ) -> None:
        """
        For a result in the `FAILURE` state, re-raises the exception, otherwise does nothing.
        """
        if self.exception:
            raise self.exception
    
    
    @property
    def is_success( self ) -> bool:
        """
        `True` if the `Result` is in the `SUCCESS` state.
        """
        return self.state == _EResultState.SUCCESS
    
    
    @property
    def is_error( self ) -> bool:
        """
        `True` if the `Result` is in the `ERROR` state.
        """
        return self.state == _EResultState.FAILURE
    
    
    @property
    def is_pending( self ) -> bool:
        """
        `True` if the `Result` is in the `PENDING` state.
        """
        return self.state == _EResultState.PENDING
    
    
    def __repr__( self ):
        """
        Imperfect Python representation.
        """
        if self.is_pending:
            return "{}({}, {}, {}, {})".format( type( self ).__name__, self.index, self.command, repr( self.args ), repr( self.state ) )
        elif self.is_success:
            return "{}({}, {}, {}, {}, result = {})".format( type( self ).__name__, self.index, self.command, repr( self.args ), repr( self.state ), repr( self.result ) )
        else:
            return "{}({}, {}, {}, {}, exception = {})".format( type( self ).__name__, self.index, self.command, repr( self.args ), repr( self.state ), repr( self.exception ) )
    
    
    def __str__( self ) -> str:
        """
        Complete string representation.
        """
        if self.is_pending:
            return "(Pending) {} {}".format( self.command, self.args )
        elif self.is_success:
            return "(Success) {} {} = {}".format( self.command, self.args, self.result )
        else:
            return "(Failure) {} {} = {}".format( self.command, self.args, self.exception )
