import re
from typing import Sequence, List, Optional, Callable, Pattern

import os

import intermake.helpers.printing as pr
from mhelper import async_helper, SubprocessError


DStrReceiver = Callable[[str], None]


class __SubprocessRun:
    def __init__( self,
                  title: str,
                  garbage: List[Pattern],
                  collect_stdout: Optional[DStrReceiver],
                  collect_stderr: Optional[DStrReceiver],
                  hide: bool,
                  trace: bool,
                  end: str ):
        self.garbage = garbage
        self.collect_stdout = collect_stdout
        self.collect_stderr = collect_stderr
        self.is_blank = [True, True]
        self.hide = hide
        self.trace = [] if trace else None
        self.end = end
        
        if hide:
            self.action = pr.pr_action( title ).__enter__()
    
    
    def close( self ):
        if self.hide:
            self.action.__exit__( None, None, None )
    
    
    def __print_( self, text, stream, stream_index ):
        if self.trace is not None:
            self.trace.append( text )
        
        if self.hide:
            self.action.increment()
            return
        
        if any( y.search( text ) for y in self.garbage ):
            return
        
        if not text:
            if self.is_blank[stream_index]:
                return
            
            self.is_blank[stream_index] = True
        else:
            self.is_blank[stream_index] = False
        
        pr.printx( "<{0}>{1}</{0}>".format( stream, pr.escape( text ) ) )
    
    
    def print_1( self, x ):
        self.__print_( x, "stdout", 0 )
        if self.collect_stdout is not None:
            self.collect_stdout( x + self.end )
    
    
    def print_2( self, x ):
        self.__print_( x, "stderr", 1 )
        if self.collect_stderr is not None:
            self.collect_stderr( x + self.end )


def run_subprocess( command: Sequence[str],
                    *,
                    garbage: Optional[List[str]] = None,
                    collect: Optional[DStrReceiver] = None,
                    collect_stdout: Optional[DStrReceiver] = None,
                    collect_stderr: Optional[DStrReceiver] = None,
                    hide: bool = False,
                    trace: bool = None,
                    stdin: str = None,
                    no_err: bool = False,
                    end: str = "" ) -> int:
    """
    Runs the specified subprocess
    
    :param end:                 Appended to end of lines.
                                Normally `""` assuming `collect` writes to a list,
                                but may be `"\n"` if writing to a file, etc.
    :param no_err:              When set, no SubprocessError is raised.
    :param trace:               When set, STDOUT and STDERR are retained internally.
                                On error, these will displayed to the user.
                                The default value `None`, turns this on if `hide` is set.
    :param stdin:               Standard input (as a UTF-8 string)
    :param collect_stderr:      Function to receive std-err.
    :param collect:             Overrides both `collect_stderr` and `collect_stdout`.  
    :param hide:                Hide output (displays progress bar instead) 
    :param collect_stdout:      Function to receive std-out.
                                e.g. `my_list.append`.
    :param command:             Commands and arguments
    :param garbage:             List containing one or more regex that specify lines
                                dropped from display. This affects the inline display only and
                                does not affect the `trace` or `collect_*` parameters. 
    """
    #
    # Default arguments
    #
    if garbage is None:
        garbage: List[str] = []
    
    if trace is None:
        trace = hide
    
    if collect is not None:
        collect_stdout = collect
        collect_stderr = collect
    
    #
    # Compile garbage regex
    #
    garbage: List[Pattern] = [re.compile( x ) for x in garbage]
    
    #
    # Run the process
    #
    spr = __SubprocessRun( " ".join( command ), garbage, collect_stdout, collect_stderr, hide, trace, end )
    
    try:
        return async_helper.async_run( command, spr.print_1, spr.print_2, check = True, stdin = stdin )
    except SubprocessError as ex:
        if no_err:
            return ex.return_code
        
        pr.printx( "<error>")
        pr.printx("*** AN ERROR OCCURRED ***" )
        pr.printx( "Command  : {}",  command ) 
        pr.printx( "Exception: {}", ex ) 
        pr.printx( "Directory: {}", os.getcwd() )
        
        if stdin:
            pr.printx( "*** DUMPING THE INPUT DATA BECAUSE AN ERROR OCCURRED ***" )
            for index, line in enumerate( stdin.split( "\n" ) ):
                pr.printx( "LINE {}: {} ", index, line )
            
            pr.printx( "*** END OF INPUT ***" )
        
        if spr.trace is not None:
            pr.printx( "*** DUMPING THE BUFFERED OUTPUT DATA BECAUSE AN ERROR OCCURRED ***" )
            for index, line in enumerate( spr.trace ):
                pr.printx( "LINE {}: {} ", index, line ) 
            
            pr.printx( "*** END OF OUTPUT ***" )
        
        raise
    finally:
        spr.close()
