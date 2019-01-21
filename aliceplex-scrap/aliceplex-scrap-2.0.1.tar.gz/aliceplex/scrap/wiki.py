import re
from datetime import date, datetime
from enum import Enum
from functools import lru_cache
from itertools import product
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

import requests
from aliceplex.schema import Episode, Person
from aliceplex.schema.format import normalize
from bs4 import BeautifulSoup
from bs4.element import Tag

from aliceplex.scrap.base import EpisodeScraper
from aliceplex.scrap.utils import default

__all__ = [
    "WikiTableScraper", "SmartWikiScrapper", "JpSmartWikiScrapper",
    "WikiFields"
]
T = TypeVar("T")


class WikiFields(Enum):
    Title = "title"
    Aired = "aired"
    Directors = "directors"
    Writers = "writers"


class WikiTableScraper(EpisodeScraper):
    def __init__(self, url: str,
                 table: int = 0,
                 mapping: Dict[WikiFields, int] = None,
                 multiple_row: Optional[int] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.table_offset = table
        self.mapping = default(mapping, {})
        self.multiple_row = multiple_row

    @lru_cache(maxsize=None)
    def table(self) -> List[List[str]]:
        response = requests.get(self.url)
        html = response.text
        soup = BeautifulSoup(html, "html5lib")
        tables = soup.find_all("table", class_="wikitable")
        if not 0 <= self.table_offset < len(tables):
            raise IndexError(f"There are only {len(tables)} table(s).")
        return table_as_dict(tables[self.table_offset])

    def convert(self, field: WikiFields) -> Callable[[Any], Any]:
        return {
            WikiFields.Title: self.parse_title,
            WikiFields.Aired: self.parse_date,
            WikiFields.Directors: self.parse_directors,
            WikiFields.Writers: self.parse_writers
        }.get(field, str)

    def join(self, field: WikiFields) -> Callable[[Any], Any]:
        return {
            WikiFields.Title: self.join_title,
            WikiFields.Aired: self.join_aired,
            WikiFields.Directors: self.join_directors,
            WikiFields.Writers: self.join_writers
        }.get(field, str)

    def scrap(self, episode_num: int, episode: Episode):
        if self.multiple_row is None or self.multiple_row < 0:
            self.single_scrap(episode_num, episode)
        else:
            self.multi_scrap(episode_num, episode)

    def single_scrap(self, episode_num: int, episode: Episode):
        row = self.row(episode_num)
        for field, col in self.mapping.items():
            value = row[col]
            setattr(episode, field.value, self.convert(field)(value))

    def multi_scrap(self, episode_num: int, episode: Episode):
        row_nums = self.row_map()[self.row_num(episode_num)]
        for field, col in self.mapping.items():
            values = []
            for row_num in row_nums:
                row = self.table()[row_num]
                values.append(self.convert(field)(row[col]))
            value = self.join(field)(values)
            setattr(episode, field.value, value)

    def row_num(self, episode_num: int):
        return episode_num

    def row(self, episode_num: int):
        return self.table()[self.row_num(episode_num)]

    @lru_cache(maxsize=None)
    def row_map(self) -> Dict[int, List[int]]:
        row_map: Dict[int, List[int]] = {}
        index = 0
        prev = None
        for row, cols in enumerate(self.table()):
            if row_map.get(index) is None:
                row_map[index] = []
            current = cols[self.multiple_row]
            if current == prev or row == 0:
                row_map[index].append(row)
            else:
                index += 1
                row_map[index] = [row]
            prev = current
        return row_map

    def parse_title(self, value: str) -> List[str]:
        title = normalize(value)
        title = re.sub(r"\n+", " ", title)
        return [title]

    def parse_date(self, value: str) -> date:
        return datetime.strptime(value, "%Y-%m-%d").date()

    def parse_directors(self, value: str) -> List[Person]:
        return [Person(name=value) for value in value.split()]

    def parse_writers(self, value: str) -> List[Person]:
        return [Person(name=value) for value in value.split()]

    def join_title(self, values: List[str]) -> List[str]:
        return values

    def join_aired(self, values: List[date]) -> date:
        if len(values) != 1:
            self.logger.warn("More than 1 date")
        return values[0]

    def join_set(self, values: List[str]) -> List[str]:
        exists = set()
        result = []
        for value in values:
            if value not in exists:
                exists.add(value)
                result.append(value)
        return result

    def join_directors(self, values: List[str]) -> List[Person]:
        return [Person(name=value) for value in self.join_set(values)]

    def join_writers(self, values: List[str]) -> List[Person]:
        return [Person(name=value) for value in self.join_set(values)]


def table_as_dict(table_tag: Tag):
    """
    https://stackoverflow.com/a/48451104/3673259
    """
    # pylint: disable=too-many-locals
    rowspans = []  # track pending row_spans
    rows = table_tag.find_all("tr")

    # first scan, see how many columns we need
    col_count = 0
    for r, row in enumerate(rows):
        cells = row.find_all(["td", "th"], recursive=False)
        # count columns (including spanned).
        # add active row_spans from preceding rows
        # we *ignore* the colspan value on the last cell, to prevent
        # creating "phantom" columns with no actual cells, only extended
        # colspans. This is achieved by hardcoding the last cell width as 1.
        # a colspan of 0 means “fill until the end” but can really only apply
        # to the last cell; ignore it elsewhere.
        col_count = max(
            col_count,
            sum(int(c.get("colspan", 1)) or 1 for c in cells[:-1]) +
            len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom.
        rowspans += [int(c.get("rowspan", 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    # it doesn"t matter if there are still rowspan numbers "active"; no extra
    # rows to show in the table means the larger than 1 rowspan numbers in the
    # last table row are ignored.

    # build an empty matrix for all possible cells
    # noinspection PyUnusedLocal
    table = [[None] * col_count for row in rows]

    # fill matrix from row data
    rowspans = {}  # track pending row_spans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  # how many columns are skipped due to row and colspans
        th_td = row_elem.find_all(["td", "th"], recursive=False)
        for col, cell in enumerate(th_td):
            # adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            # fill table data
            rowspan = rowspans[col] = (int(cell.get("rowspan", 1)) or
                                       len(rows) - row)
            colspan = int(cell.get("colspan", 1)) or col_count - col
            # next column is offset by the colspan
            span_offset += colspan - 1

            # delete sup tag
            for sup in cell.find_all("sup"):
                sup.decompose()

            for sup in cell.find_all("style"):
                sup.decompose()

            for ruby in cell.select("ruby"):  # type: Tag
                if ruby.select("rp"):
                    continue
                for rt in ruby.select("rt"):
                    rt.insert_before("(")
                    rt.insert_after(")")
            for br in cell.select("br"):
                br.replace_with("\n")
            value = cell.get_text()
            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass

        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    return table


class SmartWikiScrapper(WikiTableScraper):
    def __init__(self, url: str,
                 tag: str,
                 tag_offset: int = 0,
                 expect: Dict[Tuple[int, int], str] = None,
                 **kwargs):
        super().__init__(url, **kwargs)
        self.tag = tag
        self.tag_offset = tag_offset
        self.expect = default(expect, {})

    @lru_cache(maxsize=None)
    def table(self) -> List[List[str]]:
        response = requests.get(self.url)
        html = response.text
        soup = BeautifulSoup(html, "html5lib")
        tag_element = soup.select_one(f"#{self.tag}")
        table = tag_element.find_next("table", class_="wikitable")
        for i in range(0, self.tag_offset):
            if table is None:
                raise IndexError(f"There are only {i} table(s).")
            table = table.find_next("table", class_="wikitable")
        return table_as_dict(table)

    def scrap(self, episode_num: int, episode: Episode):
        for key, value in self.expect.items():
            row, col = key
            if self.table()[row][col] != value:
                raise ValueError(f"{value} is expected at row {row} and"
                                 f" column {col}.")
        super().scrap(episode_num, episode)

    def assert_expect(self):
        for key, value in self.expect.items():
            row, col = key
            assert self.table()[row][col] == value, \
                f"{value} is expected at row {row} and  column {col}."


class JpSmartWikiScrapper(SmartWikiScrapper):
    def __init__(self, subject: str,
                 tag: str = "各話リスト",
                 tag_offset: int = 0,
                 **kwargs):
        url = f"https://ja.wikipedia.org/wiki/{subject}"
        super().__init__(url, tag, tag_offset, **kwargs)
