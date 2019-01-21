import xlsxwriter as xlsxwriter

from performance import SHEET_NAME, COLORS


class Excel2(object):

    def __init__(self):
        self.cur_row = 1
        self.sheet = None
        self.workbook = None
        self.column_count = 0

    def create_memory_sheet(self, output, datas):
        assert isinstance(output, str)
        self.workbook = xlsxwriter.Workbook(output)
        self.sheet = self.workbook.add_worksheet(name=SHEET_NAME)
        # cell 格式类型
        # bold = self.workbook.add_format({'bold': 1})
        self.column_count = datas.__len__()
        self.sheet.write_row('A1', datas.keys())
        self.cur_row += 1
        return self.sheet

    def add_data(self, datas):
        # print("add data: " + datas)
        self.sheet.write_row('A' + str(self.cur_row), datas.values())
        self.cur_row += 1

    def create_chart(self):
        count = self.cur_row - 1
        chart = self.workbook.add_chart({'type': 'line'})
        start = 'A'
        for i in range(self.column_count):
            col = chr(ord(start) + i)
            name = '=%s!$%s$1' % (SHEET_NAME, col)
            values = '=%s!$%s$2:$%s$%d' % (SHEET_NAME, col, col, count)
            chart.add_series({
                'name': name,
                'values': values,
                'line': {'color': COLORS[i]}
            })
        chart.set_style(1)
        chart.height = 600
        chart.width = 960
        self.sheet.insert_chart("M25", chart)

    def save(self):
        self.create_chart()
        self.workbook.close()
        pass

