import intermake

# This is here to avoid cyclic dependencies

class IGuiMainWindow:
    def command_completed( self, result: intermake.Result ) -> None:
        """
        The derived class should respond to the command's completion.
        """
        raise NotImplementedError( "abstract" )
    
    
    def return_to_console( self ) -> bool:
        raise NotImplementedError( "abstract" )