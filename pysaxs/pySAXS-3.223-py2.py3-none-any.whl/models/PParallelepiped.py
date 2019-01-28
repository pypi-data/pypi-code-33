from pySAXS.models.model import Model
from pySAXS.LS.LSsca import *
import numpy

class Parallelepiped(Model):
    '''
    Cubes and parallelepiped
    by OS : 03/11/2011
    '''
    
    def PParallelepiped(self,q,par):
        """
        q array of q (A-1)
        par[0] side length 1 (in 1/q)
        par[1] side length 2 (in 1/q)
        par[2] side length 3 (in 1/q)
        par[3] SLD particle (cm-2)
        par[4] SLD medium (cm-2)
        par[5] number density (cm-3)
        """        
        a = par[0]
        b = par[1]
        c = par[2]
        rho1 = par[3]
        rho2 = par[4]
        n=par[5]

        prefactor = 1e-48*n*(rho1-rho2)**2

        f = (a*b*c)**2*Ppara(q,a,b,c)
        return prefactor*f
    
    '''
    parameters definition
    
    Model(2,PCube,Qlogspace(1e-4,1.,500.),
    ([250.,10.,1.5e14,2e11,1e10]),
    ("side length 1",
    "side length 2","Side length 3","scattering length density of sphere (cm-2)",
    "scattering length density of medium (cm-2)","number density" (cm-3)),
    ("%f","%f","%1.3e","%1.3e","%1.3e"),
    (True,True,True,False,False,False)),
    
    
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PParallelepiped #function
        self.N=0
        self.q=Qlogspace(3e-4,1.,500.)                            #q range(x scale)
        self.Arg=[30.,30.,30.,9.8e11,9.8e10,1e10]                   #list of parameters
        self.Format=["%f","%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,True,False,False,False]           #list of boolean for fitting
        self.name="Parallelepiped"                      #name of the model
        self.Doc=["side length 1 ",\
             "side length 2",\
             "side length 2",\
             "scattering length density of particle (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "Number density (cm-3)"]           #list of description for parameters
        self.Description="Parallelepiped"  # description of model
        self.Author="Olivier Spalla"                 #name of Author
    
