# -*- coding: utf-8 -*-
from hydroinform import DFS


class Point(object):
    def __init__(self, x=0.0,y=0.0):
        self.X=x
        self.Y=y

class RiverPoint(Point):
    def __init__(self, x = 0, y = 0, chainage=0.0):
        super(RiverPoint, self).__init__(x, y)
        self.chainage = chainage

class GridPoint(RiverPoint):
    def __init__(self, x=0,y=0,chainage=0, z=0.0, type=1):
        super(GridPoint, self).__init__(x,y,chainage)
        self.z=z
        self.type=type
        self.index = -1


class Node(Point):
    """description of class"""
    def __init__(self, x=0,y=0,Type=1,name=''):
        super(Node, self).__init__(x,y)
        self.Type =Type
        self.Name=name

class Reach(object):

    def __init__(self, type, name, topoid, flowdir):
        self.Type = type
        self.id=-1
        self.Name = name
        self.TopoID = topoid
        self.FlowDirection = flowdir
        self.NumberOfDigipoints=0
        self.NumberOfGridpoints=0
        self.UpstreamNode=None
        self.DownstreamNode =None
        self.Digipoints=[]
        self.gridpoints=[]
        self.gridpointsH=[]
        self.gridpointsQ=[]
        self.xsecs =[]
        self.dataitems={}


class xsecpoint(object):
    def __init__(self, x, z):
        self.x=x
        self.z=z
        self.marker=-1

class xsec(object):
    def __init__(self, name, NumberOfPoints):
        self.name =name
        self.NumberOfPoints = NumberOfPoints
        self.xsecpoints=[]
        self.Type =-1

class DataItem(object):
    def __init__(self, name):
        self.name = name
        self.chainages =[]
        self.offset=0
        return super(DataItem, self).__init__()

class network(object):
    def __init__(self):
        self.nodes=[]
        self.reaches=[]
        return super(network, self).__init__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()

    def dispose(self):
        self.res.Dispose()

    def getvalues(self, Item=2, TimeStep=0):
        toreturn={}
        for reach in self.reaches:
            if Item-1 in reach.dataitems:
                values = self.res.GetData(TimeStep,Item)[reach.dataitems[Item-1].offset: reach.dataitems[Item-1].offset + len(reach.dataitems[Item-1].chainages)]
                for i in range(0, len (values)):
                    if reach.Name not in toreturn:
                        toreturn[reach.Name] ={}
                    toreturn[reach.Name][reach.dataitems[Item-1].chainages[i]]=values[i]
        for reach, val in toreturn.iteritems():
            toreturn[reach]= sorted(val.items(), key=lambda x: x[0])
        return toreturn


    def readRES1d(self, Filename):
        self.res= DFS.RES1DBase.FromFile(Filename)
        nodestart=1

        NumberOfDynamicItems = self.res.StaticItems[nodestart].readData()[0]
        self.DataItems =[]

        names = self.res.StaticItems[nodestart+1].readData().split(';')
        for i in range(0, NumberOfDynamicItems):
            self.DataItems.append(DataItem(names[i].replace("\"", "")))
            self.DataItems[i].grouptype =self.res.StaticItems[nodestart+2].readData()[i]
            self.DataItems[i].ItemIndex=i

        listlength = self.res.StaticItems[nodestart+5].readData()
        nodestart+=6
        for i in range(0, NumberOfDynamicItems):
            if listlength[i]!=0:
                self.DataItems[i].ReachIndeces=self.res.StaticItems[nodestart].readData()
                nodestart+=1

        for i in range(0, NumberOfDynamicItems):
            if self.DataItems[i].grouptype==2:
                self.DataItems[i].ReachNoVals=self.res.StaticItems[nodestart].readData()
                self.DataItems[i].chainages=self.res.StaticItems[nodestart+1].readData()
                nodestart+=2

        #Read nodes
        while self.res.StaticItems[nodestart].Name!='NoNodes':
            nodestart+=1

        numberofnodes = self.res.StaticItems[nodestart].readData()[0]
        xs =self.res.StaticItems[nodestart+3].readData()
        ys =self.res.StaticItems[nodestart+4].readData()
        types =self.res.StaticItems[nodestart+1].readData()
        names = self.res.StaticItems[nodestart+2].readData().split(';')
        for i in range(0,numberofnodes):
            self.nodes.append(Node(xs[i],ys[i],types[i], names[i]))

        #Read reaches
        reachstart= nodestart + 5
        numberofreaches = self.res.StaticItems[reachstart].readData()[0]
        reachtypes = self.res.StaticItems[reachstart+1].readData();
        allnames= self.res.StaticItems[reachstart+2].readData()
        reachnames = allnames.split(';')
        topoids = self.res.StaticItems[reachstart+3].readData().split(';')
        ups = self.res.StaticItems[reachstart+4].readData()
        dws = self.res.StaticItems[reachstart+5].readData()
        dir = self.res.StaticItems[reachstart+6].readData()
        nodigipoints = self.res.StaticItems[reachstart+7].readData()
        nogridpoints = self.res.StaticItems[reachstart+8].readData()
        for i in range(0,numberofreaches):
            r = Reach(reachtypes[i], reachnames[i].replace("\"", ""), topoids[i].replace("\"", ""), dir[i])
            r.UpstreamNode = self.nodes[ups[i]]
            r.DownstreamNode = self.nodes[dws[i]]
            r.NumberOfDigipoints=nodigipoints[i]
            r.NumberOfGridpoints=nogridpoints[i]
            self.reaches.append(r)

        for di in self.DataItems:
            if di.grouptype==2:
                if not hasattr(di, 'ReachIndeces'):
                    di.ReachIndeces=range(0,numberofreaches)
                lcount=0
                for i in di.ReachIndeces:
                    ldi =DataItem(di.name)
                    ldi.ItemIndex =di.ItemIndex
                    ldi.offset =di.offset
                    ldi.chainages = di.chainages[di.offset:di.offset+di.ReachNoVals[lcount]]
                    di.offset +=di.ReachNoVals[lcount]
                    lcount+=1
                    self.reaches[i].dataitems[di.ItemIndex]=ldi


        #Now build each individual reach
        Hindex=0
        Qindex=0
        rcount=0
        offset = reachstart + 9
        for r in self.reaches:
            if self.res.StaticItems[offset].Name!='dpChainages':
                k=1

            #The digipoints
            dpChainages = self.res.StaticItems[offset].readData()
            dpXs = self.res.StaticItems[offset+1].readData()
            dpYs = self.res.StaticItems[offset+2].readData()
            for i in range(0, r.NumberOfDigipoints):
                dp = RiverPoint(dpXs[i],dpYs[i], dpChainages[i])
                r.Digipoints.append(dp)

            #The gridpoints
            gpType = self.res.StaticItems[offset+3].readData()
            gpChainages = self.res.StaticItems[offset+4].readData()
            gpXs = self.res.StaticItems[offset+5].readData()
            gpYs = self.res.StaticItems[offset+6].readData()
            gpZs = self.res.StaticItems[offset+7].readData()
            for i in range(0, r.NumberOfGridpoints):
                dg = GridPoint(gpXs[i],gpYs[i], gpChainages[i], gpZs[i], gpType[i])
                r.gridpoints.append(dg)
                if dg.type==1025:
                    r.gridpointsH.append(dg)
                    dg.index = Hindex
                    Hindex+=1
                else:
                    r.gridpointsQ.append(dg)
                    dg.index=Qindex
                    Qindex+=1
                   
            #Some structures
            if self.res.StaticItems[offset+8].Name=='structureNumberOfSubTypes':
                offset +=3
            
            #We may already be at the next reach
            if self.res.StaticItems[offset+10].Name=='dpChainages':
                offset+=10
            elif self.res.StaticItems[offset+8].Name=='dpChainages':
                offset+=8
            else: #Now for xsecs
                csIDs = self.res.StaticItems[offset+8].readData().split(';')
                csnopoints= self.res.StaticItems[offset+10].readData()

                cstypes= self.res.StaticItems[offset+9].readData()
                csXs = self.res.StaticItems[offset+11].readData()
                csZs = self.res.StaticItems[offset+12].readData()
                csNoMarkers = self.res.StaticItems[offset+13].readData()
                csMarkers = self.res.StaticItems[offset+14].readData()
                csMarkersIndices = self.res.StaticItems[offset+15].readData()
                csstart=0
                csmarkstart =0
                gpoffset=0
                for i in range(0, len(csnopoints)):
                    if cstypes[i+gpoffset] == 1000:
                        gpoffset+=1
                    cs = xsec(csIDs[i+gpoffset].replace("\"", ""), csnopoints[i])
                    cs.Type = cstypes[i]
                    for n in range(csstart, csstart+ cs.NumberOfPoints):
                        cs.xsecpoints.append(xsecpoint(csXs[n],csZs[n]))
                    r.xsecs.append(cs);
                    csstart+=cs.NumberOfPoints
                    for k in range(csmarkstart, csmarkstart + csNoMarkers[i]):
                        cs.xsecpoints[csMarkersIndices[k]].marker=csMarkers[k]
                    csmarkstart += csNoMarkers[i]
                    cs.Gridpoint = r.gridpointsH[i+gpoffset]

                offset+=16

