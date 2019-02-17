import sys
sys.path.append("/opt/local/libexec/freecad/lib/")
import FreeCAD     as _fc
import FreeCADGui  as _fcg
_fcg.setupWithoutGUI()

import numpy              as _np
import logging            as _log

import pyg4ometry.geant4  as _g4
import pyg4ometry.transformation as _trans

class Reader(object) : 
    def __init__(self, fileName, registryOn = True) : 
        self.fileName = fileName

        # load file
        self.load(fileName) 

        # assign registry 
        if registryOn  : 
            self._registry = _g4.Registry()

    def load(self, fileName) :         
        _fc.loadFile(fileName) 
        self.doc = _fc.activeDocument()

    def convertStructure(self) : 
        '''Convert file with structure''' 
        self.rootLogical = self.recurseObjectTree(self.doc.RootObjects[0])[0]
        self._registry.setWorld(self.rootLogical.name)

    def convertFlat(self) :
        '''Convert file without structure'''

        import pyg4ometry.geant4.solid.Box
        import pyg4ometry.geant4.solid.TessellatedSolid
        import pyg4ometry.geant4.LogicalVolume 
        import pyg4ometry.geant4.PhysicalVolume
        import pyg4ometry.gdml.Defines

        tmin = _fc.Vector(1e99,1e99,1e99)
        tmax = _fc.Vector(-1e99,-1e99,-1e99)

        logicals   = [] 
        placements = [] 
        
        for obj in self.doc.Objects :
            if obj.TypeId == "Part::Feature" : 

                # tesellate         
                m = obj.Shape.tessellate(0.1)

                # global placement
                globalPlacement = PartFeatureGlobalPlacement(obj,_fc.Placement())

                # info log output
                _log.info('freecad.reader.convertFlat> Part::Feature label=%s typeid=%s placement=%s' %(obj.Label, obj.TypeId, obj.Placement))
                            
                # remove placement 
                placement = obj.Placement.inverse()
                
                # mesh includes placement and rotation (so it needs to be removed)
                for i in range(0,len(m[0])) : 
                    m[0][i] = placement.multVec(m[0][i])
                                
                # facet list 
                f =  MeshToFacetList(m)

                # mesh extent
                [mmin, mmax] = FacetListAxisAlignedExtent(f)
                gmin = globalPlacement.multVec(mmin)
                gmax = globalPlacement.multVec(mmax)

                if gmin.x < tmin.x :
                    tmin.x = gmin.x
                if gmin.y < tmin.y :
                    tmin.y = gmin.y
                if gmin.z < tmin.z :
                    tmin.z = gmin.z

                if gmax.x > tmax.x :
                    tmax.x = gmax.x
                if gmax.y > tmax.y :
                    tmax.y = gmax.y
                if gmax.z > tmax.z :
                    tmax.z = gmax.z
                    
                
                # solid 
                s = pyg4ometry.geant4.solid.TessellatedSolid(obj.Label, f, registry=self._registry) 

                # logical
                l = pyg4ometry.geant4.LogicalVolume(s,"G4_Galactic",obj.Label+"_lv",registry=self._registry)
                
                # physical 
                x = globalPlacement.Base[0] 
                y = globalPlacement.Base[1] 
                z = globalPlacement.Base[2]

                # rotation for placement
                m44 = globalPlacement.toMatrix()
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

                logicals.append(l)
                placements.append([tba,[x,y,z]])

        bSolid   = pyg4ometry.geant4.solid.Box("worldSolid",1,1,1,registry=self._registry)
        bLogical = pyg4ometry.geant4.LogicalVolume(bSolid,"G4_Galactic","worldLogical",registry=self._registry)
        
        for i in range(0,len(logicals)) : 
            # logical volume
            a1 = placements[i][0][0]
            a2 = placements[i][0][1]
            a3 = placements[i][0][2]            
        
            x = placements[i][1][0]
            y = placements[i][1][1]
            z = placements[i][1][2]

            p = pyg4ometry.geant4.PhysicalVolume(pyg4ometry.gdml.Defines.Rotation("z1",str(a1),str(a2),str(a3),self._registry,False),
                                                 pyg4ometry.gdml.Defines.Position("p2",str(x),str(y),str(z),self._registry,False),
                                                 logicals[i],                                                    
                                                 obj.Label+"_pv",
                                                 bLogical,
                                                 registry=self._registry)                
        print tmin, tmax, tmax-tmin
        self.rootLogical = bLogical
        self._registry.setWorld("worldLogical")
        
    def getRegistry(self) : 
        return self._registry

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

