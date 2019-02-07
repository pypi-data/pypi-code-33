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

import sys

from .scanner import Scanner
from .parser import Parser
from .translator import Translator
from .error import *
from .token import Token
from .tokentype import TokenType


class Interpreter(object):

    def __init__(self, arguments):
        # program options
        self._fileList = arguments['<file>']
        self._ignoreWhitespace = arguments['--ignore']

        # scanner outputs
        self.tokenList = []
        self.tokenListSize = 0

        # parser outputs
        self.translationSteps = {}

    def process_input(self, source):

        # scan input
        try:
            for line in source.input(self._fileList):
                self._scan_source(line)
        except ScanError as err:
            print("Error[scanner]: Bad input provided", file=sys.stderr)
            print(err.message, file=sys.stderr)
            sys.exit(-1)

        # remove EOF characters resulting from paged input
        self.tokenList = [token for token in self.tokenList if token.token_type != TokenType.EOF]
        self.tokenList.append(Token(TokenType.NEW_LINE, '\n', None, -1))  # add newline to end
        self.tokenListSize = len(self.tokenList)

        # parse tokens
        if bool(self.tokenList):
            try:
                self.translationSteps = Parser(
                    self.tokenList,
                    self.tokenListSize,
                    self._ignoreWhitespace
                ).parse()
            except BadDefinitionError as err:
                print("Error[parser]: BadDefinitionError", file=sys.stderr)
                print(err.message, file=sys.stderr)
                sys.exit(-1)
            except ExistingVariableError as err:
                print("Error[parser]: ExistingVariableError", file=sys.stderr)
                print(err.message, file=sys.stderr)
                sys.exit(-1)
            except ExistingMacroError as err:
                print("Error[parser]: ExistingMacroError", file=sys.stderr)
                print(err.message, file=sys.stderr)
                sys.exit(-1)
            except NonExistingMacroError as err:
                print("Error[parser]: NonExistingMacroError", file=sys.stderr)
                print(err.message, file=sys.stderr)
                sys.exit(-1)
            except LoopParameterError as err:
                print("Error[parser]: LoopParameterError", file=sys.stderr)
                print(err.message, file=sys.stderr)
                sys.exit(-1)

        # translate steps
        if bool(self.translationSteps):
            try:
                Translator(self.translationSteps).translate()
            except IncorrectParametersError as err:
                print('Error[translator]: IncorrectParametersError', file=sys.stderr)
                print(err.message, file=sys.stderr)
                sys.exit(-1)
            except LoopParameterError as err:
                print('Error[translator]: LoopParameterError', file=sys.stderr)
                print(err.message, file=sys.stderr)
                sys.exit(-1)

    def _scan_source(self, source):
        for token in Scanner(source).scan():
            self.tokenList.append(token)
