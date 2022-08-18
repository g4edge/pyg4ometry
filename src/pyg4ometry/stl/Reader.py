import numpy as _np
import re as _re
import warnings as _warnings
import struct
import io

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
    """
    STL file reader

    :param filename: Input STL filename
    :type filename: str
    :param solidname: Name of the solid to be created
    :type solidname: str
    :param scale: Scaling of STL (e.g. for units)
    :type scale: float
    :param centre: Flag to centre STL solid
    :type centre: boolean
    :param registry: Registry to add solid to
    :type registry: Registry
    :param forcebinary: Forces to load this STL file in binary format, otherwise the file format is determined from whether it starts with the string 'solid'
    :type forcebinary: boolean
    """

    def __init__(self, filename, solidname="stl_tessellated", scale=1, centre = False, registry=None, forcebinary = False):
        if registry is None:  # If a registry is not supplied, make an empty one
            registry = _g4.Registry()

        self.filename = filename
        self._registry = registry
        self.solidname = solidname

        self.worldVolumeName  = str()
        self.facet_list = []

        self.scale = float(scale)

        # load file
        with open(self.filename, 'rb') as f:
            data = f.read()
            # this detection is not good, there might be binary STL files that start with 'solid'.
            is_binary = forcebinary or struct.unpack('5s', data[0:5])[0] != b'solid'
            try:
                self.facet_list = list(self._load_binary(data) if is_binary else self._load_ascii(data))
            except Exception as e:
                raise RuntimeError(f'Failed reading STL file {self.filename}. Either the file is corrupt, uses non-standard '
                    + f'extensions, or file type has been detected wrongly. Trying to load a binary file?: {is_binary}'
                    + (' - binary loading can be forced by setting forcebinary=True' if not is_binary else '')) from e

        # centre model if requested
        if centre:
            self.extentCentre()


        self.solid = _g4.solid.TessellatedSolid(self.solidname, self.facet_list, self._registry,
                                                _g4.solid.TessellatedSolid.MeshType.Stl)

    def _load_ascii(self, data):
        """
        Load ASCII STL file from bytes instance

        :type data: bytes
        """
        # Compile re to match numbers
        num_re = _re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")

        def extractXYZ(string):
            # The scaling here is a bit cheeky, but the scale parameter in
            # GDML seems to be ignored by Geant4 for Tessellated Solids
            return tuple([self.scale*float(v) for v in string.split() if num_re.match(v)])

        f = io.TextIOWrapper(io.BytesIO(data))
        line = f.readline()
        facet = None
        while line:
            sline = line.strip()
            if sline.startswith("facet"):  # Indicates a facet, only first char comparison
                assert(facet == None)
                normal = extractXYZ(sline)
                facet = _Facet(normal)

            elif sline.startswith("vertex"):
                assert(facet != None)
                vertex = extractXYZ(sline)
                facet.add_vertex(vertex)

            elif sline.startswith("endfacet"):
                yield facet.dump()
                facet = None

            line = f.readline()

    def _load_binary(self, data):
        """
        Load binary STL file from bytes instance

        :type data: bytes
        """
        # ignore the first 80 bytes of data, as this is the header.
        faces = struct.unpack('<I', data[80:84])[0]

        def extractVector(d):
            vec = struct.unpack('<fff', d)
            return tuple([self.scale*v for v in vec])

        for fc in range(0, faces):
            fo = 84 + fc*50 # offset of the current facet
            facet = _Facet(extractVector(data[fo:fo+12]))
            for v in range(1, 4):
                vo = fo + v*12
                facet.add_vertex(extractVector(data[vo:vo+12]))
            # ignore last 2 bytes of facet definition - this might break if the additional byte count
            # _actually_ refers to an additional byte count, but it not always does (some application
            # directly store metadata in those two bytes).
            yield facet.dump()

    def extent(self):
        '''
        Compute the axis aligned extent of the STL solid.

        :returns: list of minima and maxima in 3 axes
        :rtype: [[xmin,ymin,zmin],[xmax, ymax, zmax]]
        '''

        xmin =  1e9
        ymin =  1e9
        zmin =  1e9
        xmax = -1e9
        ymax = -1e9
        zmax = -1e9

        for f in self.facet_list :
            for v in f[0] :
                if v[0] < xmin :
                    xmin = v[0]
                if v[1] < ymin :
                    ymin = v[1]
                if v[2] < zmin :
                    zmin = v[2]

                if v[0] > xmax :
                    xmax = v[0]
                if v[1] > ymax :
                    ymax = v[1]
                if v[2] > zmax :
                    zmax = v[2]

        return [[xmin,ymin,zmin],[xmax,ymax,zmax]]

    def extentCentre(self):
        '''
        Translate STL mesh to centre of the extent
        '''

        e  = _np.array(self.extent())
        de = e[1] - e[0]
        c  = (e[1] + e[0])/2.0
        self.translate(-c)

    def translate(self, translation = [0,0,0]):
        '''
        Translate STL mesh by translation

        :param translation: Vector to translate mesh
        :type translation: list(3) or array(3)

        '''

        facet_list = []

        for f in self.facet_list :
            vl = []
            n = f[1]
            for v in f[0] :
                vt = list(_np.array(v) + _np.array(translation))
                vl.append(vt)

            facet_list.append([vl,n])

        self.facet_list = facet_list

    def getSolid(self):
        '''
        Get geant4.solid

        :return: G4Tesselated for STL
        :rtype: TessellatedSolid
        '''

        return self.solid

    def getRegistry(self):
        '''
        Return registry
        '''

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

        :param filename: Output file name
        :type filename: str
        :param gmad_tester: Flag for writing BDSIM gmad tester
        :type gmad_tester: boolean


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
