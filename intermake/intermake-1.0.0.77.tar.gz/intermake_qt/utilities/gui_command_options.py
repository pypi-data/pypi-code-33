from mhelper import safe_cast

import intermake
import mhelper_qt as qt

from intermake_qt.utilities import formatting


def show_menu( window, command: intermake.Command ):
    from intermake_qt.extensions.gui_controller import GuiController
    
    controller: GuiController = intermake.Controller.ACTIVE
    options = controller.gui_settings
    cmd_options = options.per_command_get( command )
    
    mnu_root = qt.QMenu()
    alive = { }
    
    __mk_options( alive, options.default_command, mnu_root, options, "Default settings", True )
    __mk_options( alive, cmd_options, mnu_root, options, formatting.get_nice_name( "Settings for “{}”".format( command.name ) ), False )
    
    r = qt.show_menu( window, mnu_root )
    
    if r is None:
        return
    
    a, b, c = alive[r]
    
    if a is not None:
        assert hasattr( a, b ), "{} {}".format( a, b )
        setattr( a, b, c )
        from intermake_qt.extensions.gui_controller import GuiController
        controller: GuiController = safe_cast( "intermake.Controller.ACTIVE", intermake.Controller.ACTIVE, GuiController )
        controller.save_gui_settings()


def __mk_options( alive, cmd_options, mnu_root, options, name, d ):
    mnu_name = __mk_menu( alive, mnu_root, name )
    if d:
        #
        # HELP submenu
        #
        mnu_help = __mk_menu( alive, mnu_name, "Help" )
        __mk_action( alive, mnu_help, "Show as buttons", options, "inline_help", False )
        __mk_action( alive, mnu_help, "Show as inline text", options, "inline_help", True )
    #
    # AUTO-START submenu
    #
    mnu_prompt = __mk_menu( alive, mnu_name, "Prompt" )
    __mk_action( alive, mnu_prompt, "Use the default", cmd_options, "auto_start_if_parameterless", None )
    __mk_action( alive, mnu_prompt, "Start running the command", cmd_options, "auto_start_if_parameterless", True )
    __mk_action( alive, mnu_prompt, "Confirm before running the command", cmd_options, "auto_start_if_parameterless", False )
    #
    # AUTO-CLOSE submenu 1
    #
    mnu_success = __mk_menu( alive, mnu_name, "On success" )
    __mk_action( alive, mnu_success, "Use the default", cmd_options, "auto_close_on_success", None )
    __mk_action( alive, mnu_success, "Automatically close the messages window", cmd_options, "auto_close_on_success", True )
    __mk_action( alive, mnu_success, "Keep the messages window open", cmd_options, "auto_close_on_success", False )
    #
    # AUTO-CLOSE submenu 2
    #
    mnu_failure = __mk_menu( alive, mnu_name, "On failure" )
    __mk_action( alive, mnu_failure, "Use the default", cmd_options, "auto_close_on_failure", None )
    __mk_action( alive, mnu_failure, "Automatically close the messages window", cmd_options, "auto_close_on_failure", True )
    __mk_action( alive, mnu_failure, "Keep the messages window open", cmd_options, "auto_close_on_failure", False )
    #
    # SCROLL-MESSAGES submenu 2
    #
    mnu_scroll = __mk_menu( alive, mnu_name, "Scroll to new messages" )
    __mk_action( alive, mnu_scroll, "Use the default", cmd_options, "auto_scroll_messages", None )
    __mk_action( alive, mnu_scroll, "Always", cmd_options, "auto_scroll_messages", True )
    __mk_action( alive, mnu_scroll, "Never", cmd_options, "auto_scroll_messages", False )


def __mk_menu( alive, menu, text ):
    new_menu = qt.QMenu()
    new_menu.setTitle( text )
    alive[new_menu] = None, None, None
    menu.addMenu( new_menu )
    return new_menu


def __mk_action( alive, menu, text, a, b, c ):
    action = qt.QAction()
    action.setText( text )
    action.setCheckable( True )
    action.setChecked( getattr( a, b ) is c )
    action.setStatusTip( "{}={}".format( b, c ) )
    alive[action] = a, b, c
    menu.addAction( action )
    return action
