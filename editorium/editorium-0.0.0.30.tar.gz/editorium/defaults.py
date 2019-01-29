__default_editorium = None


def default_editorium():
    """
    Obtains the default editorium, creating it if it doesn't already exist.
    
    :return: An object of class `Editorium`.
    :rtype: Editorium  
    """
    global __default_editorium
    
    if __default_editorium is None:
        e = create_default()

        __default_editorium = e
    
    return __default_editorium


def create_default():
    import editorium.default_editors as d
    from editorium.bases import Editorium
    e = Editorium()
    e.editors.append( d.ReadonlyEditor )
    e.editors.append( d.PasswordEditor )
    e.editors.append( d.FilenameEditor )
    e.editors.append( d.AnnotationEditor )
    e.editors.append( d.BoolEditor )
    e.editors.append( d.StringCoercionEnumEditor )
    e.editors.append( d.FlagsEditor )
    e.editors.append( d.FloatEditor )
    e.editors.append( d.IntEditor )
    e.editors.append( d.StringEditor )
    e.editors.append( d.ListTEditor )
    e.editors.append( d.NullableEditor )
    e.editors.append( d.NoneEditor )
    e.editors.append( d.UnionEditor )
    e.editors.append( d.FallbackEditor )
    return e
