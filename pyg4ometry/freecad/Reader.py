import sys
import FreeCAD     as _fc
import FreeCADGui  as _fcg
_fcg.setupWithoutGUI()

import numpy              as _np
import logging            as _log
import random             as _random

import pyg4ometry.geant4                          as _g4
import pyg4ometry.transformation                  as _trans
from   pyg4ometry.geant4._Material import Material as _Material
from   pyg4ometry.meshutils import MeshShrink

class Reader(object) : 

    def __init__(self, fileName, registryOn = True, fileNameAux = None) : 
        self.fileName = fileName

        # load file
        self.load(fileName) 

        # if auxilary data available 
        if fileNameAux != None : 
            self.loadAuxilaryData(fileNameAux)
            
        # assign registry 
        if registryOn  : 
            self._registry = _g4.Registry()

    def load(self, fileName) :
        _fc.loadFile(fileName) 
        self.doc = _fc.activeDocument()

    def simplifyModel(self, volumeCut = 5e5) : 

        for o in self.doc.Objects : 
            if o.TypeId == "Part::Feature" : 
                v = o.Shape.Volume 
                # print o.Label, v
                if v < volumeCut : 
                    o.Document.removeObject(o.Name)
        
        self.doc.saveAs(self.fileName.replace(".step","_Simplified.FCStd"))

    def relabelModel(self) : 
        for obj in self.doc.Objects : 
            obj.Label = obj.Label.replace("(","_")
            obj.Label = obj.Label.replace(")","_")
            obj.Label = obj.Label.replace("-","_")
            obj.Label = obj.Label.replace(u' ','_')
            obj.Label = obj.Label.replace(u'.','_dot_')
            obj.Label = obj.Label.replace(u',','_comma_')
            obj.Label = obj.Label.replace(u':','_colon_')
            obj.Label = obj.Label.replace(u'\\','_fs_')

            if obj.Label[0].isdigit() :
                obj.Label = "number"+obj.Label


    def loadAuxilaryData(self, fileName, colorByMaterial = True) : 
        f = open(fileName,"r") 

        self.solidAux = {}         # TODO rename self.auxVolumeData
        self.materialSet = set()   # TODO rename self.auxMaterialSet
        
        for l in f : 
            sl = l.split()
            solidName      = sl[0]
            color          = map(float,sl[1].split(','))
            representation = sl[2]
            material       = sl[3]

            # add auxilary information to dictionary
            self.solidAux[solidName] = {'color':color, 'representation':representation, 'material':material}

            # material list 
            self.materialSet.add(material) 
            
        # unique materials
        if colorByMaterial : 
            for m in self.materialSet : 
                rc = _random.uniform(0,1)
                gc = _random.uniform(0,1)
                bc = _random.uniform(0,1)            
                for sn in self.solidAux.keys() :
                    if self.solidAux[sn]['material'] == m : 
                        self.solidAux[sn]['color'] = [rc,gc,bc,1]
            
    def convertStructure(self) : 
        '''Convert file with structure''' 
        self.rootLogical = self.recurseObjectTree(self.doc.RootObjects[0])[0]
        self._registry.setWorld(self.rootLogical.name)

    def setLogicalVolumeMaterial(self, logicalVolumeName, material="G4_Galactic"):
        if not logicalVolumeName in self._registry.logicalVolumeList:
            raise ValueError("Logical volume "+ logicalVolumeName+" not found in registry")
        else:
            if isinstance(material, _Material):
                self.material = material
            elif isinstance(material, str):
                self.material = _Material.nist(material)
            else:
                raise SystemExit("Unsupported type for material: {}".format(type(material)))

    def convertFlat(self, meshDeviation = 0.05,
                    centreName          = '',
                    globalOffset        = _fc.Vector(),
                    globalRotation      = _fc.Rotation(),
                    extentScale         = 1.0,
                    daughterMaterial    = "G4_Galactic",
                    storePartCentrePos  = False,
                    meshShrinkFactor    = 1e-6):
        '''Convert file without structure'''

        import pyg4ometry.geant4.solid.Box
        import pyg4ometry.geant4.solid.TessellatedSolid
        import pyg4ometry.geant4.LogicalVolume 
        import pyg4ometry.geant4.PhysicalVolume
        import pyg4ometry.gdml.Defines

        tmin = _fc.Vector(1e99,1e99,1e99)
        tmax = _fc.Vector(-1e99,-1e99,-1e99)

        names      = [] 
        logicals   = [] 
        placements = [] 
        extents    = []  # mesh extents (min, max) for each part feature
        centres    = []  # geometric mesh centre for each part feature

        if centreName != '' : 
            centreObject = self.doc.getObjectsByLabel(centreName)[0]
            centrePlacement = centreObject.getGlobalPlacement()
        else : 
            centrePlacement = _fc.Placement()

        # global translation
        if isinstance(globalOffset,_fc.Vector):
            if globalOffset.Length != 0:
                centrePlacement.move(globalOffset)

        for obj in self.doc.Objects :
            if obj.TypeId == "Part::Feature" :
                # object centre of mass
                # com = obj.Shape.CenterOfMass

                # object extents in freecad world
                objMin = _fc.Vector(1e99, 1e99, 1e99)
                objMax = _fc.Vector(-1e99, -1e99, -1e99)

                name = obj.Label

                # tesellate         
                m = list(obj.Shape.tessellate(meshDeviation))

                # global placement
                globalPlacement = obj.getGlobalPlacement()

                # global rotation
                if isinstance(globalRotation, _fc.Rotation):
                    if globalRotation.Angle != 0:
                        globalPlacement.Base     = globalRotation.multVec(globalPlacement.Base)
                        globalPlacement.Rotation = globalRotation.multiply(globalPlacement.Rotation)

                # info log output
                _log.info('freecad.reader.convertFlat> Part::Feature label=%s typeid=%s placement=%s' %(obj.Label, obj.TypeId, obj.Placement))
                            
                # remove placement 
                placement = obj.Placement.inverse()

                # mesh includes placement and rotation (so it needs to be removed)
                for i in range(0,len(m[0])) :
                    m[0][i] = placement.multVec(m[0][i]) 

                    # global mesh vector 
                    mGlobal = globalPlacement.multVec(m[0][i])

                    # find minimum and maximum
                    if mGlobal.x < objMin.x :
                        objMin.x = mGlobal.x
                    if mGlobal.y < objMin.y :
                        objMin.y = mGlobal.y
                    if mGlobal.z < objMin.z :
                        objMin.z = mGlobal.z

                    if mGlobal.x > objMax.x :
                        objMax.x = mGlobal.x
                    if mGlobal.y > objMax.y :
                        objMax.y = mGlobal.y
                    if mGlobal.z > objMax.z :
                        objMax.z = mGlobal.z

                # find minimum and maximum of whole part feature
                if objMin.x < tmin.x :
                    tmin.x = objMin.x
                if objMin.y < tmin.y :
                    tmin.y = objMin.y
                if objMin.z < tmin.z :
                    tmin.z = objMin.z

                if objMax.x > tmax.x :
                    tmax.x = objMax.x
                if objMax.y > tmax.y :
                    tmax.y = objMax.y
                if objMax.z > tmax.z :
                    tmax.z = objMax.z

                objCentre = (objMax - objMin) / 2.0 + objMin
                extents.append([objMin,objMax])
                centres.append(objCentre)

                # Mesh tidying
                mc = MeshCleaning(m)
                # print 'Removed triangles',mc

                # Mesh shrinking 
                vn = MeshShrink(m,meshShrinkFactor)

#                print obj.Label, obj.TypeId, len(m[0])
                if len(m[0]) == 0 :                      # skip empty meshes (can happen with compound objects)
                    continue

                # Mesh analysis
                ma = MeshAnalysis(m)
              
                # facet list 
                # f =  MeshToFacetList(m)

                # solid 
                s = pyg4ometry.geant4.solid.TessellatedSolid(obj.Label, m, self._registry, pyg4ometry.geant4.solid.TessellatedSolid.MeshType.Freecad) 

                # logical
                l = pyg4ometry.geant4.LogicalVolume(s,daughterMaterial,obj.Label+"_lv",registry=self._registry)
                
                # physical
                x = globalPlacement.Base[0] - centrePlacement.Base[0] 
                y = globalPlacement.Base[1] - centrePlacement.Base[1]
                z = globalPlacement.Base[2] - centrePlacement.Base[2]

                # rotation for placement
                m44 = globalPlacement.toMatrix().inverse()
                m33 = _np.zeros((3,3))
                m33[0][0] = m44.A11
                m33[0][1] = m44.A12
                m33[0][2] = m44.A13
                m33[1][0] = m44.A21
                m33[1][1] = m44.A22
                m33[1][2] = m44.A23
                m33[2][0] = m44.A31
                m33[2][1] = m44.A32
                m33[2][2] = m44.A33                
                tba = _trans.matrix2tbxyz(m33)

                names.append(obj.Label)
                logicals.append(l)
                placements.append([tba,[x,y,z]])

        tsize   = (tmax-tmin)*(1+0.0)
        tcentre = (tmax-tmin)/2.0+tmin

        # scale world volume extents
        if extentScale != 1.0:
            tsize.scale(extentScale,extentScale,extentScale)

        bSolid   = pyg4ometry.geant4.solid.Box("worldSolid",tsize.x,tsize.y,tsize.z,registry=self._registry)
        bLogical = pyg4ometry.geant4.LogicalVolume(bSolid,"G4_Galactic","worldLogical",registry=self._registry)
        
        for i in range(0,len(logicals)) : 
            # logical volume
            a1 = placements[i][0][0]
            a2 = placements[i][0][1]
            a3 = placements[i][0][2]
        
            x = placements[i][1][0]-tcentre.x
            y = placements[i][1][1]-tcentre.y
            z = placements[i][1][2]-tcentre.z

            # local geometric centres of each part's mesh - note this is NOT synonymous with the part's position
            localCentreX = centres[i][0] - tcentre.x
            localCentreY = centres[i][1] - tcentre.y
            localCentreZ = centres[i][2] - tcentre.z

            if storePartCentrePos:
                localPos = pyg4ometry.gdml.Defines.Position(names[i] + "_centre", str(localCentreX),str(localCentreY),str(localCentreZ), registry=self._registry, addRegistry=True)

            p = _g4.PhysicalVolume(pyg4ometry.gdml.Defines.Rotation(names[i]+"_z1",str(a1),str(a2),str(a3),registry=self._registry,addRegistry=False),
                                   pyg4ometry.gdml.Defines.Position(names[i]+"_p2",str(x),str(y),str(z),registry=self._registry,addRegistry=False),
                                   logicals[i],                                                    
                                   names[i]+"_pv",
                                   bLogical,
                                   registry=self._registry)

            # set attributes 
            try : 
                if len(self.solidAux.keys()) != 0 : 
                    p.visOptions.representation = self.solidAux[names[i]]['representation']
                    p.visOptions.color          = self.solidAux[names[i]]['color'][0:3]
                    p.visOptions.alpha          = self.solidAux[names[i]]['color'][3]
            except AttributeError : 
                pass

        self.rootLogical = bLogical
        self.rootPlacement = [tcentre.x,tcentre.y, tcentre.z]
        self._registry.setWorld(bLogical.name)
        
    def getRegistry(self) : 
        return self._registry

    def printPartFeatures(self, fileName = None, randomColors = False) : 
        ''' Print to screen or write to file Part::Features with color and material''' 

        if fileName != None : 
            f = open(fileName,"w")
        for obj in self.doc.Objects : 
            if obj.TypeId == "Part::Feature" : 
                if fileName == None :
                    # label r,g,b,a surface/wireframe material
                    print(obj.Label+'\t\t 1.0,0.0,0.0,1.0 \t surface \t G4_Galactic')
                else : 
                    if not randomColors :
                        f.write(obj.Label+'\t\t 1.0,0.0,0.0,1.0 \t surface \t G4_Galactic\n')
                    else : 
                        r = _random.uniform(0,1)
                        g = _random.uniform(0,1)
                        b = _random.uniform(0,1)
                        a = _random.uniform(0,1)
                        f.write(obj.Label+'\t\t %f,%f,%f,%f\t surface \t G4_Galactic\n' % (r,g,b,a))
        if fileName != None : 
            f.close()

    def printStructure(self) :
        for obj in self.doc.RootObjects : 
            self.recursePrintObjectTree(obj)

    def recursePrintObjectTree(self, obj) :
        
        if obj.TypeId == 'App::Part' : 
            _log.info('freecad.Reader.recursePrintObjectTree> App::Part %s %s %s' % (obj.TypeId,obj.Label,obj.Placement))
            for gobj in obj.Group : 
                self.recursePrintObjectTree(gobj)
        elif obj.TypeId == 'Part::Feature' : 
            print('Part::Feature', obj.TypeId, obj.Label, obj.Placement)

    def recurseObjectTree(self, obj) : 

        import pyg4ometry.geant4.solid.Box
        import pyg4ometry.geant4.solid.TessellatedSolid
        import pyg4ometry.geant4.LogicalVolume 
        import pyg4ometry.geant4.PhysicalVolume
        import pyg4ometry.gdml.Defines
        
        if obj.TypeId == 'App::Part' :         # mapped to logical volume, group objects mapped to physical
            _log.info('freecad.reader.recurseObjectTree> App::Part label=%s grouplen=%d placement=%s' %(obj.Label, len(obj.Group), obj.Placement))

            bSolid   = pyg4ometry.geant4.solid.Box(obj.Label+"_solid",100,100,100,registry=self._registry)
            bLogical = pyg4ometry.geant4.LogicalVolume(bSolid,"G4_Galactic",obj.Label+"_lv",registry=self._registry)
            
            for gobj in obj.Group :
                [lv, placement] = self.recurseObjectTree(gobj)

                # position for placement
                x = placement.Base[0] 
                y = placement.Base[1] 
                z = placement.Base[2]

                # rotation for placement
                m44 = placement.toMatrix()
                m33 = _np.zeros((3,3))
                m33[0][0] = m44.A11
                m33[0][1] = m44.A12
                m33[0][2] = m44.A13
                m33[1][0] = m44.A21
                m33[1][1] = m44.A22
                m33[1][2] = m44.A23
                m33[2][0] = m44.A31
                m33[2][1] = m44.A32
                m33[2][2] = m44.A33                
                tba = _trans.matrix2tbxyz(m33)

                # logical volume
                p = pyg4ometry.geant4.PhysicalVolume(pyg4ometry.gdml.Defines.Rotation("z1",str(tba[0]),str(tba[1]),str(tba[2]),self._registry,False),
                                                     pyg4ometry.gdml.Defines.Position("p2",str(x),str(y),str(z),self._registry,False),
                                                     lv,                                                    
                                                     gobj.Label+"_pv",
                                                     bLogical,
                                                     registry=self._registry)
                # bLogical.add(p)
            return [bLogical,obj.Placement]

                
            return objects
        elif obj.TypeId == 'Part::Feature' :   # mapped to logical volumes
            _log.info('freecad.reader.recurseObjectTree> Part::Feature label=%s placement=%s' % (obj.Label, obj.Placement))
            
            # tesellate         
            m = obj.Shape.tessellate(0.1)

            # remove placement 
            placement = obj.Placement.inverse()

            # mesh includes placement and rotation (so it needs to be removed)
            for i in range(0,len(m[0])) : 
                m[0][i] = placement.multVec(m[0][i])
            
            # facet list 
            # f =  MeshToFacetList(m)
            
            # solid 
            s = pyg4ometry.geant4.solid.TessellatedSolid(obj.Label, m, registry=self._registry) 

            # logical
            l = pyg4ometry.geant4.LogicalVolume(s,"G4_Galactic",obj.Label+"_lv",registry=self._registry)

            # solid 
            return [l,obj.Placement]
                       
        else : 
            print('freecad.reader> unprocessed %s' %(obj.TypeId))


def MeshToFacetList(mesh) : 
    verts    = mesh[0]
    wind     = mesh[1]

    facet_list = []

    for tri in wind :
        i1 = tri[0]
        i2 = tri[1]
        i3 = tri[2]

        facet_list.append( (((verts[i1][0],verts[i1][1],verts[i1][2]),
                             (verts[i2][0],verts[i2][1],verts[i2][2]),
                             (verts[i3][0],verts[i3][1],verts[i3][2])),(0,1,2)) )
    return facet_list

def WriteSMeshFile(mesh,filename) : 
    f = open(filename,"w")
    
    verts    = mesh[0]
    wind     = mesh[1]

    f.write("# part 1 - node list\n")
    f.write("%i  3  0  0 \n" % (len(verts)))
    iv  = 0
    for v in verts : 
        f.write("%i %f %f %f\n" % (iv,v[0],v[1],v[2]))
        iv=iv+1
    
    f.write("# part 2 - facet list\n") 
    f.write("%i 0\n" % (len(wind)))

    iw = 0    
    for w in wind : 
        f.write("3 %i %i %i\n" % (w[0], w[1], w[2]))

    f.write("# part 3 - hole list\n") 
    f.write("0\n")

    f.write("# part 4 - region list\n") 
    f.write("0\n")

        

    f.close()


def FacetListAxisAlignedExtent(facetList) : 
    xMin = 1e99
    yMin = 1e99
    zMin = 1e99
    xMax = -1e99
    yMax = -1e99
    zMax = -1e99
    
    for f in facetList : 
        for v in f[0] : 
            if v[0] > xMax :
                xMax = v[0]
            if v[0] < xMin :
                xMin = v[0]

            if v[1] > yMax :
                yMax = v[1]
            if v[0] < yMin :
                yMin = v[1]

            if v[2] > zMax :
                zMax = v[2]
            if v[2] < zMin :
                zMin = v[2]

    min = _fc.Vector() 
    max = _fc.Vector() 

    min.x = xMin
    min.y = yMin
    min.z = zMin

    max.x = xMax
    max.y = yMax
    max.z = zMax

    return [min,max]

def PartFeatureGlobalPlacement(obj,placement) : 
    if len(obj.InList) != 0 : 
        return PartFeatureGlobalPlacement(obj.InList[0], obj.Placement.multiply(placement))
    else :
        return obj.Placement.multiply(placement)


def MeshAnalysis(m) : 
    verts = m[0]
    facet = m[1]

    area_array = []
    l01_array  = []
    l02_array  = []
    l12_array  = [] 
    hmin_array = []
    
    for tri in facet : 
        i1 = tri[0]
        i2 = tri[1]
        i3 = tri[2]

        v1 = _np.array(verts[i1])
        v2 = _np.array(verts[i2])
        v3 = _np.array(verts[i3])
        
        e1 = v1-v1
        e2 = v2-v1
        e3 = v3-v1

        e2xe3  = _np.cross(e2,e3)
        a      = 0.5*_np.linalg.norm(e2xe3)
        l01 = _np.linalg.norm(e1)
        l02 = _np.linalg.norm(e2)
        l12 = _np.linalg.norm(e2-e1)
        
        l01_array.append(l01)
        l02_array.append(l02)
        l12_array.append(l12)

        area_array.append(a)
        hmin_array.append(2*a/_np.array([l01,l02,l12]).max())

    l01_array  = _np.array(l01_array)
    l02_array  = _np.array(l02_array)
    l12_array  = _np.array(l12_array)
    area_array = _np.array(area_array)
    hmin_array = _np.array(hmin_array)

    #h = _np.histogram(area_array,100,(area_array.min(), area_array.max()))
    #print 'l01  ',l01_array.min(), l01_array.max()
    #print 'l02  ',l02_array.min(), l02_array.max()
    #print 'l12  ',l12_array.min(), l12_array.max()
    #print 'area ', area_array.min(), area_array.max(), hmin_array.min(), (1.0*(hmin_array<1e-9)).sum()

    return {'l01min': l01_array.min(), 'l01max': l01_array.max(),
            'l02min': l02_array.min(), 'l02max': l02_array.max(),
            'l12min': l12_array.min(), 'l12max': l12_array.max(),
            'areamin':area_array.min(), 'areamax':area_array.max()}
    
def MeshCleaning(m) : 
    verts = m[0]
    facet = m[1]

    idx = 0 
    iremoved = 0

    for tri in facet : 
        i1 = tri[0]
        i2 = tri[1]
        i3 = tri[2]

        v1 = _np.array(verts[i1])
        v2 = _np.array(verts[i2])
        v3 = _np.array(verts[i3])
        
        e1 = v1-v1
        e2 = v2-v1
        e3 = v3-v1

        l01 = _np.linalg.norm(e1)
        l02 = _np.linalg.norm(e2)
        l12 = _np.linalg.norm(e2-e1)

        e2xe3  = _np.cross(e2,e3)
        a      = 0.5*_np.linalg.norm(e2xe3)        
        hmin   = 2*a/_np.array([l01,l02,l12]).max()

        # remove zero area facets 
        if a == 0 :
            del facet[idx]
            iremoved = iremoved+1 

        # remove facets which would fail geant4 cuts 
        if hmin < 1e-9 :
            del facet[idx]
            iremoved = iremoved+1 
        
        idx = idx+1

        return iremoved

