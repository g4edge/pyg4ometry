import numpy as _np
import pyg4ometry as _pyg4

def beamPipe(stlFileName, vis=True, interactive=True) :

    datFileName = stlFileName.replace("stl", "dat")

    v = _pyg4.features.extract(stlFileName,
                               angle = 46,
                               circumference=2*_np.pi*8,
                               planes=[],
                               outputFileName=datFileName,
                               bViewer=True,
                               bViewerInteractive=False)

    fd = _pyg4.features.algos.FeatureData()
    fd.readFile(datFileName)

    # 2,15
    # 9, 7
    p1 = fd.features[2]["plane"]
    p2 = fd.features[15]["plane"]

    pp1 = _pyg4.features.Plane(p1[0:3], p1[3:])
    pp2 = _pyg4.features.Plane(p2[0:3], p2[3:])
    pp3 = _pyg4.features.Plane([0, 0, 0], [0, 0, 1])

    cs = _pyg4.features.CoordinateSystem()
    cs.makeFromPlanes(pp1, pp2, pp3)

    cs1 = cs.coordinateSystem(0,0.01,0)
    cs2 = cs.coordinateSystem(0,0.02,0)
    cs3 = cs.coordinateSystem(0,0.03,0)
    cs4 = cs.coordinateSystem(0,0.04,0)

    v.addPlane(cs.origin, cs.e1, cs.e2, cs.dist)
    # v.addPlane(cs.origin, cs1.e1, cs1.e2, cs.dist)
    v.addAxis(cs.origin,[cs.dist,cs.dist,cs.dist],cs.rot,label=True,disableCone=True)
    v.view(interactive=True)

    v = _pyg4.features.extract(stlFileName,
                               angle = 46,
                               circumference=2*_np.pi*8,
                               planes=[cs1,cs2,cs3,cs4],
                               outputFileName=datFileName,
                               bViewer=True,
                               bViewerInteractive=True)

    return True