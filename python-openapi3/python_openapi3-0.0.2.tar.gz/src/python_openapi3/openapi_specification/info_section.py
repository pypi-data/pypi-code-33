from python_openapi3._util import ensure_class, OASBase, DEFAULT_IGNORE


class OASContactObject(OASBase):
    """
    >>> sorted(OASContact("joran","asd@asds.asd","ASDASD").to_dict().items())
    [('email', 'asd@asds.asd'), ('name', 'joran'), ('url', 'ASDASD')]
    """
    def __init__(self,name,email=DEFAULT_IGNORE,url=DEFAULT_IGNORE):
        self.update(locals())

class OASLicenseObject(OASBase):
    """
    >>> sorted(OASLicenseObject("GPL").to_dict().items())
    [('name', 'GPL'), ('url', '')]

    """
    def __init__(self,name,url=DEFAULT_IGNORE):
        self.update(locals())

class OASInfoObject(OASBase):
    def __init__(self, title,version, description=DEFAULT_IGNORE,
                 termsOfService=DEFAULT_IGNORE, contact=DEFAULT_IGNORE,
                 license=DEFAULT_IGNORE):
        self.update(locals())