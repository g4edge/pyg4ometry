from . import XCAFApp as _XCAFApp
from . import XCAFDoc as _XCAFDoc
from . import TCollection as _TCollection
from . import STEPCAFControl as _STEPCAFControl
from . import Message as _Message
from . import TDF as _TDF
from . import pythonHelpers as _ph

class Reader :
    def __init__(self, fileName):
        self.app = _XCAFApp.XCAFApp_Application.GetApplication();
        self.doc = self.app.NewDocument(_TCollection.TCollection_ExtendedString("MDTV-CAF"))

        self.readStepFile(fileName)

        self.main = self.doc.Main()
        self.shapeTool = _XCAFDoc.XCAFDoc_DocumentTool.ShapeTool(self.main)

    def readStepFile(self,fileName):
        stepReader = _STEPCAFControl.STEPCAFControl_Reader()
        mpr = _Message.Message_ProgressRange()
        stepReader.ReadFile(fileName)
        stepReader.Transfer(self.doc, mpr)

    def freeShapes(self):
        ls = _TDF.TDF_LabelSequence()
        self.shapeTool.GetFreeShapes(ls)
        return ls

    def traverse(self,label = None):

        name = _ph.get_TDataStd_Name_From_Label(label)
        loc  = _ph.get_XCAFDoc_Location_From_Label(label)
        node = _ph.get_TDataStd_TreeNode_From_Label(label)

        print(name, _ph.get_shapeTypeString(self.shapeTool,label),loc)

        for i in range(1,label.NbChildren()+1,1) :
            b, child = label.FindChild(i,False)
            self.traverse(child)

        rlabel = _TDF.TDF_Label()
        self.shapeTool.GetReferredShape(label, rlabel)
        if not rlabel.IsNull() :
            self.traverse(rlabel)

