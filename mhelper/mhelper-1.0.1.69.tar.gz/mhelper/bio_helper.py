import re
from io import StringIO
from typing import Iterator, Tuple


_BIOPYTHON_FIX = re.compile( "([0-9.]+):[0-9.]+" )


def convert_file( in_filename, out_filename, in_format, out_format ):
    from Bio import AlignIO
    
    with open( in_filename, "rU" ) as input_handle:
        with open( out_filename, "w" ) as output_handle:
            alignments = AlignIO.parse( input_handle, in_format )
            AlignIO.write( alignments, output_handle, out_format )


def parse_phylip( *, text = None, file = None, lines = None, ignore_num_seq: bool = False ) -> Iterator[Tuple[str, str]]:
    """
    Same as :function:`parse_fasta`, but for PHYLIP.
    """
    lines = __read_file( file, text, lines )
    
    heading = [x for x in lines[0].split( " " ) if x]
    count = int( heading[0] )
    length = int( heading[1] )
    num = 0
    
    for index, line in enumerate( lines[1:] ):
        if not line:
            continue
        
        if "\t" not in line:
            raise ValueError( "This PHYLIP file is invalid because I don't understand the line #«{}», «{}»".format( index, line ) )
        
        name, value = line.split( "\t", 1 )
        name = name.strip()
        value = value.strip()
        
        if len( value ) != length:
            raise ValueError( "This PHYLIP file is invalid because sequence #«{}» («{}») is «{}» sites long but the header stipulates «{}» sites.".format( index, name, len( value ), length ) )
        
        num += 1
        yield name, value
    
    if not ignore_num_seq and num != count:
        raise ValueError( "This PHYLIP file is invalid because it contains «{}» sequences but the header stipulates «{}».".format( num, count ) )


def parse_fasta( *, text = None, file = None, lines = None ) -> Iterator[Tuple[str, str]]:
    """
    Parses a FASTA file.
    Accepts multi-line sequences.
    Accepts ';' comments in the file.
    
    Nb. BioPython's SeqIO.parse doesn't handle comments for FASTA.
    
    :param text:    FASTA text 
    :param file:    Path to FASTA file 
    :param lines:   FASTA lines
    :return:        Tuples of sequence names and sites 
    """
    lines = __read_file( file, text, lines )
    
    heading = None
    sequence = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith( ">" ):
            if heading is not None:
                yield heading, "".join( sequence )
            
            heading = line[1:]
            sequence = []
        elif not line.startswith( ";" ):
            sequence.append( line )
    
    if heading is not None:
        yield heading, "".join( sequence )


def __read_file( file, text, lines ):
    if file is not None:
        if text is not None:
            raise ValueError( "Cannot specify both :param:`file` and :param:`text` to :function:`__read_file`." )
        
        if lines is not None:
            raise ValueError( "Cannot specify both :param:`file` and :param:`lines` to :function:`__read_file`." )
        
        from mhelper import file_helper
        result = file_helper.read_all_lines( file )
    elif text is not None:
        if lines is not None:
            raise ValueError( "Cannot specify both :param:`text` and :param:`lines` to :function:`__read_file`." )
        
        result = text.split( "\n" )
    elif lines is not None:
        result = lines
    else:
        raise ValueError( "Must specify either :param:`file`, :param:`text` or :param:`lines` when calling :function:`__read_file`." )
    
    if not result:
        raise ValueError( "Cannot read the file because there is no data. file = «{}», text = «{}», lines = «{}»".format( file, text, lines ) )
    
    return result


def biotree_to_newick( tree) -> str:
    from Bio.Phylo.BaseTree import Tree
    tree:Tree

    handle = StringIO()
    Phylo.write( [tree], handle, "newick" )
    result = handle.getvalue()
    
    # Work around stupid BioPython bug
    # https://github.com/biopython/biopython/issues/1315
    # TODO: Remove this fix when the issue is fixed
    result = _BIOPYTHON_FIX.sub( "\\1", result )
    
    return result


def newick_to_biotree( newick ):
    from Bio import Phylo
    from Bio.Phylo.BaseTree import Tree
    handle = StringIO( newick )
    r:Tree =Phylo.read( handle, "newick" )
    return r
