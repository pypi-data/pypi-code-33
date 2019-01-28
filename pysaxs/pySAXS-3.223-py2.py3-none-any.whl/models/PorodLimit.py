from pySAXS.models.model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class PorodLimit(Model):
    '''
    Porod
    
    for Porod Model
    by OT 10/06/2009
    '''
    def PorodLimitFunction(self,q,par):
        """
        Porod model to fit q-4 part at high q
        par[0] : Scattering length density contrast in cm-2
        par[1] : S/V cm-1
        """
        return par[0]*q**-4.0
            
    '''
    parameters definition
    class Model(7,Porod,/
    Qlogspace(1e-4,1.,500.),(
    [1.0e10,1e6]),
    ("Scattering contrast (cm-2)",
    "S/V (cm-1)"),("%1.3e","%1.3e"),
    (True,True)),
     
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PorodLimitFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[1.0e10]#,1e6]           #list of defaults parameters
        self.Format=["%6.2f"]#,"%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True]    #list of boolean for fitting
        self.name="Porod Limit"          #name of the model
        self.Doc=["Scattering contrast (cm-2)"]#,             "S/V (cm-1)"] #list of description for parameters
