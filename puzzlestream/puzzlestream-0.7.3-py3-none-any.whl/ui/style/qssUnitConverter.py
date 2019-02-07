import re


class qssUnitConverter(object):

    def __init__(self, qssPath, oldUnit, newUnit, convFactor):
        with open(qssPath, 'r') as qssFile:
            self.__convString = qssFile.read()
        self.__oldUnit = oldUnit
        self.__newUnit = newUnit
        self.__convFactor = convFactor

    def convert(self, outputFile=None):
        cF = self.__convFactor
        cS = self.__convString
        oU = self.__oldUnit
        nU = self.__newUnit

        strList = list(set([s for s in re.split(" |:", cS) if oU in s]))
        replacements = []
        for oldString in strList:
            split = oldString.split(oU)
            newNumber = str(float(split[0])*cF)
            newString = newNumber+nU
            for i in range(len(split)-1):
                newString += split[i+1]
            replacements.append((" " + oldString, " " + newString))

        for r in replacements:
            cS = cS.replace(r[0], r[1])

        self.__convString = cS

        if outputFile is not None:
            with open(outputFile, "w") as qssFile:
                qssFile.write(self.__convString)

        return self.__convString


myConv = qssUnitConverter("./sheet.qss", "px", "em", 0.08)
print(myConv.convert("./sheet-em.qss"))
