from pySAXS.models.model import Model
import numpy
import scipy


class Trapez(Model):
    '''
    Trapez model
    by OT : 09/12/2011
    '''
    def trapez(self,x,center=0,fwmh=1,slope=1,height=1,zero=0):
        y=numpy.zeros(numpy.shape(x))
        #print y
        for i in range(len(x)):
            if x[i]<center:
                y[i]=scipy.special.erf((x[i]-center+fwmh*0.5)/slope)
            else:
                y[i]=-scipy.special.erf((x[i]-center-fwmh*0.5)/slope)
        y= ((y+1)*0.5*height+zero)
        #print y
        return y
    
    def TrapezFunction(self,q,par):
        """
        Trapez model to fit the peak to get exact zero position,
        based on erf function
        par[0] : center
        par[1] : FWHM
        par[2] : slope
        par[3] : height
        par[4] : zero
        """
        #print " par in trapez :",par
        #print q
        y=self.trapez(q, par[0], par[1], par[2], par[3], par[4])
        #print y
        return y
    
    def prefit(self,q,y):
        '''
        try to determine some parameters from the datas
        '''
        center=(q[0]+q[-1])/2
        FWMH=(q[-1]-q[0])/3
        slope=FWMH/10
        height=y.min()-y.max()
        zero=y.max()
        datax=q
        datay=y
        p0=[(datax[-1]+datax[0])/2-1,(datax[-1]-datax[0])/3,(datax[-1]-datax[0])/20,-(datay.max()-datay.min()),datay.max()]
        p0=numpy.array([(datax[-1]+datax[0])/2,(datax[-1]-datax[0])/3,(datax[-1]-datax[0])/20,-(datay.max()-datay.min()),datay.max()])
        #self.Arg=[center,FWMH,slope,height,zero]
        #print 'p0:',p0
        self.Arg=p0
        return self.Arg
    
    '''
    parameters definition
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.TrapezFunction #function
        self.N=0
        self.q=numpy.arange(-10,10,0.2)      #q range(x scale)
        self.Arg=[0.,2.5,0.5,2.0,0.0]            #list of parameters
        self.Format=["%f","%f","%f","%f","%f"]      #list of c format
        self.istofit=[True,True,True,True,True]    #list of boolean for fitting
        self.name="Trapez"          #name of the model
        self.Doc=["center"\
                 ,"FWHM"\
                 ,"slope"\
                 ,"height"\
                 ,"zero"] #list of description for parameters
        self.Description="Trapez model based on erf for x-ray beam"  # description of model
        self.Author="Olivier Tache'"       #name of Author


