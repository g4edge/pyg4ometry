import sys
sys.path.append("/opt/local/libexec/freecad/lib/")
import FreeCAD     as _fc
import FreeCADGui  as _fcg
_fcg.setupWithoutGUI()

import logging            as _log

import pyg4ometry.geant4  as _g4

class Reader(object) : 
    def __init__(self, fileName, registryOn = True) : 
        self.fileName = fileName

        # load file
        self.load(fileName) 
        
        if registryOn  : 
            self.registry = _g4.Registry()
        
    def load(self, fileName) :         
        _fc.loadFile(fileName) 
        self.doc = _fc.activeDocument()

    def loopRootObjects(self, reg) : 
        self.rootLogicals = []

        for obj in self.doc.RootObjects :
            # print 'freecad.reader.loopRootObjects> typeid=%s label=%s grouplen=%d' % (obj.TypeId, obj.Label, len(obj.Group))

            self.rootLogicals.append(self.recurseObjectTree(obj,reg))

    def printStructure(self) :
        for obj in self.doc.RootObjects : 
            self.recursePrintObjectTree(obj)

    def recursePrintObjectTree(self, obj) :
        
        if obj.TypeId == 'App::Part' : 
            print 'App::Part',obj.TypeId,obj.Label,obj.Placement            
            for gobj in obj.Group : 
                self.recursePrintObjectTree(gobj)
        elif obj.TypeId == 'Part::Feature' : 
            print 'Part::Feature',obj.TypeId,obj.Label,obj.Placement

    def recurseObjectTree(self, obj,reg) : 

        import pyg4ometry.geant4.solid.Box
        import pyg4ometry.geant4.solid.TessellatedSolid
        import pyg4ometry.geant4.LogicalVolume 
        import pyg4ometry.geant4.PhysicalVolume
        import pyg4ometry.gdml.Defines
        
        if obj.TypeId == 'App::Part' :         # --> logical volume (what shape?)
            print 'freecad.reader> App::Part label=%s grouplen=%d' %(obj.Label, len(obj.Group)), obj.Placement

            bSolid   = pyg4ometry.geant4.solid.Box(obj.Label+"_solid",100,100,100,registry=reg)
            bLogical = pyg4ometry.geant4.LogicalVolume(bSolid,"G4_Galactic",obj.Label+"_lv",registry=reg)
            

            for gobj in obj.Group :
                [lv, placement] = self.recurseObjectTree(gobj, reg)

                x = placement.Base[0] 
                y = placement.Base[1] 
                z = placement.Base[2] 
                p = pyg4ometry.geant4.PhysicalVolume(pyg4ometry.gdml.Defines.Rotation("z1","0","0","0",reg,False),
                                                     pyg4ometry.gdml.Defines.Position("p2",str(x),str(y),str(z),reg,False),
                                                     lv,                                                    
                                                     gobj.Label+"_pv",
                                                     bLogical,
                                                     registry=reg)
                # bLogical.add(p)
            return [bLogical,obj.Placement]

                
            return objects
        elif obj.TypeId == 'Part::Feature' :   # --> solid, logical volume, physical volume
            print 'freecad.reader> Part::Feature label=%s' % (obj.Label), obj.Placement
            
            # tesellate         
            m = obj.Shape.tessellate(0.1)

            # centre of mass 
            com = obj.Shape.CenterOfMass 

            # mesh includes some placement placement
            for i in range(0,len(m[0])) : 
                m[0][i] = m[0][i]-com
            
            # facet list 
            f =  MeshToFacetList(m)
            
            # solid 
            s = pyg4ometry.geant4.solid.TessellatedSolid(obj.Label, f, registry=reg) 

            # logical
            l = pyg4ometry.geant4.LogicalVolume(s,"G4_Galactic",obj.Label+"_lv",registry=reg)

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
