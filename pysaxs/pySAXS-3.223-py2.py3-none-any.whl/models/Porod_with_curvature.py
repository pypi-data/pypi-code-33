from pySAXS.models.model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class PorodL(Model):
    '''
    Porod Layer
    
    for Spheres poly-Gauss Model
    by OT 10/06/2009
    '''
    def PorodLFunction(self,q,par):
        """
        Porod Layer model to fit q-4 part at high q
        par[0] : Scattering lenght density contrast in cm-2
        par[1] : S/V cm-1
        par[2] : Principal curvature 1 cm-1
        par[3] : Principal curvature 2 cm-1
        """
        return 2.0*numpy.pi*1.0e-32*par[0]*par[0]*par[1]*q**-4.0*(1.0+1e-16*q**-2.0*(((par[2]+par[3])**2.)/4.+((par[2]-par[3])**2.)/8.))

            
    '''
    parameters definition
    Model(9,PorodL,Qlogspace(1e-4,1.,500.)
    ,([1.0e10,1e10,1e-7,1e6]),(
    "Scattering contrast of core (cm-2)",
    "Scattering contrast of layer (cm-2)",
    "thickness of layer (cm)",
    "S/V (cm-1)"),("%1.3e","%1.3e","%1.3e","%1.3e"),(True,True,True,True)),
   
     
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PorodLFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)                               #q range(x scale)
        self.Arg=[1.0e10,1e10,1e-7,1e6]                              #list of defaults parameters
        self.Format=["%1.3e","%1.3e","%1.3e","%1.3e"]                #list of c format
        self.istofit=[True,True,True,True]                           #list of boolean for fitting
        self.name="Porod with curvature correction"                  #name of the model
        self.Doc=["Scattering contrast of core (cm-2)",\
             "Scattering contrast of layer (cm-2)",\
             "thickness of layer (cm)",\
             "S/V (cm-1)"] #list of description for parameters
    
