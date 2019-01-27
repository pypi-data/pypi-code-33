from pathlib import Path
from .miner import PdfTxtParams, PdfTxtDocument, PdfTxtLayoutAnalyzer
from .region import Region

__all__ = ["PdfTxtParams", "PdfTxtText", "Region"]


class PDFObject:
    """
    Base PDF object wrapper exposes common
    object position info.

    """

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        return getattr(self.obj, name)

    @property
    def media_box(self):
        return self.obj.bbox


class PdfTxtText(PDFObject):
    """
    Wraps up LTTextBox object.

    """

    def __init__(self, parent, text_obj):
        super(PdfTxtText, self).__init__(text_obj)
        self.page = parent if isinstance(parent, PdfTxtPage) else PdfTxtPage(parent)
        self._reset = 0

    @property
    def sort_key(self):
        return (self.y0, self.x0, self.y1, self.x1)

    @property
    def text(self):
        return self.obj.get_text().strip()

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.y0:03.2f}, {self.x0:03.2f}) '{self.text}'>"


class PdfTxtPage(PDFObject):
    """
    Wraps up Page object.

    """

    def __init__(self, page_obj):
        super(PdfTxtPage, self).__init__(page_obj)
        self.text = []

    def add(self, text_obj):
        self.text.append(PdfTxtText(self, text_obj))

    def resort_text(self):
        for x in self.text:
            x.reverse_y_axis()
        self.text.sort(key=lambda x: x.sort_key)


class PdfTxtContext:
    """
    Wraps PdfMiner in a context manager

    """

    def __init__(self, pdf_doc, pdf_pwd=""):

        self.pdf_doc = Path(pdf_doc)
        self.pdf_pwd = pdf_pwd

    def __enter__(self):

        self.fp = fp = self.pdf_doc.open(mode="rb")  # pylint: disable=W0201
        self.doc = PdfTxtDocument(fp, passwd=self.pdf_pwd)  # pylint: disable=W0201

        self.doc.assert_extractable()

        return iter(self._parse_pages())

    def _parse_pages(self):

        device = PdfTxtLayoutAnalyzer()
        interpreter = device.create_interpreter()

        for page in self.doc.create_pages():
            interpreter.process_page(page)
            yield device.get_result()

    def __exit__(self, _type, value, traceback):
        self.fp.close()
