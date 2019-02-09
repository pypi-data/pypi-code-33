
import scrapy
from .expand_colspan_rowspan import expand_colspan_rowspan

def extract(selector):
    """
    Given a scrapy object, return a list of text rows.

    Parameters
    ----------
    selector : scrapy.selector.unified.SelectorList

    Returns
    -------
    list of list
        Each returned row is a list of str text.
    Notes
    -----
    Any cell with ``rowspan`` or ``colspan`` will have its contents copied
    to subsequent cells.
    """

    # Type checking
    if not isinstance(selector, scrapy.selector.unified.SelectorList):
        raise TypeError("Input type must be scrapy.selector.unified.SelectorList")

    # extract data
    rows = selector.xpath('//tr')
    data = expand_colspan_rowspan(rows)
    return data
