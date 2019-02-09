import pdfkit


class PdfPrinter:
    @staticmethod
    def from_file(infile, outfile):
        options = {
                "page-size": "Letter",
                "dpi": "96",
                "margin-top": "1in",
                "margin-right": "1.25in",
                "margin-bottom": "1in",
                "margin-left": "1.25in",
                "disable-smart-shrinking": None,
                "zoom": 1,
                }
        pdfkit.from_file(infile, outfile, options=options)

    @staticmethod
    def from_string(document, outfile):
        options = {
                "page-size": "Letter",
                "dpi": "96",
                "margin-top": "1in",
                "margin-right": "1.25in",
                "margin-bottom": "1in",
                "margin-left": "1.25in",
                "disable-smart-shrinking": None,
                "zoom": 1,
                }
        pdfkit.from_string(document, outfile, options=options)
