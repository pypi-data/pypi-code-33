'''
pdf2txt_get_header.py

:param url: A URL pointing at a PDF file with 2 columns and a header
:returns: Returns the y value if there is a header
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
    pdf = io.BytesIO(req.content)
    return pdf


def main():
    '''
    A wrapper function to organize the steps involved to convert a PDF into text:
        1.  Get the PDF file using a URL
        2.  Find out if there are two columns
        3.  If yes, is there a header?
        4.  What is its lower y value?
    '''
    pdf = _get_pdf_file(url=None)
    pdf = open('./data/three_col_horizontal.pdf', 'rb')
    _is_header(pdf)



def _is_header(pdf):
    '''
    If there are two columns, look if there is a box that is wider than a column.
    If yes, check out its y0 value. If it's higher than the bigges x1 value, this
    is where the header begins.
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
    Y_HEADER = 0
    BOX_WIDTH_MAX = 0
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        LTPage = device.get_result()
        if LTPage.height > LTPage.width:
            VERTICAL = True
        else:
            VERTICAL = False
        print('VERTICAL:', VERTICAL)
        for LTLine in LTPage:
            x0, x1, y0, y1 = _get_box_borders(LTLine)
            #print(x0, x1, y0, y1, BOX_WIDTH_MAX)
            if VERTICAL:
                if BOX_WIDTH_MAX == 0:
                    BOX_WIDTH_MAX = x1 - x0
                    print('BOX_WIDTH_MAX: {} - {} = {}'.format(x1, x0, BOX_WIDTH_MAX))
                elif (x1 - x0) > BOX_WIDTH_MAX and y0 < x1:
                    BOX_WIDTH_MAX = x1 - x0
                    print('BOX_WIDTH_MAX{} - {} = {}'.format(x1, x0, BOX_WIDTH_MAX))
                elif (x1 - x0) > BOX_WIDTH_MAX and y0 > x1:
                    Y_HEADER = y0
            else:
                if BOX_WIDTH_MAX == 0:
                    BOX_WIDTH_MAX = x1 - x0
                    print('BOX_WIDTH_MAX: {} - {} = {}'.format(x1, x0, BOX_WIDTH_MAX))
                elif (x1 - x0) > BOX_WIDTH_MAX and y0 < x1:
                    BOX_WIDTH_MAX = x1 - x0
                    print('BOX_WIDTH_MAX: {} - {} = {}'.format(x1, x0, BOX_WIDTH_MAX))
                elif (x1 - x0) > BOX_WIDTH_MAX and y0 > x1:
                    Y_HEADER = y0


        print('Y_HEADER:', Y_HEADER)


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



if __name__ == '__main__':
    main()
