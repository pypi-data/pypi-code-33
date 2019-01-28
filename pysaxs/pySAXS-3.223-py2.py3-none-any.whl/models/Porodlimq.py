from pySAXS.models.model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class Porodlim(Model):
    '''
    Porod
    
    for Porod Model
    by OT 10/06/2009
    '''
    def PorodFunctionlim(self,q,par):
        """
        Porod model to fit q-4 part at high q

        par[0] : limq (cm-2/A-4)
        """
        lim = par[0]
        I = lim*(q**-4)
        
        return self.Porodparameters(I,lim,par)
    
    def Porodparameters(self,I,lim,par):
        
        deltarho = par[1]
        dsty = par[2]
        sigma = (lim*1e42)/(2*numpy.pi*(deltarho*1e4)**2)
        surfspec = sigma/(dsty*1e6)
        diam = (6/(dsty*1e6*surfspec*1e-9))
        par[3] = surfspec
        par[4] = diam
        
        return I
 

    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PorodFunctionlim #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[1e-4,1.862e11,2.196,1,1]           #list of defaults parameters
        self.Format=["%f","%1.5e","%f","%f","%f"]      #list of c format
        self.istofit=[True,False,False,False,False]    #list of boolean for fitting
        self.name="Porod Specific Surface estimation"          #name of the model
        self.Doc=["lim (cm-1/A-4)",\
                  "Scattering contrast of core (cm-2)",\
                  "material density (g/cm-3)",\
                  "specific surface (m2/g)",\
                  "diameter (nm)"] #list of description for parameters
        self.Description="Porod Specific Surface estimation"  # description of model
        self.Author="Olivier Tach'e & Stanislas Doco"       #name of Author
    
