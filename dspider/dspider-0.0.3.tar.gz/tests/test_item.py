# Third Party Library
import pytest

# Dsipder Module
from dspider.item import (
    AttrCSSSelectorExtractor,
    Field,
    HTMLItem,
    JSONExtractor,
    JSONItem,
    TextCssSelectorExtractor,
    XpathExtractor,
)
from dspider.response import Response


@pytest.fixture
def response_html():
    body = b"""
        <html>
            <ul>
                <li>
                    <span class='class_a'>a</span>
                    <i>i text 1</i>
                    <b>b text 1</b>
                </li>
                <li>
                    <span class='class_b'>b</span>
                    <i>i text 2</i>
                    <b>b text 2</b>
                </li>
            </ul>
        </html>
    """
    return Response(
        url="",
        status=200,
        body=body,
        encoding="utf-8",
        headers={},
        cookies={},
        meta={},
        request=None,
        history=[],
    )


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (XpathExtractor, "//span[@class='class_a']/text()", ["a"]),
        (XpathExtractor, "//span[@class='class_b']/text()", ["b"]),
        (XpathExtractor, "//span[@class]/text()", ["a", "b"]),
        (XpathExtractor, "//span/@class", ["class_a", "class_b"]),
        (XpathExtractor, "//notexists/text()", []),
        (TextCssSelectorExtractor, "span.class_a", ["a"]),
        (TextCssSelectorExtractor, "span.class_b", ["b"]),
        (TextCssSelectorExtractor, "span", ["a", "b"]),
        (TextCssSelectorExtractor, "notexits", []),
    ],
    ids=repr,
)
def test_text_extract(response_html, Extractor, expr, expect):
    extractor = Extractor(expr)
    rv = extractor.extract_from_response(response_html)
    assert rv == expect
    rv = extractor.extract_first_from_response(response_html, default=None)
    if not expect:
        assert rv is None
    else:
        assert rv == expect[0]


@pytest.mark.parametrize(
    "expr,attr,expect", [("span", "class", ["class_a", "class_b"])], ids=repr
)
def test_attr_extract_by_css_selector(response_html, expr, attr, expect):
    extractor = AttrCSSSelectorExtractor(expr, attr=attr)
    rv = extractor.extract_from_response(response_html)
    assert rv == expect
    rv = extractor.extract_first_from_response(response_html, default=None)
    if not expect:
        assert rv is None
    else:
        assert rv == expect[0]


def test_item_extract(response_html):
    class BodyItem(HTMLItem):
        fields = {
            "span_text": Field(
                extractor=XpathExtractor("//span[@class='class_a']/text()"),
                default="",
                is_many=False,
            ),
            "span_not_exists": Field(
                extractor=XpathExtractor("//span[@class='class_not_exists']/text()"),
                default="not_exists",
                is_many=False,
            ),
        }

    item = BodyItem()
    data = item.extract_first_from_response(response_html)
    assert data is not None
    assert data.get("span_text") == "a"
    assert data.get("span_not_exists") == "not_exists"


def test_complicate_item_a(response_html):
    class ListItem(HTMLItem):
        root_extractor = XpathExtractor("//ul/li")
        fields = {
            "i": Field(XpathExtractor("i/text()")),
            "b": Field(XpathExtractor("b/text()")),
        }

    extractor = ListItem()
    rv = extractor.extract_from_response(response_html)
    assert rv == [
        {"b": "b text 1", "i": "i text 1"},
        {"b": "b text 2", "i": "i text 2"},
    ]
    rv = extractor.extract_first_from_response(response_html)
    assert rv == {"b": "b text 1", "i": "i text 1"}


def test_item_field(response_html):
    class Item(HTMLItem):
        fields = {
            "i": Field(XpathExtractor("i/text()")),
            "b": Field(XpathExtractor("b/text()")),
        }

    class List(HTMLItem):
        fields = {
            "items": Field(
                extractor=Item(root_extractor=XpathExtractor("//ul/li")), is_many=True
            )
        }

    extractor = List()
    rv = extractor.extract_from_response(response_html)
    assert rv == [
        {
            "items": [
                {"b": "b text 1", "i": "i text 1"},
                {"b": "b text 2", "i": "i text 2"},
            ]
        }
    ]
    rv = extractor.extract_first_from_response(response_html)
    assert rv == {
        "items": [
            {"b": "b text 1", "i": "i text 1"},
            {"b": "b text 2", "i": "i text 2"},
        ]
    }


@pytest.fixture
def response_json():
    body = b"""
        {
        "foo": [
            {
            "baz": 1
            },
            {
            "baz": 2
            }
        ]
        }
    """
    return Response(
        url="",
        status=200,
        body=body,
        encoding="utf-8",
        headers={},
        cookies={},
        meta={},
        request=None,
        history=[],
    )


@pytest.mark.parametrize("expr,expect", [("foo[*].baz", [1, 2])])
def test_json_extract(response_json, expr, expect):
    extractor = JSONExtractor(expr)
    rv = extractor.extract_from_response(response_json)
    assert rv == expect

    rv = extractor.extract_first_from_response(response_json)
    assert rv == expect[0]


def test_json_item(response_json):
    class ListItem(JSONItem):
        fields = {"baz": Field(JSONExtractor("baz"))}

    class JSONList(JSONItem):
        fields = {"foo": Field(ListItem(JSONExtractor("foo[*]")), is_many=True)}

    rv = JSONList().extract_from_response(response_json)
    assert rv == [{"foo": [{"baz": 1}, {"baz": 2}]}]

    rv = JSONList().extract_first_from_response(response_json)
    assert rv == {"foo": [{"baz": 1}, {"baz": 2}]}
