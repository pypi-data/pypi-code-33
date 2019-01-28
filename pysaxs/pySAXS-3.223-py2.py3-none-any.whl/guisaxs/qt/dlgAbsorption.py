from PyQt5 import QtCore, QtGui, QtWidgets, uic

import sys

try :
    from pySAXS.LS import absorptionXRL as absorption #will use xraylib
    USING_XRAYLIB=True
except:
    from pySAXS.LS import absorption #will not use xraylib
    USING_XRAYLIB=False
import numpy
import pySAXS
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class dlgAbsorption(QtWidgets.QDialog):#,dlgAbsorptionui.Ui_absorption):
    def __init__(self,parent,title='Absorption calculation',printout=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgAbsorption.ui", self)#
        
        self.parentwindow=parent
        self.printout=printout
        self.setWindowTitle(title)
        self.energy=0
        self.lambdaValue=0
        self.ActiveFormula=""
        self.ActiveAtomes=numpy.zeros(120)
        self.verbose=True
        
        #setup UI    
        #self.setupUi(self)
        self.ConstructUI()
        #start
        self.UpdateElementDisplay('H')
        
    def ConstructUI(self):
        '''
        construct the UI
        '''
        #energy
        self.lineEnergy.setValidator(QtGui.QDoubleValidator())
        self.lineEnergy.setText(str(absorption.getEnergyFromSource('Cu')))
        self.OnEnergyChanged()
        self.lineEnergy.textChanged.connect(self.UpdateFormula)
        #the x-rays sources
        sources=absorption.COMMON_XRAY_SOURCE_MATERIALS
        i=1
        for name in sources:
            #add button
            item=QtWidgets.QPushButton(name,self.groupBoxEnergy)
            item.setObjectName(name)
            item.clicked.connect(self.OnXRaysSourcesClicked)
            self.gridXraySources.addWidget(item, 0, i, 1, 1)
            i+=1
        
        
        '''
        generate mendeleiev table
        '''
        #get table
        table=absorption.MENDELEIEV_TABLE
        for j in range(len(table)):
            for i in range(len(table[0])):
                #get element
                element=table[j][i]
                if element is not None:
                    #add button
                    item=QtWidgets.QPushButton(element,self.groupBoxTable)
                    item.setMaximumSize(30, 30)
                    item.setObjectName(element)
                    item.clicked.connect(self.OnElementClicked)
                    self.gridMendeleiev.addWidget(item, j, i, 1, 1)
                    #QtCore.QObject.connect(item, QtCore.SIGNAL('editingFinished ()'), self.onModelUpdate)
        #element informations
        self.ElementSymbol.setText('-')
        self.ElementName.setText('-')
        self.ElementAtomicNumber.setText('-')
        #element add
        #self.lineNumberOfAtoms.setValidator(QtGui.QDoubleValidator())
        self.lineNumberOfAtoms.setText(str(1.0))
        self.btnAdd.clicked.connect(self.OnAddElement)
        self.btnRemove.clicked.connect(self.OnRemoveElement)
        self.btnRemoveAll.clicked.connect(self.OnRemoveAllElement)
        #formula edit validator
        #self.lineDensity.setValidator(QtGui.QDoubleValidator())
        self.lineDensity.setText(str(1.0))
        self.lineDensity.textChanged.connect(self.updateCalculation)
        self.lineCompoundMuRho.setStyleSheet('color: blue')
        self.lineElectronicDensity.setStyleSheet('color: blue')
        self.lineScatteringLengthDensity.setStyleSheet('color: red')
        #self.lineThickness.setValidator(QtGui.QDoubleValidator())
        self.lineThickness.setText(str(1.0))
        self.lineThickness.textChanged.connect(self.updateCalculation)
        self.lineXRayTransmission.setReadOnly(True)
        self.lineXRayTransmission.setStyleSheet('color: blue')
        #self.lineXRayMeasuredTransmission
        self.lineXRayMeasuredTransmission.setText(str(1.0))
        self.lineXRayMeasuredTransmission.textChanged.connect(self.updateCalculation)
        self.lineEstimatedThickness.setReadOnly(True)
        self.lineEstimatedThickness.setStyleSheet('color: blue')
        self.lineActiveFormula.setStyleSheet(_fromUtf8("background-color: rgb(244, 255, 190);"))
        # empty all the edit
        self.EmptyFormula()
        #lib
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.blue)
        self.labelLib.setPalette(palette)
        if USING_XRAYLIB:
            self.labelLib.setText('Calculation made with XRAYLIB')
            self.labelLib.setStyleSheet('color: red')   
        else:
            self.labelLib.setText('Calculation made with datas from the NIST')
        
        for compound in absorption.COMPOUNDS:
            self.listPreDefined.addItem(compound)
        #label.setText("<font style='color: red;background: black;'>Hello universe!</font>")
        self.AddPredefined.clicked.connect(self.selectCompound)
               
    def OnEnergyChanged(self):
        '''
        text for energy changed 
        -> change lambda
        '''
        self.energy=float(self.lineEnergy.text())
        if self.energy!=0:
            self.lambdaValue=absorption.KEV2ANGST/self.energy
            self.lineLambda.setText(str(self.lambdaValue))

    def OnElementClicked(self):
        '''
        user clicked on an element
        '''
        sending_button = self.sender()
        symbol=str(sending_button.objectName())
        self.UpdateElementDisplay(symbol)
    
    def UpdateElementDisplay(self,symbol):
        '''
        update the element display
        '''
        Z=absorption.SymbolToAtomicNumber(symbol)
        self.ElementSymbol.setText(symbol)
        self.ElementName.setText(absorption.getNameZ(Z))
        self.ElementAtomicNumber.setText(str(Z))
        self.Z=Z
        self.lineElementAtomicWeight.setText(str(absorption.getMasseZ(Z)))
        self.lineElementMuRho.setText(str(absorption.getMuZ(Z,self.energy)))

    def OnXRaysSourcesClicked(self):
        sending_button=self.sender()
        source=str(sending_button.objectName())
        source=source.strip()
        #print "-",source,"-"
        energy=absorption.getEnergyFromSource(source)
        self.lineEnergy.setText(str(energy))
        
        
    def OnAddElement(self):
        an=float(str(self.lineNumberOfAtoms.text()))
        if self.Z!= 0:
            if self.ActiveAtomes[self.Z-1] != 0 :
                #The new Atome is already present
                self.ActiveAtomes[self.Z-1]=self.ActiveAtomes[self.Z-1]+an
            else :
                #its a brend new atome
                self.ActiveAtomes[self.Z-1]=an
            self.UpdateFormula()
    
    def OnRemoveElement(self):
        #an=float(str(self.lineNumberOfAtoms.text()))
        if self.Z!= 0:
            self.ActiveAtomes[self.Z-1]=0
            self.UpdateFormula()

    
    def OnRemoveAllElement(self):
        self.ActiveAtomes=numpy.zeros(120)#reset the list
        self.EmptyFormula()

    def EmptyFormula(self):
        self.lineActiveFormula.setText("")
        #self.lineActiveFormula.setForeground(0,QtGui.QColor('blue'))
        self.lineCompoundMuRho.setText("")
        self.lineElectronicDensity.setText("" )
        self.lineScatteringLengthDensity.setText("")
        self.lineXRayTransmission.setText("")
        
    def selectCompound(self):
        ' a compound is selected'
        c= self.listPreDefined.currentText()
        ele=absorption.COMPOUNDS[c]
        self.ActiveFormula=str(ele[0])
        self.density=ele[1]
        self.lineActiveFormula.setText(self.ActiveFormula)
        self.lineDensity.setText(str(self.density))
        # When density text is changed updatecalculation is called
        #self.updateCalculation() 
    

    def updateCalculation(self):
        self.energy=float(self.lineEnergy.text())
        if self.energy!=0:
            self.lambdaValue=absorption.KEV2ANGST/self.energy
            self.lineLambda.setText(str(self.lambdaValue))
        
        self.ActiveFormula=str(self.lineActiveFormula.text())
        
        if self.ActiveFormula=="":
            return
        MuRho = absorption.getMuFormula(self.ActiveFormula, self.energy)
        self.lineCompoundMuRho.setText("%1.5e" % MuRho)
        
        density = float(self.lineDensity.text())
        
        ED = absorption.getElectronDensity(self.ActiveFormula, density)[0]
        self.lineElectronicDensity.setText("%1.5e" % ED)
        SLD = absorption.getElectronDensity(self.ActiveFormula, density)[1]
        self.lineScatteringLengthDensity.setText("%1.5e" % SLD)
        thickness = float(self.lineThickness.text())
        Tr = absorption.getTransmission(self.ActiveFormula, thickness, 
            density, 
            self.energy)
    #self.TransLabel.SetLabel("X-ray transmission  = %1.5e" % numpy.exp(-float(self.DensityText.GetValue())*absorptionXRL.getMuFormula(self.ActiveFormula,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())*float(self.ThicknessText.GetValue())))
        self.lineXRayTransmission.setText("%8.7f" % Tr)
        TrM = float(self.lineXRayMeasuredTransmission.text())
        Thi = absorption.getThickness(self.ActiveFormula, TrM, density, self.energy)
    #print Thi
        self.lineEstimatedThickness.setText('%6.7f' % Thi)
        if self.verbose:
            if USING_XRAYLIB:
                self.printTXT("------ Absorption tools using xraylib -----")
            else:
                self.printTXT("------ Absorption tools using NIST DATA -----")
            self.printTXT("Compound formula: ", self.ActiveFormula)
            self.printTXT("Energy : %6.3f (keV) " % self.energy)
            self.printTXT("Density : %6.3f " % density)
            self.printTXT("Compound Mu_en/rho  = %6.3f (cm2/g) " % MuRho)
            self.printTXT("Electronic density  = %1.5e (1/cm3) " % ED)
            self.printTXT("Scattering length density  = %1.5e (1/cm2) " % SLD)
            self.printTXT("with thickness of %8.7f cm -> X-ray transmission  = %8.7f" % (thickness, Tr))
            self.printTXT("with X-ray transmission of %8.7f -> thickness  = %8.7f cm" % (TrM, Thi))

    def UpdateFormula(self,verbose=False):
        Tr=-1
        ED=-1
        SLD=-1
        #print "Fupdate"
        
        
        self.ActiveFormula=""
        #If at least one atome exist
        if sum(self.ActiveAtomes)<=0.0:
            self.EmptyFormula()
        else: 
            N=self.ActiveAtomes.take(numpy.where(self.ActiveAtomes!=0)[0])
            ind=numpy.where(self.ActiveAtomes!=0)[0]
            j=0
            for i in ind:
                #self.ActiveFormula=self.ActiveFormula + str(absorptionXRL.ATOMS[int(i)]) + ' ' + str(int(N[int(j)])) + ' '
                self.ActiveFormula=self.ActiveFormula + absorption.AtomicNumberToSymbol(int(i)+1) + ' ' + str(N[int(j)]) + ' '
                j=j+1
            
            self.lineActiveFormula.setText(self.ActiveFormula.strip())
            self.updateCalculation()

    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)

if __name__ == "__main__":
      app = QtWidgets.QApplication(sys.argv)
      dlg=dlgAbsorption(None)
      dlg.exec_()
