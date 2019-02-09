import argparse
from pyquilted import __version__
from pyquilted.app_factory import AppFactory


class CliMain:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
                prog="pyquilted",
                description="pyquilted --pdf input.yml output.pdf")
        self.parser.add_argument('-v', '--version', action='version',
                                 version='%(prog)s ' + __version__)

        self.parser.add_argument('-p', '--pdf', metavar=('yml', 'pdf'),
                                 nargs=2, dest="pdf",
                                 help="print resume to pdf")
        self.parser.add_argument('-H', '--html', metavar=('yml', 'html'),
                                 nargs=2, dest='html',
                                 help="print resume to html")
        self.parser.add_argument('-s', '--sample', metavar='yml',
                                 dest='sample',
                                 help="generate sample resume in yaml")

        style_group = self.parser.add_argument_group(
                'style',
                "css styles to apply to resume content")
        style_group.add_argument('--color', metavar='"color|#rgb"',
                                 dest="name_color",
                                 help="css color code for your name")
        style_group.add_argument('--font', metavar='"font"', dest="font_main",
                                 help="css font for resume content")
        style_group.add_argument('--font-other', metavar='"font"',
                                 dest="font_other",
                                 help="css font override for heading/contacts")
        style_group.add_argument('--font-size', metavar='"size"',
                                 dest="font_size",
                                 help="css font size for resume content")

        self.args = self.parser.parse_args()

    def run(self):
        app = AppFactory(self.args).create()
        if app:
            app.run()
        else:
            self.parser.print_help()
