import mmap
import fleep

from chibi.file.snippets import (
    current_dir, exists, stat, check_sum_md5, read_in_chunks, copy
)


class Chibi_file:
    def __init__( self, file_name ):
        self._file_name = file_name
        self._current_dir = current_dir()
        if not self.exists:
            self.touch()
        self.reread()

    @property
    def file_name( self ):
        return self._file_name

    @property
    def dir( self ):
        return self._current_dir

    @property
    def is_empty( self ):
        return self.properties.size == 0

    @property
    def properties( self ):
        prop = stat( self.file_name )
        with open( self.file_name, 'rb' ) as f:
            info = fleep.get( f.read( 128 ) )

        prop.type = info.type[0] if info.type else None
        prop.extension = info.extension[0] if info.extension else None
        prop.mime = info.mime[0] if info.mime else None
        return prop

    def __del__( self ):
        try:
            self._file_content.close()
        except AttributeError:
            pass

    def find( self, string_to_find ):
        if isinstance( string_to_find, str ):
            string_to_find = string_to_find.encode()
        return self._file_content.find( string_to_find )

    def reread( self ):
        try:
            with open( self._file_name, 'r' ) as f:
                self._file_content = mmap.mmap(
                    f.fileno(), 0, prot=mmap.PROT_READ )
        except ValueError as e:
            if not str( e ) == 'cannot mmap an empty file':
                raise

    def __contains__( self, string ):
        return self.find( string ) >= 0

    def append( self, string ):
        with open( self._file_name, 'a' ) as f:
            f.write( string )
        self.reread()

    @property
    def exists( self ):
        return exists( self.file_name )

    def touch( self ):
        open( self.file_name, 'a' ).close()

    def copy( self, dest ):
        copy( self.file_name, dest )

    def chunk( self, chunk_size=4096 ):
        return read_in_chunks( self.file_name, 'r', chunk_size=chunk_size )

    def check_sum_md5( self, check_sum ):
        return check_sum_md5( self.file_name, check_sum )
