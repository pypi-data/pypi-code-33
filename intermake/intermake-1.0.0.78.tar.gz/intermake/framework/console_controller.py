"""
Defines the console host and support classes.
"""
import sys

from mhelper import ArgInspector, SwitchError, exception_helper, io_helper

import builtins

import intermake.helpers.printing as pr
from intermake.engine import Controller, EImRunMode, Result, Streaming, SxsToStderrWriter
from intermake.framework import console_configuration


class ConsoleController( Controller ):
    """
    UI controller for all the default console-based modes.
    """
    
    
    def __init__( self, app, mode: str ):
        """
        CONSTRUCTOR
        See the `Core.initialise` function for parameter descriptions.
        """
        super().__init__( app, mode )
        self.__stream_target: SxsToStderrWriter = SxsToStderrWriter( console_configuration.current )
    
    
    def get_prompt( self ) -> str:
        return self.on_get_prompt()
    
    
    def on_get_prompt( self ) -> str:
        return "{}>".format( self.app.name.lower() )
    
    
    def on_pause( self ) -> bool:
        return self.mode != EImRunMode.ARG
    
    
    def on_stop( self ) -> bool:
        if self.mode == EImRunMode.JUP:
            pr.pr_information( "The Jupyter frontend cannot be stopped without exiting the application. The application will now exit." )
            return False
        
        return True
    
    
    def __str__( self ) -> str:
        return "{}('{}' in '{}' mode)".format( type( self ).__name__, self.app.name, EImRunMode.get_name( self.mode ) )
    
    
    def on_start( self ) -> bool:
        """
        OVERRIDE 
        """
        #
        # Set the output stream to us
        #
        
        # Set the global output target
        Streaming.INSTANCE.set_target( self.__stream_target )
        
        if self.mode not in (EImRunMode.PYS, EImRunMode.ARG):
            if console_configuration.current.welcome_message:
                pr.printx( "{} {} {}. Type 'help{}' for help.", self.app.name.upper(), self.app.version, EImRunMode.get_name( self.mode ), "()" if self.mode != EImRunMode.CLI else "" )
        
        if self.mode in (EImRunMode.ARG, EImRunMode.CLI, EImRunMode.IPYI):
            # Don't use `code.interact` for the Python shell because `readline` breaks when
            # `colorama` is active so we need to intercept the `input`s.
            from intermake.framework.console_parser import start_cli
            start_cli( self.mode )
        elif self.mode == EImRunMode.JUP:
            from intermake.framework.console_parser import _PyiCommandWrapper
            builtins.__dict__.update( _PyiCommandWrapper.get_dict( self.app ) )  # TODO: This isn't great to override the builtins, how do we get out of it?
            return True  # Asynchronous
        elif self.mode == EImRunMode.PYS:
            return True  # Asynchronous
        elif self.mode == EImRunMode.PYI:
            import code
            from intermake.framework.console_parser import _PyiCommandWrapper, INTERMAKE_PROMPT
            variables = _PyiCommandWrapper.get_dict( self.app )
            sys.ps1 = INTERMAKE_PROMPT
            shell = code.InteractiveConsole( variables )
            shell.interact( banner = "" )
        else:
            raise SwitchError( "self.mode", self.mode )
    
    
    def on_execute( self, xargs: Result ) -> None:
        """
        OVERRIDE
        
        CLI mode:
        * Invokes the plugin in the current thread, this means it can return the result verbatim as well.
        * Raises exceptions in case of error, since everything is verbatim
        """
        #
        # Clear the screen before a command if necessary
        #
        if console_configuration.current.clear_screen:
            io_helper.system_cls()
            echo = True
        elif console_configuration.current.force_echo:
            echo = True
        else:
            echo = False
        
        #
        # Echo the command name if necessary
        #
        if echo:
            self.__echo_command( xargs )
        
        #
        # We are single threaded so the output stream should already have
        # been set, so just assert this.
        #
        if Streaming.INSTANCE.get_target() is not self.__stream_target:
            raise ValueError( "Expected Streaming.INSTANCE.get_target() ('{}') to be self.__stream_target ('{}') but it is not."
                              .format( Streaming.INSTANCE.get_target(),
                                       self.__stream_target ) )
        
        self.__stream_target.history = []
        
        #
        # Execute the actual command
        #
        try:
            result = xargs.execute()
        except BaseException as ex:
            xargs.set_error( exception = ex,
                             stacktrace = exception_helper.get_traceback(),
                             messages = self.__stream_target.history )
            raise
        else:
            xargs.set_result( result = result,
                              messages = self.__stream_target.history )
    
    
    def __echo_command( self, xargs ) -> None:
        msg = ["<command>{}</command>".format( xargs.command.name )]
        for arg in xargs.command.args:
            value = arg.extract( *xargs.args.args, **xargs.args.kwargs )
            assert isinstance( arg, ArgInspector )
            name = '<argument command="{}">{}</arg>'.format( xargs.command.name, arg.name )
            val_str = '<val>{}</val>'.format( value )
            
            if " " in val_str or "\"" in val_str:
                msg.append( " \"" + name + "=" + val_str + "\"" )
            else:
                msg.append( " " + name + "=" + val_str )
        
        self.__stream_target.write( "<echo>{}</echo>".format( "".join( msg ) ) )
