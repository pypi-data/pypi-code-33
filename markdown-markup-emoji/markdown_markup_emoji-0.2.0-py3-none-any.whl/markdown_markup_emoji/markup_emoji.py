# !/usr/bin/python3
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 sts=4 tw=78 et:
# -----------------------------------------------------------------------------
"""
Markup Emoji Extension for Python-Markdown

Python-Markdown extension for markup of Emoji in the markdown document.
"""
import markdown

INSIDE_ELEMENTS = (
    'p', 'div', 'span', 'em', 'i', 'strong', 'ins', 'del',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'a', 'th', 'td', 'dt', 'dd'
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

    def __init__(self, **kwargs):
        self.config = {
            'inside_elements': (INSIDE_ELEMENTS, "Convert the contents of the this tags"),
        }
        super(MarkupEmojiExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals=None):
        # Register instance with a priority.
        md.treeprocessors.register(
            MarkupEmojiTreeProcessor(md, self.config), 'markup_emoji', 4)


class MarkupEmojiTreeProcessor(markdown.treeprocessors.Treeprocessor):
    """Markup Emoji Extension Processor."""

    def __init__(self, md, config):
        super(MarkupEmojiTreeProcessor, self).__init__(md)
        self.inside_elements = config['inside_elements'][0]

    def run(self, root):
        def _check_range(char, c_range):
            for start, end in c_range:
                # if len(start) >= 2:     # Not supported unicode RANGE
                #     exit
                if start <= char <= end:
                    return True
            return False

        def _split_emoji(text):
            prev_emoji = curr_emoji = False
            words = []
            result_text = None
            for char in text:
                curr_emoji = _check_range(char, RANGE_EMOJI)
                if prev_emoji == curr_emoji:
                    result_text = (result_text or '') + char
                else:
                    words.append(result_text)
                    result_text = char
                    prev_emoji = curr_emoji
            words.append(result_text)
            if curr_emoji:
                words.append(None)
            # return list of string: ['ascii', ('CJK', 'ascii'), ...]
            return words

        def _et_copy(src):
            new = markdown.util.etree.Element(src.tag)
            new.text = src.text
            new.tail = src.tail
            for key, value in src.items():
                new.set(key, value)
            return new

        def _et_emoji(text, tail):
            new = markdown.util.etree.Element('span')
            new.text = text
            new.tail = tail
            new.set('class', 'emoji')
            return new

        def _recursive_copy(src):
            dst = _et_copy(src)
            for n, s in enumerate(list(src)):
                d = _recursive_copy(s)
                dst.append(d)

                if (s.tag == 'span' and hasattr(s.attrib, 'class')
                        and s.attrib['class'] == 'emoji'):
                    return
                if s.text and s.tag in self.inside_elements:
                    words = _split_emoji(s.text)
                    d.text = words.pop(0)
                    while len(words) > 1:
                        tail = words.pop()
                        text = words.pop()
                        emoji = _et_emoji(text, tail)
                        d.insert(0, emoji)
                if s.tail:
                    words = _split_emoji(s.tail)
                    d.tail = words.pop(0)
                    while len(words) > 1:
                        tail = words.pop()
                        text = words.pop()
                        emoji = _et_emoji(text, tail)
                        dst.insert(n + 1, emoji)

            return(dst)

        new = _recursive_copy(root)
        return new


def makeExtension(**kwargs):    # pragma: no cover
    return MarkupEmojiExtension(**kwargs)
