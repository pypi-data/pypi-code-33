class PageDoesNotExist(Exception):
    pass
    
class PageClassNotFound(Exception):
    pass

class PageActionNotFound(Exception):
    pass

class IncompatiblePageClass(Exception):
    pass


class PageExists(Exception):
    pass


class PathExists(Exception):
    pass