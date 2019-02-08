# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from .assets import STYLE_NAMES, FG_COLOURS, BG_COLOURS, ESC, END


class StyleError(Exception):
    def __init__(self, *args, **kwargs):
        super(StyleError, self).__init__(*args)


class Styled(object):
    pattern = re.compile(r".*?(?P<pattern>[[][[].*?[|].*?[]][]]).*?", re.UNICODE|re.DOTALL)
    styled_text = re.compile(r".*?[[][[].*?[\"'](?P<text>.*?)[\"'][|](?P<styles>(\w+[:-]?)+).*?[]][]].*", re.UNICODE|re.DOTALL)

    def __init__(self, s=None, *args, **kwargs):
        if s is None:
            self._s = u''
        else:
            if isinstance(s, basestring):
                if isinstance(s, str):
                    self._s = s.decode('utf-8')
                elif isinstance(s, unicode):
                    self._s = s
            else:
                raise ValueError("Invalid input object of type {}".format(type(s)))
        # format string using args and kwargs
        self._plain = self._s.format(*args, **kwargs)
        # extract tokens
        self._tokens = self._find_tokens(self._plain)
        # validate
        self._validate(self._tokens)
        # remove duplicates
        self._cleaned_tokens = self._clean(self._tokens)
        # transform text with tokens and styles
        self._styled = self._transform(self._plain, self._cleaned_tokens)
        # unstyled version for length inference
        self._unstyled = self._transform(self._plain, self._cleaned_tokens, apply=False)

    @staticmethod
    def transform(token):
        """Static method that converts tokens into styled text"""
        start, end, text, styles = token
        s = u''
        terminate = True
        for style in styles:
            pos = None
            try:
                pos, style_ = style.split('-')
            except ValueError:
                style_ = style
            try:
                if pos == u'fg':
                    s += u'{}[{}m'.format(ESC, FG_COLOURS(style_))
                elif pos == u'bg':
                    s += u'{}[{}m'.format(ESC, BG_COLOURS(style_))
                elif pos == u'no' and style_ == u'end':
                    terminate = False
                elif pos == u'yes' and style_ == u'end':
                    terminate = True
                else:
                    s += u'{}[{}m'.format(ESC, STYLE_NAMES[style_])
            except KeyError:
                raise StyleError(u"Unknown style '{}'".format(style_))
        if terminate:
            return u'{}{}{}'.format(s, text, END)
        else:
            return u'{}{}'.format(s, text)

    def _transform(self, plain, tokens, apply=True):
        """Transform the whole string into a styled string"""
        i = 0
        styled = u''
        for token in tokens:
            start, end, text, styles = token
            if apply:
                styled += plain[i:start] + self.transform(token)
            else:
                styled += plain[i:start] + text
            i = end
        styled += plain[i:]
        return styled

    def _find_tokens(self, string):
        """Find all style tokens in the string"""
        tokens = list()
        index = 0
        pos = 0
        while True:
            string = string[index:]
            pattern = self.pattern.match(string)
            if not pattern:  # or not styled_text:
                break
            found_pattern = pattern.group(u'pattern')
            styled_text = self.styled_text.match(found_pattern)
            if not styled_text:
                raise StyleError(u"Invalid tokens in pattern {}".format(found_pattern))
            text = styled_text.group(u'text')
            styles = styled_text.group(u'styles').split(u':')
            t_ = (pattern.start() + pos + (pattern.end() - len(found_pattern)), pattern.end() + pos, text, styles)
            tokens.append(
                t_,
            )
            index = pattern.end()
            pos += index
        return tokens

    def _validate(self, tokens):
        """Validate styling

        * no multiple fgs or bgs
        """
        for start, end, text, styles in tokens:
            fgs = list()
            bgs = list()
            no_ends = list()
            other = list()
            for style in styles:
                pos = None
                try:
                    pos, style_ = style.split('-')
                except ValueError:
                    style_ = style
                if pos == u'fg':
                    fgs.append(style)
                elif pos == u'bg':
                    bgs.append(style)
                elif pos == u'no' and style_ == u'end':
                    no_ends.append(style_)
                else:
                    other.append(style)
            if len(fgs) > 1:
                raise StyleError(u"Multiple foreground styles for text '{}': {}".format(text, ', '.join(styles)))
            if len(bgs) > 1:
                raise StyleError(u"Multiple background styles for text '{}': {}".format(text, ', '.join(styles)))
            if len(no_ends) > 1:
                raise StyleError(u"Multiple no-ends for text '{}': {}".format(text, ', '.join(styles)))

    def _clean(self, tokens):
        """Remove duplicates and sundry things"""
        cleaned_tokens = list()
        for start, end, text, styles in tokens:
            cleaned_tokens.append((start, end, text, list(set(styles))))
        return cleaned_tokens

    def __len__(self):
        return len(self._unstyled)

    def __str__(self):
        return self._styled.encode('utf-8')

    def __unicode__(self):
        return self._styled

    def __eq__(self, other):
        return self._unstyled.encode('utf-8') == other

    def __add__(self, other):
        """styled + other"""
        if isinstance(other, Styled):
            return Styled(self._plain + other._plain)
        else:
            return Styled(self._plain + other)

    def __radd__(self, other):
        """other + styled"""
        if isinstance(other, Styled):
            return Styled(other._plain + self._plain)
        else:
            return Styled(other + self._plain)

    def __getitem__(self, item):
        return self._styled[item]

