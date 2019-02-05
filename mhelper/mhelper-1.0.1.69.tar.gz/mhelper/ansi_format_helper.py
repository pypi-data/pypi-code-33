"""
Functions for formatting stuff using ANSI codes and/or esoteric UNICODE characters.
"""
import warnings
from typing import Union, Iterable, cast

import re
from colorama import Back, Fore, Style

from mhelper import ansi, ansi_helper, exception_helper, string_helper


def format_source( text: str,
                   keywords: Iterable[str],
                   variables: Iterable[str] ) -> str:
    """
    Prints source text, highlighting keywords and variables, and prefixing line numbers
    
    :param text:        Text to print
    :param keywords:    Keywords to highlight
    :param variables:   Variables to highlight
    :return:            Nothing
    """
    r = []
    
    text = text.split( "\n" )
    
    for i, line in enumerate( text ):
        prefix = Back.LIGHTBLACK_EX + Fore.BLACK + " " + str( i ).rjust( 4 ) + " " + Style.RESET_ALL + " "
        
        line = string_helper.highlight_words( line, keywords, Style.RESET_ALL + Fore.GREEN, Style.RESET_ALL )
        line = string_helper.highlight_words( line, variables, Style.RESET_ALL + Fore.CYAN, Style.RESET_ALL )
        
        r.append( prefix + line )
    
    return "\n".join( r )


def print_traceback( ex = None ):
    print( format_traceback_ex( ex ) )


class _Palette:
    def __init__( self, wordwrap, warning ):
        s = Style
        b = Back
        f = Fore
        self.output = []
        self.wordwrap = wordwrap or 140  # Total size of box
        self.fwidth = self.wordwrap - 2  # Size of box without borders
        self.width = self.wordwrap - 4  # Size of box without borders and margins
        self.reset_colour = s.RESET_ALL
        self.vbar, self.tl_bar, self.hbar, self.tr_bar, self.vl_bar, self.vr_bar, self.bl_bar, self.br_bar = "│┌─┐├┤└┘"
        self.error_colour = s.RESET_ALL + b.WHITE + (f.YELLOW if warning else f.RED)  # Error text colour
        self.error_bold_colour = s.RESET_ALL + b.WHITE + f.BLACK + ansi.ITALIC  # Error text quotes
        self.locals_colour = s.RESET_ALL + b.LIGHTBLACK_EX + f.BLACK  # Locals colour
        self.locals_bold_colour = s.RESET_ALL + b.LIGHTBLACK_EX + f.YELLOW  # Locals colour
        self.border_colour = s.RESET_ALL + f.WHITE + (b.YELLOW if warning else b.RED)  # Border colour
        self.code_colour = s.RESET_ALL + b.BLUE + f.WHITE  # Code extracts
        self.code_bold_colour = s.RESET_ALL + b.BLUE + f.YELLOW  # Function name
        self.file_colour = s.RESET_ALL + b.LIGHTYELLOW_EX + f.BLACK + ansi.DIM  # File lines
        self.file_bold_colour = s.RESET_ALL + b.LIGHTYELLOW_EX + f.BLUE + ansi.BOLD  # File names, line numbers
        self.outside_file_colour = s.RESET_ALL + b.CYAN + f.BLACK + ansi.DIM  # File lines
        self.outside_file_bold_colour = s.RESET_ALL + b.CYAN + f.BLUE + ansi.BOLD  # File names, line numbers
        self.title_colour = s.RESET_ALL + (b.YELLOW if warning else b.RED) + f.WHITE
        self.title_bold_colour = s.RESET_ALL + ((b.YELLOW + f.RED) if warning else (b.RED + f.YELLOW))
        
        self.left_margin = self.border_colour + self.vbar
        self.right_margin = self.border_colour + self.vbar + s.RESET_ALL
    
    
    def write_hbar( self ):
        self.output.append( self.border_colour + self.vl_bar + self.hbar * self.fwidth + self.vr_bar + self.reset_colour )
    
    
    def write_tbar( self ):
        self.output.append( self.border_colour + self.tl_bar + self.hbar * self.fwidth + self.tr_bar + self.reset_colour )
    
    
    def write_bbar( self ):
        self.output.append( self.border_colour + self.bl_bar + self.hbar * self.fwidth + self.br_bar + self.reset_colour )
    
    
    def write_message( self, *, message, colour, justify = -1, colour2 = "" ):
        from mhelper.ansi_helper import wrap
        
        message += colour
        
        for l in wrap( message, self.width, justify = justify ):
            self.output.append( self.left_margin + colour + " " + colour2 + l + colour + " " + self.right_margin )


def format_traceback_ex( exception: Union[BaseException, str] = None,
                         *,
                         wordwrap = 0,
                         warning = False ):
    """
    Formats a traceback for display suitable in an ANSI terminal.     
    """
    
    from mhelper.string_helper import highlight_quotes
    
    
    p = _Palette( wordwrap, warning )
    
    tb_co = exception_helper.get_traceback_ex( exception )
    
    # Format: Traceback
    for tb_ex in tb_co.exceptions:
        # Format: Title...
        if tb_ex.index == 0:
            p.write_tbar()
        else:
            p.write_hbar()
        p.write_message( message = p.title_bold_colour + tb_ex.type + p.title_colour + ": " + tb_ex.message,
                         colour = p.title_colour )
        p.write_hbar()
        # ...end
        
        for tb_fr in tb_ex.frames:
            # Format: Location...
            if "site-packages" in tb_fr.file_name:
                fc = p.outside_file_colour
                fbc = p.outside_file_bold_colour
            else:
                fc = p.file_colour
                fbc = p.file_bold_colour
            p.write_message( message = "{exception}.{frame}. File {file}; Line: {line}; Function: {function}" \
                             .format( exception = tb_ex.index,
                                      frame = tb_fr.index,
                                      file = fbc + tb_fr.file_name + fc,
                                      line = fbc + str( tb_fr.line_no ) + fc,
                                      function = fbc + tb_fr.function + fc ),
                             colour = fc )
            # ...end
            
            # Format: Context
            p.write_message( message = (tb_fr.code_context.replace( tb_fr.next_function,
                                                                    p.code_bold_colour + tb_fr.next_function + p.code_colour )
                                        if tb_fr.next_function
                                        else tb_fr.code_context),
                             colour = p.code_colour )
            
            # Format: Locals
            for lo in tb_fr.locals:
                p.write_message( message = ">{name} = {value}".format( name = p.locals_bold_colour + lo.name + p.locals_colour,
                                                                       value = lo.repr ),
                                 colour = p.code_colour,
                                 colour2 = p.locals_colour,
                                 justify = 1 )
    
    p.write_hbar()
    
    # Format: Exception text
    for tb_ex in tb_co.exceptions:
        # "caused by"
        if tb_ex.index != 0:
            p.write_message( message = ansi.DIM + ansi.ITALIC + "caused by",
                             colour = p.error_colour,
                             justify = 0 )
        
        # Type
        p.write_message( message = ansi.UNDERLINE + tb_ex.type,
                         colour = p.error_colour,
                         justify = -1 )
        
        # Message
        p.write_message( message = highlight_quotes( tb_ex.message, "«", "»", p.error_bold_colour, p.error_colour ),
                         colour = p.error_colour,
                         justify = -1 )
    
    p.write_bbar()
    
    return "\n".join( p.output )


def format_two_columns( *,
                        left_margin: int,
                        centre_margin: int,
                        right_margin: int,
                        left_text: str,
                        right_text: str,
                        left_prefix: str = "",
                        right_prefix: str = "",
                        left_suffix: str = "",
                        right_suffix: str = "", ):
    """
    Formats a box.
     
    :param left_margin:     Width of left margin 
    :param centre_margin:   Width of centre margin 
    :param right_margin:    Width of right margin 
    :param left_text:       Text in left column 
    :param right_text:      Text in right column 
    :param left_prefix:     Text added to left lines
    :param right_prefix:    Text added to right lines
    :param left_suffix:     Text added to left lines
    :param right_suffix:    Text added to right lines
    :return: 
    """
    r = []
    left_space = centre_margin - left_margin - 1
    right_space = right_margin - centre_margin
    
    left_lines = list( left_prefix + x + left_suffix for x in ansi_helper.wrap( left_text, left_space, justify = -1 ) )
    right_lines = list( right_prefix + x + right_suffix for x in ansi_helper.wrap( right_text, right_space ) )
    num_lines = max( len( left_lines ), len( right_lines ) )
    
    for i in range( num_lines ):
        left = left_lines[i] if i < len( left_lines ) else " " * left_space
        right = right_lines[i] if i < len( right_lines ) else " " * right_space
        
        text = (" " * left_margin) + left + Style.RESET_ALL + " " + right + Style.RESET_ALL
        r.append( text )
    
    return "\n".join( r )


# region Deprecated

# noinspection PyDeprecation
def format_traceback( exception: Union[BaseException, str],
                      traceback_ = None,
                      warning = False,
                      wordwrap = 0 ) -> str:
    """
    DEPRECATED
    
    Formats a traceback.
    
    :param exception:       Exception to display 
    :param traceback_:      Traceback text (leave as `None` to get the system traceback) 
    :param warning:         Set to `True` to use warning, rather than error, colours 
    :param wordwrap:        Set to the wordwrap width. 
    :return:                ANSI containing string  
    """
    warnings.warn( "Deprecated - use `format_traceback_ex`", DeprecationWarning )
    
    if traceback_ is None:
        return format_traceback_ex( exception, warning = warning, wordwrap = wordwrap )
    
    from mhelper.string_helper import highlight_quotes, highlight_regex
    from mhelper.ansi_helper import cjust, fix_width, wrap
    
    output = []
    wordwrap = wordwrap or 140
    width = wordwrap - 4
    S_V, S_TL, S_H, S_TR, S_VL, S_VR, S_BL, S_BR = "│┌─┐├┤└┘"
    et_col = Style.RESET_ALL + Back.WHITE + (Fore.YELLOW if warning else Fore.RED)  # Error text colour
    eq_col = Style.RESET_ALL + Back.WHITE + Fore.BLACK + ansi.ITALIC  # Error text quotes
    br_col = Fore.WHITE + (Back.YELLOW if warning else Back.RED)  # Border colour
    cd_col = Style.RESET_ALL + Back.WHITE + Fore.BLACK  # Code extracts
    fn_col = Style.RESET_ALL + Back.WHITE + Fore.BLUE  # Function name
    ln_col = Style.RESET_ALL + Back.WHITE + Fore.BLUE + ansi.DIM  # File lines
    fi_col = Style.RESET_ALL + Back.WHITE + Fore.BLUE + ansi.BOLD  # File names, line numbers
    lb = br_col + S_V + et_col + " "
    rb = et_col + " " + br_col + S_V + Style.RESET_ALL
    
    output.append( br_col + S_TL + S_H * (wordwrap - 2) + S_TR + Style.RESET_ALL )
    
    if not traceback_:
        traceback_ = exception_helper.get_traceback()
    
    lines = traceback_.split( "\n" )
    
    for i, line in enumerate( lines ):
        next_line = lines[i + 2] if i < len( lines ) - 2 else ""
        m = re.search( "Function: (.*)$", next_line )
        if m is not None:
            next_function = m.group( 1 )
        else:
            next_function = None
        
        l = line.strip()
        
        if "Local: " in l:
            l = l.replace( "Local: ", ">" )
            highlight_quotes( l, ">", "=", cd_col, et_col, count = 1 )
            output.append( lb + fix_width( et_col + l, width, justify = 1 ) + rb )
        elif "File " in l or "File: " in l:
            l = ln_col + highlight_regex( l, "\\/([^\\/]*)\"", fi_col, ln_col )
            l = highlight_regex( l, "Line: ([0-9]*);", fi_col, ln_col )
            l = highlight_regex( l, "Function: (.*)$", fi_col, ln_col )
            l = fix_width( l, width )
            output.append( lb + l + rb )
        elif line.startswith( "*" ):
            c = wordwrap - len( l ) - 6
            output.append( br_col + S_VL + cast( str, S_H * 4 ) + l + S_H * c + S_VR + Style.RESET_ALL )
        else:
            l = fix_width( l, width )
            if next_function:
                l = l.replace( next_function, fn_col + next_function + cd_col )
            
            output.append( lb + cd_col + l + rb )
    
    output.append( br_col + S_VL + S_H * (wordwrap - 2) + S_VR + Style.RESET_ALL )
    
    # Exception text
    if isinstance( exception, BaseException ):
        ex = exception
        
        while ex:
            if ex is not exception:
                output.append( lb + cjust( ansi.DIM + ansi.ITALIC + "caused by" + ansi.ITALIC_OFF + ansi.DIM_OFF, width ) + rb )
            
            output.append( lb + (cjust( ansi.UNDERLINE + type( ex ).__name__ + ansi.UNDERLINE_OFF, width ) + rb) )
            ex_text = et_col + highlight_quotes( str( ex ), "«", "»", eq_col, et_col )
            
            for line in wrap( ex_text, width ):
                line = cjust( line, width )
                output.append( lb + line + rb )
            
            ex = ex.__cause__
    
    else:
        output.append( lb + str( exception ).ljust( width ) + rb )
    
    output.append( br_col + S_BL + S_H * (wordwrap - 2) + S_BR + Style.RESET_ALL )
    
    return "\n".join( output )

# endregion
