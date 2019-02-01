import os
import datetime
from collections import defaultdict
from contextlib import contextmanager
from xlsxwriter.workbook import Workbook

today = datetime.date.today()

class EOWriter:

    def __init__(self, book=None, sheet=None):
        self.__book__ = defaultdict()
        self.__sheet__ = defaultdict(dict)
        self.__msg__ = dict()
        self.__fmt__ = defaultdict(dict)
        self.__nrow__ = defaultdict(int)
        if book is not None:
            self.setworkbook(book)
        if sheet is not None:
            self.setworksheet(sheet)

    def setworkbook(self, book=None):
        workbooks = self.__book__
        self.book = book
        if book not in workbooks:
            workbooks[book] = Workbook(book, {'strings_to_numbers': True})
            self.setformats(book)  
        workbook = workbooks[book]       
        self.workbook = workbook             
        return workbook
    
    def setworksheet(self, sheet):
        book = self.book
        workbook = self.workbook
        sheets = self.__sheet__
        try:
            worksheet = sheets[book][sheet]
        except KeyError:
            sheets[book][sheet] = workbook.add_worksheet(sheet)
        worksheet = sheets[book][sheet]
        self.sheet = sheet
        self.worksheet = worksheet
        return worksheet

    def setmsg(self, msg=None, book=None, sheet=None):
        book = book or self.book
        sheet = sheet or self.sheet
        msg = msg or today.isoformat()
        msgs = self.__msg__
        msgs[(book, sheet)] = msg
        return msg

    def getmsg(self, book=None, sheet=None):
        book = book or self.book
        sheet = sheet or self.sheet
        msgs = self.__msg__
        return msgs.get((book, sheet)) or today.isoformat()

    def define_name(self, workbook, name, value):
        workbook = workbook or self.workbook
        self.workbook.define_name(name, str(value))
        return self  

    def setformats(self, book):
        workbook = self.__book__[book]
        fmt = self.__fmt__[book]
        fmt['Bold'] = workbook.add_format({'bold': 1, 'align': 'center'})
        fmt['data'] = workbook.add_format()
        fmt['int'] = workbook.add_format({'num_format': '0'})
        fmt['float'] = workbook.add_format({'num_format': '0.00'})
        fmt['time'] = workbook.add_format({'num_format': 'yyyy-m-d h:mm;@'}) 
        fmt["center"] = workbook.add_format({"align": "center", "border": 1})
        fmt["date"] = workbook.add_format({"num_format": 'yyyy-mm-dd', "align": "left", "border": 1})
        fmt["left"] = workbook.add_format({"align": "left", "border": 1})
        fmt["percentage"] = workbook.add_format({"num_format": '0.00%', "border": 1})
        fmt["0"] = workbook.add_format({"border": 1})
        fmt["1"] = workbook.add_format({"num_format": '0.00', "border": 1})        
        for cfmt in fmt.values():
            cfmt.set_font_name(u'Arial')
            cfmt.set_font_size(10)
            cfmt.set_align('vcenter')
            cfmt.set_text_wrap(True)
        self.fmt = fmt
        return self

    def writemsg(self, worksheet, msg, row=0, r0=0):
        worksheet = worksheet or self.worksheet
        r1 = row + r0
        worksheet.merge_range(r1, 0, r1, 4, msg)
        return worksheet        

    def writeheader(self, worksheet, r0=0):
        worksheet = worksheet or self.worksheet
        fmt = self.fmt
        row = r0
        r1, r2 = row+1, row+2        
        worksheet.merge_range(r1, 0, r1, 1, "监控设置", fmt["center"])
        worksheet.merge_range(r1, 2, r1, 4, "参考值", fmt["center"])
        worksheet.merge_range(r1, 5, r1, 6, "调整基准", fmt["center"])
        worksheet.merge_range(r1, 7, r1, 8, "调整系数", fmt["center"])
        worksheet.merge_range(r1, 9, r1, 10, "调整值", fmt["center"])
        worksheet.merge_range(r1, 11, r1, 12, "设置值", fmt["center"])
        worksheet.merge_range(r1, 13, r1, 15, "实际设置区间百分比", fmt["center"])
        worksheet.write(r2, 0, "通道", fmt["center"])
        worksheet.write(r2, 1, "监控条件", fmt["center"])
        worksheet.write(r2, 2, "下限", fmt["center"])
        worksheet.write(r2, 3, "上限", fmt["center"])
        s = "中心 基准 基准系数 下限A 上限B 下限C 上限D 下限L 上限U 下限% 上限% 区间宽度%".split()
        for c in range(4, len(s)+4):
            worksheet.write(r2, c, s[c-4], fmt["center"])
        return row+3        

    @contextmanager
    def writerow(self, row, r0=3):
        worksheet = self.worksheet
        fmt = self.fmt        
        r1 = row + r0
        fmt0 = fmt["0"]
        fmt1 = fmt["1"]
        worksheet.set_column(0, 0, 4)
        worksheet.set_column(2, 3, 6)
        worksheet.write_formula(r1, 4, "($D{0}+$C{0})/2".format(r1+1), fmt1)
        worksheet.write_formula(r1, 5, "($D{0}-$C{0})/10".format(r1+1), fmt1)
        worksheet.write_formula(r1, 6, "$F{0}/$E{0}".format(r1+1), fmt["percentage"])
        formula1 = "Floor($C4+$F4*$H4, precision)".replace("4", "{0}")
        formula2 = "Ceiling($D4+$F4*$I4, precision)".replace("4", "{0}")
        worksheet.write_formula(r1, 9, formula1.format(r1+1), fmt1)           
        worksheet.write_formula(r1, 10, formula2.format(r1+1), fmt1)
        formulas = ["$J4", "$K4", "1-$L4/$E4", "$M4/$E4-1", "($M4-$L4)/$E4"]
        for c in range(11, 16):
            formula = formulas[c-11].replace("4", "{0}")
            if c < 13:
                worksheet.write_formula(r1, c, formula.format(r1+1), fmt1)
            else:
                worksheet.write_formula(r1, c, formula.format(r1+1), fmt["percentage"])
        yield

    def __call__(self, record, row=None, r0=3):
        book, sheet = self.book, self.sheet
        if row is None:
            row = self.__nrow__[(book, sheet)]
            self.__nrow__[(book, sheet)] += 1
        worksheet = self.worksheet
        fmt = self.fmt        
        fmt0 = fmt["0"]
        fmt1 = fmt["1"]
        r1 = row + r0
        if len(record) == 3:
            record = [0] + record + [0, 0]
        if len(record) == 4:
            record = record + [0, 0]
        record = [str(v) for v in record]
        with self.writerow(row, r0):                   
            worksheet.write(r1, 0, record[0], fmt["center"])
            worksheet.write(r1, 1, record[1], fmt0) 
            worksheet.write(r1, 2, record[2], fmt0)
            worksheet.write(r1, 3, record[3], fmt0)
            worksheet.write(r1, 7, record[4], fmt0)
            worksheet.write(r1, 8, record[5], fmt0)
        return record

    def save(self):
        for book, workbook in self.__book__.items():
            self.define_name(workbook, "precision", "1")
            path = os.path.split(book)[0]
            if path and (not os.path.exists(path)):
                os.makedirs(path)
            for sheet, worksheet in self.__sheet__[book].items():
                self.writeheader(worksheet)
                msg = self.getmsg(book, sheet)
                self.writemsg(worksheet, msg)
            workbook.close()

