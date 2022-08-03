from .oce import *

def findOCCShapeByName(shapeTool, shapeName):
    ls = TDF_LabelSequence()
    shapeTool.GetShapes(ls)

    for l in ls:
        nameGUID = TDataStd_Name.GetID()
        name = TDataStd_Name()
        b, name = l.FindAttribute(nameGUID, name)
        if name.Get().ToExtString() == shapeName:
            # print(name)
            return l

    return None

def find_XCAFDoc_Location_From_Label(label) :
    locGUID = XCAFDoc_Location.GetID()
    loc = XCAFDoc_Location()
    b, loc = label.FindAttribute(locGUID, loc)

    if b :
        return loc
    else :
        return None

def find_TDataStd_Name_From_Label(label) :
    nameGUID = TDataStd_Name.GetID()
    name = TDataStd_Name()
    b, name = label.FindAttribute(nameGUID, name)

    if b :
        return name.Get().ToExtString()
    else :
        return None

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
