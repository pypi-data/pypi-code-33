from PyQt5.QtWidgets import QFrame, QSizePolicy, QSpacerItem, QHBoxLayout, QVBoxLayout, QWidget

import mhelper


def add_separator( layout, pos = None ):
    if isinstance( layout, QWidget ):
        layout = layout.layout()
    
    c = QFrame()
    c.setFrameShadow( QFrame.Sunken )
    
    if isinstance( layout, QHBoxLayout ):
        c.setFixedWidth( 16 )
        c.setFrameShape( QFrame.VLine )
    elif isinstance( layout, QVBoxLayout ):
        c.setFixedHeight( 16 )
        c.setFrameShape( QFrame.HLine )
    else:
        raise mhelper.type_error( "layout", layout, (QHBoxLayout, QVBoxLayout) )
    
    if pos is not None:
        layout.insertWidget( pos, c )
    else:
        layout.addWidget( c )


def add_spacer( layout, pos = None ):
    if isinstance( layout, QWidget ):
        layout = layout.layout()
    
    if isinstance( layout, QHBoxLayout ):
        c = QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum )
    elif isinstance( layout, QVBoxLayout ):
        c = QSpacerItem( 1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding )
    else:
        raise mhelper.type_error( "layout", layout, (QHBoxLayout, QVBoxLayout) )
    
    if pos is not None:
        layout.insertSpacerItem( pos, c )
    else:
        layout.addSpacerItem( c )
