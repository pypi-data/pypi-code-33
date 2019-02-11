class Chibi_path( str ):
    def __new__( cls, *args, **kw ):
        return str.__new__( cls, *args, **kw )


    def  __add__( self, other ):
        from chibi.file.snippets import join, is_a_file
        if isinstance( other, self.__class__ ):
            if self.is_a_file:
                return self.dir_name + other

            return self.__class__( join( str( self ), str( other ) ) )
        if isinstance( other, str ):
            return self + self.__class__( other )

    @property
    def is_a_folder( self ):
        from chibi.file.snippets import join, is_a_folder
        return is_a_folder( self )

    @property
    def is_a_file( self ):
        from chibi.file.snippets import is_a_file
        return is_a_file( self )

    @property
    def dir_name( self ):
        from chibi.file.snippets import file_dir
        return self.__class__( file_dir( self ) )

    def open( self ):
        if self.is_a_folder:
            raise NotImplementedError
        from . import Chibi_file
        return Chibi_file( self )
