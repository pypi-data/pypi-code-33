from PyQt5.QtWidgets import QLayout


def delete_children( layout: QLayout ):
    for i in reversed( range( layout.count() ) ):
        item = layout.itemAt( i )
        
        if item.widget() is not None:
            item.widget().setParent( None )
        elif item.layout() is not None:
            delete_children( item.layout() )
            item.layout().setParent( None )
        else:
            layout.removeItem( item )
    
    assert layout.count() == 0, "Layout not cleared."
