import sys
import time
import hashlib
from typing import List

from mhelper import ansi
from sxsxml import SxsAnsiWriter, SxsHtmlWriter, SxsWriter
import pyperclip

from sxsxml_tests.case_parser import get_cases


class _TestFailedError( Exception ):
    pass


def dprint( x, end = "\n" ):
    import sys
    
    sys.__stdout__.write( x )
    if end:
        sys.__stdout__.write( end )


def __check_result( *,
                    name,
                    command_text,
                    command_hash,
                    writer: SxsWriter,
                    delay,
                    checker: List[str] = None ):
    name = name.upper()
    qq = ansi.BACK_LIGHT_BLACK + ansi.FORE_BLACK
    qe = ansi.RESET
    
    dprint( ansi.FORE_YELLOW + "§ " + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§ **************************************** {} TEST BEGINS ****************************************".format( name ) + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )
    
    checker.clear()
    
    __run_test( text = command_text,
                delay = delay,
                writer = writer )
    
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§ INPUT" + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )
    for i, x in enumerate( command_text ):
        dprint( "{}RX{:03}[{}{}{}]{}".format( qq, i, qe, __fmt_easy( x ), qq, qe ) )
    
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§ OUTPUT" + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )
    
    for i, x in enumerate( checker ):
        dprint( "{}TX{:03}[{}{}{}]{}".format( qq, i, qe, __fmt_easy( x ), qq, qe ) )
    
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§ APPEARANCE" + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )
    content = "".join( checker )
    dprint( "{}CNTNT[{}{}{}]{}".format( qq, qe, content, qq, qe ) )
    pyperclip.copy( content )
    actual = hashlib.sha1( content.encode( 'utf-8' ) ).hexdigest()
    
    if command_hash and command_hash != actual:
        dprint( ansi.FORE_YELLOW + "§ " + ansi.RESET )
        dprint( ansi.FORE_YELLOW + "§ *********************************************************************************************" + ansi.RESET )
        dprint( ansi.FORE_YELLOW + "§ **************************************** TEST FAILED ****************************************" + ansi.RESET )
        dprint( ansi.FORE_YELLOW + "§ *********************************************************************************************" + ansi.RESET )
        dprint( ansi.FORE_YELLOW + "§ TEST: {}".format( name ) + ansi.RESET )
        dprint( ansi.FORE_YELLOW + "§ The actual hash '{}' does not match the expected hash '{}'.".format( actual, command_hash ) + ansi.RESET )
        dprint( ansi.FORE_YELLOW + "§ " + ansi.RESET )
        raise _TestFailedError( "Test failed." )
    
    dprint( ansi.FORE_YELLOW + "§ " + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§ ********** {} TEST {} **********".format( name, "PASSED" if command_hash else "UNCHECKED" ) + ansi.RESET )
    dprint( ansi.FORE_YELLOW + "§" + ansi.RESET )


def __fmt_easy( x ):
    qq = ansi.FORE_WHITE
    qe = ansi.RESET
    x = x.replace( "\033", ansi.BACK_MAGENTA + qq + "ESC" + qe )
    x = x.replace( "\n", ansi.BACK_BLUE + qq + "LF" + qe )
    x = x.replace( "\r", ansi.BACK_RED + qq + "CR" + qe )
    x = x.replace( " ", "·" )
    return x


def __run_test( *,
                text: List[str],
                delay: float,
                writer: SxsWriter ):
    delay /= 100
    
    for line in text:
        if line.startswith( "!REPEAT " ):
            s, e, line = line[len( "!REPEAT " ):].split( " ", 2 )
            for n in range( int( s ), int( e ) ):
                writer.write( line.format( n ) + "\n" )
                time.sleep( delay )
        else:
            writer.write( line + "\n" )


# noinspection SpellCheckingInspection
def run_tests( *,
               test_name: str = None,
               writer: SxsWriter,
               delay: float = 1,
               _writer_name: str = "none",
               _checker: List[str] = None ):
    commands = get_cases( _writer_name )
    
    if test_name is not None:
        commands = [x for x in commands if x[0] == test_name]
    
    for name, hash, text in commands:
        if _checker is not None:
            __check_result( name = _writer_name + " / " + name,
                            command_text = text,
                            command_hash = hash,
                            writer = writer,
                            delay = delay,
                            checker = _checker )
        else:
            __run_test( text = text,
                        delay = delay,
                        writer = writer )
    
    if _checker is not None:
        print( "+" )
        print( "+ **************************************************************************************************" )
        print( "+ **************************************** ALL TESTS PASSED ****************************************" )
        print( "+ **************************************************************************************************" )
        print( "+" )


def main():
    gui = False
    delay = 0
    echo = False
    
    for arg in sys.argv[1:]:
        if arg == "gui":
            gui = True
        elif arg == "delay":
            delay = 1
            echo = True
    
    if gui:
        from sxsxml_tests import gui
        gui.launch()
        return
    
    checker = []
    
    if echo:
        def ec( x ):
            checker.append( x )
            sys.__stderr__.write( x )
        
        
        tgt = ec
    else:
        tgt = checker.append
    
    try:
        run_tests( delay = delay,
                   _checker = checker,
                   writer = SxsAnsiWriter( tgt ),
                   _writer_name = "ansi" )
        
        run_tests( delay = delay,
                   _checker = checker,
                   writer = SxsHtmlWriter( tgt ),
                   _writer_name = "html" )
        
        run_tests( delay = delay,
                   _checker = checker,
                   writer = SxsHtmlWriter( tgt,
                                           scripted = False ),
                   _writer_name = "htms" )
    except _TestFailedError:
        exit( 1 )


if __name__ == "__main__":
    main()
