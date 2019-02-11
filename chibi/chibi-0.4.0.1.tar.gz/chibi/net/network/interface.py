from chibi.atlas import Chibi_atlas


class Network( Chibi_atlas ):

    def up( self ):
        raise NotImplementedError

    def down( self ):
        raise NotImplementedError


class Wireless( Network ):
    pass
