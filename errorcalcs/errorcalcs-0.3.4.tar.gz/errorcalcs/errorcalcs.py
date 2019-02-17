import os

from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QWidget, QScrollArea, QComboBox,
                             QMessageBox, QFileDialog)
from PyQt5.QtGui import (QIcon, QDoubleValidator)

from errorcalcs import calc, add

class e_c(QDialog):
    def __init__(self, parent=None):
        super(e_c, self).__init__(parent)
        
        usage_button = QPushButton('Usage')
        usage_button.clicked.connect(self.open_usage)
        abl_select = QLabel('Safe used formula for')
        self.style_abl = QComboBox()
        self.style_abl.addItems(["do not safe", 'LaTex', 'raw'])
        donation_button = QPushButton('Donate')
        donation_button.clicked.connect(self.donate)
        save_button = QPushButton('save here')
        save_button.clicked.connect(self.savehere)
        open_formula = QPushButton('open')
        open_formula.clicked.connect(self.openformula)
        
        exit_button = QPushButton('exit')
        exit_button.clicked.connect(self.close_)
        
        self.originalPalette = QApplication.palette()        
        
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftGroupBox()
        self.createBottomRightGroupBox()
        
        bottomLayout = QVBoxLayout()
        #bottomLayout.addWidget(exit_button)
        
        topLayout = QGridLayout()
        topLayout.addLayout(bottomLayout, 0,0,1,4)
        topLayout.addWidget(donation_button, 1, 0)
        topLayout.addWidget(usage_button, 1, 1)
        topLayout.addWidget(exit_button, 1, 3)
        topLayout.addWidget(abl_select, 2, 0)
        topLayout.addWidget(self.style_abl, 2, 1)
        topLayout.addWidget(save_button, 2, 2)
        topLayout.addWidget(open_formula, 2, 3)
        
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)
        
        self.setWindowTitle('ErroRCalcS - error propagation')
        
        self.insert_gaussTex = False
        self.insert_gaussRaw = False
        
    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox('add variable')
        
        self.var_in = QLineEdit('')
        self.value_in = QLineEdit('')
        self.value_in.setValidator(QDoubleValidator())
        self.error_in = QLineEdit('')
        self.error_in.setValidator(QDoubleValidator())
        
        var_label = QLabel('variable:')
        value_label = QLabel('value:')
        error_label = QLabel('error:')
        
        self.var_list = []
        self.value_list = []
        self.error_list =[]
        
        self.add_button = QPushButton('add variable')
        
        topLayout = QHBoxLayout()
        
        layout = QGridLayout()
        layout.addLayout(topLayout, 0, 0, 1, 3)
        layout.addWidget(var_label, 0, 0)
        layout.addWidget(self.var_in, 0, 1)
        layout.addWidget(value_label, 1, 0)
        layout.addWidget(self.value_in, 1, 1)
        layout.addWidget(error_label, 2, 0)
        layout.addWidget(self.error_in, 2, 1)
        layout.addWidget(self.add_button, 3, 0)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 1)
        self.topLeftGroupBox.setLayout(layout)
            
        self.add_button.clicked.connect(self.add_var)
        self.add_button.clicked.connect(self.variable_func)
        
        
    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox('calculation')
        
        self.calc_in = QLineEdit('')
        
        calc_label = QLabel('formula:')
        self.result_label = QLabel('result')
        
        self.calc_button = QPushButton('calculate')
        self.calc_button.clicked.connect(self.add_formel)
        self.calc_button.clicked.connect(self.history_func)
        self.calc_button.clicked.connect(self.show_result)

        
        topLayout = QHBoxLayout()
        self.layout = QGridLayout()
        self.layout.addLayout(topLayout, 0, 0, 1, 2)
        self.layout.addWidget(calc_label, 0, 0)
        self.layout.addWidget(self.calc_in, 0, 1)
        self.layout.addWidget(self.calc_button, 1, 0)
        self.layout.addWidget(self.result_label, 1, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setColumnStretch(1, 1)
        self.topRightGroupBox.setLayout(self.layout)
    
    def createBottomLeftGroupBox(self):
        self.bottomLeftGroupBox = QGroupBox('added variables')
        layout = QVBoxLayout()
        self.bottomLeftGroupBox.setLayout(layout)
        
        self.used = QScrollArea(self)
        
        layout.addWidget(self.used)
        
        self.used.setWidgetResizable(True)
        
        usedContent = QWidget(self.used)
        self.usedLayout = QVBoxLayout(usedContent)
        usedContent.setLayout(self.usedLayout)
        
        self.used.setWidget(usedContent)
    
    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox('history')
        layout = QVBoxLayout()
        self.bottomRightGroupBox.setLayout(layout)
        
        history = QScrollArea(self)
        layout.addWidget(history)
        history.setWidgetResizable(True)
        
        historyContent = QWidget(history)
        self.historyLayout = QVBoxLayout(historyContent)
        historyContent.setLayout(self.historyLayout)
        
        history.setWidget(historyContent)
        
#############GUI_functions####################
    def clear_func(self):
        self.var_list = []
        self.value_list = []
        self.error_list = []
        
    def variable_func(self):
        if str(self.error_list[-1]) == '':
            i = (str(self.var_list[-1]) + ' = ' +
                 str(self.value_list[-1]) + '+/-0')
            self.error_list.append('0')
        else:
            i = (str(self.var_list[-1]) + ' = ' +
                 str(self.value_list[-1]) + '+/-' +
                 str(self.error_list[-1]))
        self.usedLayout.addWidget(QLabel(i))
    
    def history_func(self):
        erg = open('.__log__/rechnungen.txt', 'r')
        erg_liste = []
        for line in erg:
            erg_liste.append(str(line.strip()))
        erg.close()
        for i in erg_liste:
            self.historyLayout.addWidget(QLabel(str(i)))
        
    def add_formel(self):
        self.datei_var = open('.__log__/var.txt', 'w')
        self.datei_value = open('.__log__/value.txt', 'w')
        self.datei_error = open('.__log__/error.txt', 'w')
        
        for i in self.var_list:
            if i == '':
                pass
            else:
                print(i, file = self.datei_var)
        for i in self.value_list:
            if i == '':
                pass
            else:
                print(i.replace(',', '.'), file = self.datei_value)
        for i in self.error_list:
            if i == '':
                pass
            else:
                print(i.replace(',', '.'), file = self.datei_error)
            
        self.datei_var.close()
        self.datei_value.close()
        self.datei_error.close()
        
        datei_formel = open('.__log__/formel.txt', 'w')
        print(self.calc_in.text(), file = datei_formel)
        datei_formel.close()
        
        self.var, value, error, self.formel = add.get_ins()
        ergebnis, self.formel = calc.calculate(self.var, value, error, self.formel)
        
        rechnung = str(self.formel) + ' = ' + str(ergebnis)
        ergebnis_datei = open('.__log__/ergebnis.txt', 'w')
        rechnung_datei = open('.__log__/rechnungen.txt', 'w')
        print(ergebnis, file = ergebnis_datei)
        print(rechnung, file = rechnung_datei)
        ergebnis_datei.close()
        rechnung_datei.close()
        if self.style_abl.currentText() == 'do not safe':
            pass
        else:
            try:
                pfad, typ = self.savedpfad
            except AttributeError:
                pfad = 'saved_formulas.txt'
            
            try:
                add.export_formula(self.style_abl.currentText(), self.var, self.formel,
                                   pfad)  
            except:
                pass

        
    def add_var(self):
        
        self.var_list.append(self.var_in.text())
        self.value_list.append(self.value_in.text())
        self.error_list.append(self.error_in.text())
        
    def show_result(self):
        erg = open('.__log__/ergebnis.txt', 'r')
        erg_list = []
        for line in erg:
            erg_list.append(str(line.strip()))
        result = erg_list[0]
        self.result_label.setText(result)
        
    def donate(self):
        status = add.open_donation()
        if status == 'no_connection':
            QMessageBox.about(self, 'Internet Connection',
                              'Please check your internet connection')
            
    def savehere(self):
        self.savedpfad = QFileDialog.getSaveFileName(self, 'Save here')
        pfad, typ = self.savedpfad
        try:
            add.export_formula(self.style_abl.currentText(), self.var, self.formel,
                               pfad)
        except AttributeError:
            pass
        
    def openformula(self):
        try:
            pfad, typ = self.savedpfad
        except AttributeError:
            pfad = 'saved_formulas.txt'
        add.open_fomula(pfad)
        
    def open_usage(self):
        status = add.open_usage()
        if status == 'no_connection':
            QMessageBox.about(self, 'Internet Connection',
                              'Please check your internet connection')
            
    def close_(self):
        self.close()
########end_of_GUI_functions########################
        
def run_e_c():
    import sys
    
    try:
        os.mkdir('.__log__')
    except FileExistsError:
        pass
    
    app = QApplication(sys.argv)
    gallery = e_c()
    gallery.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_e_c()
