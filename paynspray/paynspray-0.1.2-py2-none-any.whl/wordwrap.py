import re

DefaultWrap = 60

def wordwrap(string, indent = 0, col = DefaultWrap, append = '', prepend = ''):
    """Wraps text at a given column using the provided indentation value"""
    def wrap_block(w):
        retval = (" " * indent) + prepend + w + append + chr(5)
        retval = re.sub(r'\n\005', "\n", retval)
        retval = re.sub(r'\005', "\n", retval)
        return retval

    return re.sub(r'.{1,' + "{}".format(col - indent) + '}(?:\s|\Z)', lambda w: wrap_block(w.group()), string)