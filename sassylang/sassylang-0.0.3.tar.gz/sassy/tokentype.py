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
    # sassy-specific keywords
    MACRO_START     = 1
    MACRO_END       = 2
    LET             = 3
    LOOP_START      = 4
    PROC_END        = 5
    EXEC            = 6

    # single character tokens
    LEFT_PAREN      = 7
    RIGHT_PAREN     = 8
    COMMA           = 11
    DOT             = 12
    SEMICOLON       = 15
    AMPERSAND       = 19

    SPACE           = 28
    TAB             = 29
    CARRIAGE_RETURN = 30
    NEW_LINE        = 31

    # one or two character tokens
    EQUAL           = 34
    EQUAL_EQUAL     = 35

    # literals
    IDENTIFIER      = 40
    NUMBER          = 42

    # other keywords
    EOF             = 57
