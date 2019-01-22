#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 sts=4 tw=78 et:
# -----------------------------------------------------------------------------
"""
Markup Emoji Extension for Python-Markdown

Python-Markdown extension for markup of Emoji in the markdown document.
"""
import markdown

INSIDE_ELEMENTS = (
    'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'a', 'th', 'td', 'dt', 'dd'
)
RANGE_EMOJI = (
    ('\u2700', '\u27bf'),           # Dingbats
    ('\U0001f650', '\U0001f67f'),   # Ornamental Dingbats
    ('\U0001f600', '\U0001f64f'),   # Emoticons
    ('\u2600', '\u26ff'),           # Miscellaneous Symbols
    ('\U0001f300', '\U0001f5ff'),   # Miscellaneous Symbols and Pictographs
    ('\U0001f900', '\U0001f9ff'),   # Supplemental Symbols and Pictographs
    ('\U0001f680', '\U0001f6ff'),   # Transport and Map Symbols
    ('\u200d', '\u200d'),           # ZERO WIDTH JOINER
    ('\ufe0e', '\ufe0f'),           # VARIATION SELECTOR-15/16
)


class MarkupEmojiExtension(markdown.Extension):
    """Markup Emoji Extension for Python-Markdown."""

    def extendMarkdown(self, md, md_globals=None):
        # Register instance with a priority.
        md.treeprocessors.register(
            MarkupEmojiTreeProcessor(md), 'markup_emoji', 4)


class MarkupEmojiTreeProcessor(markdown.treeprocessors.Treeprocessor):
    """Markup Emoji Extension Processor."""

    def run(self, root):
        def _check_range(char, c_range):
            for start, end in c_range:
                if len(start) >= 2:     # Not supported unicode RANGE
                    exit
                if start <= char <= end:
                    return True
            return False

        def _markup_emoji(text):
            prev_emoji = curr_emoji = False
            results = []
            result_text = None
            for char in text:
                curr_emoji = _check_range(char, RANGE_EMOJI)
                if prev_emoji == curr_emoji:
                    result_text = (result_text or '') + char
                else:
                    results.append(result_text)
                    result_text = char
                    prev_emoji = curr_emoji
            results.append(result_text)
            if curr_emoji:
                results.append(None)
            # return list of string: ['ascii', ('CJK', 'ascii'), ...]
            return(results)

        for e in root.iter():
            if e.tag == 'span' and e.attrib and e.attrib['class'] == 'emoji':
                continue
            if e.text and e.tag in INSIDE_ELEMENTS:
                results = _markup_emoji(e.text)
                e.text = results.pop(0)
                while len(results) > 1:
                    span = markdown.util.etree.Element('span')
                    span.attrib['class'] = 'emoji'
                    span.tail = results.pop()
                    span.text = results.pop()
                    e.insert(0, span)
            if e.tail:
                results = _markup_emoji(e.tail)
                if e.tag == 'br':
                    e.text = results.pop(0)
                    e.tail = None
                else:
                    e.tail = results.pop(0)
                while len(results) > 1:
                    span = markdown.util.etree.Element('span')
                    span.attrib['class'] = 'emoji'
                    span.tail = results.pop()
                    span.text = results.pop()
                    e.append(span)
        return(root)


def makeExtension(**kwargs):    # pragma: no cover
    return MarkupEmojiExtension(**kwargs)
