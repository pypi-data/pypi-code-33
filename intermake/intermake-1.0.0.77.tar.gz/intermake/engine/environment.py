from mhelper import NOT_PROVIDED
from typing import Optional

import warnings

from intermake.engine.abstract_controller import Controller, EImRunMode, _CommandAcquisition
from intermake.engine.async_result import Result
from intermake.engine.collections import CommandCollection, HelpTopicCollection
from intermake.engine.local_data import _LocalData


class _EnvironmentSettings:
    """
    User-settings for environment.
    
    :ivar startup: One or more modules to import when intermake is started.
    """
    
    
    def __init__( self ):
        self.startup = set()


class Application:
    """
    ABSTRACT
    
    The Intermake environment for a particular application.
    
    This class may be inherited.
    
    The `on_` methods are specifically designed for overriding.
    
    :cvar LAST:            The last application instantiated.
                           This is the application to which new commands get registered.
    """
    LAST: "Application" = None
    
    
    def __init__( self,
                  name: str = None,
                  *,
                  version: str = None,
                  inherit: Optional["Application"] = NOT_PROVIDED ):
        """
        CONSTRUCTOR
        
        Constructing the `Application` automatically sets `Application.LAST`.
                                    
        :param name:                Default value for property of same name.
        :param version:             Default value for property of same name.
        
        :param inherit:             Specify an existing environment to act as a base to extend.
                                    * Constants and commands from this application are imported into this one.
                                    * This application will become active in lieu of the `inherit`ed one.
        """
        #
        # Assert arguments
        #
        if not name:
            raise ValueError( "An application name must be provided." )
        
        if version is not None and not isinstance( version, str ):
            version = ".".join( str( x ) for x in version )
        
        if inherit is NOT_PROVIDED:
            from intermake.framework import app
            inherit = app
        
        #
        # Set basic fields
        #
        self.__name: str = name
        self.__version: str = version or "0.0.0.0"
        self.__inherit = inherit
        self.__commands: CommandCollection = CommandCollection( name, inherit and inherit.commands )
        self.__local_data: _LocalData = _LocalData( self.name.lower() )
        self.__help = HelpTopicCollection( name, inherit and inherit.help )
        self._environment_settings: _EnvironmentSettings = None
        
        #
        # Load settings
        #
        self._environment_settings = self.local_data.bind( "environment", _EnvironmentSettings() )
        
        #
        # Import user-specified modules
        #
        for module_name in self._environment_settings.startup:
            try:
                __import__( module_name )
            except ImportError as ex:
                warnings.warn( "Failed to import a module «{}» mandated by the user-specified environment settings: {}".format( module_name, ex ), UserWarning )
        
        #
        # Set the global variables
        #
        Application.LAST = self
        
        #
        # When a new application is created, we want to ensure a controller is running in case
        # it is being used as a Python library.
        #
        controller = Controller.ACTIVE
        
        if controller is None or (controller.app is inherit
                                  and controller.mode == EImRunMode.PYS):
            self.create_controller( EImRunMode.PYS ).start()
    
    
    def command( self, *args, **kwargs ):
        """
        Returns a decorator that exposes a function through the Intermake UI.
        
        See `self.commands.register` for more details.
        """
        return self.commands.register( *args, **kwargs )
    
    
    def is_running( self ):
        """
        Returns whether this `Application` is the currently running one.
        :return: 
        """
        return Controller.ACTIVE.app is self
    
    
    def __repr__( self ):
        """
        OVERRIDE 
        """
        return "{}({})".format( type( self ).__name__, repr( self.name ) )
    
    
    @property
    def help( self ) -> HelpTopicCollection:
        """
        Returns the `HelpTopicCollection` associated with this application.
        """
        return self.__help
    
    
    def start( self ):
        """
        Convenience function that starts up the application by parsing the command line.
        """
        self.create_controller( EImRunMode.ARG ).start()
    
    
    @property
    def name( self ) -> str:
        """
        Gets the display name of the application.
        """
        return str( self.__name )
    
    
    @property
    def commands( self ) -> CommandCollection:
        """
        The set of user-invokable commands for this application.
        """
        return self.__commands
    
    
    @property
    def local_data( self ) -> _LocalData:
        """
        Obtains the `_LocalData` store, used to apply and retrieve application settings.
        """
        return self.__local_data
    
    
    @property
    def version( self ) -> str:
        """
        Gets the application version. 
        """
        return self.__version
    
    
    def on_executed( self, args: Result ):
        """
        A derived class may override this method to perform command post-execute
        actions.
        
        If not overridden, no action is performed.
        """
        pass
    
    
    def create_controller( self, mode: str ) -> Controller:
        """
        Creates a UI controller for this application.
        """
        controller = self.on_create_controller( mode )
        controller.app = self
        return controller
    
    
    def on_create_controller( self, mode: str ) -> Controller:
        """
        VIRTUAL
        
        Allows a derived class to specify the UI controller to be used for a particular `mode`.
        
        The base implementation returns a default UI controller is returned for the modes
        specified in `EImRunMode`.
        """
        X = "intermake_"
        
        if mode.startswith( X ):
            mode = mode[len( X ):]
        
        if EImRunMode.is_console( mode ):
            from intermake.framework import ConsoleController
            return ConsoleController( self, mode )
        elif EImRunMode.is_gui( mode ):
            import intermake_qt
            return intermake_qt.GuiController( self, mode )
        else:
            raise ValueError( "{}.{} cannot create a UI controller for `mode` = '{}' because such as mode is not recognised".format( self, self.on_create_controller.__name__, mode ) )


def acquire( *args, **kwargs ) -> _CommandAcquisition:
    """
    Acquires the run-mode of the active user interface controller.
    
    The resulting object has a `run` function that can be used to run the command.
    """
    return Controller.ACTIVE.acquire( *args, **kwargs )


def run_jupyter() -> None:
    """
    Convenience command equivalent to `ui pyi`
    """
    Application.LAST.create_controller( EImRunMode.JUP ).start()


def start():
    Application.LAST.create_controller( EImRunMode.ARG ).start()
