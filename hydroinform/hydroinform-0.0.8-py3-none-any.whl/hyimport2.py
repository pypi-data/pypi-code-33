# -*- coding: utf-8 -*-
import codecs
import numpy as np
from hydroinform import DFS
from hydroinform import Res1D
from hydroinform import hymod
from operator import attrgetter

MikeZeroBinDIR=r'F:\Program Files (x86)\DHI\2017\bin\x64'

class Res1DReader(object):
    """This class reads data from a Res1d file and returns a Hymod reach network"""
    def __init__(self, Res1DFileName):
        DFS.MikeZeroBinDIR=MikeZeroBinDIR
        self.res1d=Res1D.network()
        self.res1d.readRES1d(Res1DFileName)
        self.NumberOfTimeSteps = self.res1d.res.NumberOfTimeSteps

    def getHymodNetwork(self):
        """
        Gets a hymod reach network from the res1d file
        """
        reach_network = hymod.Reach_network()

        reach_dic={}

        for r in self.res1d.reaches:
            #We only create a new reach if we do not already have a reach with that name. Otherwise we merge. TODO: Make TopoID count
            if r.Name not in reach_dic:
                reach_dic[r.Name]= hymod.Reach(r.Name)
                reach_network.reaches.append(reach_dic[r.Name])
            reach = reach_dic[r.Name]
            reach.description = r.TopoID
            for xs in r.xsecs:
                if not any(x.chainage==-xs.Gridpoint.chainage for x in reach.xss): #We can only add one xsecs at the same chainage
                    xsec = hymod.Xs(name=xs.name)
                    xsec.radius_type = 'resistance radius'
                    xsec.chainage = -xs.Gridpoint.chainage
                    xsec.x = xs.Gridpoint.X
                    xsec.y = xs.Gridpoint.Y
                    xsec.z= min(xs.xsecpoints, key=attrgetter('z')).z
                    for pp in xs.xsecpoints:
                        xsec.pps.append(hymod.Pp(pp.x, pp.z-xsec.z))
                    reach.xss.append(xsec)
                    reach.riverPoints.append(hymod.RiverPoint(xsec.chainage, xs.Gridpoint.X, xs.Gridpoint.Y))
            for dp in r.Digipoints:
                reach.riverPoints.append(hymod.RiverPoint(-dp.chainage, dp.X, dp.Y))
           
            downstreamReaches = (dr for dr in self.res1d.reaches if dr.UpstreamNode==r.DownstreamNode)
            for dr in downstreamReaches:
                if(dr.Name != r.Name):
                    reach_network.connections.append(hymod.Connection(r.Name, dr.Name, -dr.gridpoints[0].chainage))

        #Sort and remove duplicate points in reaches
        for hr in reach_network.reaches:
            hr.riverPoints = list(set(hr.riverPoints)) #To remove duplicate points
            hr.riverPoints.sort(key=lambda rp: rp.chainage) #Now sort
            hr.xss.sort(key=lambda rp: rp.chainage) #Also sort xsecs
            hr.update_perimeter_points_xy_coords(rotate180=True)

        hymod.Tools.RemoveUnnecessaryPerimeterPoints(reach_network)

        return reach_network


    def exportToCsv(self, filename, ItemNumber, TimeStep=1):
        """
        Writes a csv file with reach name, chainage and Item value. Items counts from 1, TimeStep from 0
        """
        with codecs.open(filename, encoding='utf-8', mode='w') as file:
            datadic=self.res1d.getvalues(ItemNumber, TimeStep)
            for name, chainlist in datadic.iteritems():
                for cv in chainlist:
                    file.write(name + '\t' + str(cv[0]) + '\t' + str(cv[1]) + '\n')


    def setQandH(self, reaches=[], Time=1):
        """
        Takes a list of hymod reaches and sets Q and H. Matches on reach name and interpolates on chainage
        H is added to the observations. Clear observations first if necessary.
        """
        qitem = next(i for i in self.res1d.DataItems if i.name =='Discharge')
        hitem = next(i for i in self.res1d.DataItems if i.name =='Water level' and i.grouptype==2)
        
        #Reads the data from the res1d-file
        Hdata=self.res1d.getvalues(hitem.ItemIndex+1, Time)
        Qdata=self.res1d.getvalues(qitem.ItemIndex+1, Time)

        for r in reaches:
            del r.observations[:]
            if r.name in Hdata:
                for chainageH in Hdata[r.name]:
                    r.observations.append((-chainageH[0], chainageH[1]))

            if r.name in Qdata:
                chains = [c[0] for c in Qdata[r.name]]
                qs = [c[1] for c in Qdata[r.name]]
                for xs in r.xss:
                    xs.flow =np.interp(-xs.chainage, chains, qs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the res1d-file
        """
        self.res1d.dispose()





