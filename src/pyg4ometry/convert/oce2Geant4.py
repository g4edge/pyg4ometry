import pyg4ometry as _pyg4
import pyg4ometry.pyoce as _oce

def oceShape_Geant4_Tessellated(name, shape, greg) :

    ##############################################
    # G4 tessellated solid
    ##############################################
    g4t = _pyg4.geant4.solid.TessellatedSolid(name,None,greg)

    nbVerties   = 0
    nbTriangles = 0

    ##############################################
    # create triangulation
    ##############################################
    aMesher = _oce.BRepMesh.BRepMesh_IncrementalMesh(shape, 0.5, False, 0.5, True);

    ##############################################
    # Count total number of nodes and triangles
    ##############################################
    mergedNbNodes = 0
    mergedNbTriangles = 0

    topoExp  = _oce.TopExp.TopExp_Explorer(shape, _oce.TopAbs.TopAbs_FACE, _oce.TopAbs.TopAbs_VERTEX)
    location = _oce.TopLoc.TopLoc_Location()

    while(topoExp.More()) :
        triangulation = _oce.BRep.BRep_Tool.Triangulation(_oce.TopoDS.TopoDSClass.Face(topoExp.Current()),
                                                          location,
                                                          _oce.Poly.Poly_MeshPurpose_NONE)
        topoExp.Next()

        mergedNbNodes += triangulation.NbNodes()
        mergedNbTriangles += triangulation.NbTriangles()

    print('total : nodes, triangles',mergedNbNodes,mergedNbTriangles)

    ##############################################
    # Merge triangles from faces
    ##############################################
    mergedMesh = _oce.Poly.Poly_Triangulation(mergedNbNodes, mergedNbTriangles, False,False)

    topoExp.Init(shape, _oce.TopAbs.TopAbs_FACE, _oce.TopAbs.TopAbs_VERTEX)

    nodeCounter = 0
    triangleCounter = 0

    while(topoExp.More()) :

        triangulation = _oce.BRep.BRep_Tool.Triangulation(_oce.TopoDS.TopoDSClass.Face(topoExp.Current()),
                                                          location,
                                                          _oce.Poly.Poly_MeshPurpose_NONE)

        aTrsf = location.Transformation()
        for i in range(1,triangulation.NbNodes()+1,1) :
            aPnt = triangulation.Node(i)
            aPnt.Transform(aTrsf)
            mergedMesh.SetNode(i+nodeCounter, aPnt)
            g4t.addVertex([aPnt.X(), aPnt.Y(), aPnt.Z()])

        orientation = topoExp.Current().Orientation();
        for i in range(1,triangulation.NbTriangles()+1,1) :
            aTri = triangulation.Triangle(i);
            i1, i2, i3 = aTri.Get()

            i1 += nodeCounter
            i2 += nodeCounter
            i3 += nodeCounter

            if orientation == _oce.TopAbs.TopAbs_Orientation.TopAbs_REVERSED :
                aTri.Set(i2,i1,i3)
                g4t.addTriangle([i2 - 1, i1 - 1, i3 - 1])
            else :
                aTri.Set(i1,i2,i3)
                g4t.addTriangle([i1 - 1, i2 - 1, i3 - 1])

            mergedMesh.SetTriangle(i+triangleCounter, aTri)

        nodeCounter += triangulation.NbNodes()
        triangleCounter += triangulation.NbTriangles()

        topoExp.Next()

    g4t.removeDuplicateVertices()

def _oce2Geant4_traverse(shapeTool,label,greg, addBoundingSolids = False) :
    name  = _oce.pythonHelpers.get_TDataStd_Name_From_Label(label)
    loc   = _oce.pythonHelpers.get_XCAFDoc_Location_From_Label(label)
    shape = shapeTool.GetShape(label)
    locShape = shape.Location()
    node = _pyg4.pyoce.TCollection.TCollection_AsciiString()
    _oce.TDF.TDF_Tool.Entry(label,node)
    if name is None :
        name = node.ToCString()

    # determine if shape is assembly, compound or simple shape
    print(name+" | "+node.ToCString()+" | "+_oce.pythonHelpers.get_shapeTypeString(shapeTool, label))

    # if simple add solid and return solid

    # IO to check things are going ok
    # print(name)
    #if loc is not None :
    #    loc.Get().ShallowDump()
    #locShape.ShallowDump()

    # Loop over children
    for i in range(1, label.NbChildren() + 1, 1):
        b, child = label.FindChild(i, False)
        _oce2Geant4_traverse(shapeTool,child,greg)
    # if compound or assembly return assembly

    # If referring to simple shape
    rlabel = _oce.TDF.TDF_Label()
    shapeTool.GetReferredShape(label, rlabel)
    if not rlabel.IsNull():
        _oce2Geant4_traverse(shapeTool,rlabel,greg)

def oce2Geant4(shapeTool, shapeName) :
    greg = _pyg4.geant4.Registry()

    label = _oce.pythonHelpers.findOCCShapeByName(shapeTool, shapeName)
    if label is None :
        print("Cannot find shape, exiting")
        return

    # find name of shape
    name = _oce.pythonHelpers.get_TDataStd_Name_From_Label(label)

    # traverse cad and make geant4 geometry
    _oce2Geant4_traverse(shapeTool, label, greg)


