from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMenu, QWidget, QWidgetAction, QLabel, QSizePolicy

from mhelper import array_helper


def show_menu( control: QWidget, *args ) -> object:
    if not args:
        raise ValueError( "Cannot call `show_menu` with no `args`." )
    
    if len( args ) == 1 and isinstance( args[0], QMenu ):
        return __show_menu( control, args[0] )
    
    menu = QMenu()
    
    control = control.sender()
    
    if control.window().styleSheet():
        menu.setStyleSheet( control.window().styleSheet() )
    
    if len( args ) == 1 and array_helper.is_simple_sequence( args[0] ):
        args = args[0]
    
    r = []
    
    for arg in args:
        r.append( menu.addAction( str( arg ) ) )
    
    selected = menu.exec_( control.mapToGlobal( QPoint( 0, control.height() ) ) )
    
    if selected is None:
        return None
    
    return args[r.index( selected )]


def __show_menu( window: QWidget, menu: QMenu ):
    return menu.exec_( window.sender().mapToGlobal( QPoint( 0, window.sender().height() ) ) )


def show_menu_from_bar( control, menu: QMenu ):
    menu_bar = control.parent().menuBar()
    p = menu_bar.mapToGlobal( menu_bar.rect().bottomLeft() )
    return menu.exec_( p )


def add_section( menu: QMenu, text: str ):
    a = QWidgetAction( menu )
    label = QLabel()
    label.setText( text )
    label.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
    label.setWordWrap( True )
    label.setStyleSheet( "background:transparent;color:#4040C0;font-weight:bold;font-size:10px;border-bottom:2px groove #C0C0C0;padding-bottom: 4px;" )
    a.setDefaultWidget( label )
    a.setEnabled( False )
    menu.addAction( a )
