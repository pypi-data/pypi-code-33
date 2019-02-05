from typing import Optional, cast, List, Callable, Dict
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProxyStyle, QStyle, QWidget
from mhelper import Logger, ansi_format_helper, override, virtual, exception_helper, ignore, TTristate

import sys
import threading
import intermake
import editorium

from intermake_qt.forms.frm_maintenance import FrmMaintenance
from intermake_qt.utilities.interfaces import IGuiMainWindow
from intermake_qt.utilities import css_processing


__author__ = "Martin Rusilowicz"

_sig_log = Logger( "gui signals" )


class _FnWrapper:
    """
    Wraps a function, we need to do this because QT won't let us send raw functions across threads, but we can send an object that behaves like a function.
    """
    
    
    def __init__( self, fn ) -> None:
        self.__fn = fn
    
    
    def __call__( self, *args, **kwargs ) -> Optional[object]:
        return self.__fn( *args, **kwargs )
    
    
    def __str__( self ) -> str:
        return str( self.__fn )


class _GraphicalUiSettings:
    """
    :ivar gui_css:         CSS stylesheet. Takes a full path or a name of an Intermake style sheet
                           (with or without the `.css` extension). If not specified uses `main.css`.
    :ivar inline_help:     Setting for the "arguments" form, controls whether help is displayed inline.
    :ivar default_command: Controls behaviour when executing a command that has not been individually
                           configured.
    :ivar per_command:     Overrides the `default_command` behaviour for individual commands, specified
                           as a command-name to setting dictionary.
    """
    
    
    def __init__( self ) -> None:
        super().__init__()
        self.inline_help: bool = False
        self.gui_css = ""
        self.default_command = _GraphicalUiCommandSettings()
        self.per_command: Dict[str, _GraphicalUiCommandSettings] = { }
    
    
    def read( self, command, setting, default ):
        x = self.per_command_get( command )
        r = getattr( x, setting )
        
        if r is not None:
            return r
        
        r = getattr( self.default_command, setting )
        
        if r is not None:
            return r
        
        return default
    
    
    def per_command_get( self, command ) -> "_GraphicalUiCommandSettings":
        r = self.per_command.get( command.name )
        
        if r is None:
            r = _GraphicalUiCommandSettings()
            self.per_command[command.name] = r
        
        return r


class _GraphicalUiCommandSettings:
    def __init__( self ):
        self.auto_close_on_success: TTristate = None
        self.auto_close_on_failure: TTristate = None
        self.auto_start_if_parameterless: TTristate = None
        self.auto_scroll_messages: TTristate = None


class _CreateWindowArgs:
    def __init__( self, can_return_to_cli: bool ):
        self.can_return_to_cli = can_return_to_cli


class GuiController( intermake.Controller ):
    """
    Manages a set of asynchronous workers and their progress dialogue
    
    :ivar __settings:       These settings used by the GUI which can be configured by the user through the `set` command.
    :ivar owner_window:     The main window
    :ivar thread_local:     Thread-local data store. Each thread gets its own version of this, including the main thread. 
    """
    
    ARG_AUTO_CLOSE = -1, "auto_close"
    ARG_PARENT_WINDOW = 0, "window"
    ARG_CONFIRM = -1, "confirm"
    ARG_LISTEN = -1, "callback"
    
    
    def __init__( self, app: intermake.Application, mode: str ) -> None:
        """
        CONSTRUCTOR
        """
        super().__init__( app, mode )
        self.__settings: _GraphicalUiSettings = None
        self.owner_window = cast( IGuiMainWindow, None )
        self.thread_local = threading.local()
        self.__exec_index = 0
        
        self.__current_wait_form: FrmMaintenance = None
        self.__current_async_result: intermake.Result = None
        self.__current_bee_thread: BeeThread = None
        
        self.editorium = editorium.create_default()
        self.editorium.default_messages.coercers = self.coercers
        self.style_sheet = css_processing.load_css( self.gui_settings.gui_css )
        self.style_sheet_parsed = css_processing.parse_css( self.style_sheet )
        
        threading.currentThread().name = "main_intermake_gui_thread"
    
    
    def __str__( self ) -> str:
        return "GuiController(QT)"
    
    
    @virtual
    def on_create_window( self, args: _CreateWindowArgs ):
        """
        VIRTUAL
        
        The base class creates the main GUI window.
        The derived class may override this to provide their own window.
        
        :param args:    Information that may be of use
        :return:        The created window. This should be an `IGuiMainWindow`
        """
        
        from intermake_qt.forms.frm_intermake_main import FrmIntermakeMain
        frm_main = FrmIntermakeMain( app = self.app,
                                     controller = self,
                                     can_return_to_cli = args.can_return_to_cli )
        return frm_main
    
    
    @override
    def on_start( self ) -> None:
        """
        Helper function to start the GUI
        """
        # Unfortunate notice: If the GUI fails to initialise with a segmentation fault this is probably a bad QT
        # installation. The user will need to reinstall QT/PyQt5. TODO: Detect this scenario and inform the user.
        intermake.pr.pr_information( "GUI-Frontend. The GUI is now active. Input will not be accepted in this terminal until the GUI completes." )
        
        import sys
        from PyQt5.QtWidgets import QApplication
        
        # Read the CSS
        style = self.style_sheet_parsed.get( 'QApplication.style', "" )
        small_icon_size = int( self.style_sheet_parsed.get( 'QApplication.smallIconSize', "16" ) )
        
        # Start the GUI
        if style:
            QApplication.setStyle( _ProxyStyle( style, small_icon_size ) )
        
        app = QApplication( sys.argv )
        app.setStyleSheet( self.style_sheet )
        puc = self._previous_ui_controller
        can_return_to_cli = not isinstance( puc, intermake.ConsoleController ) or cast( intermake.ConsoleController, puc ).console_configuration.run_mode != intermake.EImRunMode.ARG
        main_window = self.on_create_window( _CreateWindowArgs( can_return_to_cli = can_return_to_cli ) )
        self.owner_window = main_window
        main_window.show()
        
        app.exec_()
        intermake.pr.pr_verbose( "The GUI has closed." )
        
        if not main_window.return_to_console():
            raise intermake.ExitError( "No return to console selected." )
    
    
    @property
    def gui_settings( self ) -> _GraphicalUiSettings:
        if self.__settings is None:
            self.__settings = self.app.local_data.bind( "gui", _GraphicalUiSettings() )
        
        return self.__settings
    
    
    def save_gui_settings( self ):
        self.app.local_data.commit( self.gui_settings )
    
    
    @override
    def on_execute( self, xargs: intermake.Result ) -> None:
        """
        IMPLEMENTATION
        
        This host's run command uses `FrmMaintenance` to perform the legwork.
        Acceptable host args include:
            `window` (`QWidget`)
            `auto_close` (`bool`) 
        """
        args = self.__process_arguments( xargs )
        
        if not args:
            return None
        
        self.__process_invocation( xargs, *args )
    
    
    def __process_arguments( self, xargs: intermake.Result ):
        """
        Extracts controller arguments from the command ready to be run.
        """
        
        #
        # Process argument: HOST WINDOW?
        #
        window: QWidget = xargs.ui_args.get( *self.ARG_PARENT_WINDOW, self.owner_window )
        
        if window is None:
            raise ValueError( "The GUI expects a Window when running a command. DId you remember to set the `window` parameter when calling `acquire`?" )
        
        #
        # Process argument: CALLBACK
        #
        callback: Callable[[intermake.Result], None] = xargs.ui_args.get( *self.ARG_LISTEN, None )
        
        if callback is not None:
            xargs.listen( callback )
        
        #
        # Process argument: AUTO-START / CONFIRM
        #
        confirm: bool = xargs.ui_args.get( *self.ARG_CONFIRM, False )
        
        if confirm and xargs.command.args:
            start = False  # cannot auto-start even if overridden
        else:
            start = self.gui_settings.read( xargs.command, "auto_start_if_parameterless", not confirm )
        
        if not start:
            # Confirm means show the arguments form, we then exit
            from intermake_qt.forms.frm_arguments import FrmArguments
            avc = FrmArguments.query( owner_window = window,
                                      editorium = self.editorium,
                                      command = xargs.command,
                                      defaults = xargs.args )
            
            if avc is None:
                # Cancelled
                xargs.set_error( intermake.TaskCancelledError( "User denied starting task." ), None, None )
                return None
            
            # Accepted - change the arguments to the user's choice
            xargs.args = avc.to_argskwargs()
        
        #
        # Process argument: AUTO-CLOSE
        #
        auto_close: bool = xargs.ui_args.get( *self.ARG_AUTO_CLOSE, False )
        
        #
        # Results
        #
        return window, auto_close
    
    
    def __process_invocation( self, xargs, window, auto_close ):
        """
        Runs the command after processing all arguments.
        """
        #
        # Construct the async placeholder
        #
        self.__current_async_result = xargs
        #
        # Show the "please wait" form
        #
        self.__current_wait_form = FrmMaintenance( window, xargs.command, auto_close )
        self.__current_wait_form.setModal( True )
        self.__current_wait_form.show()
        #
        # Launch the worker thread
        # SEE: `BeeThread.run`
        #
        try:
            self.__current_bee_thread = BeeThread( self, xargs, self.__current_wait_form )
            self.__current_bee_thread.start()
        except Exception as ex:
            # Thread failed to start
            self.bee_finished( None, ex, exception_helper.get_traceback(), ["<verbose>Thread failed to start.</verbose>"] )
    
    
    def __get_next_exec_index( self ):
        self.__exec_index += 1
        return self.__exec_index
    
    
    @override
    def on_executed( self, result ):
        self.owner_window.command_completed( result )
    
    
    def bee_finished( self, result: object, exception: Exception, traceback: str, messages: List[str] ) -> None:
        """
        Called when a thread finishes (back in the main thread)
        """
        # Close the dialogue.
        # ***** It is the dialogue that sets the result *****
        self.__current_wait_form.handle_worker_finished( self.__current_async_result, result, exception, traceback, messages )


class _ProxyStyle( QProxyStyle ):
    def __init__( self, style: Optional[str], small_icon_size: int ):
        if style != "default":
            super().__init__( style )
        else:
            super().__init__()
        
        self.__small_icon_size = small_icon_size
    
    
    def pixelMetric( self, QStyle_PixelMetric, option = None, widget = None ):
        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return self.__small_icon_size
        else:
            return QProxyStyle.pixelMetric( self, QStyle_PixelMetric, option, widget )


class GuiControllerWithBrowser( GuiController ):
    class Settings:
        """
        :ivar enable_browser:  Web browser status.
        
                               .. note::
                               
                                   This parameter is interpreted as a boolean but can be anything.
                                   `True` - enables the browser.
                                   `False` - disables the browser.
                                        
                                   Values with a `__bool__` may be used for application specific control.
                                   e.g. `0` = disabled, `1` = enabled, `2` = enabled, but ask before show
        """
        
        
        def __init__( self ):
            self.enable_browser: bool = True
    
    
    @classmethod
    def get_settings( cls ) -> Settings:
        return intermake.Controller.ACTIVE.app.local_data.bind( cls.__name__, cls.Settings() )
    
    
    def on_start( self ):
        settings = self.get_settings()
        
        if settings.enable_browser:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            ignore( QWebEngineView )
        
        super().on_start()


class BeeThread( QThread ):
    """
    Thread that runs commands in a "please wait" window.
    """
    __callback = pyqtSignal( _FnWrapper )
    
    
    def __init__( self, hive: GuiController, async_result: intermake.Result, dialogue ):
        ##########################
        # THIS IS THE GUI THREAD #
        ##########################
        QThread.__init__( self )
        self.__callback.connect( self.__invoke_returned )
        self.__async_result = async_result
        self.dialogue: FrmMaintenance = dialogue
        self.__hive: GuiController = hive
        self.__writer = _SxsGuiWriter( self )
    
    
    @override  # QThread
    def run( self ) -> None:
        #############################
        # THIS IS THE WORKER THREAD #
        #############################
        
        #
        # Name the thread
        #
        threading.currentThread().name = "intermake_busybee_running_{}".format( self.__async_result.command.name )
        
        #
        # Set thread-local data
        #
        intermake.Streaming.INSTANCE.set_target( self.__writer )
        
        #
        # Execute the command
        #
        try:
            true_result = self.__async_result.execute()
            result = true_result, None, None, self.__writer.history
        except Exception as ex:
            result = None, ex, exception_helper.get_traceback(), self.__writer.history
            
            # Print a message for the debugger
            sys.__stderr__.write( "EXCEPTION IN __BusyBee.run:\n" )
            sys.__stderr__.write( ansi_format_helper.format_traceback( ex ) )
            sys.__stderr__.write( "\n" )
        
        #
        # Respond with the result
        #
        self.invoke_in_main_thread( lambda: self.__hive.bee_finished( *result ) )
    
    
    def invoke_in_main_thread( self, where ) -> None:  # WORKER
        """
        Calls "where" back in the main thread
        """
        where = _FnWrapper( where )
        _sig_log( "S __invoke_emit --> {}".format( where ) )
        self.__callback.emit( where )  # --> MAIN (via signal)
        _sig_log( "E __invoke_emit --> {}".format( where ) )
    
    
    @staticmethod
    def __invoke_returned( where ) -> None:  # <- MAIN (via signal)
        """
        The callback from invoke_in_main_thread - just calls "where".
        """
        _sig_log( "S __invoke_returned --> {}".format( where ) )
        where()
        _sig_log( "E __invoke_returned --> {}".format( where ) )


class _SxsGuiWriter:
    def __init__( self, thread ):
        self.thread = thread
        self.history = []
    
    
    def write( self, data: str ):
        self.history.append( data )
        
        if self.thread.dialogue.handle_was_cancelled():
            raise intermake.TaskCancelledError()
        
        self.thread.invoke_in_main_thread( lambda: self.thread.dialogue.handle_message_from_worker( data ) )
