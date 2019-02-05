from intermake_debug import commands
import intermake

from mhelper import safe_cast


@intermake.app.command()
def run_tests():
    """
    Test command.
    """
    false = False
    
    if false:
        intermake.commands.exit_controller()
        intermake.commands.invoke_python_help()
        intermake.commands.start_cli()
        intermake.commands.start_gui()
        intermake.commands.start_pyi()
        intermake.commands.start_ui()
        commands.debug_make_boring()
        commands.debug_error()
        test_sxs_fail()
    
    intermake.commands.start_cli()
    intermake.commands.start_debug()
    intermake.commands.clear_screen()
    intermake.commands.print_error()
    intermake.commands.toggle_command_set()
    intermake.commands.print_command_list()
    intermake.commands.eggs()
    intermake.commands.print_history()
    intermake.commands.print_help()
    intermake.commands.print_version()
    intermake.commands.import_python_module( "itertools" )
    intermake.commands.print_messages()
    intermake.commands.toggle_logging()
    intermake.commands.change_working_directory()
    intermake.commands.execute_cli_text( "beans" )
    intermake.commands.execute_cli_text( intermake.commands.configure.name )
    intermake.commands.change_workspace()
    
    commands.debug_echo( "hello" )
    commands.debug_echo_numeric( 1 )
    commands.debug_modules()
    commands.debug_coercers()
    commands.debug_eval( "1+1" )
    commands.debug_which( commands.debug_which.__name__ )
    commands.debug_css()
    commands.debug_system( ["echo", "hello"] )
    
    test_printing()
    test_sxs()
    test_rst()


@intermake.app.command()
def test_printing( size: int = 5 ):
    """
    Tests printing to the UI.
    
    :param size: Number of iterations (log scale)
    """
    count = 10 ** size
    
    intermake.pr.printx( "This is a message." )
    intermake.pr.printx( "This is a <key>key</key>." )
    intermake.pr.printx( "This is a <value>value</value>." )
    intermake.pr.printx( "This is a <command>value</command>.".format( "test_progress" ) )
    intermake.pr.printx( "This is <file>{}</file>.".format( __file__ ) )
    intermake.pr.printx( "<system>This is a system message.</system>" )
    intermake.pr.printx( "<verbose>This is a verbose message.</verbose>" )
    intermake.pr.printx( "<error>This is an error message.</error>" )
    intermake.pr.printx( "<warning>This is a warning message.</warning>" )
    intermake.pr.printx( "<table>" )
    intermake.pr.printx( "<tr><td>This</td><td>is</td><td>a</td></tr>" )
    intermake.pr.printx( "<tr><td>table</td><td>containing</td><td>a</td></tr>" )
    intermake.pr.printx( "<tr><td>square</td><td>of</td><td>nine</td></tr>" )
    intermake.pr.printx( "</table>" )
    
    for _ in intermake.pr.pr_iterate( range( count ), title = "Single iteration" ):
        pass
    
    for x in intermake.pr.pr_iterate( range( 10 ), title = "Nested iteration" ):
        for _ in intermake.pr.pr_iterate( range( int( count / 10 ) ), title = "Child iteration {} of 10".format( x + 1 ) ):
            pass


@intermake.app.command()
def test_sxs():
    """
    Tests SXS styles.
    """
    import sxsxml_tests
    a: intermake.SxsToStderrWriter = safe_cast( "intermake.Streaming.INSTANCE.get_target()", intermake.Streaming.INSTANCE.get_target(), intermake.SxsToStderrWriter )
    sxsxml_tests.run_tests( writer = a.writer,
                            delay = 0 )


@intermake.app.command()
def test_sxs_fail():
    """
    Tests SXS failure.
    """
    intermake.pr.printx( "</section>" )


@intermake.app.command()
def test_rst():
    """
    Tests RST parsing (this text).
    """
    intermake.pr.pr_rst( test_rst.__doc__ )
