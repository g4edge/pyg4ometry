import pyg4ometry as _pyg4

def test(fileName) :

    x = _pyg4.pyoce.XCAF()
    x.loadStepFile(fileName)

    st = x.shapeTool()

    # st.Dump()

    ls = _pyg4.pyoce.TDF_LabelSequence()
    st.GetShapes(ls)

    for l in ls :
        s = st.GetShape(l)

        shape = st.IsShape(l)
        simpleShape = st.IsSimpleShape(l)
        subShape = st.IsSubShape(l)
        assembly = st.IsAssembly(l)
        component = st.IsComponent(l)
        compound = st.IsCompound(l)
        toplevel = st.IsTopLevel(l)
        free = st.IsFree(l)
        reference = st.IsReference(l)
        print(l,
              'shape=',shape,
              ' simpleShape=',simpleShape,
              ' subShape=',subShape,
              ' assembly=',assembly,
              ' component=',component,
              ' compound=',compound,
              ' toplevel=', toplevel,
              ' free=', free,
              ' reference=', reference)

    l = ls(1)
    s = st.GetShape(l)



    aMesher = _pyg4.pyoce.BRepMesh_IncrementalMesh(s, 0.01, False, 0.01, True);
    print(l5,s5)

    mpr = _pyg4.pyoce.Message_ProgressRange()
    stlW = _pyg4.pyoce.StlAPI_Writer()
    stlW.Write(s5,"PleaseFindMe.stl",mpr)
