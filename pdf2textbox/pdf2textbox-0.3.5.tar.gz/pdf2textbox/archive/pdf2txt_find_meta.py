'''
pdf2txt_find_meta.py

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


def pdf2txt_find_meta():
    '''
    A wrapper function to organize the steps involved to convert a PDF into text:
        1.  Get the PDF file using a URL
        2.  Find number of columns
        3.  Is there a header? What are its borders?
    '''
    pdf = _get_pdf_file(url=None)
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
    #resolve = resolve1(document.catalog)
    boxes = dict()
    page_nr = 0
    X0_MIN = 0
    X1_MAX = 0
    Y0_MIN = 0
    Y1_MAX = 0
    BOX_WIDTH_MAX = 0
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        LTPage = device.get_result()
        page_nr += 1
        boxes[page_nr] = dict()
        i = 1
        for LTLine in LTPage:
            x0, x1, y0, y1 = _get_box_borders(LTLine)
            X0_MIN = _get_X0_MIN(X0_MIN, x0)
            X1_MAX = _get_X1_MAX(X1_MAX, x1)
            Y0_MIN = _get_Y0_MIN(Y0_MIN, y0)
            Y1_MAX = _get_Y1_MAX(Y1_MAX, y1)
            if BOX_WIDTH_MAX == 0:
                BOX_WIDTH_MAX = x1 - x0
            else:
                if (x1 - x0) > BOX_WIDTH_MAX:
                    BOX_WIDTH_MAX = x1 - x0

            try:
                text = LTLine.get_text()
            except AttributeError:
                text = None

            key = 'box_{}'.format(i)
            box = namedtuple('box', ['x0', 'x1', 'y0', 'y1', 'text'])
            boxes[page_nr][key] = box(x0, x1, y0, y1, text)
            i += 1
    _show_box_borders(boxes)
    dprint(BOX_WIDTH_MAX)
    dprint(X0_MIN)
    dprint(X1_MAX)



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


def _show_box_borders(boxes):
    for key, val in boxes.items():
        #print('page', key)
        left_border = list()
        left_col_left_border = list()
        right_col_left_border = list()
        height = list()
        for kk, vv in val.items():
            if vv.x0 not in left_border:
                left_border.append(vv.x0)
            if vv.y0 not in height:
                height.append(vv.y0)
        length_max = 0
        for i in left_border:
            length = len(str(i))
            if length > length_max:
                length_max = length
        for i in left_border:
            if len(str(i)) < length_max:
                left_col_left_border.append(i)
            else:
                right_col_left_border.append(i)
    dprint(sorted(left_col_left_border))
    dprint(sorted(right_col_left_border))


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


def _print_page_attributes(page):
    print('dir(page)')
    print(dir(page))
    #print(page.attrs)                      # {'Tabs': /'S', 'Group': {'S': /'Tr...
    #print(page.mediabox)                   # [0, 0, 595.32, 841.92]
    #print(page.cropbox)                    # same as mediabox
    #print(page.pageid)                     # pagenumber?
    #print(page.contents)                   # [<PDFStream(2): raw=7846, {'Filter':
                                            #   /'FlateDecode', 'Length': 7845}>]
    #print(page.resources)                  # {'ExtGState': {'GS7': <PDFObjRef:3...
    #print(page.beads)                      # None
    #print(page.annots)                     # None
    #print(page.lastmod)                    # None
    #print('dir(page.doc)')
    #print(dir(page.doc))
    #print(page.doc.info)                   # [{'ModDate': b"D:20180605092459+02'...
    #print(page.doc.catalog)                # {'PageMode': /'UseOutlines', 'Type'...
    #print(page.doc.find_xref(parser=parser))
                                            # 96595
    #print(page.doc.get_outlines)           # <bound method PDFDocument.get_outl...
    #print(page.doc.get_outlines())         # <generator object PDFDocument.get_...
    #print(page.doc.xrefs)                  # [<PDFXRef: offsets=dict_keys([1, 2...
    #print('dir(page.doc.xrefs)')
    #print(dir(page.doc.xrefs))
    #print('dir(LTPage)')
    #print(dir(LTPage))
    #print(LTPage.add)                      # <bound method LTContainer.add of ...
    #print(LTPage.analyze)                  # <bound method LTLayoutContainer.a...
    #print(LTPage.analyze(laparams))        # None
    #print(LTPage.bbox)                     # (0, 0, 595.32, 841.92)
    #print(LTPage.extend)                   # <bound method LTContainer.extend ...
    #print(LTPage.group_objects)            # <bound method LTLayoutContainer. ...
    #print(dir(LTPage.group_textboxes))     # <bound method LTLayoutContainer. ...
    #print(LTPage.group_textlines)          # <bound method LTLayoutContainer. ...
    #print(LTPage.groups)                   # [<LTTextGroupLRTB 56.640, 42.586,
                                            #   541.541, 797.571>]
    #print(LTPage.hdistance)                # <bound method LTComponent.hdista ...
    #print(LTPage.height)                   # 841.92
    #print(LTPage.width)                    # 594.32
    #print(LTPage.hoverlap)                 # <bound method LTComponent.hoverl ...
    #print(LTPage.is_empty)                 # <bound method LTComponent.is_emp ...
    #print(LTPage.is_hoverlap)              # <bound method LTComponent.is_hov ...
    #print(LTPage.pageid)                   # same as page.pageid
    #print(LTPage.set_bbox)                 # <bound method LTComponent.set_bb ...
    #print(LTPage.vdistance)                # <bound method LTComponent.vdista ...
    #print(LTPage.x0)                       # 0
    #print(LTPage.x1)                       # 595.32
    #print(LTPage.y0)                       # 0
    #print(LTPage.y1)                       # 841.92


def _print_LTLine_attributes(LTLine):
    print('dir(LTLine)')
    print(dir(LTLine))
    #print()
    #print(LTLine.add)
    #print(LTLine.analyze)
    #print(LTLine.get_text)
    #print(dir(LTLine.get_text))


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
    pdf2txt_find_meta()
