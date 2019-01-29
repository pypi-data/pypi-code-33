from mhelper import file_helper

import sys

from sxsxml.sxs.base import SxsWriter
from sxsxml.support import XsProgress


class SxsHtmlWriter( SxsWriter ):
    """
    Writes HTML from an SXS stream.
    """
    PROGRESS_PREFIX = "<progress "
    PROGRESS_SUFFIX = ">"
    BASIC_CSS = """
    span.verbose
    {
    color: #C0C0C0;
    }
    
    span.progress_l
{
    position: absolute;
    left: 0px;
    background: #2196F3; 
    height:100%;
}

span.progress_r
{
    position: absolute;
    right: 0px;
}

span.progress_c
{
    position: absolute;
    left: 0px;
    width:100%;
    height:100%;
    text-align: center;
}

div.progress
{
    position: relative;
    background: white;
    width: 100%;
    height:16px;
    border: 1px solid silver;
    border-radius: 4px;
}

div.section
{
}

div.question
{
    style:"background: #FFFFE0";
}

a.answer
{
}

span.key
{
    font-weight : bold;
}

span.value
{
    font-style: italic;
}

span.code
{
    font-family: monospace;
}

a.file
{
    font-family: monospace;
}

span.error
{
    background: red; 
    color: white;
}

span.warning
{
    background: yellow; 
    color: black
}

span.positive
{
    color: green;
}

span.negative
{
    color: red;
}

span.neutral
{
    color: brown;
}

a.command
{
    font-family: monospace;
}
"""
    
    
    def __init__( self, out = sys.__stdout__.write, scripted = True ):
        super().__init__( out = out )
        self.progress_bars = set()
        self.last_eol = False
        self.scripted = scripted
    
    
    def on_format_text( self, x ):
        x = x.replace( "\n", "<br/>\n" )
        self.last_eol = x.endswith( "\n" )
        
        return x
    
    
    def on_format_heading( self, level, name ):
        if name:
            return '<div class="section"><h{0}>{1}</h{0}>'.format( level, name )
        else:
            return '<div style="section">'
    
    
    def _exit_default( self ):
        self.on_text( "!!Unknown element '{}'!!{}".format( self.element.name, self.pop() ) )
    
    
    def on_format_section_end( self ):
        return "</div>\n"
    
    
    def on_consume_eol( self ):
        pass
    
    
    def on_format_progress( self, p: XsProgress ):
        self.ignore_next_eol()
        
        i = p.id.replace( " ", "_" )
        
        if self.scripted:
            if i in self.progress_bars:
                # Bar exists - update it
                r = self.__mk_progress_bar_update_script( i, p )
            else:
                # Create a new bar
                self.progress_bars.add( i )
                r = self.__mk_progress_bar( i, p )
        else:
            if i in self.progress_bars:
                # Bar exists - update it
                self.progress_bars.add( i )
                r = "{}0 {} {}{}".format( self.PROGRESS_PREFIX, 1 if p.is_end else 0, i, self.PROGRESS_SUFFIX ) + self.__mk_simple_progress_bar( p )
            else:
                # Create a new bar
                self.progress_bars.add( i )
                r = "{}1 {} {}{}".format( self.PROGRESS_PREFIX, 1 if p.is_end else 0, i, self.PROGRESS_SUFFIX ) + self.__mk_simple_progress_bar( p )
        
        if p.is_end:
            self.progress_bars.remove( i )
        
        return r
    
    
    def __mk_progress_bar_update_script( self, i, p ):
        return ('<script>\n'
                'document.getElementById("{0}_l").style.width="{1}%";\n'
                'document.getElementById("{0}_l").innerHTML="{2}";\n'
                'document.getElementById("{0}_r").innerHTML="{3}";\n'
                'document.getElementById("{0}_c").innerHTML="{4}";\n'
                '</script>\n').format( i, p.percent, p.value, p.max, self.__get_progress_text( p ) )
    
    
    def __mk_progress_bar( self, i, p ):
        return ('<div class="progress">\n'
                '<span id="{0}_l" style="width:{1}%" class="progress_l">\n'
                '{2}\n'
                '</span>\n'
                '<span id="{0}_r" class="progress_r">\n'
                '{3}\n'
                '</span>\n'
                '<span id="{0}_c" class="progress_c">\n'
                '{4}\n'
                '</span>\n'
                '</div>\n').format( i, p.percent, p.value, p.max, self.__get_progress_text( p ) )
    
    
    def __get_progress_text( self, p ):
        return self.section_name + ": " + ("done" if p.is_end else p.text)
    
    
    def __mk_simple_progress_bar( self, p ):
        return "<span class='progress'>{}/{} = {}%</span>".format( p.value, p.max, p.percent, self.__get_progress_text( p ) )
    
    
    def on_format_question( self, question, options ):
        if not options:
            options = ("*",)
        
        return (
            '<div class="question">'
            '<p>{}</p>'
            '<p>'
            '{}'
            '</p>'
            '</div>\n').format( question, " ".join( ('[<a class="answer" href="{0}">{0}</a>]'.format( x ) for x in options) ) )
    
    
    def on_format_table( self, rows ):
        return (
            '<table>'
            '{}'
            '</table>').format(
                "".join( "<tr>{}</tr>".format(
                        "".join( "<td>{}</td>".format( cell ) for cell in row ) ) for row in rows ) )
    
    
    def on_format_hr( self ):
        return "<hr/>"
    
    
    def on_format_italic( self, x ):
        return '<i>{}</i>'.format( x )
    
    
    def on_format_key( self, x ):
        return '<span class="key">{}</span>'.format( x )
    
    
    def on_format_value( self, x ):
        return '<span class="value">{}</span>'.format( x )
    
    
    def on_format_file( self, x ):
        return '<a class="file" href="{}">{}</a>'.format( x, file_helper.get_filename( x ) )
    
    
    def on_format_code( self, x ):
        return '<span class="code">{}</span>'.format( x )
    
    
    def on_format_error( self, x ):
        return '<span class="error">{}</span>'.format( x )
    
    
    def on_format_warning( self, x ):
        return '<span class="warning">{}</span>'.format( x )
    
    
    def on_formatted_progress( self, p: XsProgress ):
        pass
    
    
    def on_format_positive( self, x ):
        return '<span class="positive">{}</span>'.format( x )
    
    
    def on_format_negative( self, x ):
        return '<span class="negative">{}</span>'.format( x )
    
    
    def on_format_neutral( self, x ):
        return '<span class="neutral">{}</span>'.format( x )
    
    
    def on_format_command( self, x ):
        return '<a class="command" href="{0}">{0}</a>'.format( x )
    
    
    def on_format_verbose( self, x ):
        return '<span class="verbose">{}</span>'.format( x )
    
    
    def on_format_list( self, rows, ordered ):
        return "<{0}>{1}</{0}>".format( "ol" if ordered else "ul", "<li>{}</li>".format( x for x in rows ) )
