import os
import time

import xlsxwriter as xlsxwriter

from performance import SHEET_NAME, COLORS, matlab_plt


class excelx(object):

    def __init__(self):
        self.cur_row = 1
        self.sheet = None
        self.workbook = None
        self.column_count = 0
        self.file = None

    def create_memory_sheet(self, output, datas):
        assert isinstance(output, str)
        self.file = output
        self.workbook = xlsxwriter.Workbook(output)
        self.sheet = self.workbook.add_worksheet(name=SHEET_NAME)
        self.column_count = datas.__len__() + 1
        keys = list(datas.keys())
        keys.insert(0, '')
        self.sheet.write_row('A1', keys)
        self.cur_row += 1
        return self.sheet

    def add_data(self, datas):
        cur_time = time.strftime("%H:%M:%S")
        values = list(datas.values())
        values.insert(0, cur_time)
        self.sheet.write_row('A' + str(self.cur_row), values)
        self.cur_row += 1

    def create_chart(self, chart_name=None):
        count = self.cur_row - 1
        chart = self.workbook.add_chart({'type': 'line'})
        start = 'A'
        for i in range(1, self.column_count):
            col = chr(ord(start) + i)
            name = '=%s!$%s$1' % (SHEET_NAME, col)
            values = '=%s!$%s$2:$%s$%d' % (SHEET_NAME, col, col, count)
            categories = '=%s!$A$2:$A$%d' % (SHEET_NAME, count)
            chart.add_series({
                'name': name,
                'categories': categories,
                'values': values,
                'line': {'color': COLORS[i]}
            })
        chart.set_style(1)
        chart.height = 600
        chart.width = 1200
        chart.set_title({'name': chart_name})
        self.sheet.insert_chart("G15", chart)

    def save(self, output_dir):
        self.create_chart("内存(KB)")
        self.workbook.close()
        plt_temp = output_dir + os.path.sep + "plt_temp.png"
        matlab_plt.plt_export_chart(self.file, plt_temp)
        return plt_temp


