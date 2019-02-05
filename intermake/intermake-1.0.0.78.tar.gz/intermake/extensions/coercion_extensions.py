import stringcoercion


class _MAnnotationCoercer( stringcoercion.AbstractCoercer ):
    """
    Annotations providing UI hints can be ignored.
    For instance a `Filename[str]` can be presented as any other `str`.
    """
    
    
    def on_coerce( self, args: stringcoercion.CoercionInfo ):
        return args.collection.coerce( args.annotation.mannotation_arg, args.source )
    
    
    def on_get_archetype( self ) -> type:
        from mhelper import MAnnotation
        return MAnnotation
    
    
    def on_can_handle( self, info: stringcoercion.CoercionInfo ) -> bool:
        return info.annotation.is_mannotation


def init(coercers: stringcoercion.CoercerCollection):
    coercers.register( _MAnnotationCoercer() )
