from pySAXS.models.model import Model
from pySAXS.LS.LSsca import *
import numpy

class Triedra(Model):
    '''
    Cubes and parallelepiped
    by OS : 11/11/2011
    '''
    
    def PTriedre(self,q,par):
        """
        q array of q (A-1)
        par[0] side length  (in 1/q)
        par[1] thickness of the triedre (in 1/q)
        par[2] SLD particle (cm-2)
        par[3] SLD medium (cm-2)
        par[4] number density (cm-3)
        """        
        a = par[0]
        e=par[1]
        rho1 = par[2]
        rho2 = par[3]
        n=par[4]

        prefactor = 1e-48*n*(rho1-rho2)**2
        sign=[1,1,1,1,1]

        f = 3./16.*(e*a**2)**2*Pdqpoly(q,FaceTri(Triedre(a,e)),sign,24)
        return prefactor*f
    
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PTriedre #function
        self.N=0
        self.q=Qlogspace(3e-4,1.,50.)                             #q range(x scale)
        self.Arg=[30.,20.,9.8e11,9.8e10,1e10]                         #list of parameters
        self.Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,False,False,False]           #list of boolean for fitting
        self.WarningForCalculationTime=False
        self.name="Not for fit: Triedra!"                      #name of the model
        self.Doc=["side length  ",\
             "thickness (in 1/q)",\
             "scattering length density of particle (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "Number density (cm-3)"]           #list of description for parameters
        self.Description="Triedra "  # description of model
        self.Author="Olivier Spalla"                 #name of Author
    
