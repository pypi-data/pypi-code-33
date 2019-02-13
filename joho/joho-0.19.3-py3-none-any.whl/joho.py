#! python
# -*- coding: utf-8 -*-
# Basic information:

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from time import sleep
from subprocess import call
from sys import platform #used in the run()
import os.path
import numpy as np #used in this module

#To facilitate the user.
from numpy import *
from matplotlib.pyplot import *


VERSION = "LCCHEN 2019"
DEFAULT_OUTPUT_FILENAME = "output.html"
#The following console commands are used to open the html file
FIREFOX_WIN = "C:\\Program Files\\Mozilla Firefox\\Firefox.exe"
FIREFOX_LINUX = "firefox"
PREVIEW_MAC = "open"
LECTURE_HEADER =   "情報処理及び実習 TAC101 " + "(" + VERSION + ")"
pi = np.pi
def cos(x):
    return np.cos(x)
def sin(x):
    return np.sin(x)

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


Installation
~~~~~~~~~~~~
    pip install joho
"""
"""
    Rules & Conventions:
    -> Web Page Main Title is under Heading1
    -> Section is under Heading 2
    -> MakeTableContent creates a list for Heading 2
    -> At the end, show() is needed to save the output html and
    -> call the external program to open it.
"""

SVG_WIDTH = 800
SVG_HEIGHT = 600
SyntaxColor_Comment = "s1"
SyntaxColor_Quote = "s2"
SyntaxColor_Number = "s3"
SyntaxColor_Function = "s4"
SyntaxColor_Statement = "s5"

WelcomeMessage= "Generated automatically by Python for\n"\
                + len(LECTURE_HEADER + VERSION)*"=" + "\n"\
                + LECTURE_HEADER+ " [" + VERSION + "]\n"\
                + len(LECTURE_HEADER + VERSION)*"=" +"\n"\
                + "\n"
CSS_SETTING = {
    "h1" :{
        "color":"black",
        "font-family":"Helvetica Neue",
        },
    "h2" :{
        "color":"dark-blue",
        "font-family":"Helvetica Neue",
        "font-weight":"normal",
        },
    "h3" :{
        "color":"rgb(0, 113, 207)",
        "font-family":"Helvetica Neue",
        "font-weight":"normal",
        "margin-left" : "0px",
        },
    "p":{
        "font-family":"courier",
        "font-size":"16px",
        "color":"black",
        "margin-left" : "0px",
        #"line-height": "100%"
    },
    "MyHeaderTag":{
        "font-family":"arial",
        "font-size":"15px",
        "color":"gray"
    },
    #"SVG":{
    #    "border-style":"solid",
    #    "border-width":"1"
    #},
    "myClickSequence":{
        "font-family": "courier",
        "color":"darkred",
        "font-size": "16px",
        "border-width": "1px",
        "background":"#e3e3e3"
    },
    "video":{
        "margin-left" : "0px",
    },
    "img":{
        "margin-left" : "0px",
    },
    "iframe":{
        "margin-left" : "0px",
    },
    "mytag_code":{
        "font-family": "courier",
        "color":"darkred",
        "background":"rgb(245,245,245)",
        #"font-weight":"light",
    },
    "mytag_highlight":
    {
        "background":"yellow"
    },
    "mytag_bold_red":{
        "font-family": "courier",
        "color":"darkred",
        "font-weight": "bold"
        #"font-weight":"light",
    },
    "mytag_courier":{
        "font-family": "courier",
    },
    "table" :{
        "font-family": "arial, sans-serif",
        "border-collapse": "collapse",
        "width": "80%",
        "margin-left":"40px",
    },
    "td, th" :{
        "border": "1px solid #dddddd",
        "text-align": "left",
        "padding": "8px",
    },
    "tr:nth-child(even)": {
        "background-color": "#dddddd"
    },
    "code":
    {
        "class":"language-python",
        "data-lang":"python",
        "overflow":"auto"
    },
    "pre":
    {
        "font-size":"16px",
        "background":"rgb(232,255,203)",
        "border-style": "solid",
        "border-color": "rgb(159,210,152)",
        "border-width":"1px",
        "margin-left":"40px",
        #"margin-right":"600px",
        "padding":"10px"
    },
    "math":
    {
        "font-size":"24px",
        "background":"rgb(232,255,203)",
        "border-style": "solid",
        "border-color": "rgb(159,210,152)",
        "border-width":"1px",
        "margin-left":"40px",
        #"margin-right":"600px",
        "padding":"10px"
    },
    SyntaxColor_Comment:
    {
        #"color":"rgb(42,130,146)"
        #"color":"rgb(92,93,85)"
        "color":"gray",
        "font-style":"italic"
    },
    SyntaxColor_Quote:
    {
        "color":"rgb(56,110,112)"
    },
    SyntaxColor_Number:
    {
        "color":"darkred"
    },
    SyntaxColor_Function:
    {
        "color":"rgb(0,120,33)",
        "font-weight":"normal"
    },
    SyntaxColor_Statement:
    {
        #"color":"rgb(198,120,221)",
        #"color":"rgb(210,80,0)",
        "color":"darkred",
        "font-weight":"bold"
    },
    ".noselect":
    {
    "-webkit-touch-callout": "none",
    "-webkit-user-select"  : "none",
    "-khtml-user-select"   : "none",
    "-moz-user-select"     : "none",
    "-ms-user-select"      : "none",
    "user-select"          : "none",
    }
}

# My custom tag that is enclosed within the <p> </p>
# Used together with write(...)
# e.g write(...,  mytag(string), ...)
#    return <p> ...<tag>string</tag>...</p>

TAB = " "*4
SPACE =" "
EOL = "\n"
QUOTE = "\""
LESSTHAN = "<"
MORETHAN = ">"
COLON = ":"
SEMICOLON = ";"
SLASH = "/"
EQUAL = "="
DOUBLE_QUOTE = "\""
SINGLE_QUOTE = "\'"
COMMA = ","
HTML_SPACE = "&nbsp;"
HTML_ARROW ="&#9658;"
HTML_BULLET ="&#9679;"#"#&bull;"
HTML_NEWLINE = "<br>"


Global_Buffer = ""
Global_Title = ""

# The counter for the number to be displayed in heading2.
# It can be reset by the user.
# This value will not affect the actual total number of
# pushed heading2 items
Heading_2_Counter = 1
# string to be added before the displayed number.
Heading_2_CounterPrefix = ""
# string to be added after the displayed number.
Heading_2_CounterSuffix = ". "
Heading_2_Content =[]

def RemoveCommonIndent(S):
    """
    Only works for soft indent !
    if S =  "   aa"+\
            "   bb"

    return S = "aa"+\
               "bb"
    """
    NumberOfSpace = 0
    if S[0] != SPACE:
        return S
    while S[NumberOfSpace] == SPACE:
        NumberOfSpace += 1
    S = S[NumberOfSpace:] # get rid of the first indent
    S = S.replace(EOL + NumberOfSpace*SPACE, EOL)
    return S

def SetHeading2Counter(value = 1):
    global Heading_2_Counter
    Heading_2_Counter = value
    return
def SetHeading2CounterSuffix(value = ""):
    global Heading_2_CounterSuffix
    Heading_2_CounterSuffix = value
    return
def SetHeading2CounterPrefix(value = ""):
    global Heading_2_CounterPrefix
    Heading_2_CounterPrefix = value
    return

def rgb(R, G, B):
    """
        Convert decimal RGB to hex in HTML style. e.g.  #RRGGBB
        e.g. rgb(10,10,10) = #101010
        use generic hex function to convert.
        e.g. hex(10) return '0x10'. The first two characters
        are discarded by [2:]
    """
    R = hex(R)
    R = R[2:]
    if len(R)<2:
        R="0" + R
    G = hex(G)
    G = G[2:]
    if len(G)<2:
        G="0" + G
    B = hex(B)
    B = B[2:]
    if len(B)<2:
        B="0" + B
    return "#" + R + G + B

#The following Default values are used to produce SVG output
class DefaultColor:
    Circle_Fill = "#FDEBD0"
    Circle_Line = "#BA4A00"#"#a65200"#rgb(40,100,200)
    Polygon_Fill = "#4EA3EC"#"rgb(78, 163, 236)"
    Polygon_Line = "darkblue"
    Rectangle_Fill = "#FDFFCA"#"rgb(253, 255, 202)"
    Rectangle_Line = "#D8E25E"#"rgb(216, 226, 94)"
    Path_Fill = "none"
    Path_Line = "red"
    Line = "#34495E"  #rgb(0, 180, 51)
    Arrow_Fill = "black"
    Arrow_Line = "none"
    Grid = "gray"
    Text = "black"
class DefaultLineWidth:
    Line = 4
    Circle = 4
    Polygon = 2
    Rectangle = 1
    Arrow = 0
    Grid = 0.5
    Path = 1
class DefaultSize:
    Video = 400
    Image = 400
    Text = 15 #the unit is px
    Arrow_Height = 20
    Arrow_Width = 30
    Arrow_Thick = 6
class DefaultFont:
    Text = "arial"

def AddBrBeforeEOL(S):
    return S.replace(EOL, "<br>"+EOL)
def Bind(S, tag):
    """
    -----------------------------
    Bind(string S, string binder)
    -----------------------------
    Bind the string S with binder
    eg:
        Bind("hello","HHH")
        output:
            <HHH>
                hello
            </HHH>
    """
    return  LESSTHAN + tag+ MORETHAN\
            + S\
            + LESSTHAN + SLASH + tag + MORETHAN

def GetQuotePosition(S, quote):
    pos = []
    n  = S.find(quote)
    while n != -1:
        pos += [n]
        n  = S.find(quote, n+1)
    return pos
def GetQuotePair(S, quote):
    pair = []
    pos = GetQuotePosition(S, quote)
    for i in range(int(len(pos)/2)):
        pair += [ (pos[2*i], pos[2*i + 1]) ]
    return pair
def IsWithinQuote(n, S, quote):
    """
    Check if the character pointed by index n
    is within the Quoation pair.
    e.g. say S : ab"cd"
    IsWithinQuote(1, S) = False
    IsWithinQuote(4, S) = True
    """
    quote_pair= GetQuotePair(S, quote)
    WithinQuote = False
    if len(quote_pair) != 0:
        for q in quote_pair:
            if n > q[0] and n < q[1]:
                WithinQuote = True
                break
    return WithinQuote
def IsWithinComment(n, S):
    """
    This one use the HTML
    comment Tag: SyntaxColor_Comment to Check
    """
    Ans = False
    commentstart = S.find("<"+SyntaxColor_Comment+">")
    commentstop = S.find("</"+SyntaxColor_Comment+">", n)
    if n > commentstart and n < commentstop:
        Ans = True
    return Ans
def FindAll (String, target):
    """
    return the result in array
    e.g. FindAll("abbba", "a")
        returns
            [0,4]
    """
    R = []
    n = String.find(target)
    while(n > -1):
        R += [n]
        n = String.find(target, n+1)
    return R
def FindFirstNumber(S, begin = 0):
    """
        returns the tuple (start, stop)
        e.g., "a 12"
            returns (2,4)
    """
    Number = (".", "0", "1", "2", "3", "4", "5", "6","7", "8","9")
    Operator =(",", "+", "-","*","/","%", "=", "[", "(", "{", ":"," ")
    start = -1
    stop = -1
    n = begin
    while n < len(S):
        #check if it is a number
        if S[n] not in Number:
            n = n + 1
            continue

        # Check if it is within quote_pair
        if IsWithinQuote(n, S, DOUBLE_QUOTE)or IsWithinQuote(n, S, SINGLE_QUOTE):
            n = n + 1
            continue

        # First bypass the SPACE character if there is any
        c = 1
        #while (S[n - c] == " ") and (n>c):
        #    c += 1

        # Check if the character before it is a valid operator or opening
        if S[n - c] not in Operator:
            n += 1
            continue
        # Gotcha
        start = n

        # Loop until the end of number
        while (S[n] in Number) :
            n += 1
            if n > len(S)-1:
                break
        stop = n
        break
    return (start, stop)
def Highlight_Comment(S):
    n = S.find("#")
    while(n > -1):
        if IsWithinQuote(n, S, DOUBLE_QUOTE) or IsWithinQuote(n, S, SINGLE_QUOTE):
            n = S.find("#", n +1) #find the next one
            continue
        S =  S[:n]\
            + "<"\
            + SyntaxColor_Comment\
            + ">"\
            + S[n:]\
            + "</"\
            + SyntaxColor_Comment\
            + ">"
        return S
    return S
def Highlight_Quote(S, quote = "\""):
    n = S.find(quote)
    m = 0
    while n != -1:
        if IsWithinComment(n,S):
            n = S.find(quote, n + 1)
            continue
        if m%2 == 0:
            S = S[:n] + "<" + SyntaxColor_Quote + ">" + S[n:]
            n = S.find(quote, n + len("<" + SyntaxColor_Quote + ">") + 1)
        else:
            S = S[:n+1] + "</" + SyntaxColor_Quote + ">" + S[n+1:]
            n = S.find(quote, n + len("<" + SyntaxColor_Quote + ">") + 1)
        m += 1
    return S
def Highlight_Number(S):
    (number_start, number_stop) = FindFirstNumber(S)
    while(number_start > -1):
        if IsWithinComment(number_start, S):
            OffsetForNextSearch = number_stop
            (number_start, number_stop) = FindFirstNumber(S, OffsetForNextSearch)
            continue
        S = S[: number_start]\
            + "<" + SyntaxColor_Number + ">"\
            + S[number_start:number_stop]\
            + "</" + SyntaxColor_Number + ">"\
            + S[number_stop:]
        OffsetForNextSearch =\
            number_start \
                + len("<" + SyntaxColor_Number + ">"\
                    + S[number_start:number_stop]
                    + "</" + SyntaxColor_Number + ">")

        (number_start, number_stop) = FindFirstNumber(S, OffsetForNextSearch)
    return S
def Highlight_Function(S):
    ValidFunction = ["print", "array", "range",
                    "input", "len",
                    "write", "draw", "show",
                    "circle", "line", "polygon"
                    ]
    for F in ValidFunction:
        p = S.find(F)
        while(p > -1):
            if IsWithinQuote(p, S, DOUBLE_QUOTE) or IsWithinQuote(p,S,SINGLE_QUOTE):
                NextSearch = p + len(F)
                p = S.find(F, NextSearch)
                continue

            # Check if the statement is within the comment
            if IsWithinComment(p,S):
                NextSearch = p + len(F)
                p = S.find(F, NextSearch)
                continue

            # Bypass the space
            c = 0
            while S[p + len(F) + c] == " ":
                c += 1
            # Check if function is followed by a valid bra
            if S[p + len(F) + c] == "(":
                S = S[: p]\
                + "<" + SyntaxColor_Function + ">"\
                + S[ p : p+len(F) ]\
                + "</" + SyntaxColor_Function + ">"\
                + S[ p + len(F) : ]
            NextSearch = p + len(F)\
                        + len("<" + SyntaxColor_Function + ">"\
                                +"</" + SyntaxColor_Function + ">")
            p = S.find(F, NextSearch)
    return S
def Highlight_Statement(S):
    ValidStatement = ['and', 'assert', 'break', 'class',
                    'continue', 'def',
                    'del', 'elif', 'else', 'except', 'exec', 'finally',
                    'for', 'from', 'global', 'if', 'import', 'in',
                    'is', 'lambda', 'not', 'or', 'pass',
                    'raise', 'return', 'try', 'while', 'yield',
                    "int","float", "str", "list"]
    for F in ValidStatement:
        p = S.find(F)
        while(p > -1):
            if IsWithinQuote(p, S, DOUBLE_QUOTE) or IsWithinQuote(p, S, SINGLE_QUOTE):
                NextSearch = p + len(F)
                p = S.find(F, NextSearch)
                continue

            # Check if the statement is within the comment
            if IsWithinComment(p,S):
                NextSearch = p + len(F)
                p = S.find(F, NextSearch)
                continue

            if p + len(F) < len(S):
                # Check if the statement is followed by a valid SPACE
                if S[p + len(F) ] == ":":
                    pass
                elif S[p + len(F) ] == " ":
                    pass
                else:
                    NextSearch = p + len(F)
                    p = S.find(F, NextSearch)
                    continue


            # Check if the statement is the first in the line or
            # has valid SPACE before it.
            if p == 0:
                pass
            elif not S[p-1] == " ":
                NextSearch = p + len(F)
                p = S.find(F, NextSearch)
                continue

            S = S[: p]\
            + "<" + SyntaxColor_Statement + ">"\
            + S[ p : p+len(F) ]\
            + "</" + SyntaxColor_Statement + ">"\
            + S[ p + len(F) : ]
            NextSearch = p + len(F)\
                        + len("<" + SyntaxColor_Statement + ">"\
                                +"</" + SyntaxColor_Statement + ">")
            p = S.find(F, NextSearch)
    return S
def HighlightSyntax(S):
    S = S.split(EOL)
    Y = ""
    for x in S:
        x = Highlight_Comment(x)
        x = Highlight_Quote(x)
        x = Highlight_Quote(x,"\'")
        x = Highlight_Number(x)
        x = Highlight_Function(x)
        x = Highlight_Statement(x)
        Y += x + EOL
    return Y

def CSS(setting):
    """
    e.g.
        h1 {
            color: black;
            font-size:30px;
            font-family: helvetica;
        }
        h2 {
            color: darkblue;
            font-size:24px;
            font-family: helvetica;
        }
    """
    S = "<style>" +EOL
    for key in setting:
        S += key + "{" + EOL
        for Attribute in setting[key]:
            S += Attribute + COLON\
                + setting[key][Attribute] + SEMICOLON + EOL
        S += "}" + EOL
    S += "</style>" + EOL
    return S
def Tag_Code(S):
    return Bind(S, "mytag_code")
def Tag_Highlight(S):
    return Bind(S, "mytag_highlight")
def Tag_Bold_Red(S):
    return Bind(S, "mytag_bold_red")
def Tag_Courier(S):
    return Bind(S, "mytag_courier")
def Unicode(code):
    if isinstance(code, int):
        code = hex(code)[2:] #get rid of the "0x"

    return "&#x"\
            + code\
            +";"
def ItisHTML():
    return "<!DOCTYPE html>"\
            + EOL
def use_utf8():
    return "<meta charset=\"utf-8\">" + EOL
def comment(S):
    return "<!--" + SPACE + S + SPACE + "!-->" + EOL
def EncloseHTML(S):
    S = CSS(CSS_SETTING) + S
    return ItisHTML()\
            + comment(WelcomeMessage)\
            + use_utf8()\
            + Bind(S, "html")
def EncloseBody(S):
    return Bind(S, "body")
def xml(tag, args, endslash=False, additional=None):
    """
    xml(string tag, dictionary args, bool endslash)
    return
        <tag args_key = "args_value" ... >
    e.g.
        d = {"width":10, "height":20}
        xml("TAG", d)
    returns
        <TAG width="10" height="20">
    """
    if not isinstance(args, dict):
        print("Error: def xml!")
        return
    S = LESSTHAN + tag
    for key in args:
        #If none. there is no need to output it to HTML file
        if args[key] is not None:
            S += SPACE+ key + EQUAL + DOUBLE_QUOTE + str(args[key]) + DOUBLE_QUOTE

    if additional is not None:
        S += additional

    if endslash:
        S += SLASH
    S += MORETHAN
    return S
def EncloseSVG(S, w, h, padding = None):
    Inputs = {"width":w, "height":h}
    PaddingScript = ""
    if padding is not None:
        PaddingScript +=  SPACE\
                    + "style="\
                    + DOUBLE_QUOTE\
                    + "padding-left:"\
                    + str(padding)\
                    + DOUBLE_QUOTE

    return "<svg width="\
            + DOUBLE_QUOTE + str(w) + DOUBLE_QUOTE + SPACE\
            + "height="\
            + DOUBLE_QUOTE + str(h) + DOUBLE_QUOTE\
            + PaddingScript\
            + ">"\
            + EOL\
            + S + EOL\
            + "</svg>" + EOL


def MakeTableContent(Message = None):
    global Global_Buffer
    OverWrite = ""
    if Message is not None:
        OverWrite += Bind(Message, "h2")
    n = 0
    for hd2 in Heading_2_Content:
        OverWrite += "<p>"\
                    + link(hd2, "#H2_" + str(n+1))\
                    + "</p>"
        n += 1
    Global_Buffer = OverWrite + Global_Buffer
    return

def title(S):
    global Global_Title
    Global_Title = S
    return

def heading1(S):
    global Global_Buffer
    S = AddBrBeforeEOL(S)
    Global_Buffer += Bind(S, "h1")
    return

def heading2(S):
    global Global_Buffer
    global Heading_2_Counter
    global Heading_2_Content
    S = AddBrBeforeEOL(S)
    S = Heading_2_CounterPrefix\
        + str(Heading_2_Counter)\
        + Heading_2_CounterSuffix\
        + S
    Heading_2_Content += [S]
    Global_Buffer += Bind(
                    S,
                    "h2 id=\"H2_" + str(Heading_2_Counter) + "\"")
    Heading_2_Counter += 1

    return
def heading3(S):
    global Global_Buffer
    S = AddBrBeforeEOL(S)
    Global_Buffer += Bind(S, "h3")
    return
def HR():
    return "<hr>" + EOL

def Header(S):
    return Bind(Bind(S, "MyHeaderTag"), "p")

#=============================================
# Simple SVG Built-in Functions (Non-Path)
# returns string
#=============================================
def circle(x, y, r,
        fillcolor = DefaultColor.Circle_Fill,
        linecolor = DefaultColor.Circle_Line,
        linewidth= DefaultLineWidth.Circle):
    inputs = {
        "cx":x,
        "cy":y,
        "r": r,
        "stroke": linecolor,
        "stroke-width": linewidth,
        "fill" : fillcolor
        }
    return xml("circle", inputs, True) + EOL

def rectangle(x, y, width, height,
    fillcolor = DefaultColor.Rectangle_Fill,
    linecolor = DefaultColor.Rectangle_Line,
    linewidth= DefaultLineWidth.Rectangle,
    rx = 0,
    ry = 0):
    inputs = {
        "x":x,
        "y":y,
        "width":width,
        "height":height,
        "rx":rx,
        "ry":ry,
        "stroke": linecolor,
        "stroke-width": linewidth,
        "fill" : fillcolor,
        }
    return xml("rect", inputs, True) + EOL

def line(x1, y1, x2, y2,
        linewidth=DefaultLineWidth.Line,
        linecolor = DefaultColor.Line):

    inputs = {
        "x1":x1,
        "y1":y1,
        "x2":x2,
        "y2":y2,
        "stroke": linecolor,
        "stroke-width": linewidth,
        }
    return xml("line", inputs, True) + EOL

def polyline(xarray, yarray,
        linecolor = DefaultColor.Line,
        linewidth=DefaultLineWidth.Line,
        fillcolor = None):
    if not len(xarray)==len(yarray):
        print("error: arrays length not equal")
        return;

    points = ""

    for i in range(len(xarray)):
        points += str(xarray[i]) + COMMA + str(yarray[i])
        if not i==len(xarray)-1:
            points += SPACE
    inputs = {
        "points": points,
        "stroke": linecolor,
        "stroke-width": linewidth,
        "fill" : fillcolor
        }
    return xml("polyline", inputs, True) + EOL

def polygon(xarray, yarray,
            fillcolor = DefaultColor.Polygon_Fill,
            linecolor = DefaultColor.Polygon_Line,
            linewidth= DefaultLineWidth.Polygon):
    if not len(xarray)==len(yarray):
        print("error: arrays length not equal")
        return;

    points = ""
    for i in range(len(xarray)):
        points += str(xarray[i]) + COMMA + str(yarray[i])
        if not i==len(xarray)-1:
            points += SPACE
    inputs = {
        "points": points,
        "stroke": linecolor,
        "stroke-width": linewidth,
        "fill" : fillcolor
        }
    return xml("polygon", inputs, True) + EOL

def text(x, y, S,
    fontsize=DefaultSize.Text,
    color = DefaultColor.Text,
    font=DefaultFont.Text):
    Inputs = {
        "x" : str(x),
        "y" : str(y),
        "font-family" : font,
        "font-size" : str(fontsize)
    }
    R = xml("text", Inputs, False)
    R = R + S + "</text>"
    return R

#=============================================
# my Macros based on SVG Built-in Function
# returns string
#=============================================
def line_by_length_angle(xo, yo, r, angle,
        linecolor = DefaultColor.Line,
        linewidth=DefaultLineWidth.Line):
    """
        positive angle is clockwise
    """
    radian = (angle/180)*np.pi

    y2 = yo + r*np.sin(radian)
    x2 = xo + r*np.cos(radian)
    return line(
            xo, yo, x2, y2,
            linecolor,
            linewidth)

def polyline_by_length_angle(xo, yo, rs, angles,
    linecolor = DefaultColor.Line,
    linewidth = DefaultLineWidth.Line,
    fillcolor = None):
    if not len(rs)==len(angles):
        print("error: arrays length not equal")
        return;

    points = ""
    radians = np.array(angles)
    radians = radians * np.pi/180
    points += str(xo) + COMMA + str(yo) + SPACE
    x_prev = xo
    y_prev = yo
    for i in range(len(rs)):
        x = x_prev + rs[i]*np.cos(radians[i])
        y = y_prev + rs[i]*np.sin(radians[i])
        points += str(x) + COMMA + str(y)
        x_prev = x
        y_prev = y
        if not i==len(rs)-1:
            points += SPACE
    inputs = {
        "points": points,
        "stroke": linecolor,
        "stroke-width": linewidth,
        "fill" : fillcolor,
        }
    return xml("polyline", inputs, True) + EOL

def polygon_by_length_angle(xo, yo, r, angle,
            fillcolor = DefaultColor.Polygon_Fill,
            linecolor = DefaultColor.Polygon_Line,
            linewidth= DefaultLineWidth.Polygon ):
    if not len(r)==len(angle):
        print("error: arrays length not equal")
        return;

    radians = np.array(angle)
    radians = radians * np.pi/180
    x_prev = xo
    y_prev = yo
    xarray = [xo]
    yarray = [yo]
    for i in range(len(r)):
        x_prev =  x_prev + r[i]*np.cos(radians[i])
        y_prev = y_prev + r[i]*np.sin(radians[i])
        xarray += [x_prev]
        yarray += [y_prev]
    return polygon(xarray,yarray,fillcolor, linecolor, linewidth)

#=============================================
# SVG native Transformation Functions
# returns string
#=============================================
def rotate(Drawing, angle, xo = 0, yo = 0):
    return "<g transform=\"rotate"\
            +"(" + str(angle) + SPACE\
            +((str(xo)+ SPACE) if xo is not None else "")\
            +((str(yo)+ SPACE) if yo is not None else "")\
            +")\""\
            + ">" + EOL\
            + Drawing\
            + "</g>"\
            + EOL

def move(Drawing, dx, dy):
    return "<g transform=\"translate"\
            +"(" + str(dx) + COMMA + str(dy) + ")\""\
            + ">" + EOL\
            + Drawing\
            + "</g>"\
            + EOL

# Non-native macro
def grid(spacing = 10,
    linecolor = DefaultColor.Grid,
    linewidth = DefaultLineWidth.Grid):
    Number_of_Xgrid = int(SVG_WIDTH/spacing) + 1
    Number_of_Ygrid = int(SVG_HEIGHT/spacing)
    S = ""
    for nx in range(Number_of_Xgrid):
        x = nx * spacing
        S += line(x, 0, x, SVG_HEIGHT,
            linecolor = linecolor,
            linewidth = linewidth)
    for ny in range(Number_of_Ygrid):
        y = ny * spacing
        S += line(0, y, SVG_WIDTH,y,
            linecolor = linecolor,
            linewidth = linewidth)
    return S

def arrow(  xo, yo,
            length,
            angle = 0,
            thick = DefaultSize.Arrow_Thick,
            color = DefaultColor.Arrow_Fill,
            linecolor = DefaultColor.Arrow_Line,
            linewidth = DefaultLineWidth.Arrow,
            arrow_height = DefaultSize.Arrow_Height,
            arrow_width = DefaultSize.Arrow_Width):
    """
        length : total length including the line
        height: height of the horizontal arrow
        width : width of the horizontal arrow
    """
    A = polygon([
                xo,
                xo + length - arrow_width,
                xo + length - arrow_width,
                xo + length,
                xo + length - arrow_width,
                xo + length - arrow_width,
                xo
                ],
                [
                yo - thick/2,
                yo - thick/2,
                yo - arrow_height/2,
                yo,
                yo + arrow_height/2,
                yo + thick/2,
                yo + thick/2,
                ],
                color,
                linecolor,
                linewidth)
    if angle != 0:
        A = rotate(A, angle, xo, yo)
    return A

#=============================================
# SVG native Animate Transform Functions
# returns string
#=============================================
def animate_move(Drawing,
        x1, y1,
        x2, y2,
        duration, begin = 0, Number = "indefinite"):
    Inputs = {
        "attributeName": "transform",
        "attributeType":"XML",
        "type": "translate",
        "from": str(x1) + SPACE + str(y1),
        "to" :  str(x2) + SPACE + str(y2),
        "begin" : str(begin)+ "s",
        "dur" : str(duration) + "s",
        "repeatCount" : "indefinite" if Number is None else str(Number)
    }
    return EOL + "<g>"\
            + Drawing\
            + EOL\
            + xml("animateTransform", Inputs)\
            +"</g>"

def animate_rotate(Drawing,
        angle1, cx1, cy1,
        angle2, cx2, cy2, duration, begin=0, Number="indefinite"):
    """
    <animateTransform attributeName="transform"
                             attributeType="XML"
                             type="rotate"
                             from="0 200 200"
                             to="-360 200 200"
                             begin="3s"
                             dur="3s"
                             repeatCount="1"/>
    """
    Inputs = {
        "attributeName": "transform",
        "attributeType":"XML",
        "type": "rotate",
        "from": str(angle1)\
                + SPACE\
                + str(cx1)\
                + SPACE\
                + str(cy1),
        "to" : str(angle2)\
                + SPACE\
                + str(cx2)\
                + SPACE\
                + str(cy2),
        "begin" : str(begin)+ "s",
        "dur" : str(duration) + "s",
        "repeatCount" : "indefinite" if Number is None else str(Number)
    }
    return EOL + "<g>"\
            + Drawing\
            + EOL\
            + xml("animateTransform", Inputs)\
            +"</g>"

#Not functional if object color is assigned.
def animate_color(Drawing,
            color1,
            color2,
            duration,
            begin=0, Number=None):
    Inputs = {
        "attributeName": "fill",
        "attributeType":"XML",
        "from": color1,
        "to" :  color2,
        "begin" : str(begin)+ "s",
        "dur" : str(duration) + "s",
        "repeatCount" : "indefinite" if Number is None else str(Number)
    }
    return  EOL + "<g>"\
            + Drawing\
            + EOL\
            + xml("animateColor", Inputs)\
            +"</g>"

# SVG for path =============================================
# SVG Path Commands
# returns string
#=============================================
def path_moveto(x,y):
    return "M" + str(x) + SPACE+ str(y) + SPACE
def path_lineto(x,y):
    return "L" + str(x) + SPACE+ str(y) + SPACE
def path_horizontalto(x):
    return "H" + str(x) + SPACE
def path_verticalto(y):
    return "V" + str(y) + SPACE
def path_relative_moveto(dx,dy):
    return "m" + str(dx) + SPACE + str(dy) +SPACE
def path_relative_lineto(x,y):
    return "l" + str(dx) + SPACE+ str(dy) + SPACE
def path_relative_horizontalto(dx):
    return "h" + str(x) + SPACE
def path_relative_verticalto(dy):
    return "v" + str(y) + SPACE
def path_close():
    return "Z"+ SPACE
def path(path_command,
    linecolor = DefaultColor.Path_Line,
    linewidth= DefaultLineWidth.Path,
    fillcolor = DefaultColor.Path_Fill):
    if fillcolor == None:
        fillcolor = "None"
    inputs = {
        "d": path_command,
        "stroke": linecolor,
        "stroke-width": linewidth,
        "fill" : fillcolor
        }
    return xml("path", inputs, True) + EOL
    #<path d="M150 0 L75 200 L225 200 Z" />

#= HTML tag =============================================
# misc string objects
# returns string
#=============================================
def link(message, url):
    return "<a href="\
            + DOUBLE_QUOTE + url + DOUBLE_QUOTE\
            + ">"\
            + message\
            + "</a>"
def horizontal_line():
    return "<hr>"


# Common Tools =============================================
# my Control Functions
# returns NULL
#=============================================
def WriteToGlobal(S):
    # Push string to the global buffer that is to be
    # written to html file
    global Global_Buffer
    Global_Buffer += S
    return
def insert_click_sequence(*args):
    S = ""
    N = len(args)
    n = 0
    for s in args:
        S += Bind(s, "myClickSequence")
        if n < N -1:
            S += HTML_SPACE + HTML_ARROW + HTML_SPACE
        n += 1
    WriteToGlobal(Bind(S, "p"))
    return
def _insert_video(Filename, height = DefaultSize.Video):
    S = "<video height=" \
        + DOUBLE_QUOTE + str(height) + DOUBLE_QUOTE + SPACE\
        + "controls" + SPACE + "autoplay" +SPACE + "loop>"\
        + "<source src=" \
        + DOUBLE_QUOTE + Filename + DOUBLE_QUOTE + SPACE \
        + "type=\"video/mp4\">" \
        + "</video>"
    WriteToGlobal(S)
    return
def insert_video(Filename, height = DefaultSize.Video):
    S = "<video height=" \
        + DOUBLE_QUOTE + str(height) + DOUBLE_QUOTE + SPACE\
        + "controls" + SPACE + "loop>"\
        + "<source src=" \
        + DOUBLE_QUOTE + Filename + DOUBLE_QUOTE + SPACE \
        + "type=\"video/mp4\">" \
        + "</video>"
    WriteToGlobal(S)
def insert_image(Filename, height = DefaultSize.Image, border = 0, caption=""):
    S = "<img src="\
        + DOUBLE_QUOTE + Filename + DOUBLE_QUOTE + SPACE\
        + "height=" + DOUBLE_QUOTE + str(height) + DOUBLE_QUOTE
    if border > 0:
        S += "border= " + DOUBLE_QUOTE + str(border) + DOUBLE_QUOTE
    S += ">"
    if caption:
        S = "<figure>"+ S + "<figcaption>" + caption + "</figcaption>""</figure>"
    WriteToGlobal(S)
    return
def _insert_youtube(url, width, height):
    inputs = {
        "width ":width,
        "height":height,
        "src": url,
        "frameborder":0,
        "gesture": "media",
    }
    S = xml("iframe", inputs, endslash=False, additional= "allowfullscreen")
    S += "</iframe>"
    WriteToGlobal(S)
    return
def insert_youtube(EmbededCode):
    WriteToGlobal(EmbededCode)
    return
def insert_newline():
    WriteToGlobal("<br>")
    return
def insert_link(message, url):
    WriteToGlobal(link(message, url))
    return
def insert_table(coloum, datalist, align = "left"):
    """

    Arrange horizontally
    <table>
      <tr>
        <th>Company</th>
        <th>Contact</th>
        <th>Country</th>
      </tr>
      <tr>
        <td>Alfreds Futterkiste</td>
        <td>Maria Anders</td>
        <td>Germany</td>
      </tr>
      <tr>...
      """
    ROW = ""
    COL = ""
    n = 0
    for d in datalist:

        #for the case of th
        if n < coloum :
            COL += Bind(d, "th") + EOL
            n += 1
        else:
            COL += Bind(d, "td")
            n += 1
        if n == 0:
            pass
        else:
            if (n) % coloum == 0:
                ROW += Bind(COL, "tr") + EOL
                COL = ""

    S = Bind(ROW, "table")
    WriteToGlobal(S)
    return
def insert_pdf(Filename):
    WriteToGlobal("<iframe src=" \
                + DOUBLE_QUOTE + Filename + DOUBLE_QUOTE\
                + "style=\"width: 100%;height: 100%;border: none;\"></iframe>")
def insert_horizontal_line():
    WriteToGlobal(horizontal_line())
    return
def insert_code(S, noselect = False):
    S = RemoveCommonIndent(S)
    Result = "<pre"
    if noselect:
        Result += " class = noselect"
    Result += ">"
    Result += Bind(S, "code")
    Result += "</pre>"
    WriteToGlobal( Result)
    return

# Following are the unsucccesful attempt to parse verbal mathematics to MathML
# I gave up the idea of verbal parsing in favor of lower level
# MathML function
def IsOperator(x):
    ValidOperator = ["+","-","*","/", "^", ">", "<","="]
    if x in ValidOperator:
        return True
    else:
        return False
def FindOperator(S, begin = 0):
    S = S[begin:]
    for n in range(len(S)):
        if IsOperator(S[n]):
            return n + begin
    return -1
def FindIdentifier(S, begin=0):
    """
        Identifier is alphabets string in between operator or space
    """
    Alphabet = "ABCDEFGHINMOPQRSTUVWXYZ"
    alphabet = "abcdefghinmopqrstuvwxyz"
    S = S[begin:]
    for n in range(len(S)):
        if S[n] in Alphabet or S[n] in alphabet:
            #Search to the end
            m = 1;
            while not IsOperator(S[n+m]) and S[n+m]!=SPACE:
                m += 1
                if n + m == len(S):
                    break
            return (n,n+m)
    return (-1,-1)
def FindSuperScript(S, begin = 0):
    """
    Find ".3^2" = 2
    Find ".3^{20}" = (2, 6)
    """
    S = S[begin:]
    for n in range(len(S)):
        if S[n] == "^":
            m = 1
            if S[n + m] != "{":
                return (n + begin, begin + n + m)
            m += 1
            while S[n+m] != "}":
                m += 1
            return (n, n+m)
    return -1
def PutTagBetweenOperator(S, Tag1 = "<mo>", Tag2 = "</mo>"):
    n = FindOperator(S)
    while(n > -1):
        S = S[:n] + Tag1 + S[n] + Tag1 + S[n+1:]
        n = FindOperator(S,
                n\
                + len(Tag1)
                + len(Tag2)
                + 1
                 )
    return S
def PutTagBetweenNumber(S, Tag1 = "<mn>", Tag2 = "</mn"):
    (n, m) = FindFirstNumber(S)
    while(n > -1):
        S = S[:n] + Tag1 + S[n:m] + Tag2 + S[m:]
        (n,m) = FindFirstNumber(S,
                n\
                + len(Tag1)
                + len(Tag2)
                + (m-n)
                 )
    return S
def PutTagBetweenIdentifier(S, Tag1 = "<mi>", Tag2 = "</mi"):
    (n, m) = FindIdentifier(S)
    while(n > -1):
        S = S[:n] + Tag1 + S[n:m] + Tag2 + S[m:]
        (n,m) = FindIdentifier(S,
                n\
                + len(Tag1)
                + len(Tag2)
                + (m-n)
                 )
        return S
    return
def PutTagForSuperScript(S):
    Tag1 = "<msup>"
    Tag2 = "</msup>"

    return

# == Low level MathML function ===================
def mOperator(op):
    return "<mo>" + op + "</mo>"
def mNumber(num):
    return "<mn>" + num + "</mn>"
def mIdentifier(ID):
    return "<mi>" + ID + "</mi>"
def mSubscript(identifier, base):
    return "<msub>" + identifier + SPACE + base + SPACE+ "</msub>"
def mSuperscript(identifier, power):
    return "<msup>" + identifier + SPACE + power + "</msup>"
def mSubSuperscript(base, subscript, superscript):
    return "<msubsup>"\
            + base\
            + SPACE\
            + subscript\
            + SPACE\
            + superscript\
            + "</msubsup>"
def mFrac(numerator, denominator):
    return "<mfrac>"\
            + "<mrow>"\
            + numerator\
            + "</mrow>"\
            + "<mrow>"\
            + denominator\
            + "</mrow>"\
            + "</mfrac>"
def mSqrt(x):
    return "<msqrt>" + x + "</msqrt>"
def mUnderOver(base, underscript, overscript):
    return "<munderover>"\
            + base\
            + underscript\
            + overscript\
            + "</munderover>"
def mOver(base, overscript):
    return "<mover>"\
            + base\
            + overscript\
            + "</mover>"
def mRow(xy):
    return "<mrow>" + xy + "</mrow>"
def mFenced(X):
    return "<mfenced>" + X + "</mfenced>"
def mTable3(*X):
    if len(X) % 3 != 0:
        print("Error in mTable3")
        return -1
    S = "<mtable columnalign=\"left\" >"

    n = 0
    for x in X:
        if n == 0:
            S += "<mtr>" + "<mtd>" + x + "</mtd>"
        elif n == len(X) -1:
            S += "<mtd>" + x + "</mtd>" + "</mtr>"
        elif n % 3 == 0:
            S += "</mtr>"+"<mtr>" + "<mtd>" + x + "</mtd>"
        else:
            S += "<mtd>" + x + "</mtd>"
        n += 1
    S += "/<mTable>"
    return S
def mathml(S):
    return "<math xmlns='http://www.w3.org/1998/Math/MathML' display='block'>"\
            + S\
            + "</math>" + EOL
def insert_math(S):
    WriteToGlobal(mathml(S))
    return



def write(*Args):
    S = ""
    for s in Args:
        s = str(s)
        s = AddBrBeforeEOL(s)
        S += s
    WriteToGlobal(Bind(S, "p") + EOL)
    return

#==  aka insert_svg ==========================
def draw(S, width = SVG_WIDTH, height = SVG_HEIGHT,
            border = True,
            padding = None):
    if border:
        P = path_moveto(0,0)\
            + path_lineto(width, 0)\
            + path_lineto(width, height)\
            + path_lineto(0, height)\
            + path_close()
        S = path(P,
            linecolor = "gray",
            linewidth = 1,
            fillcolor = None)\
            + S
    S = EncloseSVG(S, width, height, padding)
    WriteToGlobal(S)
    return

#== open the output html
def show(Filename = DEFAULT_OUTPUT_FILENAME):
    global Global_Buffer
    global Global_Title
    if len(Global_Title) > 0:
        Global_Buffer = Bind(Global_Title, "h1") + Global_Buffer
    Global_Buffer = Header(LECTURE_HEADER)\
                    + HR()\
                    + Global_Buffer
    Global_Buffer = EncloseBody(Global_Buffer)
    Global_Buffer = EncloseHTML(Global_Buffer)
    save(Global_Buffer, Filename)
    Global_Buffer = ""
    run(Filename)
    return

def save(S, Filename):
    with open(Filename,"w") as f:
        f.write(S)
    f.close()
def GetBrowserName():
    if platform == "darwin":
        return PREVIEW_MAC
    elif platform == "win32":
        return FIREFOX_WIN
    elif platform == "linux" or platform == "linux2":
        return FIREFOX_LINUX

def run(Filename):
    Opener = GetBrowserName()
    call( [ Opener,Filename ] )
    return

def google(keyword, number = 4):
    Search = "https://google.co.jp/search?"\
                + "num=" + str(number)\
                + "&q=" + str(keyword)
    Opener = GetBrowserName()
    call([Opener, Search])
    return
#s = ""
#s+=circle(100,100,50)
#s+=line(100,100,100,0)
#a=rotate(s,45,100,100 ) + circle(100,100,100, fillcolor = None)
#draw(s)
#
#show()
