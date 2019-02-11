# -*- coding: utf-8 -*-
"""Code editor module.

contains PSCodeEdit, a subclass of PyCodeEdit
"""

import difflib

import autopep8
from puzzlestream.ui import colors
from puzzlestream.ui.codestyle import PSCodeStyleDark, PSCodeStyleLight
from pygments.token import Text
from pyqode.core.api import ColorScheme
from pyqode.core.modes import RightMarginMode
from pyqode.python.widgets import PyCodeEdit
from PyQt5.QtGui import QBrush, QColor, QKeySequence
from PyQt5.QtWidgets import QShortcut


class PSCodeEdit(PyCodeEdit):
    """PyCodeEdit with some added functionality."""

    def __init__(self, server_script=None, args=None):
        """Editor init.

        Args:
            server_script: Location of the PyCodeEdit server script file (.py).
            args (list): Additional args to be passed to the server.
        """
        super().__init__(server_script=server_script, args=args)

        # shortcuts
        self.__shortcuts = {}

        # set default colors
        self.setRightMarginColor()
        p = self.panels.get("QuickDocPanel")
        self.add_action(p.action_quick_doc, sub_menu="")

    def setRightMarginColor(self, color=QColor(42, 92, 129)):
        """Set colour of right margin line to color,"""
        self._modes.get(RightMarginMode).color = color

    def setCurrentLineColor(self, color=QColor(42, 92, 129)):
        """Set colour of current active line to color,"""
        self._modes.get("CaretLineHighlighterMode").background = color

    def setSyntaxColorScheme(self, scheme="dark"):
        """Set syntax colour scheme to scheme (str, dark or light)."""
        if scheme == "dark":
            style = PSCodeStyleDark
        elif scheme == "light":
            style = PSCodeStyleLight
        else:
            return

        colorScheme = self.syntax_highlighter.color_scheme
        colorScheme._load_formats_from_style(style)
        self.syntax_highlighter.color_scheme = colorScheme
        self.syntax_highlighter.refresh_editor(colorScheme)
        self.syntax_highlighter.rehighlight()

        matcher = self.modes.get("SymbolMatcherMode")
        bg = QColor(colors.get("light-blue"))
        matcher.match_background = QBrush(bg)
        matcher.match_foreground = QBrush(QColor(style.background_color))

        occ = self.modes.get("OccurrencesHighlighterMode")
        occ.background = QBrush(bg)
        occ.foreground = QBrush(QColor(style.background_color))

    def addShortcut(self, sequence, target):
        """Add shortcut to the editor.

        Args:
            sequence (str): Key sequence.
            target: Method to be executed when sequence is entered.
        """
        sc = QShortcut(QKeySequence(sequence), self)
        sc.activated.connect(target)
        self.__shortcuts[sequence] = sc

    def autoformat(self):
        cursor = self.textCursor()
        cursorPos = cursor.position()
        text = self.toPlainText()
        newText = autopep8.fix_code(text, options={'aggressive': 2})

        cursor.beginEditBlock()
        pos = 0
        for d in difflib.ndiff(text, newText):
            if d.startswith("+"):
                cursor.setPosition(pos)
                cursor.insertText(d[-1])
            elif d.startswith("-"):
                cursor.setPosition(pos + 1)
                cursor.deletePreviousChar()
                pos -= 1

            pos += 1
        cursor.endEditBlock()

        cursor.setPosition(cursorPos + len(newText) - len(text))
        self.setTextCursor(cursor)
