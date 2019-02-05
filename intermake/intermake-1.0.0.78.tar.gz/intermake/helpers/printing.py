"""
`intermake.printing` or `intermake.pr` supplements output with HTML-like formatting "SXS-HTML"
and redirects output to the GUI if that is the active frontend. Please see the `sxshtml` library
for full formatting details. 
"""
import sys
from typing import Optional, Union, Sequence, Iterable, IO, TypeVar, Callable, Tuple
from mhelper import exception_helper, string_helper, ansi_helper

import re
import textwrap
import docutils.core
import time

from intermake.engine import Streaming


T = TypeVar( "T" )
TIterable = Union[Sequence[T], Iterable[T], IO]
TText = Optional[Union[str, Callable[[int], str]]]


def printx( message, *args, end = "\n" ):
    """
    `printx` ("print-extended") writes text to `Streaming.INSTANCE`. This is directed
    by `intermake` at the SXS-HTML interpreter, which that renders output suitable for the current
    UI and then displays it in that UI.
    
    HTML-like codes are accepted as specified in the `sxsxml` library. To escape all codes
    use `pr_information` instead or, if stdout has been redirected, use `builtins.print`.
    """
    if args:
        message = fmt( message, *args )
    
    Streaming.INSTANCE.write( message + end )


def fmt_rst( data: Optional[Union[str, bytes]] ) -> str:
    """
    Formats a block of RST text.
    """
    data = data or ""
    data = textwrap.dedent( data )
    data = docutils.core.publish_parts( source = data, writer_name = 'xml' )["whole"]
    data = data.split( '-->', 1 )[1]
    return data


def pr_rst( data: Optional[Union[str, bytes]] ):
    """
    Formats and prints a block of RST text.
    """
    printx( fmt_rst( data ) )


def pr_list( items ):
    """
    Prints a list of items.
    """
    printx( "<ul>{}</ul>".format( "".join( "<li>{}</li>".format( escape( x ) ) for x in items ) ) )


def escape( text: str, condition: bool = True ) -> str:
    """
    Escapes HTML-codes in text, allowing the text to be rendered verbatim with `printx`.
    """
    text = str( text )
    
    if not condition:
        return text
    
    if "\033" in text:
        text = "(ANSI_STRIPPED:)" + ansi_helper.without_ansi( text )
    
    text = text.replace( "<", "&lt;" )
    text = text.replace( ">", "&gt;" )
    text = text.replace( '"', "&quot;" )
    text = text.replace( "'", "&apos;" )
    return text


_escape = escape


def fmt( message, *args ):
    """
    `builtins.format`s a `message` with all `args` passed through `escape`.
    """
    return message.format( *(escape( x ) for x in args) )


def pr_information( message, *, end = "\n" ):
    """
    `escape`s the `message` and passes it to `printx`.
    """
    printx( escape( message ), end = end )


def pr_style( style, message ):
    """
    Gives the message the designated style and passes it to `printx`.
    """
    printx( fmt_style( style, message ) )


def fmt_style( style, message ):
    """
    Gives the message the designated style.
    """
    return "<{0}>{1}</{0}>".format( style, escape( message ) )


def pr_question( message, options = () ):
    """
    Sends a `<question>` to printx. 
    """
    printx( fmt_question( message, options ) )
    return input()


def fmt_question( message, options ):
    """
    Formats a `<question>`. 
    """
    return "<question>{}</question>".format( escape( message ), "".join( "<option>{}</option>".format( escape( x ) ) for x in options ) )


def pr_table( rows, *, escape = True ):
    printx( fmt_table( rows, escape = escape ) )


def fmt_table( rows, *, escape = True ):
    r = ["<table>"]
    for row in rows:
        r.append( fmt_row( row, escape = escape ) )
    r.append( "</table>" )
    return "\n".join( r )


def fmt_row( items, *, escape = True ):
    return "<tr>{}</tr>".format( "".join( "<td>{}</td>".format( _escape( item, escape ) ) for item in items ) )


def fmt_file( file ):
    """
    Formats a `<file>` 
    """
    return "<file>{}</file>".format( escape( file ) )


def pr_verbose( message: str ):
    """
    Sends a `<verbose>` to printx. 
    """
    printx( "<verbose>{}</verbose>".format( escape( message ) ) )


def pr_warning( message: str, *_, **__ ):
    """
    Sends a `<warning>` to printx. 
    
    * and ** are ignored, these are for compatibility with warnings.showwarning
    """
    printx( "<warning>{}</warning>".format( escape( message ) ) )


def fmt_code( message: str ):
    return "<code>{}</code>".format( escape( message ) )


def fmt_section_start( name: str ):
    return '<section name="{}">'.format( escape( name ) )


def fmt_section_end():
    return '</section>'


class pr_section:
    """
    An enter...exit block that sends a `<section>` and `</section>` to `printx`.
    """
    
    
    def __init__( self, name ):
        printx( fmt_section_start( name ) )
    
    
    def __enter__( self ):
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        printx( fmt_section_end() )


class pr_action:
    """
    An enter...exit block that sends an `<action>` and `</action>` to `printx`
    with support for periodic progress updates via `<progress>`.
    """
    
    
    def __init__( self, title: str, count: int = 0, text: TText = None ):
        printx( '<action name="{}" max="{}">'.format( escape( title ), count ) )
        self.value = 0
        self.next_issue = 0
        
        if text is None:
            self.get_text = lambda x: ""
        elif isinstance( text, str ):
            closure = text
            self.get_text = lambda x: closure.format( x )
        else:
            self.get_text = text
        
        self.still_alive()
    
    
    def __enter__( self ):
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        printx( '</action>' )
    
    
    def increment( self, n = 1 ):
        self.value += n
        self.still_alive()
    
    
    def set_value( self, value ):
        self.value = value
        self.still_alive()
    
    
    def still_alive( self ):
        if time.time() > self.next_issue:
            text = self.get_text( self.value )
            printx( '<progress value="{}">{}</progress>'.format( self.value, escape( text ) ) )
            self.next_issue = time.time() + 0.2


def pr_enumerate( *args, **kwargs ) -> Iterable[Tuple[int, T]]:
    """
    Equivalent to `enumerate(pr_iterate(...))`.
    """
    return enumerate( pr_iterate( *args, **kwargs ) )


def pr_iterate( iterable: TIterable, title: str, count: int = None, text: TText = None ) -> Iterable[T]:
    """
    Iterates over an iterable and relays the progress to the GUI as SXS-HTML.
    
    :param iterable:        What to iterate over. This can be any iterable, though special cases for `list` `tuple` and file objects allow an automated `count`. 
    :param title:           See `pr.action.__init__` 
    :param count:           See `pr.action.__init__`.
                            The default is len(iterable), or the length of the file in bytes (for a file object). 
    :param text:            See `pr.action.__init__`.
    :return:                Yields each item from `iterable`. 
    """
    if count is None:
        try:
            count = len( iterable )
            count_is_file = False
        except TypeError:
            try:
                original_position = iterable.tell()
                count = iterable.seek( 0, 2 )
                iterable.seek( original_position )
                count_is_file = True
            except AttributeError:
                count = 0
                count_is_file = False
    else:
        count_is_file = False
    
    with pr_action( title, count, text ) as action_:
        for x in iterable:
            if count_is_file:
                action_.set_value( iterable.tell() )
            else:
                action_.increment()
            
            yield x


def pr_traceback( exception: Exception ):
    """
    Formats an exception traceback as SXS-HTML and sends it to `printx`.
    """
    printx( fmt_traceback( exception ) )


def fmt_traceback( exception: Union[BaseException, str], traceback = None ) -> str:
    """
    Formats an error traceback as SXS-HTML.
    
    :param exception:       Exception to display 
    :param traceback:      Traceback text (leave as `None` to get the system traceback) 
    :return:                ANSI containing string  
    """
    output_list = []
    output_list.append( "<section name='Traceback'>" )
    output_list.append( "<section name='Callstack'>" )
    
    if not traceback:
        traceback = exception_helper.get_traceback()
    
    lines = traceback.split( "\n" )
    
    for i, line in enumerate( lines ):
        next_line = lines[i + 2] if i < len( lines ) - 2 else ""
        m = re.search( "Function: (.*)$", next_line )
        if m is not None:
            next_function = m.group( 1 )
        else:
            next_function = None
        
        print_line = escape( line.strip() )
        
        if print_line.__contains__( "File: " ):
            print_line = string_helper.highlight_regex( print_line, "\\/([^\\/]*)\"", "<file>", "</file>" )
            print_line = string_helper.highlight_regex( print_line, "Line: ([0-9]*);", "<key>", "</key>" )
            print_line = string_helper.highlight_regex( print_line, "Function: (.*)$", "<key>", "</key>" )
            output_list.append( print_line )
        elif line.startswith( "*" ):
            output_list.append( print_line )
        else:
            if next_function:
                print_line = print_line.replace( next_function, "<key>" + next_function + "</key>" )
            
            output_list.append( print_line )
    
    output_list.append( "</section>" )
    
    # Exception text
    cause_depth = 1
    ex = exception
    prev = None
    
    while ex:
        if prev is not None:
            output_list.append( "<section name='Exception: {} - cause of {}'>".format( type( ex ).__name__, type( prev ).__name__ ) )
        
        else:
            output_list.append( "<section name='Exception: {}'>".format( type( ex ).__name__ ) )
        
        cause_depth += 1
        txt = escape( str( ex ) )
        txt = string_helper.highlight_quotes( txt, "«", "»", "<code>", "</code>" )
        output_list.append( txt )
        
        if isinstance( exception, BaseException ):
            prev = ex
            ex = ex.__cause__
        else:
            ex = None
    
    for _ in range( cause_depth ):
        output_list.append( "</section>" )
    
    return "\n".join( output_list )


class StdOutWrapper:
    """
    SINGLETON.
    
    Wraps a stream to `pr_information`. 
    """
    INSTANCE: "StdOutWrapper" = None
    
    
    def write( self, data ):
        pr_information( data, end = "" )
    
    
    def flush( self ):
        Streaming.INSTANCE.flush()


StdOutWrapper.INSTANCE = StdOutWrapper()
