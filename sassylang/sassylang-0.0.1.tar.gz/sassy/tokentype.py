#Copyright 2018 Jonathan Sacramento

#This file is part of sassy.
#
#sassy is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#sassy is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with sassy. If not, see <http://www.gnu.org/licenses/>.

from enum import Enum


class TokenType(Enum):
    # sassy - specific keywords
    MACRO_START     = 1
    MACRO_END       = 2
    LET             = 3
    LOOP_START      = 4
    PROC_END        = 5
    EXEC            = 6

    # single character tokens
    LEFT_PAREN      = 7
    RIGHT_PAREN     = 8
    LEFT_BRACE      = 9
    RIGHT_BRACE     = 10
    COMMA           = 11
    DOT             = 12
    MINUS           = 13
    PLUS            = 14
    SEMICOLON       = 15
    SLASH           = 16
    STAR            = 17
    PERCENT         = 18
    AMPERSAND       = 19
    DOLLAR          = 20
    HASH            = 21
    AT              = 22
    PIPE            = 23
    QUESTION_MARK   = 24
    COLON           = 25
    LEFT_SQR_PAREN  = 26
    RIGHT_SQR_PAREN = 27

    SPACE           = 28
    TAB             = 29
    CARRIAGE_RETURN = 30
    NEW_LINE        = 31

    # one or two character tokens
    BANG            = 32
    BANG_EQUAL      = 33
    EQUAL           = 34
    EQUAL_EQUAL     = 35
    GREATER         = 36
    GREATER_EQUAL   = 37
    LESS            = 38
    LESS_EQUAL      = 39

    # literals
    IDENTIFIER      = 40
    STRING          = 41
    NUMBER          = 42

    # other keywords
    AND             = 43
    CLASS           = 44
    ELSE            = 45
    FALSE           = 46
    FOR             = 47
    IF              = 48
    NIL             = 49
    OR              = 50
    PRINT           = 51
    RETURN          = 52
    SUPER           = 53
    TRUE            = 54
    VAR             = 55
    WHILE           = 56
    EOF             = 57
