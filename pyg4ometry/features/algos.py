import vtk as _vtk
import numpy as _np
import scipy.linalg as _la
import matplotlib.pyplot as _plt
import random as _rand
from scipy.spatial.transform import Rotation as _Rotation

class Line :
    '''Line class taking a point and dir(ection)

    :param dir: direction
    :type  dir: list or array - 3 values
    '''

    def __init__(self, point, dir):
        self.point = point
        self.dir   = dir

    def eval(self, par):
        return par*_np.array(self.dir)+_np.array(self.point)

    def intersectPlane(self, plane):
        '''Intersection of line (self) with plane (unimplemented)

        :param plane: plane object
        :type plane: Plane

        :return: Point of intersection between plane and line
        :rtype: list or array

        '''

        return plane.intersectLine(self)

    def __repr__(self):
        return "p0: "+repr(self.point)+" d: "+repr(self.dir)

    def __iter__(self):
        self.i = -1
        return self

    def __next__(self):
        self.i += 1
        if self.i < 3 :
            return self.point[self.i]
        elif self.i >= 3 and self.i < 6 :
            return self.dir[self.i-3]
        else:
            raise StopIteration

    def flatten(self):
        return iter(self)

class Plane :
    '''Plane class taking a point on plane and normal

    :param point: point on plane
    :type point: list, array
    :param normal: vector of normal
    :type normal: list, array
    '''

    def __init__(self, point, normal, e2 = None, e3=None):
        self.point = point
        self.normal = normal

    def intersect(self, object):
        '''Intersection between Line or Plane

        :param object: Object to intersect with Plane (either Line or Plane)
        :type object: Line or Plane

        '''

        if type(object) == Line:
            return self.intersectLine(object)
        elif type(object) == Plane:
            return self.intersectPlane(object)

    def intersectLine(self,line):
        '''Intersection between plane (self) and line'''

        par = _np.dot(self.normal,_np.array(self.point) - _np.array(line.point))/_np.dot(self.normal, line.dir)
        return line.eval(par)

    def intersectPlane(self,plane):
        '''Compute intersection between two planes self and plane'''
        n1 = self.normal
        n2 = plane.normal

        p1 = self.point
        p2 = plane.point

        d = _np.cross(n1,n2)
        d = d/_np.sqrt((d**2).sum())

        d1 = -_np.dot(n1,p1)
        d2 = -_np.dot(n2,p2)

        # https://mathworld.wolfram.com/Plane-PlaneIntersection.html
        m = _np.vstack([n1,n2])
        b = -_np.array([d1,d2])
        p = _np.dot(_np.linalg.pinv(m),b)

        l = Line(p,d)
        return l

    def angleBetween(self, plane):
        '''Compute angle between two planes (self and plane)

        :param plane: Plane to intersect with self
        :type plane: Plane
        :return: angle between two planes
        :rtype: float
        '''

        n1 = self.normal
        n2 = plane.normal

        return _np.arccos(_np.dot(n1,n2))

    def __repr__(self):
        return "p0: "+repr(self.point)+" n: "+repr(self.normal)

    def __iter__(self):
        self.i = -1
        return self

    def __next__(self):
        self.i += 1
        if self.i < 3 :
            return self.point[self.i]
        elif self.i >= 3 and self.i < 6 :
            return self.normal[self.i-3]
        else:
            raise StopIteration

    def flatten(self):
        return iter(self)

class CoordinateSystem :
    def __init__(self, origin = [0,0,0], e1 = [1,0,0], e2 = [0,1,0]):
        self.origin = _np.array(origin)
        self.e1 = _np.array(e1)
        self.e2 = _np.array(e2)
        self._commonInit()

    def _commonInit(self):
        self.e3 = _np.cross(self.e1,self.e2)

        #if not _np.isclose(_np.dot(self.e1,self.e2),0) :
        #    raise Exception("CoorindateSystem","Not orthogonal")

        #self.rot = _np.vstack([self.e1,self.e2,self.e3])

        self.rot = _Rotation.align_vectors(_np.vstack([self.e1,self.e2,self.e3]), [[1,0,0],[0,1,0],[0,0,1]])[0].as_matrix()

    def makeFromPlanes(self, p1, p2, p3):
        l1 = p1.intersect(p2)

        o = p3.intersect(l1)
        e1 = p1.point - o
        self.dist = _np.linalg.norm(e1)
        e1 = e1/_np.linalg.norm(e1)

        e2 = l1.dir

        self.e1 = _np.array(e1)
        self.e2 = _np.array(e2)
        self.origin = o

        self._commonInit()

        print('CoordinateSystem.makeFromPlanes intersection line',l1)
        print('CoordinateSystem.makeFromPlanes axis1            ',e1)
        print('CoordinateSystem.makeFromPlanes axis2            ',e2)
        print('CoordinateSystem.makeFromPlanes origin           ',o)

    def coordinateSystem(self, rotX = 0.0, rotY = 0.0, rotZ = 0.0):
        r1 = _Rotation.from_euler("xyz",[rotX,rotY,rotZ])
        r2 = _Rotation.from_matrix(self.rot)

        rTotal = _np.dot(r2, r1)

        xp = _np.dot(rTotal.as_matrix(),[1,0,0])
        yp = _np.dot(rTotal.as_matrix(),[0,1,0])

        cs = CoordinateSystem(self.origin, xp,yp)

        return cs

    def plane(self, rotX = 0.0, rotY = 0.0, rotZ = 0.0):
        r1 = _Rotation.from_euler("xyz",[rotX,rotY,rotZ])
        r2 = _Rotation.from_matrix(self.rot)

        rTotal = _np.dot(r2, r1)

        np = _np.dot(rTotal.as_matrix(), [0, 0, 1])

        return Plane(self.origin, np)

    def transform(self, points):
        pointsPrime = _np.dot(_la.inv(self.rot),points.transpose()).transpose()+self.origin
        return pointsPrime

    def __repr__(self):
        return "origin="+str(self.origin)+" e1="+str(self.e1)+" e2="+str(self.e2)+" e3="+str(self.e3)

class vtkViewer :

    '''
    Simple visualiser for feature extraction only
    '''


    def __init__(self):
        self.polydataD = {}
        self.mapperD   = {}
        self.actorD    = {}

        # Create a rendering window and renderer
        self.ren = _vtk.vtkRenderer()
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.SetSize(1024, 1024)
        self.renWin.AddRenderer(self.ren)
        # Create a RenderWindowInteractor to permit manipulating the camera
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)
        style = _vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)

        self.ren.SetBackground(1.0, 1.0, 1.0)

    def _polyDataToActor(self,polydata,colour = [0,0,0,1] , lineWidth=5):
        """Wrap the provided vtkPolyData object in a mapper and an actor,
        returning the actor."""
        mapper = _vtk.vtkPolyDataMapper()
        if _vtk.VTK_MAJOR_VERSION <= 5:
            # mapper.SetInput(reader.GetOutput())
            mapper.SetInput(polydata)
        else:
            mapper.SetInputData(polydata)

        mapper.ScalarVisibilityOff()
        actor = _vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(colour[0], colour[1], colour[2])
        actor.GetProperty().SetOpacity(colour[3])
        actor.GetProperty().SetLineWidth(lineWidth)
        return [mapper,actor]

    def addPolydata(self, key, polydata, colour = [0,0,0,1], lineWidth = 5, label = None, labelPos = [0,0,0]):
        # print("vtkViewer.addPolydata ",label,labelPos)

        self.polydataD[key]  = polydata
        mapper, actor        = self._polyDataToActor(polydata,colour, lineWidth)
        self.mapperD[key]    = mapper
        self.actorD[key]     = actor
        self.ren.AddActor(actor)

        if label is not None :
            atext = _vtk.vtkVectorText()
            atext.SetText(label)
            textMapper = _vtk.vtkPolyDataMapper()
            textMapper.SetInputConnection(atext.GetOutputPort())
            textActor = _vtk.vtkFollower()
            textActor.SetMapper(textMapper)
            textActor.AddPosition(labelPos)
            textActor.GetProperty().SetColor(colour[0:3])
            textActor.SetScale(100,100,100)
            self.ren.AddActor(textActor)

    def addAxis(self, origin, length = [1,1,1], rotation = [[1,0,0],[0,1,0],[0,0,1]],  label = False, disableCone = False):
        axes = _vtk.vtkAxesActor()
        axes.SetAxisLabels(label)

        # transform to move axes
        tran = _vtk.vtkTransform()
        # tran.Translate(origin[0],origin[1], origin[2])
        tran.SetMatrix([rotation[0][0],rotation[0][1],rotation[0][2],origin[0],
                        rotation[1][0],rotation[1][1],rotation[1][2],origin[1],
                        rotation[2][0],rotation[2][1],rotation[2][2],origin[2],
                                     0,             0,             0,       1])
        axes.SetTotalLength(length[0], length[1], length[2])
        axes.SetUserTransform(tran)
        if disableCone :
            axes.SetConeRadius(0)
            axes.SetTotalLength(length[0]*(1+axes.GetNormalizedTipLength()[0]),
                                length[1]*(1+axes.GetNormalizedTipLength()[1]),
                                length[2]*(1+axes.GetNormalizedTipLength()[2]))
        self.ren.AddActor(axes)

    def addPlane(self, point, p1, p2, length=1):
        # print('vtkViewer.addPlane',point,p1,p2)

        planeSource = _vtk.vtkPlaneSource()
        planeSource.SetCenter(point)
        planeSource.SetPoint1(point+p1*length)
        planeSource.SetPoint2(point+p2*length)
        planeSource.Update()

        plane = planeSource.GetOutput()

        # Create a mapper and actor
        mapper = _vtk.vtkPolyDataMapper()
        mapper.SetInputData(plane)

        actor = _vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1,1,1)
        actor.GetProperty().SetOpacity(0.5)

        self.ren.AddActor(actor)

    def addLine(self, line):
        pass

    def view(self, interactive = True):
        self.iren.Initialize()
        self.renWin.Render()
        if interactive :
            self.iren.Start()

def vtkLoadStl(fname):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = _vtk.vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def vtkPolydataToActor(polydata) :
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning the actor."""
    mapper = _vtk.vtkPolyDataMapper()
    if _vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(polydata)
    else:
        mapper.SetInputData(polydata)
    actor = _vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().SetRepresentationToWireframe()
    return actor

def vtkPolydataToConnectedEdges(polydata, angle = 89) :
    if type(polydata) == list :
        rL = []
        for e in polydata :
            i = _vtkPolydataToConnectedEdges(e, angle)
            rL.extend(i)
        return rL
    else :
        return _vtkPolydataToConnectedEdges(polydata, angle)

def _vtkPolydataToConnectedEdges(polydata, angle = 89) :
    '''Feature extract from polydata given an angular cut

    :param angle: Angle between plane > angle is returned
    :type angle: float
    :return: Connected boundaries with > angle
    :rtype: list of vtkPolydata
    '''

    if angle > 0 :
        featureEdges = _vtk.vtkFeatureEdges()
        featureEdges.SetInputData(polydata)
        featureEdges.SetFeatureAngle(angle)
        featureEdges.FeatureEdgesOn()
        featureEdges.Update()

    connectivityFilter = _vtk.vtkPolyDataConnectivityFilter()
    if angle > 0 :
        connectivityFilter.SetInputConnection(featureEdges.GetOutputPort());
    else :
        connectivityFilter.SetInputData(polydata)
    connectivityFilter.SetExtractionModeToAllRegions();
    # connectivityFilter.ColorRegionsOn();
    connectivityFilter.Update()

    connectedEdges = []

    for r in range(0, connectivityFilter.GetNumberOfExtractedRegions(), 1):
        connectivityFilter.SetExtractionModeToSpecifiedRegions()
        connectivityFilter.InitializeSpecifiedRegionList()
        connectivityFilter.AddSpecifiedRegion(r)
        connectivityFilter.Update()
        connectedEdge = _vtk.vtkPolyData()
        connectedEdge.DeepCopy(connectivityFilter.GetOutput())
        connectedEdges.append(connectedEdge)

    return connectedEdges

def vtkPolydataEdgeInformation(polydata, bPlot = False) :
    '''Calculate path information for 2D vtkPolydata lines

    :param polydata: Geometry to extract information
    :type polydata: vtkPlydata or list of vtkPolydata
    :return: Information on each boundary
    :rtype: list of information dict

    '''

    if type(polydata) == list :
        rL = []
        for e in polydata :
            i = _vtkPolydataEdgeInformation(e, bPlot)
            rL.append(i)
        return rL
    else :
        return _vtkPolydataEdgeInformation(polydata, bPlot)

def _vtkPolydataEdgeInformation(polydata, bPlot = False) :
    '''Calculate path information for 2D vtkPolydata lines'''

    info = {}

    points = []
    uniquePoints = {}

    circum = 0
    # loop over cells (lines)
    for cid in range(0,polydata.GetNumberOfCells(),1):
        l = polydata.GetCell(cid)
        ps = l.GetPoints()

        for pid in range(0,ps.GetNumberOfPoints(),1) :
            p = ps.GetPoint(pid)

            if pid >= 0 and pid< ps.GetNumberOfPoints()-1 :
                p2 = ps.GetPoint(pid+1)
                circum += _np.sqrt((p2[0]-p[0])**2 + (p2[1]-p[1])**2 + (p2[2]-p[2])**2)
        if p not in uniquePoints:
            uniquePoints[p] = 1
        else:
            uniquePoints[p] += 1

        points.append(p)

    # unique point array
    upa = _np.array([k for k in uniquePoints.keys()])
    pa  = _np.array(points)

    # centre of points
    centre = upa.mean(0)

    # remove centre
    upacs = upa - centre

    # svd
    [u,s,vh] = _la.svd(upacs.transpose())

    # normal
    n = u[:,2]

    # plane point
    p = _np.dot(n,centre)*n

    # compute points projected on XY plane
    ez = [0,0,1]

    er = _np.cross(n,ez)
    en = _np.sqrt(er[0]**2 + er[1]**2 + er[2]**2)

    if en > 1.0 :
        en = 1.0

    if en != 0 :
        ar = _np.arcsin(en)
        er = er/en
    else :
        ar = 0
        er = ez

    pt = _vtk.vtkTransform() # plane transform
    pt.RotateWXYZ(ar/_np.pi*180,er[0],er[1],er[2])

    upaxy = []
    for up in upacs :
        upxy = pt.TransformPoint(up[0],up[1],up[2])
        upaxy.append(upxy)

    plane = Plane(p,n)

    info["centre"]        = centre
    info["plane"]         = plane
    info["planeQuality"]  = _np.fabs(upacs.dot(n)).sum()
    info["circumference"] = circum
    info["max"]           = upacs.max(0)
    info["min"]           = upacs.min(0)
    info["range"]         = info["max"] - info["min"]
    info["uniquepoints"]  = upa
    info["uniquepointsxy"]= _np.array(upaxy)

    if bPlot :
        fig = _plt.figure()
        ax = fig.add_subplot(projection='3d')

        ax.scatter(upa[:,0], upa[:,1], upa[:,2])
        ax.scatter(0, 0, 0,marker="+")
        _plt.xlabel("x")
        _plt.ylabel("y")

        m = upa.max()
        _plt.xlim(-m,m)
        _plt.ylim(-m,m)

    return info

def pyg4PlaneToVtkPlane(pyg4Plane) :
    '''Convert Plane to vtkPlane '''

    vtkPlane = _vtk.vtkPlane()
    vtkPlane.SetNormal(pyg4Plane.normal)
    vtkPlane.SetOrigin(pyg4Plane.point)
    return vtkPlane

def pyg4ArrayToVtkPolydataLine(pyg4Array) :
    '''Convert data array to vtkPolydata '''

    vtkPoints = _vtk.vtkPoints()
    for p in pyg4Array :
        vtkPoints.InsertNextPoint(p[0],p[1],p[2])

    vtkCellArray = _vtk.vtkCellArray()
    vtkCellArray.InsertNextCell(len(pyg4Array))
    for i in range(0,len(pyg4Array),1) :
        vtkCellArray.InsertCellPoint(i)

    vtkPolydata = _vtk.vtkPolyData()
    vtkPolydata.SetPoints(vtkPoints)
    vtkPolydata.SetLines(vtkCellArray)

    return vtkPolydata

def vtkCutterPlane(plane, polydata) :
    '''Calculate path information for 2D vtkPolydata lines

    :param polydata: Geometry to extract information
    :type polydata: vtkPlydata or list of vtkPolydata
    :return: Information on each boundary
    :rtype: list of information dict

    '''

    if type(plane) == list :
        rL = []
        for p in plane :
            i = _vtkCutterPlane(p, polydata)
            rL.append(i)
        return rL
    else :
        return _vtkCutterPlane(plane, polydata)

def _vtkCutterPlane(plane, polydata) :
    '''Cutter plane on polydata'''

    cutter = _vtk.vtkCutter()
    cutter.SetInputData(polydata)
    cutter.SetCutFunction(pyg4PlaneToVtkPlane(plane))
    cutter.Update()
    return cutter.GetOutput()

def extract(inputFileName,
            angle = 89,
            planeQuality = 0.1,
            circumference = 300,
            outputFileName = None ,
            planes = [],
            bViewer= False,
            bViewerInteractive = False) :

    p = vtkLoadStl(inputFileName)
    e = vtkPolydataToConnectedEdges(p, angle)
    i = vtkPolydataEdgeInformation(e)

    cpdList = []
    cpdiList = []
    ciList = []
    for plane in planes :

        cpd = vtkCutterPlane(plane.plane(),p)
        cpdi = vtkPolydataEdgeInformation(cpd)
        ce = vtkPolydataToConnectedEdges(cpd,0)
        ci = vtkPolydataEdgeInformation(ce)

        cpdi["uniquepointsxy"] = plane.transform(cpdi["uniquepoints"])
        cpdList.append(cpd)
        cpdiList.append(cpdi)
        for ci_i in range(0,len(ci),1) :
            ci[ci_i]["uniquepointsxy"] = plane.transform(ci[ci_i]["uniquepoints"])
        ciList.append(ci)

    if outputFileName is not None :

        def iterToStr(iterable) :
            s = ''

            if iterable is None :
                return s

            for i in iterable.flatten() :
                s+= str(i) + " "

            return s

        of = open(outputFileName,"w")
        for io in i :
            # if io["planeQuality"] < planeQuality and io["circumference"] > circumference :
            of.write("feature\n")
            for k in io :
                of.write(k+": "+iterToStr(io[k])+"\n")

        for j, pi, ic in zip(range(0,len(planes),1),planes,cpdiList) :
            of.write("cutter\n")
            for k in ic:
                of.write(k + ": " + iterToStr(ic[k]) + "\n")

            for ic in ciList[j] :
                of.write("cutter-feature \n")
                for k in ic :
                    of.write(k + ": " + iterToStr(ic[k]) + "\n")

        of.close()

    if not bViewer :
        return

    v = vtkViewer()
    v.addPolydata(p,p,[0,0,1,0.1])
    #v.addAxis([0,0,0],[200,200,200])

    for edge,info,id in zip(e,i,range(0,len(i),1)) :
        if info["planeQuality"] < planeQuality:
            if info["circumference"] > circumference :
                v.addPolydata(edge, edge, [0,0,1,1],label=str(id), labelPos=info["uniquepoints"][_rand.randrange(0,len(info["uniquepoints"]))])
                v.addAxis(info["centre"],info["range"])
            else :
                v.addPolydata(edge,edge, [0,1,0,1],label=str(id), labelPos=info["uniquepoints"][_rand.randrange(0,len(info["uniquepoints"]))])
        else :
            v.addPolydata(edge,edge, [1,0,0,1],label=str(id), labelPos=info["uniquepoints"][_rand.randrange(0,len(info["uniquepoints"]))])

    for cut,info,id in zip(cpdList, cpdiList, range(0,len(cpdList),1)) :
        v.addPolydata(cut, cut, [0, 0, 0, 1],label=str(id), labelPos=info["uniquepoints"][_rand.randrange(0,len(info["uniquepoints"]))])

    v.addAxis([0,0,0],[250,250,250])
    v.view(interactive=bViewerInteractive)

    return v

class FeatureData :

    def __init__(self):
        self.features = []
        self.cutters  = []

    def readFile(self, fileName):
        f = open(fileName,'r')

        def readInfo(f) :
            d = {}
            # center
            d['centre'] = _np.array(list(map(float,f.readline().split()[1:])))
            d['plane'] = _np.array(list(map(float,f.readline().split()[1:])))
            d['planeQuality'] = float(f.readline().split()[1])
            d['circumference'] = float(f.readline().split()[1])
            d['max'] = _np.array(list(map(float, f.readline().split()[1:])))
            d['min'] = _np.array(list(map(float, f.readline().split()[1:])))
            d['range'] = _np.array(list(map(float, f.readline().split()[1:])))
            d['uniquepoints'] = _np.reshape(_np.array(list(map(float, f.readline().split()[1:]))),(-1,3))
            d['uniquepointsxy'] = _np.reshape(_np.array(list(map(float, f.readline().split()[1:]))),(-1,3))

            return d

        while True :
            l = f.readline()
            if l.rfind("cutter-feature") != -1 :
                d = readInfo(f)
                self.cutters[-1]["features"].append(d)
            elif l.rfind("feature") != -1 :
                d = readInfo(f)
                self.features.append(d)
            elif l.rfind("cutter") != -1:
                d = readInfo(f)
                d["features"] = []
                self.cutters.append(d)
            elif l == '' :
                break

    def plotFeature(self, iFeature):
        f = _plt.figure(1)

        featureData = self.features[iFeature]
        featureUXY      = featureData["uniquepointsxy"]

        _plt.plot(featureUXY[:,0],featureUXY[:,1],"+")

    def plotCutter(self, iCutter):
        f = _plt.figure(1)

        cutData = self.cutters[iCutter]
        cutDataUXY      = cutData["uniquepointsxy"]
        cutDataFeatures = cutData["features"]


        _plt.plot(cutDataUXY[:,0]-(cutDataUXY[:,0].max()+cutDataUXY[:,0].min())/2.0,
                                     cutDataUXY[:,1]-(cutDataUXY[:,1].max()+cutDataUXY[:,1].min())/2.0,"+")

        for feature in cutDataFeatures :
            featureUXY = feature["uniquepointsxy"]
            _plt.plot(featureUXY[:, 0]-(featureUXY[:,0].max()+featureUXY[:,0].min())/2.0,
                      featureUXY[:, 1]-(featureUXY[:,1].max()+featureUXY[:,1].min())/2.0, "+")



def test(fileName, featureIndexList = [], planeQuality = 0.1, circumference = 300, bPlotRadii = False) :
    p = vtkLoadStl(fileName)
    e = vtkPolydataToConnectedEdges(p, 89)
    i = vtkPolydataEdgeInformation(e)

    v = vtkViewer()

    v.addPolydata(p,p,[0,0,1,0.1])
    v.addAxis([0,0,0],[200,200,200])

    for edge,info,id in zip(e,i,range(0,len(i),1)) :
        if info["planeQuality"] < planeQuality:
            if info["circumference"] > circumference :
                if id in featureIndexList :
                    v.addPolydata(edge, edge, [0,0,1,1])
                else :
                    v.addPolydata(edge, edge)
                v.addAxis(info["centre"],info["range"])

                print(id)
            else :
                v.addPolydata(edge,edge, [0,1,0,1])
        else :
            v.addPolydata(edge,edge, [1,0,0,1])

    i1 = i[featureIndexList[0]]
    i2 = i[featureIndexList[1]]
    p1 = i1["plane"]
    p2 = i2["plane"]
    il = p1.intersectPlane(p2)
    da = p1.angleBetween(p2)
    print("intersection line    : ",il)
    print("angle between planes : ",da*180.0/_np.pi)

    l1a = [il.point,p1.point]
    l2a = [il.point,p2.point]
    l1a_pd = pyg4ArrayToVtkPolydataLine(l1a)
    l2a_pd = pyg4ArrayToVtkPolydataLine(l2a)

    if bPlotRadii :
        v.addAxis(il.point,[1000,1000,1000])
        v.addPolydata(l1a_pd,l1a_pd,colour=[0,0,1,0.5], lineWidth=2)
        v.addPolydata(l2a_pd,l2a_pd,colour=[0,0,1,0.5], lineWidth=2)

    d1 = il.point - p1.point
    d2 = il.point - p2.point

    print("r1",_np.sqrt((d1**2).sum()))
    print("r2",_np.sqrt((d2**2).sum()))

    x1 = i1["uniquepointsxy"][:,0]
    y1 = i1["uniquepointsxy"][:,1]
    x2 = i2["uniquepointsxy"][:,0]
    y2 = i2["uniquepointsxy"][:,1]

    x1 = x1 - (x1.max() + x1.min())/2
    y1 = y1 - (y1.max() + y1.min())/2

    x2 = x2 - (x2.max() + x2.min())/2
    y2 = y2 - (y2.max() + y2.min())/2

    _plt.plot(x1,y1,"o",label=str(featureIndexList[0]))
    _plt.plot(x2,y2,"+",label=str(featureIndexList[1]))
    _plt.legend()
    _plt.grid()
    v.view()

    return i