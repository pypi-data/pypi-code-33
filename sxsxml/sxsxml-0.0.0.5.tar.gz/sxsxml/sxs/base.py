import sys
import time

from sxsxml.abstract import XsStackedWriter
from sxsxml.support import XsProgress


class SxsWriter( XsStackedWriter ):
    """
    ABSTRACT
    
    Base class for SXS formatted streams.
    
    See ``readme.rst`` for the expected markup.
    """
    _CELL_START = "<$CS>"
    _CELL_END = "<$CE>"
    _ROW_START = "<$RS>"
    _ROW_END = "<$RE>"
    _START_TIME_TAG = "<$ST>"
    _NEWLINE = "<$NL>"
    
    
    def __init__( self, out = sys.__stdout__.write ):
        super().__init__( out )
        
        self.__sections = []
        self.__special_text = False
        self.__ignore_next_eol = False
        self.__in_table = False
        self.__no_newlines = 0
        self.section_name = "Untitled main section"
        
        self.map( ["document"], self.__enter_document, self.__exit_document )
        self.map( ["action"], self.__enter_action, self.__exit_action )
        self.map( ["argument"], self._enter_default, self.__exit_argument )
        self.map( ["literal", "tt", "code"], self._enter_default, self.__exit_code )
        self.map( ["command"], self._enter_default, self.__exit_command )
        self.map( ["error"], self._enter_default, self.__exit_error )
        self.map( ["file"], self._enter_default, self.__exit_file )
        self.map( ["heading"], self.__enter_heading, self.__exit_heading )
        self.map( ["hr"], self.__enter_hr, self.__exit_hr )
        self.map( ["emphasis", "em", "i", "cite", "title_reference"], self._enter_default, self.__exit_i )
        self.map( ["key"], self._enter_default, self.exit_key )
        self.map( ["li"], self._enter_default, self.__exit_li )
        self.map( ["negative"], self._enter_default, self.__exit_negative )
        self.map( ["neutral"], self._enter_default, self.__exit_neutral )
        self.map( ["ol"], self._enter_default, self.__exit_ol )
        self.map( ["option"], self._enter_default, self.__exit_option )
        self.map( ["br", "p", "paragraph"], self._enter_default, self.__exit_paragraph )
        self.map( ["positive"], self._enter_default, self.__exit_positive )
        self.map( ["progress"], self.__enter_progress, self.__exit_progress )
        self.map( ["question"], self.__enter_question, self.__exit_question )
        self.map( ["section"], self.enter_section, self.__exit_section )
        self.map( ["stderr"], self._enter_default, self.__exit_stderr )
        self.map( ["stdout"], self._enter_default, self.__exit_stdout )
        self.map( ["strong", "b"], self._enter_default, self.__exit_i )
        self.map( ["system"], self.__enter_system, self.__exit_system )
        self.map( ["table"], self.__enter_table, self.__exit_table )
        self.map( ["td"], self._enter_default, self.__exit_td )
        self.map( ["title"], self._enter_default, self.__exit_title )
        self.map( ["tr"], self._enter_default, self.__exit_tr )
        self.map( ["definition_list", "dl", "bullet_list", "ul"], self._enter_default, self.__exit_ul )
        self.map( ["value"], self._enter_default, self.__exit_value )
        self.map( ["verbose"], self.__enter_verbose, self.__exit_verbose )
        self.map( ["warning"], self._enter_default, self.__exit_warning )
    
    
    def __consume_eol( self ):
        self.on_consume_eol()
        self.ignore_next_eol()
    
    
    def ignore_next_eol( self ):
        self.__ignore_next_eol = True
    
    
    @property
    def section_depth( self ):
        # This prevents an indent being carried over into a tables cells
        # TODO: Find a better way that allows headings in cells
        if self.__in_table:
            return 0
        
        return len( self.__sections )
    
    
    def __enter_document( self ):
        self.__no_newlines += 1
    
    
    def __exit_document( self ):
        self.__no_newlines -= 1
        assert self.__no_newlines >= 0
    
    
    def on_text( self, x: str ):
        if not x:
            return
        
        if self.__special_text:
            super().on_text( x )
            return
        
        # If we are consuming an EOL then consume it...
        if self.__ignore_next_eol:
            self.__ignore_next_eol = False
            
            if x.startswith( "\n" ):
                x = x[1:]
            
            if not x:
                return
        
        if self.__no_newlines:
            x = x.replace( "\n", " " )
        
        x = x.replace( self._NEWLINE, "\n" )
        
        r = self.on_format_text( x )
        
        if r:
            super().on_text( r )
    
    
    def on_format_text( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    #
    # SECTION
    #
    def enter_section( self ):
        self.__sections.append( self.element )
        self.__print_title( self.element.get( "name" ) )
        self.__consume_eol()
    
    
    def __exit_title( self ) -> None:
        self.__print_title( self.pop() )
    
    
    def __print_title( self, name ):
        self.section_name = name
        
        if name:
            r = self.on_format_heading( len( self.__sections ), name )
            x = self.__sections.pop( -1 )
            self.on_text( r )
            self.__sections.append( x )
    
    
    def on_format_heading( self, l, x ) -> str:
        raise NotImplementedError( "abstract" )
    
    
    def __exit_section( self ) -> None:
        assert self.__sections.pop() is self.element
        r = self.on_format_section_end()
        if r:
            self.on_text( r )
        self.__consume_eol()
    
    
    def on_consume_eol( self ):
        raise NotImplementedError( "abstract" )
    
    
    def __enter_heading( self ):
        self.push()
    
    
    def __exit_heading( self ):
        self.on_text( self.on_format_heading( int( self.element.get( "level", 1 ) ), self.pop() ) + self.on_format_section_end() )
    
    
    #
    # SYSTEM
    #
    def __enter_system( self ):
        self.element.attr["name"] = "System"
        self.enter_section()
    
    
    def __exit_system( self ):
        self.__exit_section()
    
    
    #
    # GENERAL
    #
    
    def on_format_positive( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_negative( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_neutral( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    #
    # PROGRESS
    #
    def __enter_action( self ):
        setattr( self.element, self._START_TIME_TAG, time.time() )
        self.enter_section()
    
    
    def __exit_action( self ):
        self.__print_progress( self.__sections[-1].get( "max", "?" ), "" )
        self.__exit_section()
    
    
    def __enter_progress( self ):
        self.push()
        self.__special_text = True
    
    
    def __exit_progress( self ):
        self.__special_text = False
        value = self.get( "value", "?" )
        self.__print_progress( value, self.pop() )
    
    
    def __print_progress( self, value, text ):
        start = getattr( self.__sections[-1], self._START_TIME_TAG )
        elapsed = time.time() - start
        max = self.__sections[-1].get( "max", "?" )
        text = text.replace( "\n", "" )
        p = XsProgress( self.section_name, value, max, text, elapsed )
        r = self.on_format_progress( p )
        super().on_text( r )
        self.on_formatted_progress( p )
    
    
    def on_formatted_progress( self, p: XsProgress ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_progress( self, p: XsProgress ):
        raise NotImplementedError( "abstract" )
    
    
    #
    # QUESTION
    #
    def __enter_question( self ):
        self.push()
    
    
    def __exit_question( self ):
        question, options = _ss_split( self.pop(), self._ROW_START, self._ROW_END )
        question = self.on_format_question( question.strip(), options )
        
        super().on_text( question )
    
    
    def on_format_question( self, question, options ):
        raise NotImplementedError( "abstract" )
    
    
    def __exit_option( self ):
        self.on_text( self._ROW_START + self.pop() + self._ROW_END )
        self.__consume_eol()
    
    
    #
    # TABLE
    #
    def __exit_td( self ) -> None:
        self.on_text( self._CELL_START + self.pop() + self._CELL_END )
    
    
    def __exit_tr( self ) -> None:
        self.on_text( self._ROW_START + self.pop() + self._ROW_END )
    
    
    def __enter_table( self ):
        self.__in_table = True
        self.push()
    
    
    def __exit_table( self ) -> None:
        self.__in_table = False
        rows = _ss_split( self.pop(), self._ROW_START, self._ROW_END )[1]
        rows = [_ss_split( y, self._CELL_START, self._CELL_END )[1] for y in rows]
        cols = max( len( row ) for row in rows )
        rows = [row + ([""] * (cols - len( row ))) for row in rows]
        text = self.on_format_table( rows )
        
        self.on_text( text )
    
    
    def on_format_table( self, rows ):
        raise NotImplementedError( "abstract" )
    
    
    #
    # LISTS
    #
    def __exit_li( self ):
        self.on_text( self._ROW_START + self.pop() + self._ROW_END )
    
    
    def __exit_ul( self ):
        rows = _ss_split( self.pop(), self._ROW_START, self._ROW_END )[1]
        text = self.on_format_list( rows, ordered = False )
        self.on_text( text )
    
    
    def __exit_ol( self ):
        rows = _ss_split( self.pop(), self._ROW_START, self._ROW_END )[1]
        text = self.on_format_list( rows, ordered = True )
        self.on_text( text )
    
    
    #
    # VERBOSE
    #
    def __enter_verbose( self ):
        self.push()
    
    
    def __exit_verbose( self ):
        self.on_text( self.on_format_verbose( self.pop() ) )
    
    
    #
    # BASIC FORMATTING
    #
    def __enter_hr( self ) -> None:
        pass
    
    
    def __exit_hr( self ) -> None:
        self.on_text( self.on_format_hr() )
        self.__consume_eol()
    
    
    def on_format_hr( self ):
        raise NotImplementedError( "abstract" )
    
    
    def __exit_i( self ) -> None:
        self.on_text( self.on_format_italic( self.pop() ) )
    
    
    def exit_key( self ) -> None:
        self.on_text( self.on_format_key( self.pop() ) )
    
    
    def on_format_italic( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_key( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def __exit_value( self ) -> None:
        self.on_text( self.on_format_value( self.pop() ) )
    
    
    def on_format_value( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def __exit_file( self ) -> None:
        self.on_text( self.on_format_file( self.pop() ) )
    
    
    def on_format_file( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def __exit_code( self ) -> None:
        self.on_text( self.on_format_code( self.pop() ) )
    
    
    def on_format_code( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def __exit_error( self ) -> None:
        self.on_text( self.on_format_error( self.pop() ) )
    
    
    def on_format_error( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def __exit_paragraph( self ):
        self.on_text( self.pop() + self._NEWLINE )
    
    
    def __exit_positive( self ) -> None:
        self.on_text( self.on_format_positive( self.pop() ) )
    
    
    def __exit_negative( self ) -> None:
        self.on_text( self.on_format_negative( self.pop() ) )
    
    
    def __exit_neutral( self ) -> None:
        self.on_text( self.on_format_neutral( self.pop() ) )
    
    
    def __exit_warning( self ) -> None:
        self.on_text( self.on_format_warning( self.pop() ) )
    
    
    def __exit_command( self ) -> None:
        self.on_text( self.on_format_command( self.pop() ) )
    
    
    def __exit_stdout( self ) -> None:
        self.on_text( self.on_format_positive( self.pop() ) )
    
    
    def __exit_stderr( self ) -> None:
        self.on_text( self.on_format_negative( self.pop() ) )
    
    
    def __exit_argument( self ) -> None:
        self.on_text( self.on_format_key( self.pop() ) )
    
    
    def on_format_warning( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_command( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_section_end( self ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_verbose( self, x ):
        raise NotImplementedError( "abstract" )
    
    
    def on_format_list( self, rows, ordered ):
        raise NotImplementedError( "abstract" )


def _ss_split( text, prefix, suffix ):
    z = []
    v = []
    x = text.split( prefix )
    
    z.append( x[0] )
    
    for y in x[1:]:
        a, b = y.split( suffix, 1 )
        v.append( a )
        z.append( b )
    
    return "".join( z ), v
