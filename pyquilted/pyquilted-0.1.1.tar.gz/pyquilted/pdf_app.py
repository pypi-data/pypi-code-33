from pyquilted.resume_to_html import ResumeToHtml
from pyquilted.pdf_printer import PdfPrinter


class PdfApp(ResumeToHtml):
    def __init__(self, resume_file, path, style=None, options=None):
        self.style = style
        self.options = options
        self.resume_file = resume_file
        self.path = path

    def run(self):
        self.resume_to_html()
        self._print_pdf()

    def _print_pdf(self):
        PdfPrinter.from_string(self.html, self.path)
