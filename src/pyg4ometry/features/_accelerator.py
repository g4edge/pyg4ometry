import numpy as _np
import pyg4ometry as _pyg4
# import pyg4ometry.pyoce as _oce


def beamPipeCADFeature(shape) :

    wirePnts = []

    topoExp  = _oce.TopExp_Explorer(shape, _oce.TopAbs_WIRE, _oce.TopAbs_VERTEX)
    location = _oce.TopLoc_Location()

    while(topoExp.More()) :
        wire = _oce.TopoDS.Wire(topoExp.Current())
        #print(wire)
        topoExpWire = _oce.TopExp_Explorer(wire, _oce.TopAbs_EDGE, _oce.TopAbs_VERTEX)

        edgePnts = []
        while(topoExpWire.More()):
            edge = _oce.TopoDS.Edge(topoExpWire.Current())
            edgeLocation = _oce.TopLoc_Location()
            start = 0
            end = 0
            curve, l, s, e = _oce.BRep_Tool.Curve(edge, edgeLocation, start, end)

            for par in _np.linspace(s,e,20) :
                pnt = curve.Value(par)
                edgePnts.append([pnt.X(), pnt.Y(), pnt.Z()])
            #print(edge,curve,l,s,e)

            topoExpWire.Next()

        wirePnts.append(edgePnts)
        topoExp.Next()

    return wirePnts

def beamPipe(stlFileName, feature1 = -1, feature2 = -1, planeAngles = [[0,0,0]], vis=True, interactive=True) :

    datFileName = stlFileName.replace("stl", "dat")

    if feature1 == -1 :
        vis = True
        interactive = True

    v = _pyg4.features.extract(stlFileName,
                               angle = 46,
                               circumference=2*_np.pi*8,
                               planes=[],
                               outputFileName=datFileName,
                               bViewer=vis,
                               bViewerInteractive=interactive)

    fd = _pyg4.features.algos.FeatureData()
    fd.readFile(datFileName)

    if feature1 == -1 :
        return

    p1 = fd.features[feature1]["plane"]
    p2 = fd.features[feature2]["plane"]

    pp1 = _pyg4.features.Plane(p1[0:3], p1[3:])
    pp2 = _pyg4.features.Plane(p2[0:3], p2[3:])
    pp3 = _pyg4.features.Plane([0, 0, 0], [0, 0, 1])

    cs = _pyg4.features.CoordinateSystem()
    cs.makeFromPlanes(pp1, pp2, pp3)

    csa  = [cs.coordinateSystem(ang[0],ang[1],ang[2]) for ang in planeAngles]

    if vis :
        v.addPlane(cs.origin, cs.e1, cs.e2, cs.dist)
        v.addAxis(cs.origin,[cs.dist,cs.dist,cs.dist],cs.rot,label=True,disableCone=True)
        v.view(interactive=True)

    v = _pyg4.features.extract(stlFileName,
                               angle = 46,
                               circumference=2*_np.pi*8,
                               planes=csa,
                               outputFileName=datFileName,
                               bViewer=vis,
                               bViewerInteractive=interactive)
