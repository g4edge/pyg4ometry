import ROOT as _ROOT
import pyg4ometry.geant4 as _g4
import pyg4ometry.transformation as _transformation
import numpy as _np
import scipy.linalg as _la

from collections import defaultdict as _defaultdict

def _isClose(a, b, relativeTolerance=1e-5, absoluteTolerance=0.0):
    """
    return True if values are close to each other. As judged by the
    absolute difference between a and b is greater than relative_tolerance
    times that difference. Implementation from PEP 485 (python > 3.5)
    """
    return abs(a-b) <= max(relativeTolerance * max(abs(a), abs(b)), absoluteTolerance)

def rootMatrix2pyg4ometry(matrix, reader):
    if _ROOT.addressof(matrix) in reader.matrices:
        boolRotPyG4 = reader.matrices[_ROOT.addressof(matrix)]['pyg4RotObj']
        boolTraPyG4 = reader.matrices[_ROOT.addressof(matrix)]['pyg4TraObj']
        boolScaPyG4 = reader.matrices[_ROOT.addressof(matrix)]['pyg4ScaObj']
        rotation    = _np.frombuffer(reader.matrices[_ROOT.addressof(matrix)]['rootObj'].GetRotationMatrix(),dtype=_np.float64,count=9).reshape((3,3))
        translation = _np.frombuffer(reader.matrices[_ROOT.addressof(matrix)]['rootObj'].GetTranslation(),dtype=_np.float64,count=3)
        reader.matrices[_ROOT.addressof(matrix)]['count'] += 1
        return [boolRotPyG4, boolTraPyG4, boolScaPyG4, rotation, translation]
    else:
        rotation    = _np.frombuffer(matrix.GetRotationMatrix(),dtype=_np.float64,count=9).reshape((3,3))
        translation = _np.frombuffer(matrix.GetTranslation(),dtype=_np.float64,count=3)
        scale       = [1,1,1]
        if matrix.IsReflection() :
            q, r = _np.linalg.qr(rotation)
            #print("matrix {}".format(matrix.GetName()))
            #print("matrix ", rotation[0][0],rotation[0][1],rotation[0][2])
            #print("matrix ",rotation[1][0],rotation[1][1],rotation[1][2])
            #print("matrix ",rotation[2][0],rotation[2][1],rotation[2][2])
            #print("matrix IsScale({}), IsReflection({}), IsCombi({}), IsGeneral({}), Det({})".format(matrix.IsScale(), matrix.IsReflection(),matrix.IsCombi(),matrix.IsGeneral(),_np.linalg.det(rotation)))
            # q,r = _np.linalg.qr(rotation)
            r,q = _la.rq(rotation)
            #print("matrix scale : ",matrix.GetScale()[0],matrix.GetScale()[1],matrix.GetScale()[2])
            #print("matrix Q")
            #print(q)
            #print("matrix R")
            #print(r)
            scale[0] = r[0][0]
            scale[1] = r[1][1]
            scale[2] = r[2][2]
            rotation = q

        # compensate for precision problems with repeated calculations
        scale = [round(s,4) for s in scale]

        rotPyG4 = list(_transformation.matrix2tbxyz(rotation))
        traPyG4 = list(translation*10) # TODO check units on booleans
        scaPyG4 = list(scale)

        #print('g4 rot', rotPyG4)
        #print('g4 tra', traPyG4)
        #print('g4 sca', scaPyG4)

        reader.matrices[_ROOT.addressof(matrix)] = {"name": matrix.GetName(),
                                                    "count": 1,
                                                    "pyg4RotObj": rotPyG4,
                                                    "pyg4TraObj": traPyG4,
                                                    "pyg4ScaObj": scaPyG4,
                                                    "rootObj": matrix}
        return [rotPyG4, traPyG4, scaPyG4,rotation, translation]

def rootShape2pyg4ometry(shape, reader, warnAboutBadShapes=True):
    registry = reader._registry

    suffixSeparator = reader.suffixSeparator

    shapePyG4    = None
    shapeName    = shape.GetName()
    shapeAddress = _ROOT.addressof(shape)
    shapeClass   = shape.Class_Name()

    shouldTessellate = shapeName in reader.solidsToTessellate

    if reader.objectNames[shapeName] > 0:
        suffix = suffixSeparator + str(reader.objectNames[shapeName])
        reader.objectNames[shapeName] += 1
        shapeName = shapeName + suffix
    else:
        reader.objectNames[shapeName] += 1

    if shapeAddress in reader.shapes:
        reader.shapes[shapeAddress]["count"] += 1
        return reader.shapes[shapeAddress]["pyg4Obj"]

    # check for name clashes (so degenerate shape names)
    #if shapeName in reader._registry.solidDict:
    #    shapeName += "_"
    #    shapeName += str(shapeAddress)

    reader.shapes[shapeAddress] = {"name": shapeName, "class": shapeClass, "count": 1, "pyg4Obj": None,
                                 "rootObj": shape}

    def Arb8(aShape, aShapeName, aRegistry):
        if aShape.GetDz() <= 0:
            return None
        vertices = aShape.GetVertices()
        result = _g4.solid.GenericTrap(aShapeName,
                                       vertices[0],  vertices[1],
                                       vertices[2],  vertices[3],
                                       vertices[4],  vertices[5],
                                       vertices[6],  vertices[7],
                                       vertices[8],  vertices[9],
                                       vertices[10], vertices[11],
                                       vertices[12], vertices[13],
                                       vertices[14], vertices[15],
                                       aShape.GetDz(),
                                       aRegistry, lunit="cm")
        return result

    def Trap(aShape, aShapeName, aRegistry):
        c1 = aShape.GetBl1() <= 0 or aShape.GetTl1() <= 0 or aShape.GetH1() <= 0
        c2 = aShape.GetBl2() <= 0 or aShape.GetTl2() <= 0 or aShape.GetH2() <= 0
        if c1 or c2:
            result = Arb8(aShape, aShapeName, aRegistry)
        elif aShape.IsTwisted():
            result = Arb8(aShape, aShapeName, aRegistry)
        elif aShape.GetDz() <= 0:
            return None
        else:
            result = _g4.solid.Trap(aShapeName,
                                    aShape.GetDZ()*2,
                                    aShape.GetTheta(),
                                    aShape.GetPhi(),
                                    aShape.GetH1()*2,
                                    aShape.GetBl1()*2,
                                    aShape.GetTl1()*2,
                                    aShape.GetAlpha1(),
                                    aShape.GetH2()*2,
                                    aShape.GetBl2()*2,
                                    aShape.GetTl2()*2,
                                    aShape.GetAlpha2(),
                                    aRegistry,
                                    lunit="cm",
                                    aunit="deg")
        return result

    if shapeClass == "TGeoBBox":
        if shape.GetDX() <= 0 or shape.GetDY() <= 0 or shape.GetDZ() <= 0:
            return None
        shapePyG4 = _g4.solid.Box(shapeName,
                                  shape.GetDX()*2,
                                  shape.GetDY()*2,
                                  shape.GetDZ()*2,
                                  registry,
                                  lunit="cm")
    elif shapeClass == "TGeoArb8":
        shapePyG4 = Arb8(shape, shapeName, registry)
    elif shapeClass == "TGeoTube":
        if shape.GetDz() <= 0 or shape.GetRmax() <= 0:
            return None
        shapePyG4 = _g4.solid.Tubs(shapeName,
                                   shape.GetRmin(),
                                   shape.GetRmax(),
                                   shape.GetDz()*2,
                                   0,
                                   360,
                                   registry,
                                   lunit="cm",
                                   aunit="deg")
    elif shapeClass == "TGeoTubeSeg":
        if shape.GetDz() <= 0 or shape.GetRmax() <= 0:
            return None
        shapePyG4 = _g4.solid.Tubs(shapeName,
                                   shape.GetRmin(),
                                   shape.GetRmax(),
                                   shape.GetDz()*2,
                                   shape.GetPhi1(),
                                   shape.GetPhi2()-shape.GetPhi1(),
                                   registry,
                                   lunit="cm",
                                   aunit="deg")
    elif shapeClass == "TGeoCtub":
        if shape.GetDz() <= 0 or shape.GetRmax() <= 0:
            return None
        nlow  = shape.GetNlow()
        nhigh = shape.GetNhigh()
        shapePyG4 = _g4.solid.CutTubs(shapeName,
                                      shape.GetRmin(),
                                      shape.GetRmax(),
                                      shape.GetDz()*2,
                                      shape.GetPhi1(),
                                      shape.GetPhi2()-shape.GetPhi1(),
                                      [nlow[0],nlow[1],nlow[2]],
                                      [nhigh[0],nhigh[1],nhigh[2]],
                                      registry,
                                      lunit="cm",
                                      aunit="deg")
    elif shapeClass == "TGeoConeSeg":
        if shape.GetDz() <= 0:
            return None
        shapePyG4 = _g4.solid.Cons(shapeName,
                                   shape.GetRmin1(),
                                   shape.GetRmax1(),
                                   shape.GetRmin2(),
                                   shape.GetRmax2(),
                                   shape.GetDz()*2,
                                   shape.GetPhi1(),
                                   shape.GetPhi2()-shape.GetPhi1(),
                                   registry,
                                   lunit="cm",
                                   aunit="deg")
    elif shapeClass == "TGeoPara":
        shapePyG4 = _g4.solid.Para(shapeName,
                                   shape.GetX()*2,
                                   shape.GetY()*2,
                                   shape.GetZ()*2,
                                   shape.GetAlpha(),
                                   shape.GetTheta(),
                                   shape.GetPhi(),
                                   registry,
                                   lunit="cm",
                                   aunit="deg")
    elif shapeClass == "TGeoTrd1":
        if shape.GetDz() <= 0:
            return None
        shapePyG4 = _g4.solid.Trd(shapeName,
                                  shape.GetDx1()*2,
                                  shape.GetDx2()*2,
                                  shape.GetDy()*2,
                                  shape.GetDy()*2,
                                  shape.GetDz()*2,
                                  registry,
                                  lunit="cm")
    elif shapeClass == "TGeoTrd2":
        if shape.GetDz() <= 0:
            return None
        shapePyG4 = _g4.solid.Trd(shapeName,
                                  shape.GetDx1()*2,
                                  shape.GetDx2()*2,
                                  shape.GetDy1()*2,
                                  shape.GetDy2()*2,
                                  shape.GetDz()*2,
                                  registry,
                                  lunit="cm")
    elif shapeClass == "TGeoTrap":
        shapePyG4 = Trap(shape, shapeName, registry)
    elif shapeClass == "TGeoGtra":
        c1 = shape.GetBl1() <= 0 or shape.GetTl1() <= 0 or shape.GetH1() <= 0
        c2 = shape.GetBl2() <= 0 or shape.GetTl2() <= 0 or shape.GetH2() <= 0
        if c1 or c2:
            shapePyG4 = Arb8(shape, shapeName, registry)
        elif shape.IsTwisted():
            shapePyG4 = Arb8(shape, shapeName, registry)
        elif shape.GetTwistAngle() == 0:
            shapePyG4 = Trap(shape, shapeName, registry)
        elif shape.GetDz() <= 0:
            return None
        else:
            if warnAboutBadShapes:
                if not _isClose(shape.GetAlpha1(), shape.GetAlpha2()):
                    print("warning: Alpha2 != Alpha1 and GDML doesn't include Alpha2 for TGeoGtra in shape '",shape.GetName,"'")
            # see https://root.cern/doc/master/classTGDMLWrite.html#a4ce496683e55300ec3de53a43d707427
            shapePyG4 = _g4.solid.TwistedTrap(shapeName,
                                              shape.GetTwistAngle(),
                                              shape.GetDZ()*2,
                                              shape.GetTheta(),
                                              shape.GetPhi(),
                                              shape.GetH1()*2,  #pDy1
                                              shape.GetBl1()*2, #pDx1
                                              shape.GetTl1()*2, #pDx2
                                              shape.GetH2()*2,  #pDy2
                                              shape.GetBl2()*2, #pDx3
                                              shape.GetTl2()*2, #pDx4
                                              shape.GetAlpha1(),
                                              registry,
                                              lunit="cm",
                                              aunit="deg")
    elif shapeClass == "TGeoSphere":
        if shape.GetRmax() <= 0 or shape.GetRmax() <= 0:
            return None
        shapePyG4 = _g4.solid.Sphere(shapeName,
                                     shape.GetRmin(),
                                     shape.GetRmax(),
                                     shape.GetPhi1(),
                                     shape.GetPhi2()-shape.GetPhi1(),
                                     shape.GetTheta1(),
                                     shape.GetTheta2()-shape.GetTheta1(),
                                     registry,
                                     lunit="cm",
                                     aunit="deg")
    elif shapeClass == "TGeoTorus":
        if shape.GetRmax() <= 0:
            return None
        shapePyG4 = _g4.solid.Torus(shapeName,
                                    shape.GetRmin(),
                                    shape.GetRmax(),
                                    shape.GetR(),
                                    shape.GetPhi1(),
                                    shape.GetDphi(),
                                    registry,
                                    lunit="cm",
                                    aunit="deg")
    elif shapeClass == "TGeoPcon":
        nz   = shape.GetNz()
        z    = _np.frombuffer(shape.GetZ(),dtype=_np.float64,count=nz)
        rmin = _np.frombuffer(shape.GetRmin(),dtype=_np.float64,count=nz)
        rmax = _np.frombuffer(shape.GetRmax(),dtype=_np.float64,count=nz)

        shapePyG4 = _g4.solid.Polycone(shapeName,
                                       shape.GetPhi1(),
                                       shape.GetDphi(),
                                       z,
                                       rmin,
                                       rmax,
                                       registry,
                                       lunit="cm",
                                       aunit="deg")
    elif shapeClass == "TGeoPgon":
        nz    = shape.GetNz()
        nSide = shape.GetNedges()
        z    = _np.frombuffer(shape.GetZ(),dtype=_np.float64,count=nz)
        rmin = _np.frombuffer(shape.GetRmin(),dtype=_np.float64,count=nz)
        rmax = _np.frombuffer(shape.GetRmax(),dtype=_np.float64,count=nz)

        shapePyG4 = _g4.solid.Polyhedra(shapeName,
                                        shape.GetPhi1(),
                                        shape.GetDphi(),
                                        nSide,
                                        nz,
                                        z,
                                        rmin,
                                        rmax,
                                        registry,
                                        lunit="cm",
                                        aunit="deg")
    elif shapeClass == "TGeoEltu":
        if shape.GetA() <= 0 or shape.GetB() <= 0 or shape.GetDz() <= 0:
            return None
        shapePyG4 = _g4.solid.EllipticalTube(shapeName,
                                             shape.GetA()*2,
                                             shape.GetB()*2,
                                             shape.GetDz()*2,
                                             registry,
                                             lunit="cm")
    elif shapeClass == "TGeoCone":
        if shape.GetDz() <= 0:
            return None
        shapePyG4 = _g4.solid.Cons(shapeName,
                                   shape.GetRmin1(),
                                   shape.GetRmax1(),
                                   shape.GetRmin2(),
                                   shape.GetRmax2(),
                                   shape.GetDz()*2,
                                   0,
                                   2*_np.pi,
                                   registry,
                                   lunit="cm")
    elif shapeClass == "TGeoParaboloid":
        if shape.GetDz() <= 0 or shape.GetRhi() <= 0:
            return None
        shapePyG4 = _g4.solid.Paraboloid(shapeName,
                                         shape.GetDz()*2,
                                         shape.GetRlo(),
                                         shape.GetRhi(),
                                         registry,
                                         lunit="cm")
    elif shapeClass == "TGeoHype":
        if shape.GetDz() <= 0:
            return None
        shapePyG4 = _g4.solid.Hype(shapeName,
                                   shape.GetRmin(),
                                   shape.GetRmax(),
                                   shape.GetStIn(),
                                   shape.GetStOut(),
                                   shape.GetDz()*2,
                                   registry,
                                   lunit="cm",
                                   aunit="deg")
    elif shapeClass == "TGeoXtru":
        nVert = shape.GetNvert()
        nZ    = shape.GetNz()

        polygon = []
        for iv in range(0,nVert,1):
            polygon.append([shape.GetX(iv),shape.GetY(iv)])

        slices = []
        for iz in range(0,nZ,1):
            slices.append([shape.GetZ(iz),
                           [shape.GetXOffset(iz), shape.GetYOffset(iz)],
                           shape.GetScale(iz)])

        shapePyG4 = _g4.solid.ExtrudedSolid(shapeName,
                                            polygon,
                                            slices,
                                            registry,
                                            lunit="cm")
    elif shapeClass == "TGeoScaledShape":
        scale = shape.GetScale().GetScale()
        shapePyG4Unscaled = rootShape2pyg4ometry(shape.GetShape(), reader, warnAboutBadShapes)
        shapePyG4 = _g4.solid.Scaled(shapeName,
                                     shapePyG4Unscaled,
                                     scale[0],
                                     scale[1],
                                     scale[2],
                                     registry)
    elif shapeClass == "TGeoTessellated":
        nVert   = shape.GetNvertices()
        nFacet  = shape.GetNfacets()

        verts = []
        for iVert in range(0,nVert,1) :
            vertex = shape.GetVertex(iVert)
            verts.append([vertex.x()*10,
                          vertex.y()*10,
                          vertex.z()*10])

        facets = []
        for iFacet in range(0,nFacet,1) :
            facet = shape.GetFacet(iFacet)
            if facet.GetNvert() == 3 :
                facets.append([facet.GetVertexIndex(0),
                               facet.GetVertexIndex(1),
                               facet.GetVertexIndex(2)])
            elif facet.GetNvert() == 4:
                facets.append([facet.GetVertexIndex(0),
                               facet.GetVertexIndex(1),
                               facet.GetVertexIndex(2),
                               facet.GetVertexIndex(3)])
        shapePyG4 = _g4.solid.TessellatedSolid(shapeName,
                                               [verts,facets],
                                               registry,
                                               _g4.solid.TessellatedSolid.MeshType.Freecad)


    elif shapeClass == "TGeoCompositeShape":
        boolNode            = shape.GetBoolNode()
        boolNodeLeftShape   = boolNode.GetLeftShape()
        boolNodeRightShape  = boolNode.GetRightShape()
        boolNodeLeftMatrix  = boolNode.GetLeftMatrix()
        boolNodeRightMatrix = boolNode.GetRightMatrix()

        boolLeftShapePyG4   = rootShape2pyg4ometry(boolNodeLeftShape, reader, warnAboutBadShapes)
        boolRightShapePyG4  = rootShape2pyg4ometry(boolNodeRightShape, reader, warnAboutBadShapes)

        [boolNodeLeftRotPyG4, boolNodeLeftTraPyG4, boolNodeLeftScaPyG4, matROOT, traROOT ]  = rootMatrix2pyg4ometry(boolNodeLeftMatrix,  reader)
        [boolNodeRightRotPyG4, boolNodeRightTraPyG4, boolNodeRightScaPyG4, matROOT, traROOT] = rootMatrix2pyg4ometry(boolNodeRightMatrix, reader)

        # needed for nested booleans solids
        if shapeName in reader._registry.solidDict:
            shapeName += "_"
            shapeName += str(shapeAddress)

        if boolNode.Class_Name() == "TGeoUnion":
            shapePyG4 = _g4.solid.Union(shapeName,
                                        boolLeftShapePyG4,
                                        boolRightShapePyG4,
                                        [boolNodeRightRotPyG4,boolNodeRightTraPyG4],
                                        registry)
        elif boolNode.Class_Name() == "TGeoSubtraction":
            shapePyG4 = _g4.solid.Subtraction(shapeName,
                                              boolLeftShapePyG4,
                                              boolRightShapePyG4,
                                              [boolNodeRightRotPyG4,boolNodeRightTraPyG4],
                                              registry)
        elif boolNode.Class_Name() == "TGeoIntersection":
            shapePyG4 = _g4.solid.Intersection(shapeName,
                                               boolLeftShapePyG4,
                                               boolRightShapePyG4,
                                               [boolNodeRightRotPyG4,boolNodeRightTraPyG4],
                                               registry)
        else :
            print("rootShape2pyg4ometry> Unknown boolean")
            raise ValueError
    else:
        print("ROOT.Reader.rootShape2pyg4ometry> {} not implemented ".format(shape.Class_Name()))
        shape.ComputeBBox()
        shapePyG4 = _g4.solid.Box(shapeName,
                                  shape.GetDX(),
                                  shape.GetDY(),
                                  shape.GetDZ(),
                                  registry,
                                  lunit="cm")

    # shapePyG4 could be None here
    if shouldTessellate and shapePyG4 is not None:
        shapePyG4 = shapePyG4.conver2Tessellated()
        del registry.solidDict[shapeName]

    reader.shapes[shapeAddress]['pyg4Obj'] = shapePyG4
    return shapePyG4

class Reader:
    def __init__(self, fileName,
                 upgradeVacuumToG4Galactic=True,
                 solidsToTessellate=None,
                 suffixSeparator="__",
                 warnAboutBadShapes=True,
                 maximumDepth=1e6,
                 dontLoadOverlapNodes=True):
        """
        :param fileName: Name of root file to load as Geometry.
        :type  fileName: str
        :param upgradeVacuumToG4Galactic: If true, 'upgrade' any illegal 0 density materials to valid G4_Galactic.
        :type  upgradeVacuumToG4Galactic: bool
        :param solidsToTessellate: List of solids ('shapes') by name that should be replaced by a tessellated version.
        :type  solidsToTessellate: list(str)
        :param suffixSeparator: String to go between the object name and the counter for duplicate names (e.g. NAME__1).
        :type  suffixSeparator: str
        :param warnAboutBadShapes: Print a warning if true, about any shapes we can't successfully convert.
        :type  warnAboutBadShapes: bool
        :param maximumDepth: Maximum depth to load, 0=world, 1=1st daughter. Must be > 0.
        :type  maximumDepth: int
        :param dontLoadOverlapNodes: ROOT allows purposively overlapping geometry nodes. We don't load these by default.
        :type  dontLoadOverlapNodes: bool

        Be careful the suffixSeparator doesn't match up with a typical name. e.g. NAME and NAME_1 might already exist
        so we can't choose '_' as this would produce a degenerate name.
        """
        if solidsToTessellate is None:
            solidsToTessellate = []
        self.solidsToTessellate = solidsToTessellate

        self.suffixSeparator = suffixSeparator
        self.maximumDepth    = maximumDepth

        self.tgm = _ROOT.TGeoManager.Import(fileName)
        self.first = True
        self._registry = _g4.Registry()
        self._g4Galactic = None # fall back material

        self.objectNames         = _defaultdict(int)
        self.shapes              = {}
        self.logicalVolumes      = {}
        self.matrices            = {} # map to rotations and translations in defines
        self.physicalVolumes     = {}
        self.materials           = {}
        self.materialSubstitutions = {}
        self.elements            = {}
        self.isotopes            = {}

        self.load(upgradeVacuumToG4Galactic, warnAboutBadShapes, dontLoadOverlapNodes)

        tv = self.tgm.GetTopVolume()
        self._registry.setWorld(tv.GetName())

    def getRegistry(self):
        return self._registry

    def load(self, upgradeVacuumToG4Galactic=True, warnAboutBadShapes=True, dontLoadOverlapNodes=True):
        self.loadMaterials(upgradeVacuumToG4Galactic)
        self.topVolume = self.tgm.GetTopVolume()
        self.recurseVolumeTree(self.topVolume, 0, self.maximumDepth, warnAboutBadShapes, dontLoadOverlapNodes)

    def _ROOTMatStateToGeant4MatState(self, rootMaterialState):
        """
        Based on https://root.cern.ch/doc/master/classTGeoMaterial.html#a8b69c72f90711a29726087e029e39c61
        enum TGeoMaterial::EGeoMaterialState
        """
        states = {0 : None, # as per hthe default in MaterialBase
                  1 : "solid",
                  2 : "liquid",
                  3 : "gas"}
        return states[rootMaterialState]

    def loadMaterials(self, upgradeVacuumToG4Galactic):
        materialList = self.tgm.GetListOfMaterials()

        g4galactic = _g4.MaterialPredefined("G4_Galactic", self._registry)
        self._g4Galactic = g4galactic
        #nistMaterials = _g4.getNistMaterialDict()

        # dummy may apparently always exist and no material be defined
        self.materialSubstitutions["dummy"] = g4galactic

        for iMat in range(0,materialList.GetEntries(),1) :

            material = materialList.At(iMat)
            materialAddress = _ROOT.addressof(material)
            materialName = str(material.GetName())
            materialName = materialName.replace(':','')
            #materialClass = material.Class_Name()

            if materialName.lower() == "dummy":
                self.materials[materialAddress] = g4galactic

            # check for NIST material
            #if materialName in nistMaterials.keys() :
            #    g4Mat = _g4.getNistMaterialDict()[materialName]
            #    self.materials[materialAddress] = g4Mat
            #    continue

            if self.objectNames[materialName] > 0:
                suffix = self.suffixSeparator+str(self.objectNames[materialName])
                self.objectNames[materialName] += 1
                materialName = materialName + suffix
            else:
                self.objectNames[materialName] += 1

            #print(f'ROOT.Reader.loadMaterials class={materialClass} name={materialName}')

            components = []
            properties = {}

            state = material.GetState()
            stateStr = self._ROOTMatStateToGeant4MatState(state)
            density = material.GetDensity()

            if density == 0 and upgradeVacuumToG4Galactic:
                self.materialSubstitutions[materialName] = g4galactic
                self.materials[materialAddress] = g4galactic
                continue # don't build a new material

            if not material.IsMixture() :
                Z = material.GetZ()
                A = material.GetA()
                g4Mat = _g4.MaterialSingleElement(materialName, Z, A, density, registry=self._registry, tolerateZeroDensity=True)
                g4Mat.set_state(stateStr)

            else :
                n_comp = material.GetNelements()
                g4Mat = _g4.MaterialCompound(materialName, density, n_comp, registry=self._registry, tolerateZeroDensity=True)
                g4Mat.set_state(stateStr)

                for iComp in range(0,n_comp,1) :
                    elem = material.GetElement(iComp)
                    fraction = material.GetWmixt()[iComp]
                    g4Mat.add_element_massfraction(self._makeG4Element(elem), fraction)

            temperature = material.GetTemperature()
            pressure = material.GetPressure()


            if g4Mat.type != "nist" :
                g4Mat.set_temperature( temperature )
                g4Mat.set_pressure( pressure )

            # TODO add properties (a la lines 418-421 gdml/Reader.py)

            self.materials[materialAddress] = g4Mat

    def _makeG4Element(self, rootElement):
        elemFormula = rootElement.GetName()
        elemFormula = elemFormula.replace(':','')
        elemName = elemFormula + '_elm'

        if elemName in self._registry.materialDict :
            return self._registry.materialDict[elemName]

        if not rootElement.HasIsotopes() :
            Z = rootElement.Z()
            A = rootElement.A()
            return _g4.ElementSimple(elemName, elemFormula, Z, A, registry=self._registry)

        elemNisotopes = rootElement.GetNisotopes()

        elemMat = _g4.ElementIsotopeMixture(elemName, elemFormula, elemNisotopes, registry=self._registry)

        for iIsotope in range(0,elemNisotopes,1) :
            isotope = rootElement.GetIsotope(iIsotope)
            abundance = rootElement.GetRelativeAbundance(iIsotope)
            elemMat.add_isotope(self._makeG4Isotope(isotope), abundance)

        return elemMat

    def _makeG4Isotope(self, rootIsotope):
        isotopeName = rootIsotope.GetName()
        isotopeName = isotopeName.replace(':','')

        if isotopeName in self._registry.materialDict :
            return self._registry.materialDict[isotopeName]

        Z = rootIsotope.GetZ()
        N = rootIsotope.GetN()
        A = rootIsotope.GetA()
        return _g4.Isotope(isotopeName, Z, N, A, registry=self._registry)

    def recurseVolumeTree(self, volume, thisDepth, maximumDepth, warnAboutBadShapes=True, dontLoadOverlapNodes=True):

        #print("ROOT.Reader.recurseVolumeTree class={} name={}".format(volume.GetName(),
        #                                                              volume.Class_Name()))
        volumeAddress = _ROOT.addressof(volume)
        volumeName    = volume.GetName()
        volumeClass   = volume.Class_Name()

        if self.objectNames[volumeName] > 0:
            suffix = self.suffixSeparator + str(self.objectNames[volumeName])
            self.objectNames[volumeName] += 1
            volumeName = volumeName + suffix
        else:
            self.objectNames[volumeName] += 1


        if volumeClass != "TGeoVolumeAssembly":

            # shape
            shape        = volume.GetShape()
            shapeAddress = _ROOT.addressof(shape)
            shapeName    = shape.GetName()
            shapeClass   = shape.Class_Name()

            shapePyG4 = rootShape2pyg4ometry(shape, self, warnAboutBadShapes)
            if shapePyG4 is None:
                return None # unable to make the shape.. or poorly defined

            # material
            material = volume.GetMaterial()
            materialName = material.GetName()
            materialName = materialName.replace(':','')
            if materialName in self.materialSubstitutions:
                thisMaterial = self.materialSubstitutions[materialName]
            else:
                materialAddress = _ROOT.addressof(material)
                try:
                    thisMaterial = self.materials[materialAddress]
                except KeyError:
                    print("Material '",materialName,"' is used in geometry but not defined in list of materials - using G4_Galactic")
                    thisMaterial = self._g4Galactic

        if volumeAddress in self.logicalVolumes:
            # Already have the volume so increment counter
            self.logicalVolumes[volumeAddress]["count"] += 1
            return self.logicalVolumes[volumeAddress]["pyg4Obj"]
        else:
            if volumeClass == "TGeoVolume":
                # make logical volume
                volumePyG4 = _g4.LogicalVolume(shapePyG4, thisMaterial, volumeName, self._registry)
            elif volumeClass == "TGeoVolumeAssembly":
                volumePyG4 = _g4.AssemblyVolume(volumeName,self._registry)
            else :
                print("ROOT.Reader> unknown volume class {}".format(volumeClass))

            # add logical volume to dictionaries
            self.logicalVolumes[volumeAddress] = {"name":volumeName,"class":volumeClass,"count":1,"pyg4Obj":volumePyG4,"rootObj":volume}

            # create and add daughters
            if thisDepth < maximumDepth:
                for iDaughter in range(0,volume.GetNdaughters(),1):
                    node   = volume.GetNode(iDaughter)

                    # root has it's own layered geometry where it allows overlaps
                    if node.IsOverlapping() and dontLoadOverlapNodes:
                        if warnAboutBadShapes:
                            print("ROOT overlap node named {}, not building".format(node.GetName()))
                        continue # to next node / volume

                    matrix = node.GetMatrix()

                    [nodeRotPyG4, nodeTraPyG4, nodeScaPyG4, matROOT, traROOT] = rootMatrix2pyg4ometry(matrix, self)
                    nodeRotPyG4 = _transformation.matrix2tbxyz(_np.linalg.inv(_transformation.tbxyz2matrix(nodeRotPyG4)))

                    daughterVolumePyG4 = self.recurseVolumeTree(node.GetVolume(), thisDepth+1, maximumDepth,
                                                                warnAboutBadShapes, dontLoadOverlapNodes)
                    if daughterVolumePyG4 is None:
                        vol = node.GetVolume()
                        if warnAboutBadShapes:
                            print("unable to form daughter ({}) shape: {}".format(node.GetName(), vol.GetShape().GetName()))
                        continue

                    pvName = node.GetName()
                    if self.objectNames[pvName] > 0:
                        suffix = self.suffixSeparator + str(self.objectNames[pvName])
                        self.objectNames[pvName] += 1
                        pvName = pvName + suffix
                    else:
                        self.objectNames[pvName] += 1

                    # print("daughter", pvName, nodeRotPyG4,nodeTraPyG4,nodeScaPyG4)
                    nodePyG4 = _g4.PhysicalVolume(nodeRotPyG4,
                                                  nodeTraPyG4,
                                                  daughterVolumePyG4,
                                                  pvName,
                                                  volumePyG4,
                                                  self._registry,
                                                  node.GetNumber(),
                                                  True,
                                                  nodeScaPyG4)


            if self.first:
                self._registry.setWorld(volumePyG4)
                self.first = False

            return volumePyG4
