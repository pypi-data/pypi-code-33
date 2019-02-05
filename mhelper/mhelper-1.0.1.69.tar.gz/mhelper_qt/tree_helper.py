from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


TAG_header_map = "TAG_header_map"
TAG_data = "TAG_data"


class TreeHeaderMap:
    def __init__( self, tree: QTreeWidget ):
        self.tree = tree
    
    
    def __getitem__( self, item: str ):
        return get_or_create_column( self.tree, item )


def set_as_list( tree: QTreeWidget ):
    tree.setHeaderHidden( True )
    tree.setIndentation( 0 )


def get_or_create_column( tree: QTreeWidget, key: str ):
    if hasattr( tree, TAG_header_map ):
        header_map = getattr( tree, TAG_header_map )
    else:
        header_map = { }
        setattr( tree, TAG_header_map, header_map )
    
    col_index = header_map.get( key )
    
    if col_index is None:
        col_index = len( header_map )
        header_map[key] = col_index
        
        if tree.headerItem() is None:
            tree.setHeaderItem( QTreeWidgetItem() )
        
        tree.headerItem().setText( col_index, key )
    
    return col_index


def get_selected_data( tree: QTreeWidget, tag: str = TAG_data ):
    sel = tree.selectedItems()
    
    if len( sel ) == 1:
        return get_data( sel[0], tag )
    else:
        return None


def set_data( item, data, tag: str = TAG_data ):
    setattr( item, tag, data )


def get_data( item, tag: str = TAG_data ):
    if hasattr( item, tag ):
        return getattr( item, tag )
    else:
        return None


def selected_indices( tree: QTreeWidget ):
    return (tree.indexOfTopLevelItem( x ) for x in tree.selectedItems())


def remove_selected( tree: QTreeWidget ):
    for i in sorted( selected_indices( tree ), reverse = True ):
        tree.takeTopLevelItem( i )


def iter_items( tree: QTreeWidget ):
    for i in range( tree.topLevelItemCount() ):
        yield tree.topLevelItem( i )


def iter_data( tree: QTreeWidget, tag: str = TAG_data ):
    for i in range( tree.topLevelItemCount() ):
        yield get_data( tree.topLevelItem( i ), tag )


def get_or_create_item( tree: QTreeWidget, data: object, tag: str = TAG_data ) -> QTreeWidgetItem:
    item = None
    
    for item_ in iter_items( tree ):
        data_2 = getattr( item_, tag )
        
        if data_2 == data:
            item = item_
            break
    
    if item is None:
        item = QTreeWidgetItem()
        setattr( item, tag, data )
        tree.addTopLevelItem( item )
    
    return item


def resize_all( tree: QTreeWidget ):
    for n in range( tree.columnCount() ):
        tree.resizeColumnToContents( n )
