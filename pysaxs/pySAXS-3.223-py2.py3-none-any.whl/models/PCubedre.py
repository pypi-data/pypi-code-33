from pySAXS.models.model import Model
from pySAXS.LS.LSsca import *
import numpy

class Cubedra(Model):
    '''
    Cubes and parallelepiped
    by OS : 03/11/2011
    '''
    
    def PCubedre(self,q,par):
        """
        q array of q (A-1)
        par[0] side length 1 (in 1/q)
        par[1] SLD particle (cm-2)
        par[2] SLD medium (cm-2)
        par[3] number density (cm-3)
        """        
        a = par[0]
        rho1 = par[1]
        rho2 = par[2]
        n=par[3]

        prefactor = 1e-48*n*(rho1-rho2)**2
        sign=[1,1,1,1,1,1]

        f = a**6*Pdqpoly(q,Facescube(Cubedre(a,a)),sign,32)
        return prefactor*f
    
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=PCubedre #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,50.)                             #q range(x scale)
        self.Arg=[30.,9.8e11,9.8e10,1e10]                         #list of parameters
        self.Format=["%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,False,False,False]           #list of boolean for fitting
        self.name="Not for fit: Cubedra!"                      #name of the model
        self.Doc=["side length 1 ",\
             "scattering length density of particle (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "Number density (cm-3)"]           #list of description for parameters
        self.Description="Cubedre "  # description of model
        self.Author="Olivier Spalla"                 #name of Author
    
