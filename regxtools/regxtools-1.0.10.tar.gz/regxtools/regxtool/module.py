from regxtools.regxgen import RegxGen
import re

class RegTool:
    regTable={}

    def __init__(self):
        self.regTable=RegGen.table()

    def getValues(self, ref, str):
        x = re.search(self.regTable[ref], str)
        print(x.groupdict())
