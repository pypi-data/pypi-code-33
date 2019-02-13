#!python
# -*- coding: utf-8 -*-
"""
=====
joho
=====

Description:
~~~~~~~~~~~~
* HTML and SVG module to create lecture materials for 情報処理及び実習 TAC101
at the University of Yamanashi (山梨大学).

* The output file: html.


Example:
--------
::


    #!python
    ## -*- coding: utf-8 -*-
    import joho as j
    # create html output file and
    # load the default web browser to open the file
    j.title("Topic 12: Python: HTML SGV ")
    j.insert_horizontal_line()
    j.heading2("パイソンによる HTML")
    j.write("Hello world")
    j.heading2("パイソンによる図形、アニメションの作成")
    Face =  j.line(0, 0, 100, 100) +\
            j.circle(100, 100, 50, fillcolor="none") + \
            j.polygon([200, 400, 400],[100,100,300])
    j.draw(Face + j.grid(100))
    j.MakeTableContent()
    j.show()
"""

__all__ = ["title", "heading1","heading2","heading3",
            "circle","rectangle","line","polyline","polygon","text",
            "rotate", "move", "grid", "arrow", "animate_move", "animate_rotate",
            "link",
            "insert_video","insert_image","insert_youtube","insert_newline","insert_link",
            "insert_table", "insert_pdf", "insert_horizontal_line", "insert_code",
            "MakeTableContent",
            "write", "draw", "show", "google",
            "HighlightSyntax","RemoveCommonIndent",
            "CSS_SETTING",
            "Tag_Code", "Tag_Highlight", "Tag_Bold_Red", "Tag_Courier","Unicode",
            "EOL", "TAB", "SPACE", "QUOTE",
            "HTML_SPACE", "HTML_ARROW", "HTML_BULLET", "HTML_NEWLINE",
            "SVG_WIDTH", "SVG_HEIGHT",
            "DefaultColor","DefaultLineWidth", "DefaultSize", "DefaultFont",
            "pi", "cos", "sin",
            ]
__version__ = "0.19.3"

from .joho import *
