from mhelper import ansi, ansi_helper
from typing import Callable


__RENDERER_ANSI: Callable[[str], str] = None
__RENDERER_HTML: Callable[[str], str] = None
__RENDERER_SXS: Callable[[str], str] = None


def markdown_to_sxs( markdown: str ) -> str:
    if __RENDERER_SXS is None:
        __create_renderer_sxs()
    
    return __RENDERER_SXS( markdown )

def markdown_to_ansi( markdown: str, width: int = -1 ) -> str:
    if __RENDERER_ANSI is None:
        __create_renderer_ansi()
    
    __RENDERER_ANSI.width = width
    return __RENDERER_ANSI( markdown )


def markdown_to_html( markdown: str ) -> str:
    if __RENDERER_HTML is None:
        __create_renderer_html()
    
    return __RENDERER_HTML( markdown )


LF = "\n"


def __create_renderer_html():
    import mistune
    
    global __RENDERER_HTML
    __RENDERER_HTML = mistune.Markdown( renderer = mistune.Renderer() )


def __create_renderer_ansi():
    import mistune
    
    class Colour:
        def __init__( self, ts, te, ls, le ):
            self.ts = ts
            self.te = te
            self.ls = ls
            self.le = le
    
    
    class MarkdownRenderer( mistune.Renderer ):
        def __init__( self, **kwargs ):
            super().__init__( **kwargs )
            
            self.levels = [0] * 10
            self.level = 0
            self.prefix = ""
            
            DOFR = ansi.DIM_OFF + ansi.FORE_RESET
            self.level_colours = [Colour( ansi.FORE_WHITE + ansi.BACK_BLUE, ansi.FORE_RESET + ansi.BACK_RESET, ansi.DIM + ansi.FORE_BRIGHT_CYAN, DOFR ),
                                  Colour( ansi.FORE_MAGENTA, ansi.FORE_RESET, ansi.DIM + ansi.FORE_MAGENTA, DOFR ),
                                  Colour( ansi.FORE_BLUE, ansi.FORE_RESET, ansi.DIM + ansi.FORE_BLUE, DOFR ),
                                  Colour( ansi.FORE_RED, ansi.FORE_RESET, ansi.DIM + ansi.FORE_RED, DOFR ),
                                  Colour( ansi.FORE_RED, ansi.FORE_RESET, ansi.DIM + ansi.FORE_RED, DOFR ),
                                  Colour( ansi.FORE_RED, ansi.FORE_RESET, ansi.DIM + ansi.FORE_RED, DOFR )]
            self.width = -1
        
        
        def block_quote( self, text ):
            return ansi.FORE_RED + text + ansi.RESET + LF
        
        
        def __make_prefix( self, level ):
            self.prefix = "".join( x.ls + "│" + x.le + " " for x in self.level_colours[:level] )
        
        
        def header( self, text, level, raw = None ):
            self.levels[level - 1] += 1
            self.levels[level] = 0
            
            text = ".".join( str( i ) for i in self.levels[:level] ) + ". " + text
            
            self.__make_prefix( level - 1 )
            r = self.prefix + self.level_colours[level - 1].ls + "┌" + "─" * len( text ) + self.level_colours[level - 1].le + LF
            self.__make_prefix( level )
            r += self.prefix + self.level_colours[level - 1].ts + text + self.level_colours[level - 1].te + LF
            
            return r
        
        
        def hrule( self ):
            return self.prefix + ansi.DIM + "-" * (self.width if self.width > 0 else 80) + ansi.RESET
        
        
        def list( self, body, ordered = True ):
            if body.startswith( LF + self.prefix + "● " ):
                body = self.prefix + body
            
            body = body[0] + body[1:].replace( self.prefix + LF, LF )
            
            return body + LF
        
        
        def list_item( self, text ):
            r = []
            
            for line in text.split( "\n" ):
                if line.startswith( self.prefix ):
                    line = line[len( self.prefix ):]
                
                if not line:
                    continue
                
                if line.startswith( "● " ):
                    bl = "  "
                else:
                    bl = "● "
                
                r.append( LF + self.prefix + bl + line )
            
            return "".join( r )
        
        
        def paragraph( self, text ):
            r = []
            
            if self.width > 0:
                for line in ansi_helper.wrap( text, self.width ):
                    r.append( self.prefix + line + LF )
            else:
                for line in text.split( "\n" ):
                    r.append( self.prefix + line + LF )
            
            return "".join( r ) + self.prefix + LF
        
        
        def table( self, header, body ):
            return super().table( header, body )
        
        
        def table_row( self, content ):
            return content + LF
        
        
        def table_cell( self, content, **flags ):
            return content + "\t"
        
        
        def double_emphasis( self, text ):
            return ansi.FORE_BRIGHT_YELLOW + ansi.BOLD + text + ansi.BOLD_OFF + ansi.FORE_RESET
        
        
        def emphasis( self, text ):
            return ansi.FORE_BRIGHT_YELLOW + ansi.ITALIC + text + ansi.ITALIC_OFF + ansi.FORE_RESET
        
        
        def codespan( self, text ):
            return ansi.FORE_CYAN + text + ansi.FORE_RESET
        
        
        def linebreak( self ):
            return LF
        
        
        def strikethrough( self, text ):
            return ansi.STRIKETHROUGH + text + ansi.STRIKETHROUGH_OFF
        
        
        def text( self, text ):
            return text
        
        
        def escape( self, text ):
            return text
        
        
        def autolink( self, link, is_email = False ):
            return ansi.FORE_CYAN + ansi.UNDERLINE + link + ansi.UNDERLINE_OFF + ansi.FORE_RESET
        
        
        def link( self, link, title, text ):
            return ansi.FORE_CYAN + text + ansi.DIM + " (" + ansi.UNDERLINE + link + ansi.UNDERLINE_OFF + ")" + ansi.DIM_OFF + ansi.FORE_RESET
        
        
        def image( self, src, title, text ):
            return ansi.FORE_CYAN + title + ansi.DIM + " (" + ansi.UNDERLINE + src + ansi.UNDERLINE_OFF + ") " + ansi.DIM_OFF + ansi.FORE_RESET + text
        
        
        def inline_html( self, html ):
            return html
        
        
        def newline( self ):
            return LF
        
        
        def footnote_ref( self, key, index ):
            return ansi.FORE_CYAN + key + " [" + ansi.UNDERLINE + index + ansi.UNDERLINE_OFF + "] " + ansi.FORE_RESET
        
        
        def footnote_item( self, key, text ):
            return "[" + key + "] " + text
        
        
        def footnotes( self, text ):
            return text
        
        
        def block_code( self, code, lang = None ):
            r = []
            
            code = code.strip()
            
            if code.startswith( "`" ):
                code = code[1:]
            
            if code.endswith( "`" ):
                code = code[:-1]
            
            for line in code.split( "\n" ):
                r.append( self.prefix + ansi.DIM + "░░░" + ansi.DIM_OFF + ansi.FORE_CYAN + line + ansi.FORE_RESET + LF )
            
            return "".join( r ) + self.prefix + LF
    
    
    global __RENDERER_ANSI
    __RENDERER_ANSI = mistune.Markdown( renderer = MarkdownRenderer() )


def __create_renderer_sxs():
    import mistune
    
    class Colour:
        def __init__( self, ts, te, ls, le ):
            self.ts = ts
            self.te = te
            self.ls = ls
            self.le = le
    
    
    class MarkdownRenderer( mistune.Renderer ):
        def __init__( self, **kwargs ):
            super().__init__( **kwargs )
        
        
        def block_quote( self, text ):
            return "<verbose>{}</verbose>".format( text )
        
        
        def header( self, text, level, raw = None ):
            return "<heading level='{}'>{}</heading>\n".format( level, text )
        
        
        def hrule( self ):
            return "</hr>"
        
        
        def list( self, body, ordered = True ):
            return "<{1}>{0}</{1}>".format( body, "ol" if ordered else "ul" )
        
        
        def list_item( self, text ):
            return "<li>{}</li>".format( text )
        
        
        def paragraph( self, text ):
            return text  +"\n\n"
        
        
        def table( self, header, body ):
            return "<table>{}</table>".format( body )
        
        
        def table_row( self, content ):
            return "<tr>{}</tr>".format( content )
        
        
        def table_cell( self, content, **flags ):
            return "<td>{}</td>".format( content )
        
        
        def double_emphasis( self, text ):
            return "<b>{}</b>".format( text )
        
        
        def emphasis( self, text ):
            return "<i>{}</i>".format( text )
        
        
        def codespan( self, text ):
            return "<code>{}</code>".format( text )
        
        
        def linebreak( self ):
            return "\n"
        
        
        def strikethrough( self, text ):
            return "STRIKE({})".format( text )
        
        
        def text( self, text ):
            return text
        
        
        def escape( self, text ):
            return text
        
        
        def autolink( self, link, is_email = False ):
            return link
        
        
        def link( self, link, title, text ):
            return "LINK({}; {}; {})".format( link, title, text )
        
        
        def image( self, src, title, text ):
            return "IMAGE({}; {}; {})".format( src, title, text )
        
        
        def inline_html( self, html ):
            return html
        
        
        def newline( self ):
            return "\n"
        
        
        def footnote_ref( self, key, index ):
            return "[{}]".format( key )
        
        
        def footnote_item( self, key, text ):
            return "[{}] {}".format(key, text)
        
        
        def footnotes( self, text ):
            return text
        
        
        def block_code( self, code, lang = None ):
            return "<code>{}</code>".format(code)
    
    
    global __RENDERER_SXS
    __RENDERER_SXS = mistune.Markdown( renderer = MarkdownRenderer() )
