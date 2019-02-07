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

from .token import Token
from .tokentype import TokenType
from .error import *
# import json  # used printing debug data in _consolidateOutputs()


class Parser(object):

    def __init__(self, tokens, numTokens, optIgnoreWhitespace):
        self.tokenList     = tokens
        self.tokenListSize = numTokens - 1

        self.outputSteps = {}  # operations keyed by order number
        self.macroDef    = {}  # macros keyed by macro name
        self.varDef      = {}  # variables keyed by variable name

        self._currentTokenIndex = 0
        self._stepOrderNumber   = 0  # order number for the output steps
        self._maxMacroParams    = 25  # max number of macro parameters

        # parsing options
        self._ignoreWhitespace  = optIgnoreWhitespace

    def parse(self):
        """
        Parse each line of tokens and process the
        corresponding context from the list below:

        1. Plain text: This is any line not including a keyword
        2. Macro: Macro start/end
        3. Let: Variable definition
        4. Exec: Execution of a macro
        5. Procloop: Execution of a loop
        """
        tokenStack = []
        while not self._is_end_of_loop():
            # get current line
            result, tokenStack = self._get_line()

            if len(tokenStack) > 0:
                # determine type of line (contains macro statement, plaintext)
                lineTypeToken = self._get_line_type(tokenStack)
                cleanTokenStack = self._remove_line_whitespace(tokenStack)

                # handle block
                if not self._match(lineTypeToken, self._get_keyword_token_list()):
                    self._processPlainText(cleanTokenStack)

                elif self._match(lineTypeToken, [TokenType.MACRO_START]):
                    self._processMacro(cleanTokenStack)

                elif self._match(lineTypeToken, [TokenType.LET]):
                    self._processLet(cleanTokenStack)

                elif self._match(lineTypeToken, [TokenType.LOOP_START]):
                    self._processLoop(cleanTokenStack)

                elif self._match(lineTypeToken, [TokenType.EXEC]):
                    self._processExec(cleanTokenStack)
                else:
                    errorMsg = 'Unknown char in line "' + ' '.join(tokenStack) + '"'
                    raise BadDefinitionError(errorMsg)

        return self._consolidateOutputs()

    def _advance(self):
        """
        Returns token at position _currentTokenIndex
        Returns -1 if at the end of the tokenList.
        """
        if self._is_end_of_loop():
            return -1
        else:
            self._currentTokenIndex += 1
            return self.tokenList[self._currentTokenIndex]

    def _consolidateOutputs(self):
        output = {
            'outputSteps': self.outputSteps,
            'macroDef': self.macroDef,
            'varDef': self.varDef
        }
        # uncomment below to print final parse tree
        # print('\n\n_consolidateOutputs():')
        # print(json.dumps(output, indent=3))
        return output

    def _get_line(self):
        """
        Returns the next line of tokens as a list,
        and a result integer (0 if successful, -1 on EOF).
        """
        tokenStack = []
        token = self._get_current_token()

        # check if EOF
        if self._is_end_of_loop():
            return (-1, tokenStack)

        while not self._match(token, [TokenType.NEW_LINE]):
            tokenStack.append(token)
            token = self._advance()
            if token == -1:
                return (-1, tokenStack)
        tokenStack.append(token)  # add new line char
        self._advance()  # move past newline

        return (0, tokenStack)

    def _get_line_type(self, tokenStack):
        """
        Returns the first keyword token
        in the list if it exists, the first
        token in the list otherwise if plaintext.
        Returns -1 , if the tokenStack is empty
        """
        if len(tokenStack):
            for token in tokenStack:
                if self._match(token, self._get_keyword_token_list()):
                    return token
            return tokenStack[0]
        else:
            return -1

    def _remove_line_whitespace(self, tokenStack):
        """
        Returns a whitespace-free list of tokens,
        if line contains a keyword.
        Returns unchanged list of tokens if the line
        contains just plaintext.
        """
        isKeywordLine = 0
        keywordToken = ''
        outputTokenStack = []

        if len(tokenStack):
            # determine if line contains a keyword
            token = self._get_line_type(tokenStack)
            if self._match(token, self._get_keyword_token_list()):
                isKeywordLine = 1
                keywordToken = token

            if isKeywordLine == 1:
                # let tags need to include all whitespace between "=" and ";"
                if self._match(keywordToken, [TokenType.LET]):
                    isPastEqualSymbol = 0
                    for token in tokenStack:
                        if not self._match(token, [TokenType.EQUAL]):
                            if self._match(token, [TokenType.SEMICOLON]):
                                outputTokenStack.append(token)
                                break
                            else:
                                if isPastEqualSymbol == 1:
                                    outputTokenStack.append(token)
                                else:
                                    if not self._match(token, self._get_whitespace_token_list()):
                                        outputTokenStack.append(token)
                        else:
                            isPastEqualSymbol = 1
                            outputTokenStack.append(token)
                            continue
                    return outputTokenStack
                else:
                    # strip all whitespace otherwise
                    for token in tokenStack:
                        if not self._match(token, self._get_whitespace_token_list()):
                            outputTokenStack.append(token)
                    return outputTokenStack
            else:
                return tokenStack
        else:
            return -1

    def _is_end_of_loop(self):
        """
        Returns True if at the end of the list of source tokens
        and False otherwise.
        """
        return self._currentTokenIndex >= self.tokenListSize

    def _match(self, token, tokenTypeList):
        """
        Returns True if the passed token's type
        is in the list of passed types, and False
        otherwise.
        """
        if token.token_type in tokenTypeList:
            return True
        else:
            return False

    def _increment_step_order(self):
        self._stepOrderNumber += 1

    def _decrement_step_order(self):
        self._stepOrderNumber -= 1

    def _increment_current_index(self):
        self._currentTokenIndex += 1

    def _decrement_current_index(self):
        self._currentTokenIndex -= 1

    def _get_current_token(self):
        return self.tokenList[self._currentTokenIndex]

    def _get_whitespace_token_list(self):
        return [TokenType.SPACE,
                TokenType.TAB,
                TokenType.CARRIAGE_RETURN,
                TokenType.NEW_LINE]

    def _get_keyword_token_list(self):
        return [TokenType.MACRO_START,
                TokenType.MACRO_END,
                TokenType.LET,
                TokenType.LOOP_START,
                TokenType.PROC_END,
                TokenType.EXEC]

    def _processPlainText(self, tokenStack):
        """
        Process plain text context.
        """
        outputStep = {}
        isNotWhitespaceLine = 0

        # concat current token to output string
        plainTextLine = ''
        for token in tokenStack:
            if not self._match(token, self._get_whitespace_token_list()):
                isNotWhitespaceLine = 1
            plainTextLine += token.lexeme

        # if option is set, ignore all plaintext lines
        # that are composed only of whitespace tokens
        if (not isNotWhitespaceLine) and self._ignoreWhitespace:
            return

        # store plain text data
        outputStep["type"] = "plaintext"
        outputStep["text"] = plainTextLine

        self._increment_step_order()
        self.outputSteps[self._stepOrderNumber] = outputStep

    def _processLet(self, tokenStack):
        """
        Process %let statement of the form

        %let varName = varVal ;
        """
        letTokenIndex         = 0
        varNameTokenIndex     = 1
        equalsTokenIndex      = 2
        varValStartTokenIndex = 3
        semiColonTokenIndex   = -1

        varName = ''
        varVal  = ''

        if not self._match(tokenStack[varNameTokenIndex], [TokenType.IDENTIFIER]):
            errorMsg = 'Bad let tag definition. Invalid variable name.'
            raise BadDefinitionError(errorMsg)
        varName = tokenStack[varNameTokenIndex].lexeme
        if varName in self.varDef:
            errorMsg = 'Variable "' + varName + '" already exists.'
            raise ExistingVariableError(errorMsg)

        # check for correct let tag ending
        if not self._match(tokenStack[semiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" in let tag "' + varName + '".'
            raise BadDefinitionError(errorMsg)

        # check let tag only has one '=', and process subsequent tokens
        filterList = [
            TokenType.EQUAL
        ]
        checkList = [t.lexeme for t in tokenStack if self._match(t, filterList)]
        if len(checkList) > 1:
            errorMsg = 'Bad let tag definition. More than one "=" found.'
            raise BadDefinitionError(errorMsg)

        # get variable value
        varVal = ''
        varValList = [t for t in tokenStack[varValStartTokenIndex:]]
        for v in varValList:
            if not self._match(v, [TokenType.SEMICOLON]):
                varVal += v.lexeme

        # add variable definition to dicionary
        self.varDef[varName] = varVal

    def _processMacro(self, tokenStack):
        """
        Process macro context of the form:

        %macro <macroname> (<param1>, <param2>, ...);
            <macro block>
        %mend;
        """
        macroStartTokenIndex      = 0
        macroNameTokenIndex       = 1
        macroOpenParenTokenIndex  = 2
        macroCloseParenTokenIndex = -2
        macroSemiColonTokenIndex  = -1

        macroStep   = {}
        macroName   = ''
        macroParams = []
        macroBody   = ''

        # extract macro name
        if not self._match(tokenStack[macroNameTokenIndex], [TokenType.IDENTIFIER]):
            errorMsg = 'Bad macro definition'
            raise BadDefinitionError(errorMsg)
        macroName = tokenStack[macroNameTokenIndex].lexeme

        # check for correct macro signature ending
        if not self._match(tokenStack[macroSemiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" in opening tag of macro "' + macroName + '"'
            raise BadDefinitionError(errorMsg)

        # extract macro parameters
        filterParamsList = [
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.COMMA,
            TokenType.SEMICOLON,
            TokenType.NEW_LINE
        ]
        paramList = [p for p in tokenStack[macroOpenParenTokenIndex:]
                        if not self._match(p, filterParamsList)]

        # check parameters for validity
        acceptedParamsList = [
            TokenType.IDENTIFIER
        ]
        for p in paramList:
            if not self._match(p, acceptedParamsList):
                errorMsg = 'Incorrect parameter in macro "' + macroName + '"'
                raise BadDefinitionError(errorMsg)
            else:
                macroParams.append(p.lexeme)

        # macro body
        result, tokenStack = self._get_line()
        lineTypeToken = self._get_line_type(tokenStack)
        tokenStack = self._remove_line_whitespace(tokenStack)

        if result != -1:
            while not self._match(lineTypeToken, [TokenType.MACRO_END]):
                for token in tokenStack:
                    macroBody += token.lexeme

                result, tokenStack = self._get_line()
                lineTypeToken = self._get_line_type(tokenStack)
                tokenStack = self._remove_line_whitespace(tokenStack)

                if result == -1 and not len(tokenStack):
                    errorMsg = 'No closing tag for macro "' + macroName + '"'
                    raise BadDefinitionError(errorMsg)
                if result == -1 and len(tokenStack):
                    break
        else:
            errorMsg = 'No closing tag for macro "' + macroName + '"'
            raise BadDefinitionError(errorMsg)

        # ensure correctness of remaining macro closing tag '%mend;'
        if len(tokenStack) != 2:
            errorMsg = 'Bad closing tag for macro "' + macroName + '"'
            raise BadDefinitionError(errorMsg)
        if not self._match(tokenStack[macroSemiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" on closing tag for macro "' + macroName + '"'
            raise BadDefinitionError(errorMsg)

        # store in macroDef{} and in outputSteps{}
        macroStep['type']       = 'macro'
        macroStep['parameters'] = macroParams
        macroStep['text']       = macroBody

        if macroName in self.macroDef:
            errorMsg = 'Macro "' + macroName + '" already exists'
            raise ExistingMacroError(errorMsg)

        # add macro step
        self.macroDef[macroName] = macroStep

    def _processNestedLoop(self, tokenStack):
        procloopOpenParenTokenIndex  = 1
        procloopCloseParenTokenIndex = -3
        procloopCounterVarTokenIndex = -2
        procloopSemiColonTokenIndex  = -1

        procloopMaxParameters = 3

        loopStart   = 0
        loopEnd     = 0
        loopInc     = 0
        loopVar     = ''
        loopSteps   = {}  # holds the current loop steps
        outputSteps = {}  # gets returned as the top-level output step

        # check for correct procloop signature ending
        if not self._match(tokenStack[procloopSemiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" in procloop signature.'
            raise BadDefinitionError(errorMsg)

        if not self._match(tokenStack[procloopCounterVarTokenIndex], [TokenType.IDENTIFIER]):
            errorMsg = 'Missing counter variable in procloop.'
            raise BadDefinitionError(errorMsg)
        else:
            # get loop counter variable name
            loopVar = tokenStack.pop(procloopCounterVarTokenIndex).lexeme

        # extract procloop parameter
        paramList = self._extract_params(tokenStack)

        if len(paramList) > procloopMaxParameters or len(paramList) == 0:
            errorMsg = 'Incorrect number of procloop tag parameters passed.'
            raise BadDefinitionError(errorMsg)

        # set loop params
        if len(paramList) == 1:
            loopStart = paramList[0].lexeme
        if len(paramList) == 2:
            loopStart = paramList[0].lexeme
            loopEnd   = paramList[1].lexeme
        if len(paramList) == 3:
            loopStart = paramList[0].lexeme
            loopEnd   = paramList[1].lexeme
            loopInc   = paramList[2].lexeme

        # procloop body
        loopStepsCounter = 0

        result, tokenStack = self._get_line()
        lineTypeToken = self._get_line_type(tokenStack)
        tokenStack = self._remove_line_whitespace(tokenStack)
        if result != -1:
            while not self._match(lineTypeToken, [TokenType.PROC_END]):

                if not self._match(lineTypeToken, [TokenType.LOOP_START]):
                    # plain text
                    loopStepsCounter += 1
                    loopSteps[loopStepsCounter] = self._processLoopPlainText(tokenStack)
                else:
                    loopStepsCounter += 1
                    loopSteps[loopStepsCounter] = self._processNestedLoop(tokenStack)

                result, tokenStack = self._get_line()
                lineTypeToken = self._get_line_type(tokenStack)
                tokenStack = self._remove_line_whitespace(tokenStack)
                if result == -1 and not len(tokenStack):
                    errorMsg = 'No closing tag for procloop'
                    raise BadDefinitionError(errorMsg)
                if result == -1 and len(tokenStack):
                    break
        else:
            errorMsg = 'No closing tag for procloop'
            raise BadDefinitionError(errorMsg)

        # ensure correctness of procloop closing tag '%pend;'
        if len(tokenStack) != 2:
            errorMsg = 'Bad closing tag for procloop'
            raise BadDefinitionError(errorMsg)
        if not self._match(tokenStack[procloopSemiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" on closing tag for procloop'
            raise BadDefinitionError(errorMsg)

        # build outputs
        outputSteps['type']      = 'loop'
        outputSteps['loopStart'] = loopStart
        outputSteps['loopEnd']   = loopEnd
        outputSteps['loopInc']   = loopInc
        outputSteps['loopVar']   = loopVar
        outputSteps['loopSteps'] = loopSteps

        return outputSteps

    def _processLoopPlainText(self, tokenStack):
        loopPlaintextDict = {}
        loopPlaintextBuffer = ''

        for token in tokenStack:
            loopPlaintextBuffer += token.lexeme

        # build outputs
        loopPlaintextDict['type'] = 'plaintext'
        loopPlaintextDict['text'] = loopPlaintextBuffer

        return loopPlaintextDict

    def _extract_params(self, tokenStack):
        """
        Returns list of tokens that are either
        of TokenType NUMBER or IDENTIFIER
        """
        filterParamsList = self._get_keyword_token_list()
        filterParamsList.append(TokenType.LEFT_PAREN)
        filterParamsList.append(TokenType.SEMICOLON)
        filteredList = [p for p in tokenStack if not self._match(p, filterParamsList)]

        paramAcc  = ''
        paramList = []
        for token in filteredList:
            if not self._match(token, [TokenType.COMMA, TokenType.RIGHT_PAREN]):
                paramAcc += token.lexeme
            else:
                # avoid adding empty string
                if paramAcc != '':
                    paramList.append(Token(TokenType.IDENTIFIER, paramAcc, None, -1))
                    paramAcc = ''  # reset param accumulator
                if self._match(token, [TokenType.RIGHT_PAREN]):
                    break

        return paramList

    def _processLoop(self, tokenStack):
        """
        Process loop context of the form:

        %procloop (<number of iterations>) <counters variable>;
            <proc loop body>
        %pend;

        The <proc loop body> may contain nested procloops.

        The <counter variable> is an identifier
        used to reference the count of each iteration
        of the loop when executing.
        """
        procloopOpenParenTokenIndex  = 1
        procloopCloseParenTokenIndex = -3
        procloopCounterVarTokenIndex = -2
        procloopSemiColonTokenIndex  = -1

        procloopMaxParameters = 3

        loopStart   = 0
        loopEnd     = 0
        loopInc     = 0
        loopVar     = ''
        loopSteps   = {}  # holds the current loop steps
        outputSteps = {}  # gets returned as the top-level output step

        # check for correct procloop signature ending
        if not self._match(tokenStack[procloopSemiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" in procloop signature.'
            raise BadDefinitionError(errorMsg)

        if not self._match(tokenStack[procloopCounterVarTokenIndex], [TokenType.IDENTIFIER]):
            errorMsg = 'Missing counter variable in procloop.'
            raise BadDefinitionError(errorMsg)
        else:
            # get loop counter variable name
            loopVar = tokenStack.pop(procloopCounterVarTokenIndex).lexeme

        # extract procloop parameter
        paramList = self._extract_params(tokenStack)

        # check number of parameters
        if len(paramList) > procloopMaxParameters or len(paramList) == 0:
            errorMsg = 'Incorrect number of procloop tag parameters passed.'
            raise BadDefinitionError(errorMsg)

        # set loop params
        if len(paramList) == 1:
            loopStart = paramList[0].lexeme
        if len(paramList) == 2:
            loopStart = paramList[0].lexeme
            loopEnd   = paramList[1].lexeme
        if len(paramList) == 3:
            loopStart = paramList[0].lexeme
            loopEnd   = paramList[1].lexeme
            loopInc   = paramList[2].lexeme

        # procloop body
        loopStepsCounter = 0

        result, tokenStack = self._get_line()
        lineTypeToken = self._get_line_type(tokenStack)
        tokenStack = self._remove_line_whitespace(tokenStack)

        if result != -1:
            while not self._match(lineTypeToken, [TokenType.PROC_END]):

                if not self._match(lineTypeToken, [TokenType.LOOP_START]):
                    # plain text
                    loopStepsCounter += 1
                    loopSteps[loopStepsCounter] = self._processLoopPlainText(tokenStack)
                else:
                    loopStepsCounter += 1
                    loopSteps[loopStepsCounter] = self._processNestedLoop(tokenStack)

                result, tokenStack = self._get_line()
                lineTypeToken = self._get_line_type(tokenStack)
                tokenStack = self._remove_line_whitespace(tokenStack)

                if result == -1 and not len(tokenStack):
                    errorMsg = 'No closing tag for procloop'
                    raise BadDefinitionError(errorMsg)
                if result == -1 and len(tokenStack):
                    break
        else:
            errorMsg = 'No closing tag for procloop'
            raise BadDefinitionError(errorMsg)

        # ensure correctness of procloop closing tag '%pend;'
        if len(tokenStack) != 2:
            errorMsg = 'Bad closing tag for procloop'
            raise BadDefinitionError(errorMsg)
        if not self._match(tokenStack[procloopSemiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" on closing tag for procloop'
            raise BadDefinitionError(errorMsg)

        # store loop in dict
        outputSteps['type']      = 'loop'
        outputSteps['loopStart'] = loopStart
        outputSteps['loopEnd']   = loopEnd
        outputSteps['loopInc']   = loopInc
        outputSteps['loopVar']   = loopVar
        outputSteps['loopSteps'] = loopSteps

        self._increment_step_order()
        self.outputSteps[self._stepOrderNumber] = outputSteps

    def _processExec(self, tokenStack):
        """
        Process exec statement of the form:

        %exec <macroname>(<param1>, <param2>, ...);
        """
        execMacroNameTokenIndex  = 1
        execOpenParenTokenIndex  = 2
        execCloseParenTokenIndex = -2
        execSemiColonTokenIndex  = -1

        execStep      = {}
        execMacroName = ''
        execParams    = []

        # extract exec macro name
        if not self._match(tokenStack[execMacroNameTokenIndex], [TokenType.IDENTIFIER]):
            errorMsg = 'Bad exec tag definition'
            raise BadDefinitionError(errorMsg)
        execMacroName = tokenStack[execMacroNameTokenIndex].lexeme

        # check for correct exec signature ending
        if not self._match(tokenStack[execSemiColonTokenIndex], [TokenType.SEMICOLON]):
            errorMsg = 'Missing ";" in exec tag "' + execMacroName + '"'
            raise BadDefinitionError(errorMsg)

        execParams = [p.lexeme for p in self._extract_params(tokenStack[execOpenParenTokenIndex:])]

        # check target macro for exec exists
        if execMacroName not in self.macroDef:
            errorMsg = 'Exec target macro "' + execMacroName + '" does not exist'
            raise NonExistingMacroError(errorMsg)

        # check exec params match required macro params
        if len(self.macroDef[execMacroName]['parameters']) != len(execParams):
            errorMsg = 'Exec tag params do not match target macro params'
            raise BadDefinitionError(errorMsg)

        # add exec to dicionary
        self._increment_step_order()
        execStep['type']       = 'exec'
        execStep['macroName']  = execMacroName
        execStep['parameters'] = execParams
        self.outputSteps[self._stepOrderNumber] = execStep

    def _debug_print(self, token):
        print('* {self._currentTokenIndex}: {token.token_type} \
            {token.lexeme}'.format(self=self, token=token))
