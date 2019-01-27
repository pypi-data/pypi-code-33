# -*- coding: utf-8 -*-

EMPTY_TEST_CASES = [
    [""],
    [" "],
    [" &nbsp; "],
    ["&nbsp;"],
    [u"\u0000&nbsp;\u0000 &nbsp;"],
    [None],
    [u'\u0000'],
    [u" \u0000"],
]

BLANK_CHARACTERS_TEST_CASES = [
    [" "],
    [" &nbsp; "],
    ["&nbsp;"],
    [u"\u0000&nbsp;\u0000 &nbsp;"],
    [u'\u0000'],
    [u" \u0000"],
]

FLOAT_TESTS_CASES = [
    [None, 422],
    [u'', 422],
    [u'', 422],
    [u'a', 422],
    [u'…', 422],
    [u'привет', 422],
    [1, 201],
    [1.0, 201],
    [0.0, 201],
    [.0, 201],
]

UTF8_TEST_CASES = [
    ["A", "A"],
    [u"B", u"B"],
    ["666", "666"],
    [u"777", u"777"],
    [u"ginieḰ", u"ginieḰ"],
    [unicode(u"привет"), u"привет"],
    [u"привет", u"привет"],
    [u'\u043f\u0440\u0438\u0432\u0435\u0442', u"привет"],
    [u"ہیلو", u"ہیلو"],
    [u"🧑", u"🧑"],
]

HTML_SUBSET_TEST_CASES = [
    ['<a></a>', '<a></a>'],
    ['', ''],
    ['<a>', '<a></a>'],
    ['<a href="">link</a>', '<a href="">link</a>'],
    ['<a something="">link</a>', '<a>link</a>'],
    ['<div>sad</a>', 'sad'],
    ['<div><!--sad--></a>', ''],
    ['<div></div>', ''],
    ['<b>bold</b>', '<b>bold</b>'],
    ['&lt;', '<'],
    ['&nbsp;', ''],
    ['some&nbsp;word', u'some word'],
    # strip spaces
    [' ', ''],
    [' <a></a> ', '<a></a>'],
    [' <a>something</a> ', '<a>something</a>'],
    [u' &nbsp; ', u''],
    [u' some&nbsp;word ', u'some word'],
]

HTML_SUBSET_TEST_CASES_NO_BLANK = [
    ['<a></a>', '<a></a>'],
    ['<a>', '<a></a>'],
    ['<a href="">link</a>', '<a href="">link</a>'],
    ['<a something="">link</a>', '<a>link</a>'],
    ['<div>sad</a>', 'sad'],
    ['<div><!--sad--></a>', ''],
    ['<div></div>', ''],
    ['<b>bold</b>', '<b>bold</b>'],
    ['&lt;', '<'],
    ['some&nbsp;word', u'some word'],
    # strip spaces
    [' <a></a> ', '<a></a>'],
    [' <a>something</a> ', '<a>something</a>'],
    [u' some&nbsp;word ', u'some word'],
]

NO_HTML_TEST_CASES = [
    ['<a>link</a>', 'link'],
    ['<a>link', 'link'],
    ['<a href="">link</a>', 'link'],
    ['<a something="">link</a>', 'link'],
    ['<div>sad</a>', 'sad'],
    ['<div><!--sad--></a>text', 'text'],
    ['<div>text</div>', 'text'],
    ['<b>bold</b>', 'bold'],
    ['&lt;', '<'],
    ['some&nbsp;word', u'some word'],
    # strip spaces
    [' >-< ', '>-<'],
    [' <a>link</a> ', 'link'],
    [' something ', 'something'],
    [u' >&nbsp;< ', u'> <'],
    [u' some&nbsp;word ', u'some word'],
]

# The move/appication_version has a length of 16 :(
NO_HTML_TEST_CASES_SORT = [
    ['<a>link</a>', 'link'],
    ['<a>link', 'link'],
    ['<div>sad</a>', 'sad'],
    ['<div>tt</div>', 'tt'],
    ['<b>bold</b>', 'bold'],
    ['&lt;', '<'],
    ['some&nbsp;word', u'some word'],
    # strip spaces
    [' >-< ', '>-<'],
    [' <a>link</a> ', 'link'],
    [' something ', 'something'],
    [u' >&nbsp;< ', u'> <'],
    [u' some&nbsp;word ', u'some word'],
]
