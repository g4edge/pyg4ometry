import sys
sys.path.append("/opt/local/libexec/freecad/lib/")
import FreeCAD     as _fc
import FreeCADGui  as _fcg 
_fcg.setupWithoutGUI()

class Reader(object) : 
    def __init__(self, fileName) : 
        self.fileName = fileName

        # load file
        self.load(fileName) 

    def load(self, fileName) :         
        _fc.loadFile(fileName) 
        self.doc = _fc.activeDocument()
        self.loopRootObjects()

    def loopRootObjects(self) : 
        for obj in self.doc.RootObjects :
            print 'freecad.reader.loopRootObjects> typeid=%s label=%s grouplen=%d' % (obj.TypeId, obj.Label, len(obj.Group))

            self.recurseObjectTree(obj)

    def recurseObjectTree(self, obj) : 
        if obj.TypeId == 'App::Part' :         # --> logical volume (what shape?)
            print 'freecad.reader> App::Part label=%s grouplen=%d' %(obj.Label, len(obj.Group))
            for gobj in obj.Group :
                 self.recurseObjectTree(gobj)
        elif obj.TypeId == 'Part::Feature' :   # --> solid, logical volume, physical volume
            print 'freecad.reader> Part::Feature label=%s' % (obj.Label)
        else : 
            print 'freecad.reader> unprocessed %s' %(obj.TypeId)

