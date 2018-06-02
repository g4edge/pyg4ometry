#!/usr/bin/env python
"""A handy executable for viewing GDML files effortlessly."""
import pygeometry
import sys

def main(paths):
    if len(paths) == 0:
        raise IOError("Missing path to GDML file(s).")
    else:
        for path in paths:
            f = pygeometry.gdml.Reader(path)
            worldVol = pygeometry.geant4.registry.worldVolume
            meshlist = worldVol.pycsgmesh()
            v = pygeometry.vtk.Viewer()
            v.addPycsgMeshList(meshlist)
            v.view()

if __name__ == "__main__":
    main(sys.argv[1:])
