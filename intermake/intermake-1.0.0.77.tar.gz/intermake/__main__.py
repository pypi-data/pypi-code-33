"""
Intermake is a library, not an application.

This is a sample intermake application contained entirely in one file:
    __file__

It doesn't have any features beyond the intermake core commands and one custom
command, `show`, which shows its source code.

But it's well documented so you can use it as a template for your own
applications.
"""


def main() -> None:
    """
    Entry point
    """
    
    # Print the welcome message
    print( __doc__.replace( "__file__", __file__ ) )
    
    # Setup intermake
    # - Normally we'd put the following in __init__.py, so if we're importing
    #   this as a library, we'd still set up our environment correctly
    #   However, as we're self contained, we do it here.
    
    # First we import intermake!
    import intermake as im
    
    # Now we define our environment
    # - set the name (title bar)
    # - and the short-name (prompt, folder names, etc)
    # - and set the version (we just use Intermake's own version here, you
    #   should define your own)
    app = im.Application( name = "sample",
                          version = im.__version__ )
    
    
    # If we were a proper application, we'd import our own modules here, which
    # would define some `@command` decorated functions, but as we're stand-alone
    # we'll just define one here, that shows the contents of this file
    @app.command
    def show_file( comments: bool = False ) -> None:
        """
        Shows the contents of the source file.
        
        :param comments: Whether to show comments
        """
        with open( __file__ ) as in_:
            lines = in_.readlines()
        
        is_doc = False
        
        for i, line in enumerate( lines ):
            if line.strip() == '"""':
                is_doc = not is_doc
                if not comments:
                    continue
            
            if not comments and (is_doc or line.lstrip().startswith( "#" )):
                continue
            
            im.pr.printx( "[{}] {}", i, line.rstrip() )
    
    
    # Finally, launch the UI.
    app.start()


# Standard Python boilerplate code follows
# This allows the `main` function to run if the user types `python -m intermake`
# instead of `intermake`, but stops it running if someone, for some reason,
# typed `from intermake import __main__`
if __name__ == "__main__":
    main()
