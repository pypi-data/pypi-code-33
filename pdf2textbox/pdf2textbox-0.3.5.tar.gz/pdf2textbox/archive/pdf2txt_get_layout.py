'''
pdf2txt_find_nr_cols.py

:param page: Actual page that is currently processed
:returns: Returns parameters concerning the layout of the page
:raises PDFTextExtractionNotAllowed
'''
import io
import re
import requests
import sys

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from collections import namedtuple


def _get_page_parameters(page):
    '''
    For each page find if page layout is vertical or horizontal.
    Calculate the number of columns.
    - get the width of boxes
    - divide max horizontal width by max box width --> nr of columns
    Return  VERTICAL (bool),
            HORIZONTAL (bool),
            NR_OF_COLS (int)
            X0_MIN (int, rounded)
            X1_MAX (int, rounded)
            BOX_WIDTH_MAX (int)
            Y_HEADER (int, rounded)
    '''

    X0_MIN = 0
    X1_MAX = 0
    Y0_MIN = 0
    Y0_MAX = 0
    Y1_MAX = 0
    Y_HEADER = 0
    BOX_WIDTH_MAX = 0
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        LTPage = device.get_result()

def _get_page_parameters(LTPage):
        height = LTPage.height
        width = LTPage.width
        VERTICAL, HORIZONTAL = _get_page_layout(height, width, VERTICAL, HORIZONTAL)

        for LTLine in LTPage:

            x0, x1, y0, y1 = _get_box_borders(LTLine)
            X0_MIN = _get_X0_MIN(X0_MIN=0, x0)
            X1_MAX = _get_X1_MAX(X1_MAX=0, x1)
            Y0_MIN = _get_Y0_MIN(Y0_MIN=0, y0)
            Y0_MAX = _get_Y0_MAX(Y0_MAX=0, y0)
            Y1_MAX = _get_Y1_MAX(Y1_MAX=0, y1)
            if BOX_WIDTH_MAX == 0:
                BOX_WIDTH_MAX = x1 - x0
            elif (x1 - x0) > BOX_WIDTH_MAX and y0 < y1 < Y0_MAX:
                BOX_WIDTH_MAX = x1 - x0
            if y1 >= Y0_MAX:
                if Y_HEADER == 0:
                    Y_HEADER = y0
                else:
                    Y_HEADER = y0

        yield VERTICAL, HORIZONTAL, NR_OF_COLS, X0_MIN, X1_MAX, BOX_WIDTH_MAX, Y_HEADER)


def _get_box_borders(LTLine):
    x0 = LTLine.x0
    x0 = round(x0)
    x1 = LTLine.x1
    x1 = round(x1)
    y0 = LTLine.y0
    y0 = round(y0)
    y1 = LTLine.y1
    y1 = round(y1)

    return x0, x1, y0, y1


def _get_page_layout(height, width, VERTICAL=False, HORIZONTAL=False):
    if height > width and not HORIZONTAL:
        VERTICAL = True
    elif height > width and HORIZONTAL:
        print('PDF document mixes horizontal and vertical pages')
        VERTICAL = True
        HORIZONTAL = False
    elif height < width and not VERTICAL:
        HORIZONTAL = True
    elif height < width and VERTICAL:
        print('PDF document mixes horizontal and vertical pages')
        VERTICAL = False
        HORIZONTAL = True
    else:
        print('height and width are same length?')
        print(height, width)

    return VERTICAL, HORIZONTAL


def _get_X0_MIN(X0_MIN, x0):
    #dprint(type(X0_MIN))
    if X0_MIN == 0:
        X0_MIN = x0
    else:
        if x0 < X0_MIN:
            X0_MIN = x0

    return X0_MIN


def _get_X1_MAX(X1_MAX, x1):
    if X1_MAX == 0:
        X1_MAX = x1
    else:
        if x1 > X1_MAX:
            X1_MAX = x1

    return X1_MAX


def _get_Y0_MIN(Y0_MIN, y0):
    if Y0_MIN == 0:
        Y0_MIN = y0
    else:
        if y0 < Y0_MIN:
            Y0_MIN = y0

    return Y0_MIN


def _get_Y0_MAX(Y0_MAX, y0):
    if Y0_MAX == 0:
        Y0_MAX = y0
    else:
        if y0 > Y0_MAX:
            Y0_MAX = y0

    return Y0_MAX


def _get_Y1_MAX(Y1_MAX, y1):
    if Y1_MAX == 0:
        Y1_MAX = y1
    else:
        if y1 > Y1_MAX:
            Y1_MAX = y1

    return Y1_MAX


if __name__ == '__main__':
    main()
