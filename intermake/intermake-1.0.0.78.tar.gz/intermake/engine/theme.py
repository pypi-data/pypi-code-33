"""
The Theme module is deprecated.
"""
import warnings


warnings.warn("Theme is deprecated. Please use `intermake.pr` instead.", DeprecationWarning)

from mhelper import ansi as ansi


class _BlockClass:
    def __init__( self ):
        self.SHADE = "░"
        self.HORIZONTAL = "─"
        self.LEFT_BAR = "├"
        self.RIGHT_BAR = "┤"
        self.VERTICAL = "│"
        self.TOP_LEFT = "┌"
        self.TOP_RIGHT = "┐"
        self.BOTTOM_LEFT = "└"
        self.BOTTOM_RIGHT = "┘"


class __ThemeClass:
    def __init__( self ):
        # Block drawing
        self.C: _BlockClass = _BlockClass()
        
        #
        # Special
        #
        self.RESET = ansi.RESET  # Normal text
        
        # Titles
        self.TITLE = ansi.RESET + ansi.BACK_BLUE + ansi.FORE_WHITE  # Titles (heading 1)
        self.SUBTITLE = ansi.RESET + ansi.BACK_LIGHT_BLACK + ansi.FORE_GREEN  # Titles (heading 2)
        self.HEADING = ansi.RESET + ansi.FORE_MAGENTA  # Headings (heading 2)
        
        # General
        self.EMPHASIS = ansi.RESET + ansi.FORE_BLUE  # Quotes
        self.EMPHASIS_EXTRA = ansi.RESET + ansi.FORE_BRIGHT_WHITE + ansi.BACK_LIGHT_BLACK  # Quotes
        self.COMMENT = ansi.RESET + ansi.DIM  # Comments, descriptions
        self.BOLD = ansi.RESET + ansi.FORE_YELLOW  # Key points
        self.BOLD_EXTRA = ansi.RESET + ansi.FORE_YELLOW + ansi.BACK_BLUE  # Key points, including spaces
        
        # Unique
        self.ENUMERATION = ansi.RESET + ansi.FORE_MAGENTA  # Enumerations, options
        self.FIELD_NAME = ansi.RESET + ansi.FORE_YELLOW  # Field names
        self.ARGUMENT_NAME = ansi.RESET + ansi.FORE_CYAN  # Argument names
        self.VALUE = ansi.RESET + ansi.FORE_YELLOW  # Argument values
        self.COMMAND_NAME = ansi.RESET + ansi.FORE_GREEN  # Command names, variable names
        self.COMMAND_NAME_BOLD = ansi.RESET + ansi.FORE_BRIGHT_GREEN  # Emphasised form of COMMAND_NAME
        self.CORE_NAME = ansi.RESET + ansi.FORE_YELLOW  # Emphasised form of COMMAND_NAME
        self.SYSTEM_NAME = ansi.RESET + ansi.FORE_RED  # Emphasised form of COMMAND_NAME
        
        # Status
        self.STATUS_NO = ansi.RESET + ansi.FORE_RED  # No settings
        self.STATUS_YES = ansi.RESET + ansi.FORE_GREEN  # Yes settings
        self.STATUS_INTERMEDIATE = ansi.RESET + ansi.FORE_CYAN  # Intermediate, neither, settings
        self.STATUS_IS_SET = ansi.RESET + ansi.BACK_BLUE  # Unset settings
        self.STATUS_IS_NOT_SET = ansi.RESET  # Set settings
        
        # Boxes
        self.BORDER = ansi.RESET + ansi.FORE_BRIGHT_BLACK + ansi.DIM  # Borders and lines, deemphasised
        self.BOX_TITLE = ansi.RESET + ansi.FORE_BRIGHT_WHITE + ansi.BOLD  # Titles inside tables
        self.BOX_TITLE_RIGHT = ansi.RESET + ansi.BACK_CYAN + ansi.FORE_BLACK  # Titles inside titles
        
        # Internal streams
        self.WARNING = ansi.RESET + ansi.BACK_YELLOW + ansi.FORE_RED  # Warnings
        self.WARNING_BOLD = ansi.RESET + ansi.BACK_YELLOW + ansi.FORE_RED + ansi.BOLD  # Warnings
        self.ERROR = ansi.RESET + ansi.FORE_RED  # Errors
        self.ERROR_BOLD = ansi.RESET + ansi.FORE_YELLOW  # Errors
        self.PROMPT = ansi.RESET + ansi.FORE_YELLOW  # Prompts
        
        # IO Streams
        self.IO_COMMAND = ansi.RESET + ansi.FORE_CYAN  # Streams to command line
        self.IO_STDOUT = ansi.RESET + ansi.FORE_GREEN  # Streams from command line
        self.IO_STDERR = ansi.RESET + ansi.FORE_RED  # Streams from command line
        
        # Console explorer box
        self.CX_BORDER = ansi.RESET + ansi.FORE_BLUE
        self.CX_HEADING = ansi.RESET + ansi.BACK_BLUE + ansi.FORE_WHITE
        self.CX_VALUE = ansi.RESET + ansi.DIM
        self.CX_CLASS = ansi.RESET + ansi.FORE_BRIGHT_BLACK
        self.CX_SPACER_1 = ansi.RESET + ansi.FORE_BRIGHT_BLACK + ansi.DIM
        self.CX_SPACER_2 = ansi.RESET + ansi.FORE_YELLOW + ansi.DIM
        
        # Startup banner
        self.BANNER_ZERO = ansi.RESET + ansi.FORE_BLUE + ansi.BACK_BLUE
        self.BANNER_MAIN = ansi.RESET + ansi.FORE_BLUE + ansi.BACK_YELLOW
        self.BANNER_REVERSED = ansi.RESET + ansi.FORE_YELLOW + ansi.BACK_BLUE
        self.BANNER_END_OF_THE_LINE = ansi.RESET + ansi.FORE_BLUE
        self.BANNER_COMMAND_NAME = ansi.RESET + ansi.FORE_RED + ansi.BACK_YELLOW
        
        # Query
        self.QUERY_PREFIX = ansi.RESET + ansi.FORE_WHITE + ansi.BACK_BLUE
        self.QUERY_MESSAGE = ansi.RESET + ansi.FORE_MAGENTA
        self.QUERY_OPTION = ansi.RESET + ansi.FORE_YELLOW
        self.QUERY_BORDER = ansi.RESET + ansi.FORE_BRIGHT_BLACK
        self.QUERY_PROMPT = ansi.RESET + ansi.FORE_YELLOW
        
        # Progress bars
        self.PROGRESS_SIMPLE = ansi.RESET + ansi.FORE_CYAN
        self.PROGRESS_CHAR_COLUMN_SEPARATOR = ansi.RESET
        self.PROGRESS_COLOUR_PROGRESS_SIDE = ansi.RESET + ansi.FORE_BRIGHT_BLACK + ansi.BACK_LIGHT_BLUE + ansi.DIM
        self.PROGRESS_COLOUR_TITLE_COLUMN = ansi.RESET + ansi.FORE_BLACK + ansi.BACK_LIGHT_GREEN
        self.PROGRESS_COLOUR_CURRENT_COLUMN = ansi.RESET + ansi.FORE_BLACK + ansi.BACK_LIGHT_BLUE
        self.PROGRESS_COLOUR_TIME_COLUMN = ansi.RESET + ansi.FORE_BLACK + ansi.BACK_LIGHT_BLUE + ansi.DIM
        self.PROGRESS_COLOUR_PROGRESS_POINT = ansi.RESET + ansi.BACK_WHITE + ansi.FORE_BLACK
        self.PROGRESS_COLOUR_PROGRESS_SPACE_RIGHT = ansi.RESET + ansi.BACK_WHITE + ansi.FORE_BRIGHT_BLACK
        
        self.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY = []
        self.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( ansi.RESET + ansi.BACK_RED + ansi.FORE_BRIGHT_RED )
        self.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( ansi.RESET + ansi.BACK_GREEN + ansi.FORE_BRIGHT_GREEN )
        self.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( ansi.RESET + ansi.BACK_BLUE + ansi.FORE_BRIGHT_BLUE )
        self.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( ansi.RESET + ansi.BACK_CYAN + ansi.FORE_BRIGHT_CYAN )
        self.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( ansi.RESET + ansi.BACK_MAGENTA + ansi.FORE_BRIGHT_MAGENTA )
        self.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( ansi.RESET + ansi.BACK_YELLOW + ansi.FORE_BRIGHT_YELLOW )
        
        # Colour progression
        self.PROGRESSION_FORE = [ansi.FORE_RED,
                                 ansi.FORE_GREEN,
                                 ansi.FORE_YELLOW,
                                 ansi.FORE_BLUE,
                                 ansi.FORE_MAGENTA,
                                 ansi.FORE_CYAN,
                                 ansi.FORE_BRIGHT_RED,
                                 ansi.FORE_BRIGHT_GREEN,
                                 ansi.FORE_BRIGHT_BLUE,
                                 ansi.FORE_BRIGHT_MAGENTA,
                                 ansi.FORE_BRIGHT_CYAN]
        
        self.PROGRESSION_BACK = [ansi.BACK_RED,
                                 ansi.BACK_GREEN,
                                 ansi.BACK_YELLOW,
                                 ansi.BACK_BLUE,
                                 ansi.BACK_MAGENTA,
                                 ansi.BACK_CYAN,
                                 ansi.BACK_BRIGHT_RED,
                                 ansi.BACK_BRIGHT_GREEN,
                                 ansi.BACK_BRIGHT_BLUE,
                                 ansi.BACK_BRIGHT_MAGENTA,
                                 ansi.BACK_BRIGHT_CYAN]
        
        self.PROGRESSION_COUNT = len( self.PROGRESSION_FORE )


Theme = __ThemeClass()
