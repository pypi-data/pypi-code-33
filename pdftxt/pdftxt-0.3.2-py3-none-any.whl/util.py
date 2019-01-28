import re
from math import ceil, floor


class PdfTxtError(Exception):
    pass


def character_in_region(c, x0, y0, x1, y1):
    return c.x0 >= x0 and c.x1 <= x1 and c.y0 >= y0 and c.y1 <= y1


def fetch_left_most_coordinate(characters):
    return floor(min([c.x0 for c in characters]))


def fetch_right_most_coordinate(characters):
    return ceil(max([c.x1 for c in characters]))


def parse_float_list(text):
    """
    text: expecting a comma separated list of numbers
    optionally contained in (brackets).

    Returns a list of floats.
    """
    if text is None:
        return []

    if isinstance(text, list):
        text = text[0]

    return [float(r.strip()) for r in text.strip(")").strip("(").split(",")]


def parse_page_notation(text):
    """
    Acceptable notations:

        ALL     (accepts all pages)
        1+      (accepts all pages)
        2+      (pages 2 to end)
        2       (just page 2)
        2-4     (just pages 2-4)
        2,5,8   (pages 2, 5 and 8)

    Return a function for matching page number.

    """
    text = text.strip().lower()

    def matcher(rx, txt):
        m = re.match(rx, txt)
        if m:
            return m.groupdict()
        return None

    # return accept all pages
    if text.strip().lower() in ("", "all", "1+", "1-"):

        def _accept_all(pageno):
            return True

        return _accept_all

    # return accept page plus number
    match = matcher(r"^(?P<pageno>\d+)\+$", text)
    if match:
        accepted_number = int(match["pageno"])

        def _accept_ge(pageno):
            return pageno >= accepted_number

        return _accept_ge

    # return accept single page number
    match = matcher(r"^(?P<pageno>\d+)$", text)
    if match:
        accepted_number = int(match["pageno"])

        def _accept_eq(pageno):
            return pageno == accepted_number

        return _accept_eq

    # return accept page in
    match = matcher(r"^(?P<pgstart>\d+) ?- ?(?P<pgend>\d+)$", text)
    if match:
        start_no = int(match["pgstart"])
        end_no = int(match["pgend"])
        accepted_number = list(range(start_no, end_no + 1))

        def _accept_in(pageno):
            return pageno in accepted_number

        return _accept_in

    match = matcher(r"^(?P<pages>(\d+,)+\d)$", text)
    if match:
        accepted_number = [int(t) for t in match["pages"].split(",")]

        def _accept_in(pageno):
            return pageno in accepted_number

        return _accept_in

    raise PdfTxtError("Invalid page selection notation.")
