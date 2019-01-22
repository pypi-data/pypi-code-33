from collections import namedtuple
from .util import PdfTxtError

PT2IN = 72.571_429
PT2CM = 28.346_456_7


def pt2in(points):
    return points / PT2IN


def pt2cm(points):
    return points / PT2CM


def in2pt(inches):
    return inches * PT2IN


def cm2pt(cm):
    return cm * PT2CM


Region = namedtuple("Region", "x0 y0 x1 y1")


def parse_region(text, x1=0, y1=0):
    """
    Parse commandline argument text in the form of:

        "(10,20,30,40)"

    Into a Region tuple:

        Region(x0=10, y0=20, x1=30, y1=40)

    The x1 and y1 arguments are place holders for the
    pages x1 and y1 coordinates.

    """
    if isinstance(text, list):
        text = text[0]
    coord = [float(r.strip()) for r in text.strip(")").strip("(").split(",")]

    if len(coord) != 4:
        raise PdfTxtError(
            'Region argument must contain 4 arguments. Example: "(0,0,45,100)".'
        )

    # The default region is the total page, which is represented as
    # "(0,0,0,0)". The x1 and y1 coordinates are unknown until the page
    # has been parsed. In this case, we need to swap out the x1 and y1
    # zero values in the default for the actual x1 and y1 page coordinates.
    coord[2] = x1 if coord[2] == 0 else coord[2]
    coord[3] = y1 if coord[3] == 0 else coord[3]

    if coord[2] <= 0 or coord[3] <= 0 or coord[2] < coord[0] or coord[3] < coord[1]:
        raise PdfTxtError(
            'X1 and y1 coordinates must be greater than 0. Example: "(0,0,45,100)".'
        )

    return Region(*coord)


def calculate_predefined_regions(width, height):
    """
    Generate a list of pre-defined Regions based on the
    provided width and height variables.

    """
    half_height = height / 2
    half_width = width / 2

    return {
        "full-page": Region(0, 0, width, height),
        "top-half": Region(0, half_height, width, height),
        "bottom-half": Region(0, 0, width, half_height),
        "left-half": Region(0, 0, half_width, height),
        "right-half": Region(half_width, 0, width, height),
        "top-left": Region(0, half_height, half_width, height),
        "top-right": Region(half_width, half_height, width, height),
        "bottom-left": Region(0, 0, half_width, half_height),
        "bottom-right": Region(half_width, 0, width, half_height),
    }


def fetch_region(page, region_arg):
    """
    Determine the region from the commandline arguments.

    """
    predefined_regions = calculate_predefined_regions(page.width, page.height)
    region = predefined_regions.get(region_arg)

    if not region:
        region = parse_region(region_arg, page.x1, page.y1)

    return region
