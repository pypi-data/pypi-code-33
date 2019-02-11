
from .expand_colspan_rowspan import expand_colspan_rowspan
from scrapy.selector import Selector
from scrapy.selector.unified import SelectorList


def extract(selector):
    """
    Given a scrapy object, return a list of text rows.

    Parameters
    ----------
    selector : scrapy.selector.unified.SelectorList

    Returns
    -------
    list of SelectorList
        Each returned row is a SelectorList.
    Notes
    -----
    Any cell with ``rowspan`` or ``colspan`` will have its contents copied
    to subsequent cells.
    """

    # Type checking
    if not isinstance(selector, SelectorList):
        raise TypeError("Input type must be scrapy.selector.unified.SelectorList")

    # extract data
    rows = selector.xpath('.//tr')
    extracted = expand_colspan_rowspan(rows)

    # concatenate data
    print("printing the type of extracted ")
    print(type(extracted[0][0]))
    tds = [Selector(text=''.join(row)).xpath('//th|//td') for row in extracted]
    print("printing the type of tds")
    print(type(tds[0]))
    return tds
