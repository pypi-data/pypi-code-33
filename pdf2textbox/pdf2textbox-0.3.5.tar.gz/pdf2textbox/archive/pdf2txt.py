# pdf2txt.py

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFNoOutlines
from pdfminer.pdfdocument import PDFDocument


def with_pdf():
    """
    Open the pdf document, and apply the function, returning the results
    code from http://denis.papathanasiou.org/archive/2010.08.04.post.pdf
    """
    #pdf_doc = './data/three_col_horizontal.pdf'
    #pdf_doc = './data/Id=MMP16%2F139_14622_14624.pdf'  # yet impossible
    pdf_doc = './data/Id=MMP15%2F57_5694_5696.pdf'
    result = None
    try:
        # open the pdf file
        fp = open(pdf_doc, 'rb')
        # create a parser object associated with the file object
        parser = PDFParser(fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser, password=None)
        # connect the parser and document objects
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        if doc.is_extractable:
            # apply the function and return the result
            toc = _parse_toc(doc)
            print('toc', toc)
            result = toc

        # close the pdf file
        fp.close()

    except IOError:
    # the file doesn't exist or similar problem
        print('some error')

    print('result', result)
    return result


def _parse_toc(doc):
    """
    With an open PDFDocument object, get the table of contents (toc) data
    [this is a higher-order function to be passed to with_pdf()]
    code from http://denis.papathanasiou.org/archive/2010.08.04.post.pdf
    """

    toc = []
    try:
        outlines = doc.get_outlines()
        for (level, title, dest, a, se) in outlines:
            toc.append( (level, title) )
    except PDFNoOutlines:
        pass

    return toc

def get_toc(pdf_doc, pdf_pwd=''):
    """
    Return the table of contents (toc), if any, for this pdf file
    code from http://denis.papathanasiou.org/archive/2010.08.04.post.pdf
    """

    return with_pdf(pdf_doc, pdf_pwd, _parse_toc)


if __name__ == '__main__':
    with_pdf()
