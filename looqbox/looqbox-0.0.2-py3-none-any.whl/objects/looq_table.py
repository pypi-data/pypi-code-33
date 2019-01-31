from looqbox.objects.looq_object import LooqObject
from looqbox.objects.table_head import TableHead
from looqbox.objects.table_body import TableBody
from looqbox.objects.table_footer import TableFooter
import json


class ObjTable(LooqObject):

    def __init__(self, data=None, name="objTab", title=None, head_group=None, head_group_tooltip=None, head_style=None,
                 head_tooltip=None, value_format=None, value_style=None, value_tooltip=None, value_link=None,
                 col_range=None, row_style=None, row_format=None, row_link=None, row_tooltip=None, row_range=None,
                 total=None, total_link=None, total_style=None, total_tooltip=None, show_highlight=True,
                 pagination_size=0, searchable=False, search_string="", show_border=True, show_head=True,
                 show_option_bar=True, sortable=True, striped=True, framed=False, framed_title=None, stacked=True,
                 table_class=None):

        super().__init__()
        if table_class is None:
            table_class = []
        if framed_title is None:
            framed_title = {}
        self.data = data
        self.name = name
        self.title = title
        self.head_style = head_style
        self.head_tooltip = head_tooltip
        self.head_group = head_group
        self.head_group_tooltip = head_group_tooltip
        self.show_head = show_head
        self.head_style = head_style
        self.head_tooltip = head_tooltip
        self.head_group = head_group
        self.head_group_tooltip = head_group_tooltip
        self.value_format = value_format
        self.value_style = value_style
        self.value_tooltip = value_tooltip
        self.value_link = value_link
        self.col_range = col_range
        self.row_style = row_style
        self.row_format = row_format
        self.row_link = row_link
        self.row_range = row_range
        self.row_tooltip = row_tooltip
        self.total = total
        self.total_link = total_link
        self.total_style = total_style
        self.total_tooltip = total_tooltip
        self.stacked = stacked
        self.show_border = show_border
        self.show_head = show_head
        self.show_highlight = show_highlight
        self.show_option_bar = show_option_bar
        self.search_string = search_string
        self.searchable = searchable
        self.pagination_size = pagination_size
        self.sortable = sortable
        self.striped = striped
        self.framed = framed
        self.framed_title = framed_title
        self.table_class = table_class

    @staticmethod
    def create_droplist(text, link_values):
        """
        Create a droplist from a list of values and a base text.

        The function map all the values of the columns with a format in the text using {} as base.

        Example:
            x = create_droplist({"text": Header, "link": "Link text {} and text2 {}"}, [df[col1], df[col2]])

            The first {} will use the value from df[col1] and the second {} will use the value from df[col2]

        :param text: Is the base text of the droplist, use the default dict {"text": Header, "link": "Link text"}
        Example: {"text": Header, "link": "Link text {} and text2 {}"}

        :param link_values: A list with the columns to map the values in the text

        :return: A list of the dicts mapped with the columns
        """
        link_list = []

        if not isinstance(link_values, list):
            link_values = [link_values]

        for i in range(len(link_values[0])):
            format_values = [value[i] for value in link_values]
            text_base = text.copy()
            text_base["link"] = text_base["link"].format(*format_values)
            link_list.append(text_base)

        return link_list

    @property
    def to_json_structure(self):

        table_head = TableHead(self.data, self.head_style, self.head_tooltip, self.head_group, self.head_group_tooltip,
                               self.show_head)
        table_body = TableBody(self.data, self.value_format, self.value_style, self.value_tooltip, self.value_link,
                               self.col_range, self.row_style, self.row_format, self.row_link, self.row_tooltip,
                               self.row_range)
        table_footer = TableFooter(self.data, self.total, self.total_link, self.total_style, self.total_tooltip,
                                   self.value_format)

        head_json = table_head.to_json_structure
        body_json = table_body.to_json_structure
        footer_json = table_footer.to_json_structure

        json_content = {'objectType': "table",
                        'title': [self.title],
                        'header': head_json,
                        'body': body_json,
                        'footer': footer_json,
                        'searchable': self.searchable,
                        'searchString': self.search_string,
                        'paginationSize': self.pagination_size,
                        'framed': self.framed,
                        'framedTitle': self.framed_title,
                        'stacked': self.stacked,
                        'showBorder': self.show_border,
                        'showOptionBar': self.show_option_bar,
                        'showHighlight': self.show_highlight,
                        'striped': self.striped,
                        'sortable': self.sortable,
                        "class": self.table_class
                        }

        # Transforming in JSON
        table_json = json.dumps(json_content, indent=1, allow_nan=False)

        return table_json
