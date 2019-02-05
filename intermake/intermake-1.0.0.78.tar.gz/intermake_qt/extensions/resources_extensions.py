def init():
    import sys
    from mhelper import ResourceIcon
    sys.__stderr__.write( "Notice: The `intermake_qt` module has been loaded.\n" )
    ResourceIcon.add_search( ":/intermake/*.svg" )
