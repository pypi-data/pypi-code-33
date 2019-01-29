from mhelper import ansi, string_helper, AnsiStr, ansi_helper
from typing import List

import itertools

from sxsxml.sxs.base import SxsWriter
from sxsxml.support import XsProgress


class SxsAnsiWriter( SxsWriter ):
    """
    Writes ANSI from an SXS stream.
    """
    
    BAR = ansi.DIM
    RESET = "\0\0RE"
    
    
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        self.__in_progress = False
        self.__last_out_eol = False
        self.__progress_not_finished = False
    
    
    def on_format_section_end( self ):
        return ""
    
    
    def on_format_text( self, x ):
        # If we are in a progress bar then we'll need to add a line break
        if self.__in_progress:
            self.__in_progress = False
            
            if self.__progress_not_finished:
                self.on_text( " »\n" )
            else:
                self.on_text( "\n" )
        
        self.__last_out_eol = x.endswith( "\n" )
        
        x = x.replace( "\n", "\n" + self.__section_prefix() )
        x = x.replace( self.RESET, ansi.RESET )
        return x
    
    
    def _exit_default( self ):
        text = self.pop()
        self.on_text( "{}{}{}".format( ansi.BLINK + str( self.element ) + ansi.BLINK_OFF, text, ansi.BLINK + "</>" + ansi.BLINK_OFF ) )
    
    
    def on_consume_eol( self ):
        if self.__in_progress or self.__last_out_eol:
            # Consume the EOL - return to line start and issue new prefix 
            self.on_text( "\r" )
            self.on_text( self.__section_prefix() )
        else:
            # Part way through a line - issue a new line
            self.on_text( "\n" )
    
    
    def __section_prefix( self ):
        if not self.section_depth:
            return ""
        
        return self.BAR + "│ " * self.section_depth + ansi.RESET
    
    
    def on_format_progress( self, p: XsProgress ):
        r = ("\r" + self.__section_prefix() + ansi.FORE_GREEN
             + "PROGRESS ({}) IS {} OF {}: '{}'".format( self.section_name,
                                                         p.value,
                                                         p.max,
                                                         p.text.ljust( 20, "." ) )
             + ansi.RESET)
        
        return r
    
    
    def on_formatted_progress( self, p: XsProgress ):
        self.ignore_next_eol()
        self.__in_progress = True
        self.__last_out_eol = False
        self.__progress_not_finished = p.value != p.max
    
    
    def on_format_heading( self, level, name ) -> str:
        if not name:
            return ""
        
        if level == 1:
            box = ansi.Box.DOUBLE
        elif level == 2:
            box = ansi.Box.BOLD
        elif level == 3:
            box = ansi.Box.SINGLE
        elif level == 3:
            box = ansi.Box.DOTTED
        else:
            box = None
        
        colour = ansi.RESET
        reset = ansi.RESET
        
        if box is not None:
            actual_name_ = name
            line_of_name = box.hr * len( name )
            above_name_ = " " + box.tl + box.ts + line_of_name + box.ts + box.tr
            centre_name = " " + box.ls + box.em + actual_name_ + box.em + box.rs
            below_name_ = " " + box.bl + box.bs + line_of_name + box.bs + box.br
            
            r = (self.BAR + "╭" + colour + string_helper.ljust( above_name_, 80, " " ) + reset + "\n"
                 + self.BAR + "│" + colour + string_helper.ljust( centre_name, 80, " " ) + reset + "\n"
                 + self.BAR + "│" + colour + string_helper.ljust( below_name_, 80, " " ) + reset)
        else:
            r = self.BAR + "╭" + colour + "*" * level + " " + name + reset
        
        return r
    
    
    def on_format_question( self, question, options ):
        question = ansi.FORE_BRIGHT_CYAN + question.strip() + ansi.RESET + "\n" + "\n".join( " > {}".format( ansi.FORE_BRIGHT_BLUE + x + ansi.RESET ) for x in options )
        question = ":: " + question.replace( "\n", "\n:: " )
        return question
    
    
    def on_format_table( self, rows ):
        # Note - we can't use a library because we need to preserve ansi escape sequences
        
        box = ansi.Box.BLANK
        col_lens = [max( len( AnsiStr( row[col].split( "\n" )[0] ) ) for row in rows ) for col in range( len( rows[0] ) )]
        r: List[str] = []
        x = [[("=" * l) for l in col_lens]]
        needs_l = False
        
        for row_index, row in enumerate( itertools.chain( x, [rows[0]], x, rows[1:], x ) ):
            row_lines = [list( ansi_helper.wrap( row[col], col_lens[col] ) ) for col in range( len( row ) )]
            num_row_lines = max( len( cell_line ) for cell_line in row_lines )
            
            if row_index <= 2:
                a = ansi.fore( 192 - 16, 192 - 16, 192 - 16 )
                c = ansi.back( 192, 192, 192 )
            elif row_index % 2 == 0:
                a = ansi.fore( 230 - 16, 255 - 16, 230 - 16 )
                c = ansi.back( 230, 255, 230 )
            else:
                a = ansi.fore( 255 - 16, 255 - 16, 255 - 16 )
                c = ansi.back( 255, 255, 255 )
            
            for row_line in range( num_row_lines ):
                if needs_l:
                    r.append( "\n" )
                else:
                    needs_l = True
                
                r.append( a + c + box.vr + box.em + ansi.RESET )
                
                for col, cell_lines in enumerate( row_lines ):
                    cell_line = cell_lines[row_line] if row_line < len( cell_lines ) else ""
                    
                    if col != 0:
                        r.append( a + c + box.em + box.vr + box.em + ansi.RESET + c )
                    else:
                        r.append( c )
                    
                    r.append( str( AnsiStr( cell_line ).ljust( col_lens[col] ) ) )
                    
                    r.append( ansi.RESET )
                
                r.append( a + c + box.em + box.vr + ansi.RESET )
        
        text = "".join( str( x ) for x in r )
        return text
    
    
    def on_format_hr( self ):
        return ansi.FORE_WHITE + ansi.BACK_BLUE + "-" * 80 + ansi.RESET
    
    
    def on_format_italic( self, x ):
        return ansi.ITALIC + x + ansi.ITALIC_OFF
    
    
    def on_format_key( self, x ):
        return ansi.FORE_GREEN + x + ansi.FORE_RESET
    
    
    def on_format_value( self, x ):
        return ansi.FORE_CYAN + x + ansi.FORE_RESET
    
    
    def on_format_error( self, x ):
        return self.format( ansi.BACK_RED + ansi.FORE_BRIGHT_WHITE, ansi.DIM + "ERROR: " + ansi.DIM_OFF + x )
    
    
    def on_format_code( self, x ):
        return ansi.FORE_BRIGHT_BLUE + x + ansi.FORE_RESET
    
    
    def on_format_file( self, x ):
        return ansi.FORE_YELLOW + x + ansi.FORE_RESET
    
    
    def on_format_warning( self, x ):
        return self.format( ansi.BACK_BRIGHT_YELLOW + ansi.FORE_BLACK, ansi.DIM + "WARNING: " + ansi.DIM_OFF + x )
    
    
    def on_format_positive( self, x ):
        return self.format( ansi.FORE_GREEN, x )
    
    
    def on_format_negative( self, x ):
        return self.format( ansi.FORE_RED, x )
    
    
    def on_format_neutral( self, x ):
        return self.format( ansi.FORE_CYAN, x )
    
    
    def on_format_command( self, x ):
        # Underline slows down iTerm2 massively
        # return self.format( ansi.UNDERLINE, x )
        return self.format( ansi.BOLD, x )
    
    
    def format( self, prefix, x ):
        return prefix + x.replace( self.RESET, ansi.RESET + prefix ) + self.RESET
    
    
    def on_format_verbose( self, x ):
        return self.format( ansi.DIM, x )
    
    
    def on_format_list( self, rows, ordered ):
        r = []
        
        for i, x in enumerate( rows ):
            if ordered:
                r.append( "{}{}.{} {}".format( ansi.DIM, str( i + 1 ), ansi.DIM_OFF, x ) )
            else:
                r.append( "{}•{} {}".format( ansi.DIM, ansi.DIM_OFF, x ) )
        
        return "\n".join( r )
