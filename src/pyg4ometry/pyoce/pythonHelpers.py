# from . import oce as _oce
from . import TCollection as _TCollection
from . import TDF as _TDF
from . import TDataStd as _TDataStd
from . import XCAFDoc as _XCAFDoc
from . import gp as _gp
import numpy as _np

def findOCCShapeByName(shapeTool, shapeName):
    ls = _TDF.TDF_LabelSequence()
    shapeTool.GetShapes(ls)

    for l in ls:
        name = get_TDataStd_Name_From_Label(l)
        if name == shapeName:
            return l

    raise KeyError(shapeName)

def findOCCShapeByTreeNode(label, shapeTreeNode):
    newLabel = _TDF.TDF_Label()
    aShapeTreeNode = _TCollection.TCollection_AsciiString(shapeTreeNode)
    _TDF.TDF_Tool.Label(label.Data(), aShapeTreeNode, newLabel, False)

    return newLabel

def get_TDataStd_Name_From_Label(label) :
    nameGUID = _TDataStd.TDataStd_Name.GetID()
    name = _TDataStd.TDataStd_Name()
    b, name = label.FindAttribute(nameGUID, name)

    if b :
        return name.Get().ToExtString()
    else :
        return None

def get_TDataStd_TreeNode_From_Label(label) :
    treeNode     = _TDataStd.TDataStd_TreeNode()
    treeNodeGUID = _XCAFDoc.XCAFDocClass.AssemblyGUID()

    b, treeNode = label.FindAttribute(treeNodeGUID, treeNode)

    # a = TCollection.TCollection_AsciiString()
    # TDF_Tool.Entry(l, a)
    if b :
        return treeNode
    else :
        return None

def get_XCAFDoc_Location_From_Label(label) :
    locGUID = _XCAFDoc.XCAFDoc_Location.GetID()
    loc = _XCAFDoc.XCAFDoc_Location()
    b, loc = label.FindAttribute(locGUID, loc)

    if b :
        return loc
    else :
        return None

def get_shapeTypeString(st, label) :
    retString = ""
    if st.IsShape(label) :
        retString += "Shape "
    if st.IsSimpleShape(label) :
        retString += "SimpleShape "
    if st.IsAssembly(label) :
        retString += "Assembly "
    if st.IsComponent(label) :
        retString += "Component "
    if st.IsCompound(label) :
        retString += "Compound"

    return retString

def gp_XYZ_numpy(xyz) :
    return _np.array([xyz.X(), xyz.Y(), xyz.Z()])

def test(fileName) :

    x = XCAF()
    x.loadStepFile(fileName)

    st = x.shapeTool()
    st.Dump()

    ls = TDF_LabelSequence()
    st.GetShapes(ls)

    for l in ls :

        # label methods
        depth          = l.Depth()
        father         = l.Father()
        bHasAttribute  = l.HasAttribute()
        NbAttributes   = l.NbAttributes()
        bHasChild      = l.HasChild()
        NbChildren     = l.NbChildren()
        bRoot          = l.IsRoot()
        tag            = l.Tag()
        transaction    = l.Transaction()
        bNull          = l.IsNull()

        # label attributes
        name     = TDataStd_Name()
        nameGUID = TDataStd_Name.GetID()
        found, name = l.FindAttribute(nameGUID,name)

        solidName     = TNaming_NamedShape()
        solidNameGUID = TNaming_NamedShape.GetID()
        found, solidName = l.FindAttribute(solidNameGUID,solidName)

        print(name.Get().ToExtString(),solidName.Get().ShapeType(),l.Depth(),l.Father(),bHasAttribute, NbAttributes, NbChildren)

        # shape tool methods
        shape  = st.GetShape(l)
        bShape = st.IsShape(l)
        bSimpleShape = st.IsSimpleShape(l)
        bSubShape = st.IsSubShape(l)
        bAssembly = st.IsAssembly(l)
        bComponent = st.IsComponent(l)
        bCompound = st.IsCompound(l)
        bToplevel = st.IsTopLevel(l)
        bFree = st.IsFree(l)
        bReference = st.IsReference(l)

        print('shape=',bShape,
              ' simpleShape=',bSimpleShape,
              ' subShape=',bSubShape,
              ' assembly=',bAssembly,
              ' component=',bComponent,
              ' compound=',bCompound,
              ' toplevel=', bToplevel,
              ' free=', bFree,
              ' reference=', bReference)

        # shape methods
        shape.DumpJson()
        location = shape.Location()
        location.ShallowDump()
        translation = location.Transformation().TranslationPart()
        translation.DumpJson()

    l = ls(1)
    s = st.GetShape(l)

    aMesher = BRepMesh_IncrementalMesh(s, 0.1, False, 0.1, True);

    mpr = Message_ProgressRange()
    stlW = StlAPI_Writer()
    stlW.Write(s,"PleaseFindMe.stl",mpr)
