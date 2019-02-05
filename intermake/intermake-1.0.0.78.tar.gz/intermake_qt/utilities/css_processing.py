from typing import Set

from mhelper import file_helper

import os.path


def load_css( file_name ):
    """
    PACKAGE-SCOPE (though it is used externally once, for debugging)
    
    Loads and preprocesses an application style-sheet.
    
    * The style sheet may specify a variant by including a `#VARIANT` after the
      filename, eg. `c:\my_style.css#VARIENT_FOUR`.
    * The source CSS is preprocessed and allows the special commands documented
      in the resource `:/intermake/default_css.css`.
    
    :param file_name:   Name of file or resource to load or blank to use the
                        default.
                        
    :returns:           CSS content
    
    """
    if not file_name:
        file_name = ":/intermake/default_css.css"
        
    if "#" in file_name:
        file_name, section = file_name.split( "#", 1 )
    else:
        section = "default"
    
    if file_name.startswith( ":" ):
        from PyQt5 import QtCore
        resource_stream = QtCore.QFile( file_name )
        
        if resource_stream.open( QtCore.QIODevice.ReadOnly | QtCore.QFile.Text ):
            file_content = QtCore.QTextStream( resource_stream ).readAll()
            resource_stream.close()
        else:
            raise ValueError( "The specified CSS «{}» doesn't exist in the resource stream.".format( file_name ) )
    elif not os.path.isfile( file_name ):
        raise ValueError( "The specified CSS «{}» doesn't exist on disk.".format( file_name ) )
    else:
        file_content = file_helper.read_all_text( file_name )
    
    return __preprocess_css( file_content, section )


def parse_css( source: str ):
    """
    PACKAGE-SCOPE
    
    Returns a key-value dictionary from a style-sheet.
    
    :param source: CSS content
    :return:        Dictionary of:
                        key   : str = Attribute name and section name as a string `section.attribute`
                        value : str = Value 
    """
    
    stage = 0
    title = None
    r = { }
    
    for line in source.split( "\n" ):
        if not stage:
            if "{" in line:
                stage = True
            else:
                title = [x.strip() for x in line.split( "," )]
        elif stage:
            if "}" in line:
                stage = False
            else:
                key, value = (x.strip( "; " ) for x in line.split( ":", 1 ))
                
                for key2 in title:
                    r[key2 + "." + key] = value
    
    return r


def __preprocess_css( source: str, variant: str, variant_receiver: Set[str] = None ) -> str:
    """
    FILE-SCOPE
    
    Preprocesses CSS source given the functionality listed in the comments in `:/intermake/default_css.css`.
    
    :param source:              CSS source
    :param variant:             Variant. 
    :param variant_receiver:    Optional set to receive the list of available variants
    :return:                    Preprocessed CSS. 
    """
    
    lookup_table = []
    r = []
    condition = True
    
    if variant_receiver is None:
        variant_receiver = set()
    
    for line in source.split( "\n" ):
        for k, v in lookup_table:
            line = line.replace( k, v )
        
        if line.startswith( "#" ):
            elements = line[1:].split( " " )
            elements = [x.strip() for x in elements]
            elements = [x for x in elements if x]
            name = elements[0].upper()
            
            if name == "DEFINE":
                lookup_table.append( (elements[1], elements[2]) )
            elif name == "WHEN":
                attrs = set( x.upper() for x in elements[1:] )
                variant_receiver.update( attrs )
                condition = variant.upper() in attrs
        elif condition:
            r.append( line )
    
    return "\n".join( r )
