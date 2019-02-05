"""
Manages the settings associated with the CLI parser and the CLI controller.

:data current:      The currently active settings.
                    (This is actually a proxy that resolves the settings, on
                    demand, from `ephemeral` and `saved`. It is read-only.)
:data ephemeral:    Active overrides for the current session only.
:data saved:        Settings saved and restored from disk.
                    (This is actually a proxy that loads the settings on demand
                    from `LocalData`)
"""

from typing import cast
from mhelper import SimpleProxy, reflection_helper

from intermake.engine import SxsToStderrWriter, Controller


class _ConsoleSettings( SxsToStderrWriter.Settings ):
    """
    User specified settings for the console.
    
    :ivar clear_screen:                 When set, the console display is cleared between command executions.
    :ivar force_echo:                   When set, commands are repeated back to the user.
                                        This is applied even if the user did not invoke the command themselves.
    :ivar show_external_streams:        Show output from running external applications.
    :ivar welcome_message:              Whether to show the version when the application loads.
    :ivar error_traceback:              When set, the full error traceback is printed when an error occurs in the
                                        console.
    :ivar always_start_ui:              When set, the specified UI always starts after the command-line arguments have
                                        been parsed.
    :ivar error_starts_ui:              When set, the specified UI always starts if an error occurs when executing the
                                        command-line arguments.
    :ivar default_ui:                   Specifies the default UI to start if no command-line arguments are provided.
                                        If this is blank the system default will be used (probably the Python
                                        Interactive Shell).
    """
    
    
    def __init__( self ) -> None:
        super().__init__( format_output = True,
                          remove_ansi = False,
                          remove_utf = "" )
        self.clear_screen: bool = False
        self.force_echo: bool = False
        self.show_external_streams: bool = False
        self.welcome_message = True
        self.error_traceback = False
        self.always_start_ui = ""
        self.error_starts_ui = ""
        self.default_ui = ""
    
    
    def __repr__( self ):
        return reflection_helper.describe_num_fields( self )


class __SettingsProxy:
    def __getattribute__( self, name: str ) -> object:
        if name == "__class__":
            return super().__getattribute__( name )
        
        saved_ = getattr( saved, name )
        ephemeral_ = getattr( ephemeral, name )
        
        if isinstance( saved_, dict ):
            return { **ephemeral_, **saved_ }
        else:
            return ephemeral_ or saved_


def __get_saved_console_settings() -> _ConsoleSettings:
    return Controller.ACTIVE.app.local_data.bind( "cli_frontend", _ConsoleSettings() )


current: _ConsoleSettings = cast( _ConsoleSettings, __SettingsProxy() )
ephemeral: _ConsoleSettings = _ConsoleSettings()
saved: _ConsoleSettings = SimpleProxy( __get_saved_console_settings )
