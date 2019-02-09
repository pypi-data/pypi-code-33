from pyquilted.html_app import HtmlApp
from pyquilted.pdf_app import PdfApp
from pyquilted.sample_app import SampleApp
from pyquilted.quilted.style import Style


class AppFactory:
    def __init__(self, args):
        self.args = vars(args)
        self.options = Options(**self.args)
        self.style = Style(**self.args)

    def create(self):
        app = None
        if self.options.sample:
            app = SampleApp('/sample/resume.yml', self.options.sample)
        elif self.options.html:
            app = HtmlApp(self.options.html[0], self.options.html[1],
                          style=self.style)
        elif self.options.pdf:
            app = PdfApp(self.options.pdf[0], self.options.pdf[1],
                         style=self.style)
        return app


class Options:
    def __init__(self, pdf=None, html=None, sample=None, sample_got=None,
                 **kwargs):
        self.pdf = pdf
        self.html = html
        self.sample = sample
        self.sample_got = sample_got
