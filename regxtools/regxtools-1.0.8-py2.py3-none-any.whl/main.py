from RegGen import RegGen
import re

class RegTool:
    regTable={}

    def __init__(self):
        self.regTable=RegGen.table()

    def eval(self, ref, str):
        x = re.search(self.regTable[ref], str)
        print(x.groupdict())


if __name__ == "__main__":
    RegGen.setConfig("regex.yaml").apply()
    regFormater=RegTool()
    print(regFormater.regTable)
    regFormater.eval("ADM", "adm-54")
    regFormater.eval("T3", "t3-54-5")
