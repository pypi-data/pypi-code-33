"""
Things for dealing with filenames
"""
import shutil
import warnings
from os import path
import os

import errno
from typing import Iterable, List, Optional, Union, Sequence

from mhelper.special_types import NOT_PROVIDED
from mhelper import array_helper

from os.path import exists

def incremental_name( file: str, *, zero = "", number = "-{}" ) -> str:
    """
    Finds the next available file or directory name.
    
    :param file:        File name template. Use `"{}"` for the number `format`.
                        If `"{}"` is not added, it is added before the extension.
    :param zero:        Format when the number is zero, by default this is `""`. `"{}"` is replaced with the number. 
    :param number:      Format when the number is more than zero, by default this is "-{}". `"{}"` is replaced with the number. 
    """
    import itertools
    
    if "{}" not in file:
        a, b = path.splitext( file )
        file = a + "{}" + b
    
    for n in itertools.count():
        file_name_2 = file.format( (number if n else zero).format( n ) )
        
        if not path.exists( file_name_2 ):
            return file_name_2


def read_all_text( file_name: str, default: Optional[str] = NOT_PROVIDED, *, details: str = None ) -> Optional[str]:
    """
    Reads all the text from a file, returning None if there is no file
    
    :param file_name: Path to file to read
    :param default:   Default value if file does not exist.
                      If `NOT_PROVIDED` then a `FileNotFoundError` is raised.
    :param details:   Appended to `FileNotFoundError` error message.
    :except FileNotFoundError: File does not exist. 
    """
    
    if not os.path.isfile( file_name ):
        if default is NOT_PROVIDED:
            raise FileNotFoundError( "Cannot read_all_text from file because the file doesn't exist: «{}».{}".format( file_name, (" Description of file: {}.".format( details )) if details else "" ) )
        
        return default
    
    with open( file_name, "r" ) as file:
        return file.read()


def get_subdirs( directory_name: str ) -> List[str]:
    results = []
    
    for file_name in os.listdir( directory_name ):
        full_name = os.path.join( directory_name, file_name )
        if path.isdir( full_name ):
            results.append( full_name )
    
    return results


def read_all_lines( file_name: str ) -> List[str]:
    """
    Reads all the text from a file.
    
    :except FileNotFoundError: File not found
    """
    
    if not os.path.isfile( file_name ):
        raise FileNotFoundError( "The file «{}» does not exist.".format( file_name ) )
    
    with open( file_name, "r" ) as file:
        return list( x.rstrip( "\n" ) for x in file )


def write_all_text( file_name: object, text: Union[Sequence[str], str], newline: bool = False ) -> None:
    """
    Writes all text to a file, overwriting the existing content
    """
    
    if array_helper.is_simple_iterable( text ):
        text = "\n".join( text )
        
        if newline:
            text += "\n"
    
    with open( str( file_name ), "w" ) as file:
        file.write( text )


def contains_files( directory: str, ext: str ) -> bool:
    """
    Returns if the directory contains any files.
    """
    ext = ext.upper()
    
    for root, dirs, files in os.walk( directory ):
        for file in files:
            if file.upper().endswith( ext ):
                return True
    
    return False


def get_file_name( full_path: str ) -> str:
    """
    Returns <FILE><EXT> from <PATH><FILE><EXT>
    `a/b/c.d` --> `c.d`
    """
    return path.split( full_path )[1]


def replace_extension( file_name: str, new_extension: str ) -> str:
    """
    Replaces <EXT> in <PATH><FILE><EXT>
    `a/b/c.d` <-- `d`
    """
    return path.splitext( file_name )[0] + new_extension


def get_extension( file_name: str ) -> str:
    """
    Returns <EXT> in <PATH><FILE><EXT>. Note this includes the ".".
    `a/b/c.d` --> `.d`
    """
    return path.splitext( file_name )[1]


def get_filename( file_name: str ) -> str:
    """
    Returns <FILE><EXT> in <PATH><FILE><EXT>
    `a/b/c.d` --> `c.d`
    """
    return path.split( file_name )[1]


def get_filename_without_extension( file_name: str ) -> str:
    """
    Returns <FILE> from <PATH><FILE><EXT>
    `a/b/c.d` --> `c`
    """
    file_name = path.split( file_name )[1]
    file_name = path.splitext( file_name )[0]
    return file_name


def get_full_filename_without_extension( file_name: str ) -> str:
    """
    Returns <PATH><FILE> from <PATH><FILE><EXT>
    `a/b/c.d` --> `a/b/c`
    """
    return path.splitext( file_name )[0]


def replace_filename_without_extension( file_name: str, new_name: str ) -> str:
    """
    Replaces <NAME> in <PATH><NAME><EXT>
    `a/b/c.d` <-- `c`
    """
    return path.join( get_directory( file_name ), new_name + get_extension( file_name ) )


def replace_directory( file_name: str, new_directory: str ) -> str:
    """
    Replaces ``<PATH>`` in ``<PATH><NAME><EXT>``.
    
    :param file_name:        ``<PATH><NAME><EXT>``
    :param new_directory:    New ``<PATH>``
    """
    return path.join( new_directory, get_filename( file_name ) )


def format_path( file_name: str, format: str ) -> str:
    """
    Formats a file name to a new name from ``<DIR><NAME><EXT>``.
    
    :param file_name:       Input 
    :param format:          Format:
                                {D} = Directory
                                {F} = {N}{E}
                                {N} = Name
                                {E} = Extension 
    :return: New name
    """
    directory, file = path.split( file_name )
    name, extension = path.splitext( file )
    
    x = format
    x = x.replace( "{D}", directory )
    x = x.replace( "{N}", name )
    x = x.replace( "{E}", extension )
    x = x.replace( "{F}", file )
    
    return x


def replace_filename( file_name: str, new_name: str ):
    """
    Replaces ``<NAME><EXT>`` in ``<PATH><NAME><EXT>``
    ``a/b/c.d`` --> ``c.d``
    
    :param file_name:   Path to original file 
    :param new_name:    New ``<NAME><EXT>``
    """
    return path.join( get_directory( file_name ), new_name )


def join( *args, **kwargs ):
    """
    Just calls path.join
    """
    return path.join( *args, **kwargs )


def get_directory_name( file_name: str ) -> str:
    return get_filename( get_directory( file_name ) )


def get_directory( file_name: str, up = 1 ) -> str:
    """
    Returns <PATH> in <PATH><NAME><EXT>
    """
    for _ in range( up ):
        file_name = path.split( file_name )[0]
    
    return file_name


def suffix_directory( file_name: str ) -> str:
    if file_name.endswith( path.sep ):
        return file_name
    else:
        return file_name + path.sep


def relocate( target_files: Iterable[str], new_folder: str, locate: bool ) -> None:
    """
    Given a list of files, creates a set of symbolic links to them in another folder. 
    :param target_files: List of files (complete paths unless locate is False, in which case they can be partial paths) 
    :param new_folder: Folder to create links in or remove links from  
    :param locate: Whether to create links (True) or remove them (False) 
    """
    for file in target_files:
        name = get_file_name( file )
        new_name = path.join( new_folder, name )
        
        if locate:
            os.link( file, new_name )
        else:
            os.unlink( new_name )


def split_path( path_: str ) -> List[str]:
    """
    Splits a name into its folders and file
    """
    
    folders = []
    
    while 1:
        path_, folder = os.path.split( path_ )
        
        if folder != "":
            folders.append( folder )
        else:
            if path_ != "":
                folders.append( path_ )
            break
    
    folders.reverse()
    
    return folders


def list_sub_dirs( directory: str, recurse : bool = False ) -> List[str]:
    """
    Lists the subdirectories as absolute paths.
    """
    if recurse:
        result = []
        for a, b, c in os.walk( directory ):
            if a != directory:
                result.append(a)
        return result
    else:
        return [x for x in list( path.join( directory, x ) for x in os.listdir( directory ) ) if os.path.isdir( x )]


def list_dir( directory: str, filter: str = None, recurse: bool = False ) -> List[str]:
    """
    Lists the contents of a directory as absolute filenames.
    Note that the results do not include directories - use `list_sub_dirs` for that.
    
    :param directory:       Directory to list. 
    :param filter:          Filter on files (e.g. `".txt"`). Case insensitive.  
    :param recurse:         Recurse into subfolders. 
    :return:                List of absolute filenames. 
    """
    if recurse:
        result = []
        for folder, subfolders, files in os.walk( directory ):
            for file in files:
                result.append( path.join( folder, file ) )
    else:
        result = [x for x in list( path.join( directory, x ) for x in os.listdir( directory ) ) if os.path.isfile( x )]
    
    if filter:
        filter = filter.upper()
        result = [x for x in result if x.upper().endswith( filter )]
    
    return result


def is_windows() -> bool:
    """
    Returns if the current platform is Windows.
    """
    return os.name == "nt"


def default_extension( file_name: str, extension: str ) -> str:
    """
    Returns the `file_name` if it has any extension, otherwise adds the `extension`.
    """
    if not get_extension( file_name ):
        return file_name + extension
    
    return file_name


def create_directory( *args: str, overwrite: bool = False, new: bool = False ) -> str:
    """
    Creates a directory (doesn't do anything if it already exists).
    
    Note that `os.makedirs` seems to have an bug whereby it ignores the "exists_ok" flag (py. 3.6).
    
    :param new:             Fail if directory already exists.
    :param overwrite:       Delete any existing directory.
    :param args:            Args suitable for use with `path.join`.
    :return:                Directory passed in
    """
    
    output_directory = path.join( *args )
    
    if path.isdir( output_directory ):
        if new:
            raise FileExistsError( "Cannot create '{}' because it already exists.".format( output_directory ) )
        elif overwrite:
            shutil.rmtree( output_directory )
        else:
            return output_directory
    
    try:
        os.makedirs( output_directory )
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise FileNotFoundError( "Failed to create directory «{}» due to another error.".format( output_directory ) ) from exception
    
    if not path.isdir( output_directory ):
        raise FileNotFoundError( "Command returned success but the created directory cannot be found «{}».".format( output_directory ) )
    
    return output_directory


def line_count( file_name: str, line_start: Optional[str] = None ) -> int:
    """
    Counts the number of lines in a file, optionally those just starting "line_start"
    """
    
    c = 0
    
    with open( file_name ) as f:
        for line in f:
            if (not line_start) or (line.startswith( line_start )):
                c += 1
    
    return c


def safe_file_name( name ):
    name = str( name )
    name = name.replace( "<>:\"'/\\|?*", "_" )
    
    if not name:
        return "Untitled"
    else:
        return name


def recycle_file( file_name ):
    try:
        # noinspection PyPackageRequirements
        from send2trash import send2trash
        send2trash( file_name )
    except ImportError:
        warnings.warn( "The `send2trash` module is not installed so instead of sending the file '{}' to the recycle bin I am just going to delete it. Please install `send2trash` to avoid this warning in future.".format( file_name ), UserWarning )
        os.remove( file_name )


def get_last_directory_and_filename( file_name ):
    """
    From `a/b/c/d.e` gets `c/d.e` 
    """
    return path.join( get_filename( get_directory( file_name ) ), get_filename( file_name ) )


def delete_file( file_name: str ) -> bool:
    """
    Deletes the file, if it exists.
    :return: Was deleted
    """
    if path.isfile( file_name ):
        os.remove( file_name )
        return True
    
    return False

def delete_directory(file_name:str)->bool:
    if path.isdir(file_name):
        shutil.rmtree(file_name)
        return True
    
    return False


def home() -> str:
    """
    Returns the home directory.
    :return: 
    """
    return path.expanduser( "~" )  # TODO: Does this work on Windows?


def file_size( file_name: str ) -> int:
    """
    Size of a file, or -1 on error.
    """
    try:
        return os.stat( file_name ).st_size
    except:
        return -1


def highlight_file_name_without_extension( file, highlight, normal ):
    return normal + path.join( get_directory( file ), highlight + get_filename_without_extension( file ) + normal + get_extension( file ) )


def assert_working_directory():
    """
    Having a bad working directory causes weird problems with everything else, even getting a stack trace.
    Assert it exists before we do anything else.
    """
    try:
        os.getcwd()
    except Exception as ex:
        raise ValueError( "Cannot obtain the working directory. Check the current folder exists and try again." ) from ex


# region Deprecated

def file_len( file_name: str, line_start: Optional[str] = None ) -> int:
    warnings.warn( "DEPRECATED (3 aug 2018, misleading name) - use `line_count`", DeprecationWarning )
    return line_count( file_name, line_start )


def sequential_file_name( file_name: str ) -> str:
    """
    Generates a sequential file OR directory name.
    
    Avoids conflicts with existing filenames.
    
    :remarks:
    No multi-thread support - only acknowledges existing files.
    
    :param file_name: Format of filename, with * where the number goes.
    :return: Full filename
    """
    warnings.warn( "DEPRECATED (29 aug 2018, advanced version) - use `incremental_name`.", DeprecationWarning )
    
    if "*" not in file_name:
        raise ValueError( "`sequential_file_name` requires the filename to contain a placeholder '*' to represent the number, but the value provided «{}» does not.".format( file_name ) )
    
    number = 1
    
    result = file_name.replace( "*", str( number ) )
    
    while path.exists( result ):
        number += 1
        result = file_name.replace( "*", str( number ) )
    
    return result


# endregion

class FilePath:
    """
    :ivar path:     Full path to file           (D*NE)
    :ivar name:     Name of file                (NE)
    :ivar ext:      Extension of file           (E)
    :ivar dir:      Directory of file           (D*)
    :ivar dname:    Name of directory of file   (D[-1])
    :ivar bname:    Bare name of file           (N)
    """
    
    
    def __init__( self, path ):
        self.path = path
        self.name = get_file_name( path )
        self.ext = get_extension( path )
        self.dir = get_directory( path )
        self.dname = get_directory_name( path )
        self.bname = get_filename_without_extension( path )
    
    
    def __str__( self ):
        return self.path
    
    
    def __repr__( self ):
        return "{}({})".format( type( self ).__name__, repr( self.path ) )

