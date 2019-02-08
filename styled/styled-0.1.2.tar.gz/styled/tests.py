# -*- coding: utf-8 -*-
from __future__ import print_function
from unittest import TestCase

from .styled import Styled, StyleError
from .assets import ESC, END


class NonStringType(object):
    def __init__(self, s):
        self.s = s


class TestStyled(TestCase):
    def test_default(self):
        string = 'this is a string'
        S = Styled(string)
        self.assertEqual(S, string)
        self.assertIsInstance(S, Styled)

    def test_empty(self):
        s = Styled()
        self.assertEqual(len(s), 0)

    def test_type(self):
        s = NonStringType(27)
        with self.assertRaises(ValueError):
            Styled(s)

    def test_find_tokens(self):
        s = """[[ 'a word'|fg-red ]]"""
        s = Styled(s)
        self.assertItemsEqual(s._tokens, [(0, 21, u'a word', [u'fg-red'])])
        s = Styled("""[[ 'your {} is open'|fg-blue ]]""", 'bank')
        self.assertItemsEqual(s._tokens, [(0, 33, u'your bank is open', [u'fg-blue'])])

    def test_length(self):
        u = 'I am the most handsome guy in the room.'
        u_list = u.split(' ')
        s = Styled(" ".join(u_list[:4] + ["[[ '{}'|bold ]]".format(u_list[4])] + u_list[5:]))
        self.assertEqual(len(u), len(s))

    def test_format(self):
        u = "This is a very {} affair in which {count} people were involved."
        s = Styled(u, 'noble', count=38)
        self.assertEqual(s, u.format('noble', count=38))

    def test_quotes(self):
        sq = Styled("I have a [[ 'bold \"hair\"'|fg-red ]] face.")
        dq = Styled('I have a [[ "bold \'hair\'"|fg-red ]] face.')
        tq = Styled("""I have a [[ "bold 'hair'"|fg-red ]] face.""")
        self.assertItemsEqual(sq._tokens, [(9, 35, u'bold "hair"', [u'fg-red'])])
        self.assertItemsEqual(dq._tokens, [(9, 35, u"bold 'hair'", [u'fg-red'])])
        self.assertItemsEqual(tq._tokens, [(9, 35, u"bold 'hair'", [u'fg-red'])])

    def test_style_error(self):
        with self.assertRaises(StyleError):
            Styled('I have a [[ "bold\'hair|fg-red ]] face')

    def test_concatenate(self):
        s1 = Styled("This is the [[ 'end'|bold ]]!")
        u1 = " And I will be finished."
        c1 = s1 + u1
        self.assertEqual(c1, s1 + u1)
        self.assertIsInstance(c1, Styled)
        u2 = "I will be finished..."
        s2 = Styled(" when this [[ 'ends'|bold ]]!")
        c2 = u2 + s2
        self.assertEqual(c2, u2 + s2)
        self.assertIsInstance(c2, Styled)

    def test_fg_colour(self):
        s = Styled("I have never seen a [[ 'white'|fg-white:bold ]] stallion.")
        self.assertIsInstance(s, Styled)

    def test_bg_colour(self):
        s = Styled("[[ 'White bold text on a black background.'|fg-black:bg-white:bold ]]")
        self.assertIsInstance(s, Styled)

    def test_catch_multiple_fgs(self):
        with self.assertRaises(StyleError):
            s = Styled("[[ 'useless'|fg-red:fg-orange ]]")

    def test_catch_multiple_bgs(self):
        with self.assertRaises(StyleError):
            s = Styled("[[ 'useless'|bg-red:bg-orange ]]")

    def test_catch_multiple_no_ends(self):
        with self.assertRaises(StyleError):
            s = Styled("[[ 'useless'|bg-red:no-end:no-end ]]")

    def test_clean_tokens(self):
        s = Styled("[[ 'some text'|bold:bold ]]")
        self.assertItemsEqual(s._cleaned_tokens, [(0, 27, u"some text", [u'bold'])])

    def test_iteration(self):
        s = Styled("There are some folks who [[ 'gasp'|fg-black:bg-deep_sky_blue_2:underlined:blink ]] at the thought "
                   "of the military. ")
        s += 'Woe unto them!'
        self.assertIsInstance(s, Styled)

    def test_unicode(self):
        s = Styled("We wish we had [[ 'red'|fg-red ]] faces")
        u_s = unicode(s)
        s_s = str(s)
        u_ = u"Thërę are some folkß who [[ 'gæsp'|fg-black:bg-deep_sky_blue_2:underlined:blink ]] at the " \
             u"thœught of the military. "
        e = Styled(u_)
        self.assertIsInstance(u_s, unicode)
        self.assertIsInstance(s_s, str)
        self.assertIsInstance(s, Styled)
        self.assertIsInstance(e, Styled)

    def test_concat_unicode(self):
        u_s = u"A unicode string"
        s = Styled("A [[ 'styled'|blink ]] string")
        c1 = u_s + s
        c2 = s + u_s
        self.assertIsInstance(u_s, unicode)
        self.assertIsInstance(c1, Styled)
        self.assertIsInstance(c2, Styled)

    def test_no_end(self):
        # lacks end
        u_ = u"[[ 'gæsp'|fg-black:bg-deep_sky_blue_2:underlined:blink:no-end ]]"
        e = Styled(u_)
        self.assertNotEqual(e[-3:], u'[0m'.format(ESC, END))
        # has end
        u_ = u"[[ 'gæsp'|fg-black:bg-deep_sky_blue_2:underlined:blink ]]"
        e = Styled(u_)
        self.assertEqual(e[-3:], u'[0m'.format(ESC, END))



