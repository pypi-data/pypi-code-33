import sys
import json
import time
from threading import Thread

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

import sqlparse

from bonc_vertica.settings import account_dict, encodings, csv_format_info, conn_info, logging
from bonc_vertica.vertica import Selection
from bonc_vertica.loader import DataLoader


def get_goal_by_dialog_box(goal='file', filetype=None):
    """
    启用对话框, 以根据goal参数的不同选择文件或文件夹
    :param goal:
    :param filetype:
    :return: 返回文件名或文件夹名
    """
    root = tk.Tk()
    root.withdraw()

    goal_dict = {
        'file': filedialog.askopenfilename,
        'files': filedialog.askopenfilenames,
        'directory': filedialog.askdirectory,
        'dir': filedialog.askdirectory,
        'saveas': filedialog.asksaveasfilename,
        'save_as': filedialog.asksaveasfilename,
        }

    goal_func = goal_dict.get(goal)
    goal_name = goal_func(filetype=filetype) if isinstance(filetype, tuple) else goal_func()

    root.destroy()
    return goal_name


class Uiloop():
    """
    图形化界面
    """

    def __init__(self, *args, **kwargs):
        self.sql = ''

        self.top = Tk()
        self.top.title("Vertica数据导出工具 by chenzhongrun@bonc.com.cn")

        contents = ScrolledText()
        contents.grid(row=0, column=0, rowspan=7)
        contents.insert('insert', '/*\n* 暂不支持右键菜单，请Ctrl+V粘贴或写入SQL\n*/\n')

        action = Actions(self)
        btn_im_sure = Button(
            self.top,
            text='查询并导出',
            command=lambda: action.select_and_outport(
                contents_value=contents.get('1.0', END),
                combo_account=comboxlist.get(),
                combo_encoding=combox_encodings.get()
            )
        ).grid(row=5, column=1)

        comvalue = tk.StringVar()
        comboxlist = ttk.Combobox(self.top, textvariable=comvalue)  # 初始化
        comboxlist["values"] = tuple(account_dict.keys())
        comboxlist.current(2)  # 选择第一个
        comboxlist.grid(row=3, column=1, sticky=N)

        com_encodings_value = tk.StringVar()
        combox_encodings = ttk.Combobox(self.top, textvariable=com_encodings_value)  # 初始化
        combox_encodings["values"] = encodings
        combox_encodings.current(0)  # 选择第一个
        combox_encodings.grid(row=1, column=1, sticky=N)

        label_encoding = ttk.Label(self.top, text='选择输出文件编码')
        label_encoding.grid(row=0, column=1, sticky=W)

        label_account = ttk.Label(self.top, text='选择账号')
        label_account.grid(row=2, column=1, sticky=W)

        btn_format_sql = Button(
            self.top,
            text='格式化查询语句',
            command=lambda: action.format_sql(contents)
        ).grid(row=4, column=1)

        btn_exit = Button(
            self.top,
            text='退出',
            command=action.exit
        ).grid(row=6, column=1)

    def loop(self):
        self.top.mainloop()


class Actions(object):
    """
    按钮对应的事件
    """

    def __init__(self, ui):
        self.ui = ui
        self.conn_info = conn_info
        self.account_dict = account_dict
        self.csv_format_info = csv_format_info

    def exit(self):
        logging.info('用户主动退出！')
        sys.exit(0)

    def get_execute_info(self, contents_value, combo_account, combo_encoding):
        """
        获取文本框内的内容，即SQL
        """
        self.ui.sql = contents_value
        self.ui.account = combo_account
        self.ui.encoding = combo_encoding

    def format_sql(self, contents_frame):
        sql = sqlparse.format(contents_frame.get('1.0', END), reindent=True, keyword_case='upper')
        contents_frame.delete(1.0, END)
        contents_frame.insert('insert', sql)

    def select_and_outport(self, contents_value, combo_account, combo_encoding):
        self.get_execute_info(contents_value, combo_account, combo_encoding)

        try:
            self.conn_info['user'] = self.ui.account if self.ui.account else self.conn_info['user']
            self.conn_info['password'] = self.account_dict.get(self.ui.account)
            self.csv_format_info['encoding'] = self.ui.encoding if self.ui.encoding else self.csv_format_info['encoding']
            sql = self.ui.sql
        except AttributeError:
            self.ui.top.destroy()
            sys.exit(1)

        self.ui.top.destroy()

        logging.info('即将使用以下信息连接数据库并查询数据\n{}\n'.format(json.dumps(self.conn_info, indent=2, ensure_ascii=False)))
        logging.info('要查询的SQL语句如下：\n{}\n'.format(sql))

        def task_select():
            loader = DataLoader(**self.csv_format_info)
            with Selection(self.conn_info) as selection:
                # 为避免大表造成的内存压力，此处用with上下文管理连接，保持与数据库连接，查一点写一点
                result = selection.select(sql)

                logging.info('查询成功，请求另存为文件')
                to_file = get_goal_by_dialog_box(goal='save_as')
                loader.get_save_as_file(file=to_file)

                logging.info('即将写入文件：{}'.format(loader.file))
                logging.info('数据输出格式如下：')
                print(
                    '输出文件编码为 {}\n分隔符为 {}\n包括符为 {}\n'.format(
                        loader.encoding,
                        loader.delimiter,
                        loader.quotechar
                        )
                    )
                loader.overwrite_iter_rows(iter_rows=result).load_to_csv()

            logging.info(
                '数据导出程序已完成！\n{}于{}导出入了{}行×{}列到 {}'.format(
                    self.conn_info.get('user'),
                    time.strftime('%Y-%m-%d %H:%M'),
                    loader.outport_count,
                    loader.width,
                    loader.file
                )
            )
            if loader.outport_count != loader.writen_count:
                logging.error('导出数据量与写入文件数据量不一致，请报知作者！导出了{}行，写入了行{}'.format(
                    loader.outport_count,
                    loader.writen_count
                ))

        def init_ui():
            self.ui = Uiloop()
            self.ui.loop()

        threads = [Thread(target=task_select, daemon=True), Thread(target=init_ui)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=1)

