#Copyright 2010 Brian E. Chapman
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

"""
A module defining the contextItem class.
"""
import yaml
import urllib.request, urllib.error, urllib.parse
import csv 
from io import StringIO


def _get_fileobj(_file):
    if not urllib.parse.urlparse(_file).scheme:
        _file = "file://"+_file
    return urllib.request.urlopen(_file, data=None)

def get_items(_file):
    """
        get_items(_file)

        Arguments:
            _file: string; path to a local or remote resource with itemData definitions saved in a YAML file.

        Returns:
            a list of contextItem instances
    """
    f0 = _get_fileobj(_file)
    context_items =  [contextItem((d["Lex"],
                                   d["Type"],
                                   r"%s"%d["Regex"],
                                   d["Direction"])) for d in yaml.load_all(f0)]
    f0.close()
    return context_items

def instantiateFromCSVtoitemData(csvFile, encoding='utf-8',headerRows=1,
        literalColumn = 0, categoryColumn = 1, regexColumn = 2, ruleColumn = 3):
    """
    LEGACY CODE FOR READING itemData definitions in tab separated files.
    
    takes a CSV file of itemdata rules and creates a single itemData instance.
    csvFile: name of file to read items from
    encoding: unicode enocidng to use; default = 'utf-8'
    headerRows: number of header rows in file; default = 1
    literalColumn: column from which to read the literal; default = 0
    categoryColumn: column from which to read the category; default = 1
    regexColumn: column from which to read the regular expression: default = 2
    ruleColumn: column from which to read the rule; default = 3
    """
    items = []
    header = []
    f0 = _get_fileobj(csvFile)
    reader = csv.reader(StringIO(f0.read().decode(), newline=None), delimiter="\t" )
    #reader = csv.reader(open(csvFile, 'rU'))
    # first grab numbe rof specified header rows
    for i in range(headerRows):
        row = next(reader)
        header.append(row)
    # now grab each itemData
    for row in reader:
        tmp = [row[literalColumn], row[categoryColumn],
               row[regexColumn], row[ruleColumn]]
        tmp[2] = r"{0}".format(tmp[2]) # convert the regular expression string into a raw string
        item = contextItem(tmp)
        items.append(item)
    f0.close()
    return items

class contextItem(object):


    def __init__(self, args):
        self.__literal = args[0]
        cs = args[1].split(",")
        self.__category = []
        for c in cs:
            self.__category.append(c.lower().strip())
        self.__re = r"%s"%args[2] # I need to figure out how to read this raw string in properly
        self.__rule = args[3].lower()

        # generate regex from literal if no regex provided
        if not self.__re:
            self.__re = r"\b{}\b".format(self.__literal)

    def getLiteral(self):
        """return the literal associated with this item"""
        return self.__literal
    def getCategory(self):
        """return the list of categories associated with this item"""
        return self.__category[:]
    def categoryString(self):
        """return the categories as a string delimited by '_'"""
        return '_'.join(self.__category)


    def isA(self,testCategory):
        """test whether testCategory is one of the categories associated with self"""
        try:
            return testCategory.lower().strip() in self.__category
        except:
            for tc in testCategory:
                if( tc.lower().strip() in self.__category ):
                    return True
            return False

    def getRE(self):
        return self.__re
    def getRule(self):
        return self.__rule
    def __str__(self):
        txt = """literal<<{0}>>; category<<{1}>>; re<<{2}>>; rule<<{3}>>""".format(
            self.__literal,self.__category,self.__re, self.__rule)
        return txt
    def __repr__(self):
        return self.__str__()

