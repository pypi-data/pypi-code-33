from pyquilted.resume_to_html import ResumeToHtml


class HtmlApp(ResumeToHtml):
    def __init__(self, resume_file, path, style=None, options=None):
        self.style = style
        self.options = options
        self.resume_file = resume_file
        self.path = path

    def run(self):
        self.resume_to_html()
        self._print_html()

    def _print_html(self):
        with open(self.path, 'w') as f:
            f.write(self.html)
