from PyQt5.QtWidgets import (QApplication,QTableWidget,QTableWidgetItem,QWidget,
QVBoxLayout,QHBoxLayout,QScrollArea,QLabel,QPushButton,QFileDialog,QLineEdit,QTextEdit)
from PyQt5 import QtWidgets,QtCore
import os
from pathlib import Path
import pandas as pd
import numpy as np
from pypinyin import lazy_pinyin
import re
class save_thread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(tuple)
    def __init__(self,target):
        super().__init__()
        self.target = target
    def run(self):
        p = self.target()
        self.trigger.emit((p,))
def wash_data(pd_data,ispinyin=False):
    pd_data = pd_data.fillna('')
    pd_data = pd_data.astype('str')
    
    def is_primary(s):
        r = s.shape[0]
        k = s.dropna()
        n = k.shape[0]
        if n is 0:return False
        m = k.drop_duplicates().shape[0]
        if m/n>=0.9 and m/r>0.7:
            return True
        else:
            return False
    #查找有没有email列
    if 'email' not in pd_data:
        email_pattern = re.compile('(email|邮箱)')
        tp = [key for key in pd_data.keys() if email_pattern.search(key.lower())]
        if len(tp)==1:
            key = tp[0]
            t = [0 for e in pd_data[key].values if e.find('@') != -1]
            if len(t)/pd_data.shape[0] > 0.9:
                pd_data.rename(columns={key: 'email'}, inplace=True)
            
    if 'email' in pd_data:
        pd_data['email'] = pd_data['email'].str.strip()
        pd_data['email'] = pd_data['email'].str.lower()
    

    #增加姓名拼音列
    if ispinyin and '姓名' in pd_data and '姓名_pinyin' not in pd_data:
        pd_data['姓名_pinyin'] = ''
        for index_,value in pd_data.iterrows():
            s = lazy_pinyin(value['姓名'])
            s = ''.join(s)
            pd_data.at[index_,'姓名_pinyin'] = s
    col_dict = {}
    for i in pd_data.keys():
        if is_primary(pd_data[i]):
            col_dict[i] = i+'_key'
    if col_dict:
        pd_data.rename(columns=col_dict, inplace=True)
    return pd_data
def DataFrame_cat_2(pd1,pd2):


    def add_new_data(pd1,data,primary_keys,co_keys,new_keys):
        for i in primary_keys:
            d0 = pd1.loc[pd1[i] == data[i]]
            if not d0.empty:
                d = d0.iloc[0]
                index_ = d0.index[0]
                pd1.at[index_, Remark_] += '主键 {}\n'.format(i)

                for co in co_keys:
                    if co == i:
                        continue
                    if d[co]!=data[co]:
                        if d[co]:
               
                            pd1.at[index_,co]= '{} / {}'.format(d[co],data[co])
                            pd1.at[index_, Remark_] += '不同 {}\n'.format(co)
                        else:
                  
                            pd1.at[index_,co] = data[co]

                    else:
                        pd1.at[index_, Remark_] += '同 {}\n'.format(co)

                for nw in new_keys:
                    pd1.at[index_, nw] = data[nw]
                break
        else:
            data[Remark_]='新增 '
            pd1 = pd1.append(data,ignore_index = True)
        return pd1
    for i in range(1000):    
        Remark_ = 'Remark_'+str(i)
        if Remark_ not in pd1:
            break
    pd1[Remark_] = ''
    
    co_keys = [i for i in pd2 if i in pd1 and i.endswith('_key')]
    primary_keys = [i for i in co_keys if i.find('_except')==-1]
    new_keys = [i for i in pd2 if i not in co_keys]
    # print(new_keys,'newwwwww')
    if not co_keys:
        pd2[Remark_] = '未匹配到类似信息，直接追加'
        return pd1.append(pd2, ignore_index=True)

    for i in new_keys:
        pd1[i]=''
    
    pd2[Remark_] = ''
    for _,data in pd2.iterrows():
        pd1 = add_new_data(pd1,data,primary_keys,co_keys,new_keys)

    for i,v in pd1.iterrows():
        s = v[Remark_].strip().replace('_key','').split('\n')
        s.sort(key = lambda x:'啊' if x.startswith('主') else x)
        s.reverse()
        pd1.at[i,Remark_] = '\n'.join(s)
    return pd1
def DataFrame_concat_many(*pds):
    pds = [wash_data(i) for i in pds]
    a = pds[0]
    for i in pds[1:]:
        a = DataFrame_cat_2(a,i)
    l = a.columns.tolist()
    remark = [i for i in l if i.startswith('Remark_')]
    without_remark = [i for i in l if not i.startswith('Remark_')]
    remark.sort()
    without_remark.extend(remark)

    a = a.loc[:,without_remark]

    col_dict = {i:i.replace('_key','') for i in a.keys()}
    a.rename(columns = col_dict,inplace=True)
    return a
class YTextEdit(QTextEdit):
    def setParent(self,p):
        self.parent = p
        self.setAcceptDrops(True)
    def dragEnterEvent(self,e):
        self.parent.dragEnterEvent(e)
    def dropEvent(self,e):
        self.parent.dropEvent(e)
class mainWidget(QWidget):
    
    def __init__(self):
        super().__init__(None)
        self.setupUi()
        self.init_run()
        self.setAcceptDrops(True)
        self.resize(500,300)
        self.show()
    def init_run(self):
        self.filenames = list()
        self.n_text.setText('1')
        self.verbose.setText('''使用规则:
        根据每个表中相同列名的数据进行匹配（该列的数据需要有较强的不重复性，比如会自动选择email列或者姓名列作为匹配规则，而不会使用性别，年龄这样数据重复量大的列作为匹配规则），
        如果不需要根据某一列匹配，但是该列又满足匹配列规则，可以将该列命名为"列名_except"的形式，则会自动排除该列，
        如不需要根据"开始时间"进行匹配，则只要将所有表中的开始时间列重命名为"开始时间_except"就可以了
        Tips:建议将主要的表格放在第一个，输出结果更美观
        ''')
        self.auto_slide()
    def setupUi(self):
        hbox = QHBoxLayout()
        open_button = QPushButton('打开',self)
        open_button.clicked.connect(self.open_clicked)
        n_label = QLabel('Sheet 数',self)
        self.n_text = QLineEdit('1',self)
        self.output = QPushButton('导出',self)
        self.output.clicked.connect(self.export_clicked)
        init_button = QPushButton('初始化',self)
        init_button.clicked.connect(self.init_run)
        hbox.addWidget(open_button)
        hbox.addWidget(init_button)
        hbox.addWidget(n_label)
        hbox.addWidget(self.n_text)
        hbox.addWidget(self.output)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        self.verbose = YTextEdit()
        self.bar = self.verbose.verticalScrollBar()
        self.verbose.setParent(self)
        vbox.addWidget(self.verbose)
        self.setLayout(vbox)
    def export_clicked(self,e):
        if not self.filenames:
            self.verbose.append('没有导入表格!!')
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Open File","output.xlsx",'*.xlsx *.xls')
        if not filename:
            return
        self.save_file(filename)

    def open_clicked(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open File", "", '*.xlsx *.xls *.csv')
        if not filenames:
            return 
        [self.open_file(i) for i in filenames]
    def save_file(self,filename):
        def start_save():
            pds =[]
            for i in self.filenames:
                suffix = Path(i).suffix
                if suffix == '.csv':
                    p = None
                    for code in ['utf8','utf16','gbk']:
                        try:
                            fp = open(i, 'r', encoding=code)
                            k = fp.readline()
                            if k.find(',') != -1:
                                sep = ','
                            elif k.find('\t') != -1:
                                sep = '\t'
                            else:
                                sep = ','
                            fp.seek(0, 0)
                            p = pd.read_csv(fp,dtype = 'str',sep = sep)
                            fp.close()
                            break
                        except Exception as e:
                            print(e)
                            fp.close()
                    if p is None:
                        self.verbose.append('文件读取错误：\n可以尝试将该文件({})转为excel格式(推荐)，或者用vscode打开转为utf8编码格式，然后重新尝试,Good luck!')
                        continue    
                else:
                    p = pd.read_excel(i)
                pds.append(p)
            p = DataFrame_concat_many(*pds)
            return p 
        def call_back(p):
            p = p[0]
            n = self.n_text.text()
            try:
                n = int(n)
            except:
                n = 1
            self.verbose.append('输出{}张表\n输出文件：{}'.format(n,filename))
            h = p.shape[0] 
            m = h//n
            if h%n != 0:
                m+=1
            writer = pd.ExcelWriter(filename)
            for i in range(n):
                s = p.iloc[i*m:min((i+1)*m,h)]
                s.to_excel(writer, 'Sheet'+str(i+1), index=False)
            writer.save()
            self.auto_slide()
        self.ss = save_thread(start_save)
        self.ss.trigger.connect(call_back)
        self.ss.start()
        self.verbose.append('正在处理...请稍等')
    def open_file(self,f):
        self.filenames.append(f)
        self.verbose.append('添加文件:'+f)
        self.auto_slide()
    def auto_slide(self):
        value = self.bar.value()
        self.bar.setValue(value+10000)
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls():
            urls = e.mimeData().urls()
            k = [Path(i.toLocalFile()).suffix for i in urls]
            m = [i for i in k if i.lower() in ['.xlsx','.xls','.csv']]
            if m:
                e.accept()
            else:
                e.ignore()
    def dropEvent(self,e):
        [self.open_file(i.toLocalFile()) for i in e.mimeData().urls()]
def main():
    import sys 
    app = QApplication(sys.argv)

    w = mainWidget()

    sys.exit(app.exec_())
if __name__=='__main__':
    main()
    # from IPython import embed
    # pd1 = pd.read_csv('4.csv')
    # pd2 = pd.read_excel(
    #     '/home/yxs/Documents/pythonAPP/excel/Udacity「数据分析师」进阶-7天试学班学籍表-C6.xlsx')
    # pd3 = pd.read_excel(
    #     '/home/yxs/Documents/pythonAPP/excel/Udacity「数据分析师」入门-7天试学班学籍表-C6.xlsx')

    # s = DataFrame_concat_many(pd3,pd2,pd1)
    
    # s.to_excel('output.xlsx',index=False)
    # embed()

