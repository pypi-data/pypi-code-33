'''
pdf2txt_find_nr_cols.py

:param url1: A URL pointing at a PDF file with 2 columns and a header
:returns: Returns a list containing text items that have been extracted from PDF
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

# https://stackoverflow.com/a/3985696/6597765
from pdfminer.pdftypes import resolve1



def _get_pdf_file(url=None):
    '''
    Download and return a PDF file using requests.
    '''
    if not url:
        base = 'https://www.landtag.nrw.de/portal/WWW/dokumentenarchiv/Dokument?'
        url1 = '{}Id=MMP14%2F138|16018|16019'.format(base)

        # Fragezeichen, Ausrufezeichen, 18.400, Dr., 8. Februar
        url2 = '{}Id=MMP16%2F139|14617|14630'.format(base)

        # zahlreiche Unterbrechungen, ein einzelnes Wort ("immer") ohne Kontext
        url3 = '{}Id=MMP16%2F140|14760|14768'.format(base)

        # linke Spalte und rechte Spalte nicht auf der gleichen Höhe
        # --> Abruszat's Rede rechte Spalte mit Sätzen aus linker Spalte
        url4 = '{}Id=MMP15%2F57|5694|5696'.format(base)

        # Zwei Nachnamen, ein Zitat - verliert einen Absatz (des Vorredners)
        url5 = '{}Id=MMP16%2F8|368|369'.format(base)
        url = url4

    req = requests.get(url, stream=True)
    print('url', url)
    print('status_code ', req.status_code)
    print('encoding ', req.encoding)
    print('content-type ', req.headers.get('content-type'))

    pdf = io.BytesIO(req.content)
    print('type req.content', pdf)
    return pdf


def main():
    '''
    A wrapper function to organize the steps involved to convert a PDF into text:
        1.  Get the PDF file using a URL
        2.  Find number of columns
        3.  Is there a header? What are its borders?
    '''
    pdf = _get_pdf_file(url=None)
    #pdf = open('./data/three_col_horizontal.pdf', 'rb')
    _find_nr_of_cols(pdf)


def _find_nr_of_cols(pdf):
    '''
    Calculate the number of columns.
    - get the width of boxes
    - divide max horizontal width by max box width --> nr of columns
    Return integer nr of columns
    '''
    textbox_dict = dict()
    parser = PDFParser(pdf)
    document = PDFDocument(parser, password=None)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    boxes = dict()
    page_nr = 0
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
        height = LTPage.height
        width = LTPage.width
        VERTICAL, HORIZONTAL = _get_page_layout(height, width, VERTICAL, HORIZONTAL)

        for LTLine in LTPage:
            x0, x1, y0, y1 = _get_box_borders(LTLine)
            X0_MIN = _get_X0_MIN(X0_MIN, x0)
            X1_MAX = _get_X1_MAX(X1_MAX, x1)
            Y0_MIN = _get_Y0_MIN(Y0_MIN, y0)
            Y0_MAX = _get_Y0_MAX(Y0_MAX, y0)
            Y1_MAX = _get_Y1_MAX(Y1_MAX, y1)
            if BOX_WIDTH_MAX == 0:
                BOX_WIDTH_MAX = x1 - x0
            elif (x1 - x0) > BOX_WIDTH_MAX and y0 < y1 < Y0_MAX:
                BOX_WIDTH_MAX = x1 - x0
            if y1 >= Y0_MAX:
                if Y_HEADER == 0:
                    Y_HEADER = y0
                else:
                    Y_HEADER = y0


    print('BOX_WIDTH_MAX: {}'.format(BOX_WIDTH_MAX))
    print('X0_MIN: {}'.format(X0_MIN))
    print('X1_MAX: {}'.format(X1_MAX))
    print('Y0_MIN: {}'.format(Y0_MIN))
    print('Y0_MAX: {}'.format(Y0_MAX))
    print('Y1_MAX: {}'.format(Y1_MAX))
    PAGE_WIDTH = X1_MAX - X0_MIN
    print('PAGE_WIDTH', PAGE_WIDTH)
    NR_OF_COLS = PAGE_WIDTH//BOX_WIDTH_MAX
    print('NR_OF_COLS', NR_OF_COLS)
    print('Y_HEADER', Y_HEADER)




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


def parse_layout(layout):
    """
    found here: https://stackoverflow.com/a/25262470/6597765
    Function to recursively parse the layout tree.
    """
    for lt_obj in layout:
        print('dir(lt_obj)')
        print(dir(lt_obj))
        print('dir(lt_obj.bbox)')
        print(dir(lt_obj.bbox))
        print(lt_obj.__class__.__name__)
        print(lt_obj.bbox)
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            print(lt_obj.get_text())
        elif isinstance(lt_obj, LTFigure):
            parse_layout(lt_obj)  # Recursive


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


def dprint(fmt=None, *args, **kwargs):
    # found here:
    # https://stackoverflow.com/a/44523599/6597765
    try:
        name = sys._getframe(1).f_code.co_name
    except(IndexError, TypeError, AttributeError) as e:
        print(e)
    print("[{}] {}".format(name, fmt))



if __name__ == '__main__':
    main()
