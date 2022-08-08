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
    aMesher = _oce.BRepMesh_IncrementalMesh(shape, 0.01, False, 0.01, True);

    ##############################################
    # Count total number of nodes and triangles
    ##############################################
    mergedNbNodes = 0
    mergedNbTriangles = 0

    topoExp  = _oce.TopExp_Explorer(shape, _oce.TopAbs_FACE, _oce.TopAbs_VERTEX)
    location = _oce.TopLoc_Location()

    while(topoExp.More()) :
        triangulation = _oce.BRep_Tool.Triangulation(_oce.TopoDS.Face(topoExp.Current()), location, _oce.Poly_MeshPurpose_NONE)
        topoExp.Next()

        mergedNbNodes += triangulation.NbNodes()
        mergedNbTriangles += triangulation.NbTriangles()

    print('total : nodes, triangles',mergedNbNodes,mergedNbTriangles)

    ##############################################
    # Merge triangles from faces
    ##############################################
    mergedMesh = _oce.Poly_Triangulation(mergedNbNodes, mergedNbTriangles, False, False)

    topoExp.Init(shape, _oce.TopAbs_FACE, _oce.TopAbs_VERTEX)

    nodeCounter = 0
    triangleCounter = 0

    while(topoExp.More()) :
        triangulation = _oce.BRep_Tool.Triangulation(_oce.TopoDS.Face(topoExp.Current()), location, _oce.Poly_MeshPurpose_NONE)
        topoExp.Next()


        for i in range(1,triangulation.NbNodes()+1,1) :
            aPnt = triangulation.Node(i);
            #print('pnt',aPnt.X(), aPnt.Y(), aPnt.Z())
            #aPnt.Transform(aTrsf);
            mergedMesh.SetNode(i+nodeCounter, aPnt)
            #aMesh->SetNode(aNodeIter + aNodeOffset, aPnt);
            g4t.addVertex([aPnt.X(), aPnt.Y(), aPnt.Z()])

        for i in range(1,triangulation.NbTriangles()+1,1) :
            aTri = triangulation.Triangle(i);
            i1 = aTri.Value(1)
            i2 = aTri.Value(2)
            i3 = aTri.Value(3)
            #print('tri',i1,i2,i3)

            i1 += nodeCounter
            i2 += nodeCounter
            i3 += nodeCounter

            #print('tri', i1, i2, i3)

            aTri.Set(i1,i2,i3)

            mergedMesh.SetTriangle(i+triangleCounter, aTri)
            g4t.addTriangle([i1-1,i2-1,i3-1])

        nodeCounter += triangulation.NbNodes()
        triangleCounter += triangulation.NbTriangles()

    g4t.removeDuplicateVertices()




def _oce2Geant4_traverse(xcaf,label,greg, addBoundingSolids = False) :
    name  = _oce.find_TDataStd_Name_From_Label(label)
    loc   = _oce.find_XCAFDoc_Location_From_Label(label)
    shape = xcaf.shapeTool().GetShape(label)
    locShape = shape.Location()

    # determine if shape is assembly, compound or simple shape
    print(name+" | "+_oce.shapeTypeString(xcaf.shapeTool(), label))

    # if simple add solid and return solid

    # IO to check things are going ok
    # print(name)
    #if loc is not None :
    #    loc.Get().ShallowDump()
    #locShape.ShallowDump()

    # Loop over children
    for i in range(1, label.NbChildren() + 1, 1):
        b, child = label.FindChild(i, False)
        _oce2Geant4_traverse(xcaf,child,greg)
    # if compound or assembly return assembly

    # If referring to simple shape
    rlabel = _oce.TDF_Label()
    xcaf.shapeTool().GetReferredShape(label, rlabel)
    if not rlabel.IsNull():
        _oce2Geant4_traverse(xcaf,rlabel,greg)

def oce2Geant4(xcaf, shapeName) :
    greg = _pyg4.geant4.Registry()

    label = _oce.findOCCShapeByName(xcaf.shapeTool(), shapeName)
    if label is None :
        print("Cannot find shape, exiting")
        return

    # find name of shape
    name = _oce.find_TDataStd_Name_From_Label(label)

    # traverse cad and make geant4 geometry
    _oce2Geant4_traverse(xcaf, label, greg)


