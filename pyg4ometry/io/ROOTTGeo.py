import ROOT as _ROOT
import pyg4ometry.geant4 as _g4
import pyg4ometry.transformation as _transformation
import numpy as _np

def rootMatrix2pyg4ometry(matrix, reader) :

    if _ROOT.addressof(matrix) in reader.matrices:
        boolRotPyG4 = reader.matrices[_ROOT.addressof(matrix)]['pyg4RotObj']
        boolTraPyG4 = reader.matrices[_ROOT.addressof(matrix)]['pyg4TraObj']
        rotation    = _np.frombuffer(reader.matrices[_ROOT.addressof(matrix)]['rootObj'].GetRotationMatrix(),dtype=_np.float64,count=9).reshape((3,3))
        translation = _np.frombuffer(reader.matrices[_ROOT.addressof(matrix)]['rootObj'].GetTranslation(),dtype=_np.float64,count=3)
        reader.matrices[_ROOT.addressof(matrix)]['count'] += 1
        return [boolRotPyG4, boolTraPyG4, rotation, translation]
    else:
        rotation    = _np.frombuffer(matrix.GetRotationMatrix(),dtype=_np.float64,count=9).reshape((3,3))
        translation = _np.frombuffer(matrix.GetTranslation(),dtype=_np.float64,count=3)

        rotPyG4 = list(_transformation.matrix2tbxyz(rotation))
        traPyG4 = list(translation*10) # TODO check units on booleans

        reader.matrices[_ROOT.addressof(matrix)] = {"name": matrix.GetName(),
                                                    "count": 1,
                                                    "pyg4RotObj": rotPyG4,
                                                    "pyg4TraObj": traPyG4,
                                                    "rootObj": matrix}
        return [rotPyG4, traPyG4, rotation, translation]

def rootShape2pyg4ometry(shape, reader) :

    registry = reader._registry

    shapePyG4    = None
    shapeName    = shape.GetName()
    shapeAddress = _ROOT.addressof(shape)
    shapeClass   = shape.Class_Name()

    if shapeAddress in reader.shapes :
        reader.shapes[shapeAddress]["count"] += 1
        return reader.shapes[shapeAddress]["pyg4Obj"]

    # check for name clashes (so degenerate shape names)
    if shapeName in reader._registry.solidDict:
        shapeName += "_"
        shapeName += str(shapeAddress)

    reader.shapes[shapeAddress] = {"name": shapeName, "class": shapeClass, "count": 1, "pyg4Obj": None,
                                 "rootObj": shape}

    if shapeClass == "TGeoBBox":
        shapePyG4 = _g4.solid.Box(shapeName,
                                  shape.GetDX()*2,
                                  shape.GetDY()*2,
                                  shape.GetDZ()*2,
                                  registry,
                                  lunit="cm")
    elif shapeClass == "TGeoTube":
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
        shapePyG4 = _g4.solid.Trd(shapeName,
                                  shape.GetDx1()*2,
                                  shape.GetDx2()*2,
                                  shape.GetDy()*2,
                                  shape.GetDy()*2,
                                  shape.GetDz()*2,
                                  registry,
                                  lunit="cm")
    elif shapeClass == "TGeoTrd2":
        shapePyG4 = _g4.solid.Trd(shapeName,
                                  shape.GetDx1()*2,
                                  shape.GetDx2()*2,
                                  shape.GetDy1()*2,
                                  shape.GetDy2()*2,
                                  shape.GetDz()*2,
                                  registry,
                                  lunit="cm")
    elif shapeClass == "TGeoTrap":
        shapePyG4 = _g4.solid.Trap(shapeName,
                                   shape.GetDZ(),
                                   shape.GetTheta(),
                                   shape.GetPhi(),
                                   shape.GetH1(),
                                   shape.GetTl1(),
                                   shape.GetBl1(),
                                   shape.GetAlpha1(),
                                   shape.GetH2(),
                                   shape.GetTl2(),
                                   shape.GetBl2(),
                                   shape.GetAlpha2(),
                                   registry,
                                   lunit="cm",
                                   aunit="deg")
    elif shapeClass == "TGeoGtra":
        shapePyG4 = _g4.solid.TwistedTrap(shapeName,
                                          shape.GetTwistAngle(),
                                          shape.GetDZ(),
                                          shape.GetTheta(),
                                          shape.GetPhi(),
                                          shape.GetH1(),  #pDy1
                                          shape.GetTl1(), #pDx1
                                          shape.GetBl1(), #pDx2
                                          shape.GetH2(),  #pDy2
                                          shape.GetTl2(), #pDx3
                                          shape.GetBl2(), #pDx4
                                          shape.GetAlpha2(),
                                          registry,
                                          lunit="cm",
                                          aunit="deg")
    elif shapeClass == "TGeoSphere":
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
        shapePyG4 = _g4.solid.EllipticalTube(shapeName,
                                             shape.GetA()*2,
                                             shape.GetB()*2,
                                             shape.GetDz()*2,
                                             registry,
                                             lunit="cm")
    elif shapeClass == "TGeoCone":
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
        shapePyG4 = _g4.solid.Paraboloid(shapeName,
                                         shape.GetDz()*2,
                                         shape.GetRlo(),
                                         shape.GetRhi(),
                                         registry,
                                         lunit="cm")
    elif shapeClass == "TGeoHype":
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
        shapePyG4Unscaled = rootShape2pyg4ometry(shape.GetShape(),
                                                 reader)
        shapePyG4         = _g4.solid.Scaled(shapeName,
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

        boolLeftShapePyG4   = rootShape2pyg4ometry(boolNodeLeftShape, reader)
        boolRightShapePyG4  = rootShape2pyg4ometry(boolNodeRightShape, reader)

        [boolNodeLeftRotPyG4, boolNodeLeftTraPyG4, matROOT, traROOT ]   = rootMatrix2pyg4ometry(boolNodeLeftMatrix,  reader)
        [boolNodeRightRotPyG4, boolNodeRightTraPyG4, matROOT, traROOT] = rootMatrix2pyg4ometry(boolNodeRightMatrix, reader)

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

    reader.shapes[shapeAddress]['pyg4Obj'] = shapePyG4
    return shapePyG4

class Reader:
    def __init__(self, fileName, upgradeVacuumToG4Galactic=True):
        self.tgm = _ROOT.TGeoManager.Import(fileName)

        self.first = True

        self._registry = _g4.Registry()

        self.shapes          = {}
        self.logicalVolumes  = {}
        self.matrices        = {} # map to rotations and translations in defines
        self.physicalVolumes = {}
        self.materials       = {}

        self.load(upgradeVacuumToG4Galactic)

        tv = self.tgm.GetTopVolume()
        self._registry.setWorld(tv.GetName())

    def getRegistry(self):
        return self._registry

    def load(self, upgradeVacuumToG4Galactic=True):
        self.loadMaterials(upgradeVacuumToG4Galactic)
        self.topVolume = self.tgm.GetTopVolume()
        self.recurseVolumeTree(self.topVolume)

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

        for iMat in range(0,materialList.GetEntries(),1) :

            material = materialList.At(iMat)
            materialAddress = _ROOT.addressof(material)
            materialName = material.GetName()
            materialName = materialName.replace(':','')
            materialClass = material.Class_Name()

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

            n_comp = material.GetNelements()
            if n_comp == 1:
                Z = material.GetZ()
                A = material.GetA()
                g4Mat = _g4.MaterialSingleElement(materialName, Z, A, density, registry=self._registry, tolerateZeroDensity=True)
                g4Mat.set_state(stateStr)

            else :
                g4Mat = _g4.MaterialCompound(materialName, density, n_comp, registry=self._registry, tolerateZeroDensity=True)
                g4Mat.set_state(stateStr)

                for iComp in range(0,n_comp,1) :
                    elem = material.GetElement(iComp)
                    fraction = material.GetWmixt()[iComp]
                    g4Mat.add_element_massfraction(self._makeG4Element(elem), fraction)

            temperature = material.GetTemperature()
            pressure = material.GetPressure()

            g4Mat.set_temperature( temperature )
            g4Mat.set_pressure( pressure )

            # TODO add properties (a la lines 418-421 gdml/Reader.py)


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

    def recurseVolumeTree(self, volume):

        #print("ROOT.Reader.recurseVolumeTree class={} name={}".format(volume.GetName(),
        #                                                              volume.Class_Name()))
        volumeAddress = _ROOT.addressof(volume)
        volumeName    = volume.GetName()
        volumeClass   = volume.Class_Name()

        if volumeClass != "TGeoVolumeAssembly":

            # shape
            shape        = volume.GetShape()
            shapeAddress = _ROOT.addressof(shape)
            shapeName    = shape.GetName()
            shapeClass   = shape.Class_Name()

            shapePyG4 = rootShape2pyg4ometry(shape,self)

            # material
            material = volume.GetMaterial()
            materialName = material.GetName()
            materialName = materialName.replace(':','')

        if volumeAddress in self.logicalVolumes:
            # Already have the volume so increment counter
            self.logicalVolumes[volumeAddress]["count"] += 1
            return self.logicalVolumes[volumeAddress]["pyg4Obj"]
        else:
            if volumeClass == "TGeoVolume":
                # make logical volume
                volumePyG4 = _g4.LogicalVolume(shapePyG4,materialName,volumeName,self._registry)
            elif volumeClass == "TGeoVolumeAssembly":
                volumePyG4 = _g4.AssemblyVolume(volumeName,self._registry)
            else :
                print("ROOT.Reader> unknown volume class {}".format(volumeClass))

            # add logical volume to dictionaries
            self.logicalVolumes[volumeAddress] = {"name":volumeName,"class":volumeClass,"count":1,"pyg4Obj":volumePyG4,"rootObj":volume}

            # create and add daughters
            for iDaughter in range(0,volume.GetNdaughters(),1) :
                node   = volume.GetNode(iDaughter)
                matrix = node.GetMatrix()

                [nodeRotPyG4, nodeTraPyG4, matROOT, traROOT] = rootMatrix2pyg4ometry(matrix.Inverse(), self)
                nodeTraPyG4 = list(-1*_np.linalg.inv(matROOT).dot(nodeTraPyG4))


                daughterVolumePyG4 = self.recurseVolumeTree(node.GetVolume())

                if daughterVolumePyG4 is None :
                    print("daugher is none {}".format(node.GetVolume().Class_Name()))
                nodePyG4 = _g4.PhysicalVolume(nodeRotPyG4,
                                              nodeTraPyG4,
                                              daughterVolumePyG4,
                                              node.GetName(),
                                              volumePyG4,
                                              self._registry,
                                              node.GetNumber())


            if self.first:
                self._registry.setWorld(volumePyG4)
                self.first = False

            return volumePyG4
