"""
Functions below are extracted and modified from pandas implementation.
https://github.com/pandas-dev/pandas/blob/683c7b55f5195fdf4f524239066cbf6f1301f0e7/pandas/io/html.py
"""

import re
_RE_WHITESPACE = re.compile(r'[\r\n]+|\s{2,}')


def _remove_whitespace(s, regex=_RE_WHITESPACE):
    """Replace extra whitespace inside of a string with a single space.
    Parameters
    ----------
    s : str or unicode
        The string from which to remove extra whitespace.
    regex : regex
        The regular expression to use to remove extra whitespace.
    Returns
    -------
    subd : str or unicode
        `s` with all extra whitespace replaced with a single space.
    """
    return regex.sub(' ', s.strip())


def _parse_td(row):
    """Return the td elements from a row element.

    Parameters
    ----------
    row : node-like
        A DOM <tr> node.
    Returns
    -------
    list of node-like
        These are the elements of each row, i.e., the columns.
    """
    # Look for direct children only: the "row" element here may be a
    # <thead> or <tfoot> (see _parse_thead_tr).
    return row.xpath('./td|./th')


def _text_getter(obj):
    """
    Return the text of an individual DOM node.
    Parameters
    ----------
    obj : node-like
        A DOM node.
    Returns
    -------
    text : str or unicode
        The text from an individual DOM node.
    """
    return obj.get()


def _attr_getter(obj, attr):
    """
    Return the attribute value of an individual DOM node.
    Parameters
    ----------
    obj : node-like
        A DOM node.
    attr : str or unicode
        The attribute, such as "colspan"
    Returns
    -------
    str or unicode
        The attribute value.
    """
    # Scrapy has this implementation:
    return obj.xpath('.//@{}'.format(attr)).get()


def expand_colspan_rowspan(rows):
    """
    Given a list of <tr>s, return a list of text rows.
    Parameters
    ----------
    rows : list of node-like
        List of <tr>s
    Returns
    -------
    list of list
        Each returned row is a list of str text.
    Notes
    -----
    Any cell with ``rowspan`` or ``colspan`` will have its contents copied
    to subsequent cells.
    """

    all_texts = []  # list of rows, each a list of str
    remainder = []  # list of (index, text, nrows)

    for tr in rows:
        texts = []  # the output for this row
        next_remainder = []

        index = 0
        tds = _parse_td(tr)
        for td in tds:
            # Append texts from previous rows with rowspan>1 that come
            # before this <td>
            while remainder and remainder[0][0] <= index:
                prev_i, prev_text, prev_rowspan = remainder.pop(0)
                texts.append(prev_text)
                if prev_rowspan > 1:
                    next_remainder.append((prev_i, prev_text,
                                           prev_rowspan - 1))
                index += 1

            # Append the text from this <td>, colspan times
            text = _remove_whitespace(_text_getter(td))
            rowspan = int(_attr_getter(td, 'rowspan') or 1)
            colspan = int(_attr_getter(td, 'colspan') or 1)

            for _ in range(colspan):
                texts.append(text)
                if rowspan > 1:
                    next_remainder.append((index, text, rowspan - 1))
                index += 1

        # Append texts from previous rows at the final position
        for prev_i, prev_text, prev_rowspan in remainder:
            texts.append(prev_text)
            if prev_rowspan > 1:
                next_remainder.append((prev_i, prev_text,
                                       prev_rowspan - 1))

        all_texts.append(texts)
        remainder = next_remainder

    # Append rows that only appear because the previous row had non-1
    # rowspan
    while remainder:
        next_remainder = []
        texts = []
        for prev_i, prev_text, prev_rowspan in remainder:
            texts.append(prev_text)
            if prev_rowspan > 1:
                next_remainder.append((prev_i, prev_text,
                                       prev_rowspan - 1))
        all_texts.append(texts)
        remainder = next_remainder

    return all_texts
