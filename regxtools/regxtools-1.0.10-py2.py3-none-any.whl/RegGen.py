import re, yaml, json, ast
from pathlib import Path


class RegGen:
    _config="regGen.yml"
    _regList={}
    _regTable={}

    @classmethod
    def setConfig(cls, file):
        if (file is not None) and (Path(file).is_file()):
            cls._config = file
        return cls

    @classmethod
    def apply(cls):
        with open(cls._config, "r") as file:
            data = yaml.load(file.read())
            cls._regList  = RegGen.__regList(data["params"])
            cls._regTable = RegGen.__regTable(data["items"])

    @classmethod
    def convert(cls, doc):
        '''better call it on a combined string of requests (document) '''
        for str, reg in cls._regList.items():
            doc = re.sub(str, reg, doc)
        return doc

    @classmethod
    def table(cls):
        return ast.literal_eval(
            cls.convert(str(cls._regTable)))

    @staticmethod
    def __regList(params, regList={}):
        for param in params:
            regList[param["str"]]=param["reg"]
        return regList

    @staticmethod
    def __regTable(items, regTable={}):
        for item, str in items.items():
            regTable[item]=str
        return regTable
