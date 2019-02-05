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
from .error import *


class Translator(object):

    def __init__(self, translationSteps):
        self.translationSteps = translationSteps
        self.totalSteps       = len(translationSteps['outputSteps'])
        self._currentStep     = 0
        self._loopStack       = {}  # used to keep track of nested loop counts

    def translate(self):
            self.translate_steps()

    def translate_steps(self):
        """
        Iterate through, and process each output step.

        This function will process each output step
        in the output dictionary from the parser stage.
        Each step will result in text that is printed
        to standard output.
        """

        # replace variable names first
        for var in self.translationSteps['varDef']:
            varVal    = self.translationSteps['varDef'][var]
            newVarVal = self._replace_params(self.translationSteps['varDef'], varVal)
            self.translationSteps['varDef'][var] = newVarVal

        self._currentStep = 1  # steps start at one
        while self._currentStep <= self.totalSteps:

            if self.translationSteps['outputSteps'][self._currentStep]['type'] == 'plaintext':
                self._translate_plaintext(self._currentStep)

            if self.translationSteps['outputSteps'][self._currentStep]['type'] == 'exec':
                self._translate_exec(self._currentStep)

            if self.translationSteps['outputSteps'][self._currentStep]['type'] == 'loop':
                self._translate_loop(
                    loopStart=self.translationSteps['outputSteps'][self._currentStep]['loopStart'],
                    loopEnd=self.translationSteps['outputSteps'][self._currentStep]['loopEnd'],
                    loopInc=self.translationSteps['outputSteps'][self._currentStep]['loopInc'],
                    loopVar=self.translationSteps['outputSteps'][self._currentStep]['loopVar'],
                    loopSteps=self.translationSteps['outputSteps'][self._currentStep]['loopSteps']
                )

            self._currentStep += 1
        print()  # add a newline at the end of processing

    def _translate_plaintext(self, stepNum):
        print(self.translationSteps['outputSteps'][stepNum]['text'], end='', file=sys.stdout)

    def _translate_exec(self, stepNum):
        """
        Translate exec step
        """
        # we know the macro exists
        macroName = self.translationSteps['outputSteps'][stepNum]['macroName']

        # replace params and vars in macro body
        macroParamNames = self.translationSteps['macroDef'][macroName]['parameters']
        macroParamVals = self.translationSteps['outputSteps'][stepNum]['parameters']

        # check matching number of parameters between macro def and exec
        if len(macroParamNames) != len(macroParamVals):
            errorMsg = str(macroName) + ' expects ' + str(len(macroParamNames)) + ' parameters'
            raise IncorrectParametersError(errorMsg)

        # map params to values (positional)
        paramMap = {}
        for i in range(len(macroParamNames)):
            paramMap[macroParamNames[i]] = macroParamVals[i]

        # replace parameter values in macro body
        macroText = self.translationSteps['macroDef'][macroName]['text']
        macroText = self._replace_names(paramMap, macroText)

        # replace var values in macro body
        macroText = self._replace_names(self.translationSteps['varDef'], macroText)

        # print output macro text
        print(macroText, end='', file=sys.stdout)

    def _translate_loop(self, **kwargs):
        """
        Translate loop step
        """
        loopStart = int(self._convert_param_names(kwargs['loopStart']))
        loopEnd   = int(self._convert_param_names(kwargs['loopEnd']))
        loopInc   = int(self._convert_param_names(kwargs['loopInc']))
        loopVar   = kwargs['loopVar']
        loopSteps = kwargs['loopSteps']

        # correct loop parameters to avoid range() error
        if loopInc == 0:
            loopInc = 1

        if loopEnd == 0:
            loopEnd = loopStart
            loopStart = 0

        # print output macro text
        if loopStart == 0 and loopEnd == 0:
            errorMsg = 'procloop requires integer parameters.'
            raise LoopParameterError(errorMsg)
        else:
            try:
                for counter in range(loopStart, loopEnd, loopInc):
                    # update global loop stack
                    self._loopStack[loopVar] = counter
                    for step in loopSteps.keys():
                        if loopSteps[step]['type'] == 'plaintext':
                            # replace variable values in loop body
                            output = loopSteps[step]['text']
                            output = self._replace_names(self._loopStack, output)
                            output = self._replace_names(self.translationSteps['varDef'], output)
                            print(output, end='', file=sys.stdout)
                        if loopSteps[step]['type'] == 'loop':
                            self._translate_loop(
                                loopStart=loopSteps[step]['loopStart'],
                                loopEnd=loopSteps[step]['loopEnd'],
                                loopInc=loopSteps[step]['loopInc'],
                                loopVar=loopSteps[step]['loopVar'],
                                loopSteps=loopSteps[step]['loopSteps']
                            )
            except:
                errorMsg = 'procloop requires integer parameters'
                raise LoopParameterError(errorMsg)

    def _replace_names(self, nameMap, text):
        for name in nameMap:
            formatName = "&" + name + "."
            if formatName in text:
                text = text.replace(formatName, str(nameMap[name]))
                text = self._replace_names(nameMap, text)
        return text

    def _replace_params(self, nameMap, text):
        for name in nameMap:
            formatName = "&" + name + "."
            # print('_replace_params(): checking param = "' + formatName + '"')
            if formatName in text:
                # print('_replace_params(): found param = "' + formatName + '" in "' + text + '"')
                text = text.replace(formatName, str(nameMap[name]))
                text = self._replace_params(nameMap, text)
        return text.replace(' ', '')

    def _convert_param_names(self, param):
        if str(param).isdigit():
            return param
        else:
            var = self._replace_params(self._loopStack, param)
            var = self._replace_params(self.translationSteps['varDef'], var)
        return var
