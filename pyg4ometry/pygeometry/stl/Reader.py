import pygeometry.geant4 as _g4
import pygeometry.vtk    as _vtkv
import numpy             as _np
import re as _re
import warnings as _warnings

import pygeometry.gdml as _gdml

class Reader(object):
    def __init__(self, filename, solidname="tess", visualise=True, writeGDML=False, scale=1):
        super(Reader, self).__init__()
        self.filename = filename

        self.worldVolumeName  = str()
        self.facet_list = []
        self.num_re = _re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$") #Compile re to match numbers

        self.scale = float(scale)
        # load file
        self.solid = self.load(solidname, visualise, writeGDML)

    
    def load(self, solidname="tess", visualise=True, writeGDML=False):
        #data  = open(self.filename, "r")
        def extractXYZ(string):
            #The scaling here is a bit cheeky, but the scale parameter in GDML seems to be ignored by Geanr4 for Tesselated Solids
            return tuple([self.scale*float(v) for v in string.split() if self.num_re.match(v)])

        with open(self.filename) as f:
            line = f.readline()
            cnt=1
            while line:
                sline = line.strip()
                if sline.startswith("facet"): #Indicates a facet, only first char comaprison
                    normal = extractXYZ(sline)
                    facet = _Facet(normal)

                elif sline.startswith("vertex"):
                    vertex = extractXYZ(sline)
                    facet.add_vertex(vertex)

                elif sline.startswith("endfacet"):
                    self.facet_list.append(facet.dump())
                    del facet

                line = f.readline()
                cnt += 1

        tessSolid = _g4.solid.TesselatedSolid(str(solidname), self.facet_list)

        if visualise or writeGDML:
            worldSolid   = _g4.solid.Box('worldBox',10,10,10)
            worldLogical = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

            tessLogical  = _g4.LogicalVolume(tessSolid, "G4_CONCRETE", "tessLogical")
            boxPhysical2 = _g4.PhysicalVolume([0,0,0], [0,0,0],tessLogical,'tessPhysical',worldLogical)

            # clip the world logical volume
            worldLogical.setClip();

            # register the world volume
            _g4.registry.setWorld('worldLogical')

            if visualise:
                # mesh the geometry
                m = worldLogical.pycsgmesh()

                # view the geometry
                v = _vtkv.Viewer()
                v.addPycsgMeshList(m, refine=False)
                v.view();

            if writeGDML:
                # write gdml
                w = _gdml.Writer()
                w.addDetector(_g4.registry)
                w.write('./Tessellated.gdml')
                w.writeGmadTester('Tessellated.gmad')

        return tessSolid

class _Facet():
    def __init__(self, normal=(0,0,0)):
        self.vertices = []
        self.normal   = normal

    def add_vertex(self, xyztup):
        self.vertices.append(xyztup)

    def dump(self):
        return (tuple(self.vertices), self.normal)

