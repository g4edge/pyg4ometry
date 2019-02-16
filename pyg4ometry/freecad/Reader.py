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

        # loop over the root objects 
        self.loopRootObjects()
        
    def load(self, fileName) :         
        _fc.loadFile(fileName) 
        self.doc = _fc.activeDocument()

    def loopRootObjects(self) : 
        self.rootLogicals = []

        for obj in self.doc.RootObjects :
            # print 'freecad.reader.loopRootObjects> typeid=%s label=%s grouplen=%d' % (obj.TypeId, obj.Label, len(obj.Group))

            self.rootLogicals.append(self.recurseObjectTree(obj))

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
        
        if obj.TypeId == 'App::Part' :         # --> logical volume (what shape?)
            _log.info('freecad.reader.recurseObjectTree> App::Part label=%s grouplen=%d placement=%s' %(obj.Label, len(obj.Group), obj.Placement))

            bSolid   = pyg4ometry.geant4.solid.Box(obj.Label+"_solid",100,100,100,registry=self._registry)
            bLogical = pyg4ometry.geant4.LogicalVolume(bSolid,"G4_Galactic",obj.Label+"_lv",registry=self._registry)
            

            for gobj in obj.Group :
                [lv, placement] = self.recurseObjectTree(gobj)

                x = placement.Base[0] 
                y = placement.Base[1] 
                z = placement.Base[2]

                m44 = placement.toMatrix()
                m33       = _np.zeros((3,3))
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
                print tba

                p = pyg4ometry.geant4.PhysicalVolume(pyg4ometry.gdml.Defines.Rotation("z1",str(tba[0]),str(tba[1]),str(tba[2]),self._registry,False),
                                                     pyg4ometry.gdml.Defines.Position("p2",str(x),str(y),str(z),self._registry,False),
                                                     lv,                                                    
                                                     gobj.Label+"_pv",
                                                     bLogical,
                                                     registry=self._registry)
                # bLogical.add(p)
            return [bLogical,obj.Placement]

                
            return objects
        elif obj.TypeId == 'Part::Feature' :   # --> solid, logical volume, physical volume
            _log.info('freecad.reader.recurseObjectTree> Part::Feature label=%s placement=%s' % (obj.Label, obj.Placement))
            
            # tesellate         
            m = obj.Shape.tessellate(0.1)

            # remove placement 
            placement = obj.Placement.inverse()

            # mesh includes placement and rotation
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
