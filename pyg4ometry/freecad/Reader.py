import sys
sys.path.append("/opt/local/libexec/freecad/lib/")
import FreeCAD     as _fc
import FreeCADGui  as _fcg
_fcg.setupWithoutGUI()

import numpy              as _np
import logging            as _log
import random             as _random

import pyg4ometry.geant4  as _g4
import pyg4ometry.transformation as _trans
from pyg4ometry.geant4.Material import Material as _Material

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
        
    def relabelModel(self) : 
        for obj in self.doc.Objects : 
            obj.Label = obj.Label.replace("(","_")
            obj.Label = obj.Label.replace(")","_")
            obj.Label = obj.Label.replace("-","_")
            obj.Label = obj.Label.replace(u' ','_')
            obj.Label = obj.Label.replace(u'.','dot')

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

    def convertFlat(self, meshDeviation = 0.05, centreName = '',globalOffset=_fc.Vector(), globalRotation=_fc.Rotation(), extentScale=1.0):
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

                # tesellate         
                m = obj.Shape.tessellate(meshDeviation)

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
                    if mGlobal.x < tmin.x :
                        tmin.x = mGlobal.x
                    if mGlobal.y < tmin.y :
                        tmin.y = mGlobal.y
                    if mGlobal.z < tmin.z :
                        tmin.z = mGlobal.z

                    if mGlobal.x > tmax.x :
                        tmax.x = mGlobal.x
                    if mGlobal.y > tmax.y :
                        tmax.y = mGlobal.y
                    if mGlobal.z > tmax.z :
                        tmax.z = mGlobal.z
                                                    
                # facet list 
                f =  MeshToFacetList(m)

                # solid 
                s = pyg4ometry.geant4.solid.TessellatedSolid(obj.Label, f, registry=self._registry) 

                # logical
                l = pyg4ometry.geant4.LogicalVolume(s,"G4_Galactic",obj.Label+"_lv",registry=self._registry)
                
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

        print tmin, tmax, tmax-tmin
        tsize   = tmax-tmin 
        tcentre = (tmax-tmin)/2.0+tmin

        # scale world volume extents
        if extentScale != 1.0:
            tsize.scale(extentScale,extentScale,extentScale)

        print tcentre

        bSolid   = pyg4ometry.geant4.solid.Box("worldSolid",tsize.x/2,tsize.y/2,tsize.z/2,registry=self._registry)
        bLogical = pyg4ometry.geant4.LogicalVolume(bSolid,"G4_Galactic","worldLogical",registry=self._registry)
        
        for i in range(0,len(logicals)) : 
            # logical volume
            a1 = placements[i][0][0]
            a2 = placements[i][0][1]
            a3 = placements[i][0][2]
        
            x = placements[i][1][0]-tcentre.x
            y = placements[i][1][1]-tcentre.y
            z = placements[i][1][2]-tcentre.z

            p = pyg4ometry.geant4.PhysicalVolume(pyg4ometry.gdml.Defines.Rotation("z1",str(a1),str(a2),str(a3),registry=self._registry,addRegistry=False),
                                                 pyg4ometry.gdml.Defines.Position("p2",str(x),str(y),str(z),registry=self._registry,addRegistry=False),
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
                    print obj.Label+'\t\t 1.0,0.0,0.0,1.0 \t surface \t G4_Galactic'
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
            print 'Part::Feature',obj.TypeId,obj.Label,obj.Placement

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
            f =  MeshToFacetList(m)
            
            # solid 
            s = pyg4ometry.geant4.solid.TessellatedSolid(obj.Label, f, registry=self._registry) 

            # logical
            l = pyg4ometry.geant4.LogicalVolume(s,"G4_Galactic",obj.Label+"_lv",registry=self._registry)

            # solid 
            return [l,obj.Placement]
                       
        else : 
            print 'freecad.reader> unprocessed %s' %(obj.TypeId)


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

