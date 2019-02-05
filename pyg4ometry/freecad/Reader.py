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

    def parseModel(self) : 
        for o in self.doc.RootObjects :
            print 'freecad.reader>',o.Label, len(o.Group)

            if o.TypeId == 'App::Part' :
                print 'freecad.reader> App::Part' 
            elif o.TypeId == 'Part::Feature' : 
                print 'freecad.reader> Part::Feature'
                            
    
