"""
grid.py provides functions used to analyze PDF characters grid arrangement.

"""
from math import floor, ceil
from statistics import median
from functools import partial
from .util import character_in_region


def iter_lanes(points):
    """
    Loop through collection of numbers (points) and yield
    the sequential groupings. Any gap in the sequence will
    produce a new grouping

    for example this sequence:

        [1, 2, 3, 7, 8, 9, 12, 13, 14]

    with yield:

        ((1, 2, 3), (7, 8, 9), (12, 13, 14))

    """
    last = -5
    lane = []
    for pt in points:
        if pt == last + 1:
            lane.append(pt)
        else:
            if lane:
                yield lane
            lane = [pt]
        last = pt
    yield lane


def get_attr(attr_name):
    def _getattr(obj):
        return getattr(obj, attr_name)

    return _getattr


pt_x0 = get_attr("x0")
pt_x1 = get_attr("x1")
pt_y0 = get_attr("y0")
pt_y1 = get_attr("y1")


def fetch_cell_boundaries(
    characters,
    start_outer_bound,
    end_outer_bound,
    fetch_char_start=None,
    fetch_char_end=None,
):
    # collect all points along the range
    all_points = set(range(floor(start_outer_bound), ceil(end_outer_bound) + 1))

    char_points = set()

    # fetch all horizontal (x) points occupied by charcters:
    for c in characters:
        for pt in range(floor(fetch_char_start(c)), ceil(fetch_char_end(c) + 1)):
            char_points.add(pt)
    # fetch all horizontal (x) points NOT occupied by characters:
    boundary_points = all_points - char_points

    # find the center of each column:
    return sorted([median(c) for c in iter_lanes(sorted(boundary_points))])


fetch_column_boundaries = partial(
    fetch_cell_boundaries, fetch_char_start=pt_x0, fetch_char_end=pt_x1
)

fetch_row_boundaries = partial(
    fetch_cell_boundaries, fetch_char_start=pt_y0, fetch_char_end=pt_y1
)


def iter_cell_bounds(grid_boundaries):
    for i in range(0, len(grid_boundaries) - 1):
        yield (grid_boundaries[i], grid_boundaries[i + 1])


class CollapsedCharacter:
    """
    When rows of text are too close together, or their bounding boxes
    overlap it is not possible, with either PdfMiner's row grouping, or by
    our row boundary logic, to easily separate those rows.

    This proxy class of PdfMiner's Char object reduces the height of a row
    down to middle pt of the characters height. This will allow us
    to effectively isolate rows in these instances.

    """

    def __init__(self, character):
        self._char = character
        # colapse the y coordinates of character to the
        # center of the character height and essentially
        # now has a height of 1 pt.
        _mid = (character.y1 - character.y0) / 2
        self._char_y0 = character.y0 + floor(_mid)
        self._char_y1 = character.y0 + ceil(_mid)

    def __getattr__(self, name):
        return getattr(self._char, name)

    @property
    def uncollapsed(self):
        return self._char

    @property
    def y0(self):
        return self._char_y0

    @property
    def y1(self):
        return self._char_y1

    def __repr__(self):
        return f'<CollapsedCharacter {self.x0},{self.y0},{self.x1},{self.y1} "{self.get_text()}">'

    @staticmethod
    def collapse(characters):
        for i in range(0, len(characters)):  # pylint: disable=consider-using-enumerate
            characters[i] = CollapsedCharacter(characters[i])

    @staticmethod
    def uncollapse(characters):
        for i in range(0, len(characters)):  # pylint: disable=consider-using-enumerate
            characters[i] = characters[i].uncollapsed


class Cell:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.characters = []
        self._text = ""

    @property
    def region(self):
        return (self.x0, self.y0, self.x1, self.y1)

    def __contains__(self, c):
        return character_in_region(c, self.x0, self.y0, self.x1, self.y1)

    def chars_to_str(self):
        return "".join([c.get_text() for c in self.characters])

    @property
    def text(self):
        return "".join([t.get_text() for t in self._text])

    @text.setter
    def text(self, value):
        self._text = value

    def get_text(self):
        return self.text

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.y1 - self.y0

    def __str__(self):
        return self.text

    def __repr__(self):
        txt = self.text
        if len(txt) > 20:
            txt = txt[:20] + "..."
        return f'<Cell {self.x0},{self.y0},{self.x1},{self.y1} "{txt}">'


class Table:
    def __init__(self):
        self.rows = []
        self.current_row = None

    def add_row(self):
        self.current_row = new_row = []
        self.rows.append(new_row)
        return new_row

    def add_cell(self, cell):
        self.current_row.append(cell)

    def __getitem__(self, key):
        return self.rows[key]

    def __iter__(self):
        for row in self.rows:
            for cell in row:
                yield cell


def fetch_table_cells(row_boundaries, column_boundaries):
    """
    Returns a list of row/column bounding boxes (x0, y0, x1, y1).

    """
    table = Table()
    for y0, y1 in iter_cell_bounds(row_boundaries):
        table.add_row()
        for x0, x1 in iter_cell_bounds(column_boundaries):
            table.add_cell(Cell(x0, y0, x1, y1))
    return table


def fetch_row_cells(row_boundaries, x0, x1):
    rows = []
    for y0, y1 in iter_cell_bounds(row_boundaries):
        rows.append(Cell(x0, y0, x1, y1))
    return rows


def table_cells_to_regions(table):
    """
    Transform from a table of Cell objects to a table of cell region coordinates.
    This is primarily for testing purposes.

    """
    _table = []
    for row in table.rows:
        _row = []
        for cell in row:
            _row.append(cell.region)
        _table.append(_row)
    return _table


def allocate_characters_to_table(characters, table):
    """
    Apply characters to individual Cell objects they fall within on the page.

    """
    for char in characters:
        for cell in table:
            if char in cell:
                cell.characters.append(char)
