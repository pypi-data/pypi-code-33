"""
pdftxt

Usage: pdftxt [--region=<rg>] [--pages=<pg>] [--analyze-grid | --analyze-rows]
              [--char-margin=<cm>] [--line-margin=<lm>] [--line-overlap=<lo>]
              [--word-margin=<wm>] [--box-flow=<bf>] [--collapse-lines]
              [--column-boundaries=<cb>]
              [--open-output] [--debug]
              <document> [<output>]

Options:
  --line-overlap=<lo>       Line Overlap      [Default: 0.5]
  --line-margin=<lm>        Line Margin.      [Default: 0.5]
  --char-margin=<cm>        Character Margin. [Default: 2.0]
  --word-margin=<wm>        Word Margin.      [Default: 0.1]
  --box-flow=<bf>           Box Flow.         [Default: 0.5]
  --collapse-lines          Analyze lines of text as if they
                            had no height.
  --region=<rg>             Region to assess. [Default: (0,0,0,0)]
  --pages=<pg>              Which pages to analyze. [Default: 1+]
  --analyze-grid            Parse page region as a grid.
  --column-boundaries=<cb>  Pass a list of custom column boundaries
                            to use for grid analysis.
  --analyze-rows            Parse page region as a rows.
  --open-output             Open the html file after it
                            is generated.
  --debug                   Run in debug mode.
  -h --help                 Show this screen.
  --version                 Show version.

"""
import sys
from datetime import datetime
from pathlib import Path
from docopt import docopt
from .region import fetch_region
from .api import PdfTxtParams, PdfTxtContext
from .util import parse_float_list, parse_page_notation
from . import __version__


def fetch_args():
    # pylint: disable=R0902,R0903
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
    args.output_doc = output_doc = _arg.get("<output>", None)
    args.point_measure = "point"

    args.accept_page = parse_page_notation(_arg.get("--pages", "1+"))
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
    args.column_boundaries = parse_float_list(_arg.get("--column-boundaries"))

    if output_doc:
        args.output_file = Path(output_doc)
    else:
        args.output_file = generate_default_html_filename(args)

    return args


def generate_default_html_filename(args):
    identifier = ""
    timestamp = f"-{datetime.now():%Y-%m-%d-%H%M%S}"

    if args.analyze_grid:
        identifier = "-grid"

    if args.analyze_rows:
        identifier = "-rows"

    file_name = args.pdf_doc.stem + identifier + timestamp + ".html"
    return args.pdf_doc.parent / file_name


def html(args):

    from .html import HTMLDocument

    accept_page = args.accept_page

    with PdfTxtContext(args.pdf_doc) as pdf:

        html_doc = HTMLDocument(args.pdf_doc.name)

        for page in pdf:

            if not accept_page(page.pageid):
                continue

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
                column_boundaries=args.column_boundaries,
            )

            text = analyze(region=region, layout_params=params)

            html_doc.start_page(page, region, params)

            for txt in text:
                html_doc.add_text_block(txt)

            html_doc.end_page()

        html_doc.save_to(args.output_file)

        if args.get("--open-output"):
            import subprocess

            cmd = "open"
            subprocess.call([cmd, str(args.output_file)])


def main():
    args = fetch_args()
    html(args)
