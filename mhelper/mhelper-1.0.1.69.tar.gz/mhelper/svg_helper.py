"""
Functions for writing SVG images to disk.
"""
from enum import Enum

from typing import List, Tuple, Iterable, Optional, TypeVar


__author__ = "Martin Rusilowicz"

T = TypeVar( "T" )


def _get_attributes( **kwargs ):
    r = []
    
    for k, v in kwargs.items():
        if v is not None:
            k = k.replace( "_", "-" )
            
            if isinstance( v, list ) or isinstance( v, tuple ):
                v = ",".join( str( x ) for x in v )
            elif isinstance( v, Enum ):
                v = v.name
                
                if v.startswith( "n_" ):
                    v = v[2:]
                
                v = v.replace( "_", "-" )
            
            r.append( '{}="{}"'.format( k, v ) )
    
    return " ".join( r )


class EFontWeight( Enum ):
    normal = 1
    bold = 2
    bolder = 3
    lighter = 4
    n_100 = 5
    n_200 = 6
    n_300 = 7
    n_400 = 8
    n_500 = 9
    n_600 = 10
    n_700 = 11
    n_800 = 12
    n_900 = 13
    inherit = 14


class EPriority:
    LINES = 1
    RECT = 2
    TEXT = 3


class ETextAnchor( Enum ):
    start = 1
    middle = 2
    end = 3


class EAlignmentBaseline( Enum ):
    auto = 1
    baseline = 2
    before_edge = 3
    text_before_edge = 4
    middle = 5
    central = 6
    after_edge = 7
    text_after_edge = 8
    ideographic = 9
    alphabetic = 10
    hanging = 11
    mathematical = 12
    inherit = 13


TColour = str
TMarker = str
TPos = float
TFraction = float
TDashArray = str
TPriority = int


class IPoint:
    @property
    def xy( self ):
        return self.x, self.y
    
    @property
    def x( self ):
        raise NotImplementedError( "abstract" )
    
    
    @property
    def y( self ):
        raise NotImplementedError( "abstract" )


class FixedPoint( IPoint ):
    def __init__( self, x, y ):
        self.__x = x
        self.__y = y
    
    
    @property
    def x( self ):
        return self.__x
    
    
    @property
    def y( self ):
        return self.__y


class Point( IPoint ):
    def __init__( self, x, y ):
        self.__x = x
        self.__y = y
    
    
    @property
    def x( self ):
        return self.__x
    
    
    @property
    def y( self ):
        return self.__y


    # noinspection PyMethodOverriding
    @x.setter
    def x( self, value ):
        self.__x = value
    
    # noinspection PyMethodOverriding
    @y.setter
    def y( self, value ):
        self.__y = value
    
    
    @classmethod
    def create( cls, x: Optional[int], y: Optional[int], loc: IPoint ) -> "Point":
        if x is None and y is None and loc is not None:
            return Point( loc.x, loc.y )
        elif x is not None and y is not None and loc is None:
            return Point( x, y )
        else:
            raise ValueError( "Must provide x ({}), y ({}) or loc ({}).".format( x, y, loc ) )


class SvgElement:
    def get_max( self ) -> IPoint:
        raise NotImplementedError( "abstract" )
    
    
    def get_xml( self ):
        raise NotImplementedError( "abstract" )
    
    
    def get_z( self ):
        if hasattr( self, "z" ):
            return self.z
        else:
            raise NotImplementedError( "abstract - must have `z` or `get_z`." )


class Text( SvgElement ):
    def __init__( self,
                  *,
                  x: TPos = None,
                  y: TPos = None,
                  loc: IPoint = None,
                  text: str,
                  z: TPriority = EPriority.TEXT,
                  font_family: str = None,
                  font_size: TPos = None,
                  font_weight: EFontWeight = None,
                  fill: TColour = None,
                  alignment_baseline: EAlignmentBaseline = None,
                  text_anchor: ETextAnchor = None,
                  **kwargs ):
        self.loc = Point.create( x, y, loc )
        self.text = text
        self.z = z
        self.font_family = font_family
        self.font_size = font_size
        self.font_weight = font_weight
        self.fill = fill
        self.alignment_baseline = alignment_baseline
        self.text_anchor = text_anchor
        self.kwargs = kwargs
    
    
    def get_xml( self ):
        return '<text {}>{}</text>'.format( _get_attributes( x = self.loc.x,
                                                             y = self.loc.y,
                                                             font_family = self.font_family,
                                                             font_size = self.font_size,
                                                             font_weight = self.font_weight,
                                                             fill = self.fill,
                                                             alignment_baseline = self.alignment_baseline,
                                                             text_anchor = self.text_anchor,
                                                             **self.kwargs ),
                                            self.text )
    
    
    def get_max( self ):
        return self.loc  # TODO: Inaccurate


class Line( SvgElement ):
    def __init__( self,
                  *,
                  x1: TPos = None,
                  y1: TPos = None,
                  loc1: IPoint = None,
                  x2: TPos = None,
                  y2: TPos = None,
                  loc2: IPoint = None,
                  z: TPriority = EPriority.LINES,
                  stroke: TColour = None,
                  stroke_width: TPos = None,
                  marker_end: TMarker = None,
                  **kwargs ):
        self.loc1 = Point.create( x1, y1, loc1 )
        self.loc2 = Point.create( x2, y2, loc2 )
        self.z = z
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.marker_end = marker_end
        self.kwargs = kwargs
    
    
    def get_max( self ):
        return Point( max( self.loc1.x, self.loc2.x ), max( self.loc1.y, self.loc2.y ) )
    
    
    def get_xml( self ):
        return '<line {} />'.format( _get_attributes( x1 = self.loc1.x,
                                                      y1 = self.loc1.y,
                                                      x2 = self.loc2.x,
                                                      y2 = self.loc2.y,
                                                      stroke = self.stroke,
                                                      stroke_width = self.stroke_width,
                                                      marker_end = self.marker_end,
                                                      **self.kwargs ) )


class Rect( SvgElement ):
    
    def __init__( self,
                  *,
                  x: TPos = None,
                  y: TPos = None,
                  loc: IPoint = None,
                  w: TPos = None,
                  h: TPos = None,
                  size: IPoint = None,
                  z: TPriority = EPriority.RECT,
                  rx = TPos,
                  ry = TPos,
                  fill = TColour,
                  stroke = TColour,
                  stroke_width = TPos,
                  stroke_dasharray = TDashArray,
                  fill_opacity = TFraction,
                  stroke_opacity = TFraction,
                  **kwargs ):
        self.loc = Point.create( x, y, loc )
        self.size = Point.create( w, h, size )
        self.z = z
        self.rx = rx
        self.ry = ry
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.stroke_dasharray = stroke_dasharray
        self.fill_opacity = fill_opacity
        self.stroke_opacity = stroke_opacity
        self.kwargs = kwargs
    
    
    @property
    def centre( self ) -> FixedPoint:
        return FixedPoint( self.loc.x + self.size.x / 2, self.loc.y + self.size.y / 2 )
    
    
    def get_max( self ):
        return Point( self.loc.x + self.size.x, self.loc.y + self.size.y )
    
    
    def get_xml( self ):
        return '<rect {} />'.format( _get_attributes( x = self.loc.x,
                                                      y = self.loc.y,
                                                      width = self.size.x,
                                                      height = self.size.y,
                                                      rx = self.rx,
                                                      ry = self.ry,
                                                      fill = self.fill,
                                                      stroke = self.stroke,
                                                      stroke_width = self.stroke_width,
                                                      stroke_dasharray = self.stroke_dasharray,
                                                      fill_opacity = self.fill_opacity,
                                                      stroke_opacity = self.stroke_opacity,
                                                      **self.kwargs ) )


class Ellipse( SvgElement ):
    def __init__( self,
                  *,
                  x: TPos = None,
                  y: TPos = None,
                  loc: IPoint = None,
                  w: TPos = None,
                  h: TPos = None,
                  size: IPoint = None,
                  z: TPriority = EPriority.RECT,
                  fill = TColour,
                  stroke = TColour,
                  stroke_width = TPos,
                  stroke_dasharray = TDashArray,
                  fill_opacity = TFraction,
                  stroke_opacity = TFraction,
                  **kwargs ):
        self.loc = Point.create( x, y, loc )
        self.size = Point.create( w, h, size )
        self.z = z
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.stroke_dasharray = stroke_dasharray
        self.fill_opacity = fill_opacity
        self.stroke_opacity = stroke_opacity
        self.kwargs = kwargs
        
    @property
    def centre( self ) -> FixedPoint:
        return FixedPoint( self.loc.x + self.size.x / 2, self.loc.y + self.size.y / 2 )
    
    
    def get_max( self ):
        return Point( self.loc.x + self.size.x, self.loc.y + self.size.y )
    
    
    def get_xml( self ):
        return '<ellipse {} />'.format( _get_attributes( cx = self.loc.x + self.size.x / 2,
                                                         cy = self.loc.y + self.size.y / 2,
                                                         rx = self.size.x / 2,
                                                         ry = self.size.y / 2,
                                                         fill = self.fill,
                                                         stroke = self.stroke,
                                                         stroke_width = self.stroke_width,
                                                         stroke_dasharray = self.stroke_dasharray,
                                                         fill_opacity = self.fill_opacity,
                                                         stroke_opacity = self.stroke_opacity,
                                                         **self.kwargs ) )


class SvgWriter:
    def __init__( self, width: int = 128, height: int = 128, *, enable_html: bool = False, enable_autosize: bool = True, enable_kwargs: bool = False, contents: Iterable[SvgElement] = None, title: str = None ):
        """
        CONSTRUCTOR        
        :param width:               Width of image. Ignored if `enable_autosize` is set. 
        :param height:              Height of image. Ignored if `enable_autosize` is set. 
        :param enable_html:         Output with HTML headers. Off by default.
        :param enable_autosize:     Automatically expand width and height to accommodate new content. On by default.
        :param enable_kwargs:       Permit unknown arguments. Off by default.
        :param contents:            Contents list. 
        :param title:               Title 
        """
        self.enable_html = enable_html
        self.enable_autosize = enable_autosize
        self.enable_kwargs = enable_kwargs
        self.width = width
        self.height = height
        self.title = title
        self.contents: List[SvgElement] = list( contents ) if contents is not None else []
        self.__defs: List[str] = ['<marker id="markerCircle" markerWidth="8" markerHeight="8" refX="5" refY="5"><circle cx="5" cy="5" r="3" style="stroke: none; fill:#00C000;"/></marker><marker id="markerArrow" markerWidth="13" markerHeight="13" refX="2" refY="6" orient="auto"><path d="M2,2 L2,11 L10,6 L2,2" style="fill: #00C000;" /></marker>']
    
    
    def _get_header_and_footer( self ) -> Tuple[str, str]:
        if self.enable_html:
            header = '<html><head><title>{0}</title></head><body><svg width="{1}" height="{2}">'
            footer = '</svg></body></html>'
        else:
            header = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{1}" height="{2}"><title>{0}</title>'
            footer = '</svg></body></html>'
        
        defs = '<defs>' + "\n".join( self.__defs ) + '</defs>'
        header = header.format( self.title or "", self.width, self.height )
        header += defs
        
        return header, footer
    
    
    def to_string( self ) -> str:
        data: List[Tuple[int, int, str]] = []
        
        if self.enable_autosize:
            self.width = 1
            self.height = 1
        
        for i, r in enumerate( self.contents ):
            if self.enable_autosize:
                x, y = r.get_max().xy
                if self.width < x:
                    self.width = x
                
                if self.height < y:
                    self.height = y
            
            data.append( (i, r.get_z(), r.get_xml()) )
        
        r = []
        header, footer = self._get_header_and_footer()
        r.append( header )
        r.extend( x[-1] for x in sorted( data, key = lambda x: x[1] * 10000 + x[0] ) )
        r.append( footer )
        
        return "\n".join( r )
    
    
    def _check_kwargs( self, kwargs ):
        if not self.enable_kwargs and kwargs:
            raise ValueError( "Unknown arguments passed. Did you mean to pass these parameters? If you did set `enable_kwargs` to `True` to enable unknown parameters. kwargs = {}".format( kwargs ) )
    
    
    def add_connector( self,
                       x1: TPos,
                       y1: TPos,
                       w1: TPos,
                       h1: TPos,
                       x2: TPos,
                       y2: TPos,
                       w2: TPos,
                       h2: TPos,
                       **kwargs ):
        return self.add_line( x1 = x1 + w1 / 2,
                              y1 = y1 + h1 / 2,
                              x2 = x2 + w2 / 2,
                              y2 = y2 + h2 / 2,
                              **kwargs )
    
    
    def add( self, element: T ) -> T:
        self.contents.append( element )
        return element
    
    
    def add_line( self, **kwargs ):
        return self.add( Line( **kwargs ) )
    
    
    def add_rect( self, **kwargs ) -> Rect:
        return self.add( Rect( **kwargs ) )
    
    
    def add_ellipse( self, **kwargs ) -> Ellipse:
        return self.add( Ellipse( **kwargs ) )
    
    
    def centre_text( self,
                     x: TPos,
                     y: TPos,
                     w: TPos,
                     h: TPos,
                     text: str,
                     **kwargs ):
        return self.add_text( x = x + w / 2,
                              y = y + h / 2,
                              text = text,
                              alignment_baseline = EAlignmentBaseline.middle,
                              text_anchor = ETextAnchor.middle,
                              **kwargs )
    
    
    def add_text( self, **kwargs ):
        return self.add( Text( **kwargs ) )
