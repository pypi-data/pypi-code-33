from typing import List, Iterator


class BatchList:
    def __init__( self, data, batch_size ):
        self.batch: int = batch_size
        self.data: list = list( data )
    
    
    def take( self ) -> list:
        result = self.data[0:self.batch]
        del self.data[0:self.batch]
        return result
    
    
    def __bool__( self ):
        return bool( self.data )
    
    
    def __len__( self ):
        return len( self.data )
    
    
    def __iter__( self ) -> Iterator[list]:
        while self:
            yield self.take()


def divide_workload( index, count, quantity ):
    import warnings
    warnings.warn( "deprecated - array_helper.get_workload", DeprecationWarning )
    from mhelper import array_helper
    return array_helper.get_workload( index, quantity, count )
