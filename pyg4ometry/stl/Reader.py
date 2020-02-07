import numpy             as _np
import re as _re
import warnings as _warnings

import pyg4ometry.visualisation as _vi
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd


class _Facet():
    def __init__(self, normal=(0,0,0)):
        self.vertices = []
        self.normal   = normal

    def add_vertex(self, xyztup):
        self.vertices.append(xyztup)

    def dump(self):
        return (tuple(self.vertices), self.normal)

class Reader(object):
    def __init__(self, filename, solidname="stl_tessellated", scale=1, registry=None):
        if registry is None:  # If a registry is not supplied, make an empty one
            registry = _g4.Registry()

        self.filename = filename
        self._registry = registry
        self.solidname = solidname

        self.worldVolumeName  = str()
        self.facet_list = []
        # Compile re to match numbers
        self.num_re = _re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")

        self.scale = float(scale)

        # load file
        self.load()

        self.solid = _g4.solid.TessellatedSolid(self.solidname, self.facet_list, self._registry,
                                                _g4.solid.TessellatedSolid.MeshType.Stl)

    def load(self):
        def extractXYZ(string):
            # The scaling here is a bit cheeky, but the scale parameter in
            # GDML seems to be ignored by Geanr4 for Tessellated Solids
            return tuple([self.scale*float(v) for v in string.split() if self.num_re.match(v)])

        with open(self.filename) as f:
            line = f.readline()
            cnt=1
            while line:
                sline = line.strip()
                if sline.startswith("facet"):  # Indicates a facet, only first char comaprison
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

    def getSolid(self):
        return self.solid

    def getRegistry(self):
        return self._registry

    def visualise(self):
        """
        View solid directly by using a dummy world
        """

        solid_mesh = self.solid.pycsgmesh()
        dummy_reg = _g4.Registry()
        dummy_material = _g4.MaterialPredefined("G4_Fe")
        dummy_reg.addSolid(self.solid)
        lv = _g4.LogicalVolume(self.solid, dummy_material, self.solidname+"_pv", dummy_reg)
        lv.makeWorldVolume(worldMaterial='G4_Galactic')  # Make a world volume automatically

        wv = dummy_reg.getWorldVolume()
        vis = _vi.VtkViewer()
        vis.addLogicalVolume(wv)
        vis.view(interactive=True)

    def writeDefaultGDML(self, filename="default", gmad_tester=False):
        """
        Write the tessellated solid loaded from STL to GDML. The placement has no
        rotation or translation. The world material is G4_Galactic, the solid material is G4_Fe.
        """

        if filename == "default":
            filename = self.solidname

        reg = _g4.Registry()
        material = _g4.MaterialPredefined("G4_Fe")
        reg.addSolid(self.solid)
        lv = _g4.LogicalVolume(self.solid, material, self.solidname+"_pv", reg)
        lv.makeWorldVolume(worldMaterial='G4_Galactic')  # Make a world volume automatically

        # gdml output
        w = _gd.Writer()
        w.addDetector(reg)

        fn = filename if filename.endswith(".gdml") else "{}.gdml".format(filename)
        w.write(fn)
        if gmad_tester:
            w.writeGmadTester(fn.replace("gdml", "gmad"), fn)


    '''    
    def logicalVolume(self,name, material = "G4_Galactic", reg = None) : 
        
        s = _TessellatedSolid(name+"_solid",self.facet_list,reg,_TessellatedSolid.MeshType.Stl)
        l = _LogicalVolume(s,material, name+"_pv",reg)

        return l

        tessSolid = _g4.solid.TessellatedSolid(str(solidname), self.facet_list)

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
                _vis.viewWorld()

            if writeGDML:
                # write gdml
                w = _gdml.Writer()
                w.addDetector(_g4.registry)
                w.write('./Tessellated.gdml')
                w.writeGmadTester('Tessellated.gmad')

        return tessSolid
    '''
