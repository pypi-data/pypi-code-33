"""
pdftxt

Usage: pdftxt [--region=<rg>] [--analyze-grid | --analyze-rows]
              [--char-margin=<cm>] [--line-margin=<lm>] [--line-overlap=<lo>]
              [--word-margin=<wm>] [--box-flow=<bf>] [--collapse-lines]
              [--open-output] [--debug]
              <document> [<output>]

Options:
  --line-overlap=<lo> Line Overlap      [Default: 0.5]
  --line-margin=<lm>  Line Margin.      [Default: 0.5]
  --char-margin=<cm>  Character Margin. [Default: 2.0]
  --word-margin=<wm>  Word Margin.      [Default: 0.1]
  --box-flow=<bf>     Box Flow.         [Default: 0.5]
  --collapse-lines    Analyze lines of text as if they
                      had no height.
  --region=<rg>       Region to assess. [Default: (0,0,0,0)]
  --analyze-grid      Parse page region as a grid.
  --analyze-rows      Parse page region as a rows.
  --open-output       Open the html file after it
                      is generated.
  --debug             Run in debug mode.
  -h --help           Show this screen.
  --version           Show version.

"""
import sys
from datetime import datetime
from pathlib import Path
from docopt import docopt
from .region import fetch_region
from .api import PdfTxtParams, PdfTxtContext
from . import __version__


def fetch_args():
    _arg = docopt(__doc__, argv=sys.argv[1:], version=f"pdft v{__version__}")

    class Namespace:
        def get(self, name):
            return self.args.get(name)

    args = Namespace()

    args.debug = _arg.get("--debug", False)

    if args.debug is True:
        print(_arg)

    args.args = _arg
    args.pdf_doc = Path(_arg["<document>"])
    args.output_doc = _arg.get("<output>", None)
    args.point_measure = "point"

    args.region = _arg.get("--region")
    args.analyze_grid = _arg.get("--analyze-grid", False)
    args.analyze_rows = _arg.get("--analyze-rows", False)
    args.expand_bbox = int(_arg.get("--expand-bbox", 0))
    args.line_overlap = float(_arg["--line-overlap"])
    args.char_margin = float(_arg["--char-margin"])
    args.line_margin = float(_arg["--line-margin"])
    args.word_margin = float(_arg["--word-margin"])
    args.boxes_flow = float(_arg["--box-flow"])
    args.collapse_lines = _arg.get("--collapse-lines", False)

    return args


def html(args):

    from .html import HTMLDocument

    with PdfTxtContext(args.pdf_doc) as pdf:

        html_doc = HTMLDocument(args.pdf_doc.name)

        for page in pdf:

            region = fetch_region(page, args.region)

            if args.debug:
                print(f"region: {region}")

            analyze = page.analyze

            if args.analyze_grid:
                analyze = page.analyze_grid
            elif args.analyze_rows:
                analyze = page.analyze_rows

            params = PdfTxtParams(
                line_overlap=args.line_overlap,
                char_margin=args.char_margin,
                line_margin=args.line_margin,
                word_margin=args.word_margin,
                boxes_flow=args.boxes_flow,
                collapse_lines=args.collapse_lines,
            )

            text = analyze(region=region, layout_params=params)

            html_doc.start_page(
                page,
                region,
                args.line_overlap,
                args.char_margin,
                args.line_margin,
                args.word_margin,
                args.boxes_flow,
                args.collapse_lines,
            )

            for txt in text:
                html_doc.add_text_block(txt)

            html_doc.end_page()

        if args.output_doc:
            output_file = Path(args.output_doc)
        else:
            identifier = ""
            timestamp = f"-{datetime.now():%Y-%m-%d-%H%M%S}"

            if args.analyze_grid:
                identifier = "-grid"
            if args.analyze_rows:
                identifier = "-rows"

            file_name = args.pdf_doc.stem + identifier + timestamp + ".html"
            output_file = args.pdf_doc.parent / file_name

        html_doc.save_to(output_file)

        if args.get("--open-output"):
            import subprocess

            cmd = "open"
            subprocess.call([cmd, str(output_file)])


def main():
    args = fetch_args()
    html(args)
