import pyg4ometry as _pyg4

def test(fileName) :

    x = _pyg4.pyoce.XCAF()
    x.loadStepFile(fileName)

    st = x.shapeTool()
    st.Dump()

    ls = _pyg4.pyoce.TDF_LabelSequence()
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
        name     = _pyg4.pyoce.TDataStd_Name()
        nameGUID = _pyg4.pyoce.TDataStd_Name.GetID()
        found, name = l.FindAttribute(nameGUID,name)

        solidName     = _pyg4.pyoce.TNaming_NamedShape()
        solidNameGUID = _pyg4.pyoce.TNaming_NamedShape.GetID()
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

    aMesher = _pyg4.pyoce.BRepMesh_IncrementalMesh(s, 0.1, False, 0.1, True);

    mpr = _pyg4.pyoce.Message_ProgressRange()
    stlW = _pyg4.pyoce.StlAPI_Writer()
    stlW.Write(s,"PleaseFindMe.stl",mpr)
