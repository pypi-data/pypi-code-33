'''
pdf2textbox.py

:param url1: A URL pointing at a PDF file with max 3 columns and a header
:returns: Returns a dict containing text items that have been extracted from PDF
:raises PDFTextExtractionNotAllowed
:works
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
        url = url5

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
        2.  Determine page layout
        3.  Move text and page parameters into a fitting dictionary
    '''
    pdf = _get_pdf_file(url=None)
    pdf = open('./data/three_col_horizontal.pdf', 'rb')
    _pdf_to_text(pdf)


def _pdf_to_text(pdf):
    '''
    Calculate the number of columns.
    - get the width of boxes
    - divide max horizontal width by max box width --> nr of columns
    Return integer nr of columns
    '''
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
    VERTICAL = HORIZONTAL = None

    for page in PDFPage.create_pages(document):
        page_nr += 1
        interpreter.process_page(page)
        LTPage = device.get_result()
        VERTICAL, HORIZONTAL = _get_page_layout(LTPage, VERTICAL, HORIZONTAL)
        NR_OF_COLS, X0_MIN, X1_MAX, BOX_WIDTH_MAX, Y_HEADER =\
                _get_page_parameters(LTPage)
        boxes[page_nr] = dict()
        boxes = _init_boxes(Y_HEADER, NR_OF_COLS, page_nr, boxes)

        for LTLine in LTPage:
            try:
                text = LTLine.get_text()
            except AttributeError:
                text = None
            x0, x1, y0, y1 = _get_box_borders(LTLine)

            box = namedtuple('box', ['x0', 'x1', 'y0', 'y1', 'text'])
            if y0 >= Y_HEADER:
                boxes[page_nr]['header'].append(box(x0, x1, y0, y1, text))
            elif NR_OF_COLS == 1:
                boxes[page_nr]['column'].append(box(x0, x1, y0, y1, text))
            elif NR_OF_COLS == 2:
                if x0 < (X0_MIN + BOX_WIDTH_MAX):
                    boxes[page_nr]['left_column'].append(box(x0, x1, y0, y1, text))
                else:
                    boxes[page_nr]['right_column'].append(box(x0, x1, y0, y1, text))
            elif NR_OF_COLS == 3:
                col = _choose_col(x0, x1, X0_MIN, X1_MAX, BOX_WIDTH_MAX)
                boxes[page_nr][col].append(box(x0, x1, y0, y1, text))

    for key, value in boxes.items():
        print(key)
        for kk, vv in value.items():
            print(kk)
            for box in vv:
                print('-'*60)
                print(box.x0, box.x1, box.y0, box.y1)
                print(box.text)
                #pass


def _get_page_parameters(LTPage):
    BOX_WIDTH_MAX = Y_HEADER = BOX_UPPER_Y = 0
    box_upper_y = list()
    X0_MIN = X1_MAX = Y0_MIN = Y0_MAX = Y1_MAX = 0

    for LTLine in LTPage:
        x0, x1, y0, y1 = _get_box_borders(LTLine)
        X0_MIN = _get_X0_MIN(x0, X0_MIN)
        X1_MAX = _get_X1_MAX(x1, X1_MAX)
        Y0_MIN = _get_Y0_MIN(y0, Y0_MIN)
        Y0_MAX = _get_Y0_MAX(y0, Y0_MAX)
        Y1_MAX = _get_Y1_MAX(y1, Y1_MAX)

        BOX_WIDTH_MAX = _get_box_width(BOX_WIDTH_MAX, Y0_MAX, x0, x1, y0, y1)
        Y_HEADER = _get_y_header(Y_HEADER, x0, x1, y0, y1, Y0_MAX, BOX_WIDTH_MAX)

        if y1 < Y_HEADER:
            box_upper_y.append(y1)

        Y_HEADER = _correct_y_header(box_upper_y, Y_HEADER)

    PAGE_WIDTH = X1_MAX - X0_MIN
    NR_OF_COLS = PAGE_WIDTH//BOX_WIDTH_MAX

    return NR_OF_COLS, X0_MIN, X1_MAX, BOX_WIDTH_MAX, Y_HEADER


def _init_boxes(Y_HEADER, NR_OF_COLS, page_nr, boxes):
    if Y_HEADER > 0:
        boxes[page_nr]['header'] = list()
    if NR_OF_COLS == 1:
        boxes[page_nr]['column'] = list()
    elif NR_OF_COLS == 2:
        boxes[page_nr]['left_column'] = list()
        boxes[page_nr]['right_column'] = list()
    elif NR_OF_COLS == 3:
        boxes[page_nr]['left_column'] = list()
        boxes[page_nr]['center_column'] = list()
        boxes[page_nr]['right_column'] = list()
    else:
        for counter in range(NR_OF_COLS):
            col = 'col_{}'.format(counter+1)
            boxes[page_nr][col] = list()

    return boxes


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


def _get_page_layout(LTPage, VERTICAL, HORIZONTAL):
    height = LTPage.height
    width = LTPage.width
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


def _get_X0_MIN(x0, X0_MIN):
    if X0_MIN == 0:
        X0_MIN = x0
    else:
        if x0 < X0_MIN:
            X0_MIN = x0

    return X0_MIN


def _get_X1_MAX(x1, X1_MAX):
    if X1_MAX == 0:
        X1_MAX = x1
    else:
        if x1 > X1_MAX:
            X1_MAX = x1

    return X1_MAX


def _get_Y0_MIN(y0, Y0_MIN):
    if Y0_MIN == 0:
        Y0_MIN = y0
    else:
        if y0 < Y0_MIN:
            Y0_MIN = y0

    return Y0_MIN


def _get_Y0_MAX(y0, Y0_MAX):
    if Y0_MAX == 0:
        Y0_MAX = y0
    else:
        if y0 > Y0_MAX:
            Y0_MAX = y0

    return Y0_MAX


def _get_Y1_MAX(y1, Y1_MAX):
    if Y1_MAX == 0:
        Y1_MAX = y1
    else:
        if y1 > Y1_MAX:
            Y1_MAX = y1

    return Y1_MAX


def _choose_col(x0, x1, X0_MIN, X1_MAX, BOX_WIDTH_MAX):
    if x0 < (X0_MIN + BOX_WIDTH_MAX):
        col = 'left_column'
    elif x0 > (X0_MIN + BOX_WIDTH_MAX) and x1 < (X1_MAX - BOX_WIDTH_MAX):
        col = 'center_column'
    else:
        col = 'right_column'

    return col


def _get_box_width(BOX_WIDTH_MAX, Y0_MAX, x0, x1, y0, y1):
    if BOX_WIDTH_MAX == 0:
        BOX_WIDTH_MAX = x1 - x0
    elif (x1 - x0) > BOX_WIDTH_MAX and y0 < y1 < Y0_MAX:
        BOX_WIDTH_MAX = x1 - x0

    return BOX_WIDTH_MAX


def _get_y_header(Y_HEADER, x0, x1, y0, y1, Y0_MAX, BOX_WIDTH_MAX):
    if y1 >= Y0_MAX:
        if Y_HEADER == 0:
            Y_HEADER = y0
        elif (x1 - x0) > BOX_WIDTH_MAX:
            Y_HEADER = y0

    return Y_HEADER


def _correct_y_header(box_upper_y, Y_HEADER):
    yise = dict()
    for y in box_upper_y:
        try:
            if yise[y] > 0:
                i = yise[y]
                yise[y] = i+1
        except KeyError:
            yise[y] = 1

    s = [{y: yise[y]} for y in sorted(yise, key=yise.get, reverse=True)]
    if s:
        for key in s[0]:
            Y_HEADER = key

    return Y_HEADER


if __name__ == '__main__':
    main()
