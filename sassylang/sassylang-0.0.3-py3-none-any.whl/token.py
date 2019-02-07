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

class Token(object):
    def __init__(self, token_type, lexeme, literal, line):
        self.token_type = token_type
        self.lexeme     = lexeme
        self.literal    = literal
        self.line       = line

    def __str__(self):
        return 'Type:"{self.token_type}" Lexeme:"{self.lexeme}" Lit:"{self.literal}"'.format(self=self)
