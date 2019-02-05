import json
import uuid
import logging


# content to export sheet cell
class ExportDocumentReportCellContent():
    # constructor
    def __init__(self, data, bgc='#ffffff', color="#000000", ta="left", fz="10", fm="", fw="normal", fs="normal", u="",
                 ff="arial", width=50, id=-1, row=-1, show_grid=False, contains_data=False, height=30):
        try:
            self.width = width
            self.data = data
            self.bgc = bgc
            self.color = color
            self.ta = ta
            self.fz = fz
            self.fm = fm
            self.fw = fw
            self.fs = fs
            self.u = u
            self.ff = ff
            self.id = id
            self.ww = 'break-word'
            self.ws = 'pre-line'
            self.va = 'middle'
            self.ta = 'center'
            self.height = height

            self.bls = 'solid'
            self.brs = 'solid'
            self.bts = 'solid'
            self.bbs = 'solid'

            self.blc = '#7f7f7f'
            self.brc = '#7f7f7f'
            self.btc = '#7f7f7f'
            self.bbc = '#7f7f7f'

            self.blt = 'solid'
            self.brt = 'solid'
            self.btt = 'solid'
            self.bbt = 'solid'
            # self.bgc = bgc
        except Exception as e:
            logging.error("Error initialization. " + str(e))


# export document sheet cell
class ExportDocumentReportCell():
    # constructor
    def __init__(self, sheet, row, col, cellJson):
        try:
            self.sheet = sheet
            self.row = row
            self.col = col
            self.json = cellJson
        except Exception as e:
            logging.error("Error initialization. " + str(e))


# export document group
class ExportDocumentGroup():
    # constructor
    def __init__(self, level, span):
        try:
            self.level = level
            self.span = span
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # convert model to JSON
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


# export documnet report floatings model
class ExportDocumentReportFloatings():
    # constructor
    def __init__(self, sheet, name, ftype, json):
        self.sheet = sheet
        self.name = name
        self.ftype = ftype
        self.json = json
        pass


# export sheet model report
class ExportDocumentReportSheet():
    # constructor
    def __init__(self, id, name):
        try:
            self.id = id
            self.name = name
        except Exception as e:
            logging.error("Error initialization. " + str(e))


# export sheet report document
class ExportDocumentReportModel():
    # constructor
    def __init__(self, fileName):
        try:
            self.fileName = fileName
            self.sheets = []
            self.floatings = []
            self.cells = []
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # start from 1
    def add_sheet(self, id, name):
        try:
            self.sheets.append(ExportDocumentReportSheet(id, name))
        except Exception as e:
            logging.error("Error " + str(e))

    # convert model to JSON
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
