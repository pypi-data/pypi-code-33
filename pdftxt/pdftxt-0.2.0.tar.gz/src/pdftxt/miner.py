"""
miner.py provides direct class overrides from PdfMiner.Six for use in PDFtxt.

"""
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams, LTPage, LTChar, LTTextBoxVertical, IndexAssigner
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import apply_matrix_pt
from pdftxt.grid import fetch_column_boundaries, fetch_row_boundaries
from pdftxt.grid import fetch_table_cells, fetch_row_cells
from pdftxt.grid import allocate_characters_to_table
from pdftxt.grid import CollapsedCharacter
from pdftxt.util import character_in_region
from pdftxt.util import fetch_left_most_coordinate
from pdftxt.util import fetch_right_most_coordinate


def is_white_space(txtobj):
    return txtobj.get_text().strip() != ""


class PdfTxtParams(LAParams):
    """Wraps LAParams, adding the existing
    PDFMiner `exclude_white_space` option and the
    PdfTxt-specific option `collapse_lines`.

    """

    # pylint: disable=too-many-arguments,too-few-public-methods
    def __init__(
        self,
        line_overlap=0.5,
        char_margin=2.0,
        line_margin=0.5,
        word_margin=0.1,
        boxes_flow=0.5,
        collapse_lines=False,
        exclude_white_space=True,
    ):

        super(PdfTxtParams, self).__init__(
            line_overlap=line_overlap,
            char_margin=char_margin,
            line_margin=line_margin,
            word_margin=word_margin,
            boxes_flow=boxes_flow,
        )
        self.collapse_lines = collapse_lines
        self.exclude_white_space = exclude_white_space


def make_param_obj(line_overlap, char_margin, line_margin, word_margin, boxes_flow):
    laparams = LAParams()
    laparams.line_overlap = line_overlap
    laparams.char_margin = char_margin
    laparams.line_margin = line_margin
    laparams.word_margin = word_margin
    laparams.boxes_flow = boxes_flow
    return laparams


class PdfTxtPage(LTPage):
    """
    Inherits pdfminer LTPage object and changes the functionality to:

        1. ignore everything but LTChar objects in the analysis method
        2. include the ability to filter for and analyze smaller regions of the page.

    """

    def __init__(self, pageno, bbox, rotate=0):
        super(PdfTxtPage, self).__init__(pageno, bbox, rotate=rotate)
        # filter out all the character objects in the page
        self._txt_objs = None

    def fetch_characters(self):
        self.characters = list(filter(lambda obj: isinstance(obj, LTChar), self))

    def _fetch_bounding_box(self, x0=None, y0=None, x1=None, y1=None):
        # default coordinates to page size
        x1 = self.x1 if not x1 else x1
        y1 = self.y1 if not y1 else y1
        x0 = self.x0 if not x0 else x0
        y0 = self.y0 if not y0 else y0
        return x0, y0, x1, y1

    def filter_characters(self, x0=None, y0=None, x1=None, y1=None):
        x0, y0, x1, y1 = self._fetch_bounding_box(x0, y0, x1, y1)

        fchar = []
        for c in self.characters:
            if character_in_region(c, x0, y0, x1, y1):
                fchar.append(c)
        return fchar

    def _analyze_characters(self, characters, laparams, exclude_white_space=True):
        # convert text objects into text lines
        textlines = list(self.group_objects(laparams, characters))
        textlines = list(filter(lambda obj: not obj.is_empty(), textlines))

        # convert text lines in to text boxes
        textboxes = list(self.group_textlines(laparams, textlines))

        if -1 <= laparams.boxes_flow and laparams.boxes_flow <= +1 and textboxes:
            self.groups = self.group_textboxes(laparams, textboxes)
            assigner = IndexAssigner()
            for group in self.groups:
                group.analyze(laparams)
                assigner.run(group)
            textboxes.sort(key=lambda box: box.index)
        else:

            def getkey(box):
                if isinstance(box, LTTextBoxVertical):
                    return (0, -box.x1, box.y0)
                return (1, box.y0, box.x0)

            textboxes.sort(key=getkey)

        if exclude_white_space:
            return list(filter(is_white_space, textboxes))

        return textboxes

    def analyze(self, region, layout_params):
        """Does standard PDFMiner analysis, but only on characters within
        the selected region.

        Parameters deviat from parent class method.

        """
        # pylint: disable=arguments-differ
        characters = self.filter_characters(
            x0=region.x0, y0=region.y0, x1=region.x1, y1=region.y1
        )

        if not characters:
            return []

        return self._analyze_characters(
            characters,
            layout_params,
            exclude_white_space=layout_params.exclude_white_space,
        )

    def analyze_grid(self, region, layout_params):
        """Analyzes the region for natural vertical and horizontal gaps in the text
        that extend to the edges of the region and returns text objects organized
        by table/row/cell.

        """
        characters = self.filter_characters(
            x0=region.x0, y0=region.y0, x1=region.x1, y1=region.y1
        )

        #  import ipdb;ipdb.set_trace()
        if not characters:
            return []

        if layout_params.collapse_lines is True:
            CollapsedCharacter.collapse(characters)

        columns = fetch_column_boundaries(characters, region.x0, region.x1)
        rows = fetch_row_boundaries(characters, region.y0, region.y1)

        table = fetch_table_cells(rows, columns)
        allocate_characters_to_table(characters, table)

        for cell in table:

            if layout_params.collapse_lines is True:
                CollapsedCharacter.uncollapse(cell.characters)

            if not cell.characters:
                continue

            cell.text = self._analyze_characters(
                cell.characters,
                layout_params,
                exclude_white_space=layout_params.exclude_white_space,
            )

        return table

    def analyze_rows(self, region, layout_params):
        """Analyzes the region for the natural horizontal gap in the text
        that extend from the left to right edges of the region and
        returns text objects organized by table and row.

        """
        characters = self.filter_characters(
            x0=region.x0, y0=region.y0, x1=region.x1, y1=region.y1
        )

        if not characters:
            return []

        if layout_params.collapse_lines is True:
            CollapsedCharacter.collapse(characters)

        x0 = fetch_left_most_coordinate(characters)
        x1 = fetch_right_most_coordinate(characters)

        row_boundaries = fetch_row_boundaries(characters, region.y0, region.y1)
        rows = fetch_row_cells(row_boundaries, x0, x1)

        allocate_characters_to_table(characters, rows)

        for cell in rows:

            if layout_params.collapse_lines is True:
                CollapsedCharacter.uncollapse(cell.characters)

            if not cell.characters:
                continue

            text = self._analyze_characters(
                cell.characters,
                layout_params,
                exclude_white_space=layout_params.exclude_white_space,
            )
            cell.text = text

        return rows


class PdfTxtLayoutAnalyzer(PDFLayoutAnalyzer):
    """
    Inherits PDFLayoutAnalyzer, replacing the LTPage object
    with pdftxt.PDFTextPage object, and removes the
    text analysis to be explicity called by the user.

    We are also embedding the resource manager and PDFPageInterpreter
    objects in this class.

    """

    def __init__(self):
        # creating the resource manager here
        # examples show this as being external
        self.rsrcmgr = rsrcmgr = PDFResourceManager()
        super(PdfTxtLayoutAnalyzer, self).__init__(rsrcmgr)

    def begin_page(self, page, ctm):
        # override existing - only change here
        # is replacement of LTPage object with a PdfTxtPage
        (x0, y0, x1, y1) = page.mediabox
        (x0, y0) = apply_matrix_pt(ctm, (x0, y0))
        (x1, y1) = apply_matrix_pt(ctm, (x1, y1))
        mediabox = (0, 0, abs(x0 - x1), abs(y0 - y1))
        self.cur_item = PdfTxtPage(self.pageno, mediabox)

    def end_page(self, page):
        # override existing, skipping the self.cur_item.analyse() step
        assert not self._stack, str(len(self._stack))
        assert isinstance(self.cur_item, LTPage), str(type(self.cur_item))
        self.pageno += 1
        self.cur_item.fetch_characters()
        self.receive_layout(self.cur_item)

    def get_result(self):
        return self.cur_item

    def create_interpreter(self):
        # convenience function
        return PDFPageInterpreter(self.rsrcmgr, self)


class PdfTxtDocument(PDFDocument):
    def __init__(self, pdf_file_handle, passwd=""):
        parser = PDFParser(pdf_file_handle)
        super(PdfTxtDocument, self).__init__(parser, password=passwd)

    def assert_extractable(self):
        if not self.is_extractable:
            raise PDFTextExtractionNotAllowed

    def create_pages(self):
        return PDFPage.create_pages(self)
