import pyg4ometry as _pyg4
import os as _os
import numpy as _np


def Test(vis=False, interactive=False):
    reg = _pyg4.geant4.Registry()
    radius1 = 7
    radius2 = 9
    theta = 0.1
    rho = 500

    s = theta * rho
    d = _np.sin(theta / 2.0) * rho * 2

    n1 = [_np.cos(_np.pi / 2 - theta / 2.0), 0, -_np.sin(_np.pi / 2 - theta / 2.0)]
    n2 = [_np.cos(_np.pi / 2 - theta / 2.0), 0, _np.sin(_np.pi / 2 - theta / 2.0)]

    t = _pyg4.geant4.solid.CutTubs("t1", radius1, radius2, d, 0, 2 * _np.pi, n1, n2, reg)

    stlFileName = _os.path.join(_os.path.dirname(__file__), "T721_featureExtract_cutTubs.stl")
    datFileName = stlFileName.replace("stl", "dat")
    _pyg4.convert.pycsgMeshToStl(t.mesh(), stlFileName)

    p1 = _pyg4.features.algos.Plane([0, 0, 0], [0, 0, 1])
    v = _pyg4.features.extract(
        stlFileName,
        angle=46,
        circumference=2 * _np.pi * 8,
        planes=[],
        outputFileName=datFileName,
        bViewer=vis,
        bViewerInteractive=interactive,
    )

    fd = _pyg4.features.algos.FeatureData()
    fd.readFile(datFileName)

    p1 = fd.features[2]["plane"]
    p2 = fd.features[3]["plane"]

    pp1 = _pyg4.features.Plane(p1[0:3], p1[3:])
    pp2 = _pyg4.features.Plane(p2[0:3], p2[3:])
    pp3 = _pyg4.features.Plane([0, 0, 0], [0, 1, 0])

    cs = _pyg4.features.CoordinateSystem()
    cs.makeFromPlanes(pp1, pp2, pp3)

    cs1 = cs.coordinateSystem(0, 0.01, 0)
    cs2 = cs.coordinateSystem(0, 0.02, 0)
    cs3 = cs.coordinateSystem(0, 0.03, 0)
    cs4 = cs.coordinateSystem(0, 0.04, 0)

    if v is None:
        return True

    v.addPlane(cs.origin, cs.e1, cs.e2, cs.dist)
    v.addPlane(cs.origin, cs1.e1, cs1.e2, cs.dist)
    v.addAxis(cs.origin, [cs.dist, cs.dist, cs.dist], cs.rot, label=True, disableCone=True)
    v.view(interactive=interactive)

    v = _pyg4.features.extract(
        stlFileName,
        angle=46,
        circumference=2 * _np.pi * 8,
        planes=[cs1, cs2, cs3, cs4],
        outputFileName=datFileName,
        bViewer=vis,
        bViewerInteractive=interactive,
    )

    return True


if __name__ == "__main__":
    Test()
