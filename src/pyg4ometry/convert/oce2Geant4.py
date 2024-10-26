from .. import geant4 as _g4
from .. import pyoce as _pyoce
from .. import transformation as _transformation

defaultLinDef = 0.5
deftaulAngDef = 0.5


def oceShape_Geant4_LogicalVolume(name, solid, material, greg):
    """
    Make a logical volume from input or get from registry

    :param name: Name of logical volume
    :type name: str
    :param solid: Geant4 solid
    :type solid: SolidBase
    :param material: Material for logical volume
    :type material: str or pyg4ometry.geant4.Material
    :param greg: Geant4 registry
    :type greg: geant4.Registry
    """
    try:
        return greg.logicalVolumeDict[name]
    except:
        pass

    return _g4.LogicalVolume(solid, material, name, greg)


def oceShape_Geant4_Assembly(name, greg):
    """
    Make a assembly volume from input or get from registry

    :param name: Name of logical volume
    :type name: str
    :param greg: Geant4 registry
    :type greg: geant4.Registry
    """
    try:
        return greg.logicalVolumeDict[name]
    except:
        pass

    return _g4.AssemblyVolume(name, greg, True)


def oceShape_Geant4_Tessellated(name, shape, greg, linDef=0.5, angDef=0.5):
    """
    Make a tessellated solid from a OpenCascade shape

    :param name: Name of logical volume
    :type name: str
    :param shape: OpenCascade shape
    :type shape: TopoDS_Shape
    :param greg: Geant4 registry
    :type greg: geant4.Registry
    """
    ##############################################
    # Check if already in registry
    ##############################################

    try:
        return greg.solidDict[name]
    except KeyError:
        pass

    ##############################################
    # G4 tessellated solid
    ##############################################
    g4t = _g4.solid.TessellatedSolid(name, None, greg)

    nbVerties = 0
    nbTriangles = 0

    ##############################################
    # create triangulation
    ##############################################
    aMesher = _pyoce.BRepMesh.BRepMesh_IncrementalMesh(shape, linDef, False, angDef, True)

    ##############################################
    # Count total number of nodes and triangles
    ##############################################
    mergedNbNodes = 0
    mergedNbTriangles = 0

    topoExp = _pyoce.TopExp.TopExp_Explorer(
        shape, _pyoce.TopAbs.TopAbs_FACE, _pyoce.TopAbs.TopAbs_VERTEX
    )
    location = _pyoce.TopLoc.TopLoc_Location()

    while topoExp.More():
        # print(topoExp.Current().ShapeType())
        triangulation = _pyoce.BRep.BRep_Tool.Triangulation(
            _pyoce.TopoDS.TopoDSClass.Face(topoExp.Current()),
            location,
            _pyoce.Poly.Poly_MeshPurpose_NONE,
        )
        # TODO why is the triangulation none?
        if triangulation is None:
            print("empty triangulation")
            break

        topoExp.Next()

        mergedNbNodes += triangulation.NbNodes()
        mergedNbTriangles += triangulation.NbTriangles()

    # print('total : nodes, triangles', mergedNbNodes, mergedNbTriangles)

    ##############################################
    # Empty tesselation
    ##############################################
    if mergedNbNodes == 0 or mergedNbTriangles == 0:
        return None

    ##############################################
    # Merge triangles from faces
    ##############################################
    mergedMesh = _pyoce.Poly.Poly_Triangulation(mergedNbNodes, mergedNbTriangles, False, False)

    topoExp.Init(shape, _pyoce.TopAbs.TopAbs_FACE, _pyoce.TopAbs.TopAbs_VERTEX)

    nodeCounter = 0
    triangleCounter = 0

    while topoExp.More():
        triangulation = _pyoce.BRep.BRep_Tool.Triangulation(
            _pyoce.TopoDS.TopoDSClass.Face(topoExp.Current()),
            location,
            _pyoce.Poly.Poly_MeshPurpose_NONE,
        )

        # TODO why is the triangulation none?
        if triangulation is None:
            break

        aTrsf = location.Transformation()
        for i in range(1, triangulation.NbNodes() + 1, 1):
            aPnt = triangulation.Node(i)
            aPnt.Transform(aTrsf)
            mergedMesh.SetNode(i + nodeCounter, aPnt)
            g4t.addVertex([aPnt.X(), aPnt.Y(), aPnt.Z()])

        orientation = topoExp.Current().Orientation()
        for i in range(1, triangulation.NbTriangles() + 1, 1):
            aTri = triangulation.Triangle(i)
            i1, i2, i3 = aTri.Get()

            i1 += nodeCounter
            i2 += nodeCounter
            i3 += nodeCounter

            if orientation == _pyoce.TopAbs.TopAbs_Orientation.TopAbs_REVERSED:
                aTri.Set(i2, i1, i3)
                g4t.addTriangle([i2 - 1, i1 - 1, i3 - 1])
            else:
                aTri.Set(i1, i2, i3)
                g4t.addTriangle([i1 - 1, i2 - 1, i3 - 1])

            mergedMesh.SetTriangle(i + triangleCounter, aTri)

        nodeCounter += triangulation.NbNodes()
        triangleCounter += triangulation.NbTriangles()

        topoExp.Next()

    g4t.removeDuplicateVertices()

    return g4t


def _oce2Geant4_traverse(
    shapeTool,
    label,
    greg,
    materialMap,
    labelToSkipList,
    meshQualityMap,
    badCADLabels,
    addBoundingSolids=False,
    oceName=False,
):
    name = _pyoce.pythonHelpers.get_TDataStd_Name_From_Label(label)
    node = _pyoce.TCollection.TCollection_AsciiString()
    _pyoce.TDF.TDF_Tool.Entry(label, node)

    if (
        name is None or name in badCADLabels or oceName
    ):  # TODO must be a better way of finding these generic names
        name = node.ToCString()
        name = "l_" + name.replace(":", "_")

    if name.find("-") != -1:
        name = name.replace("-", "_")

    loc = _pyoce.pythonHelpers.get_XCAFDoc_Location_From_Label(label)

    if name in meshQualityMap:
        meshQuality = meshQualityMap[name]
    else:
        meshQuality = (defaultLinDef, deftaulAngDef)

    if name in labelToSkipList:
        print("skipping", name)
        return None
    else:
        pass

    shape = shapeTool.GetShape(label)
    locShape = shape.Location()
    try:
        material = materialMap[name]
    except KeyError:
        material = "G4_Galactic"

    # print("------------------------------")
    # print(name, node.ToCString())
    # print(_oce.pythonHelpers.get_shapeTypeString(shapeTool, label))
    # print(_oce.pythonHelpers.shapeTopology(shape))

    if shapeTool.IsAssembly(label):
        # print("Assembly")

        # make assembly
        try:
            return greg.logicalVolumeDict[name]
        except:
            assembly = oceShape_Geant4_Assembly(name, greg)

        # Loop over children
        for i in range(1, label.NbChildren() + 1, 1):
            b, child = label.FindChild(i, False)
            component = _oce2Geant4_traverse(
                shapeTool,
                child,
                greg,
                materialMap,
                labelToSkipList,
                meshQualityMap,
                badCADLabels,
                addBoundingSolids,
                oceName=oceName,
            )

            # need to do this after to keep recursion clean (TODO consider move with extra parameter)
            if component:
                component.motherVolume = assembly
                assembly.add(component)

        return assembly

    elif shapeTool.IsComponent(label):
        # print("Component")

        rlabel = _pyoce.TDF.TDF_Label()
        shapeTool.GetReferredShape(label, rlabel)

        # Create solid
        logicalVolume = _oce2Geant4_traverse(
            shapeTool,
            rlabel,
            greg,
            materialMap,
            labelToSkipList,
            meshQualityMap,
            badCADLabels,
            addBoundingSolids,
            oceName=oceName,
        )

        if not logicalVolume:
            return

        ax = _pyoce.gp.gp_XYZ()
        an = 0

        trsf = locShape.Transformation()

        scale = trsf.ScaleFactor()
        trans = trsf.TranslationPart()
        b, ax, an = trsf.GetRotation(ax, an)

        trans = _pyoce.pythonHelpers.gp_XYZ_numpy(trans)
        ax = _pyoce.pythonHelpers.gp_XYZ_numpy(ax)
        rot = _transformation.axisangle2tbxyz(ax, -an)

        # make physical volume
        physicalVolume = _g4.PhysicalVolume(rot, trans, logicalVolume, name, None, greg)

        return physicalVolume

    elif shapeTool.IsShape(label):  #  and label.NbChildren() == 0:
        # print("Shape with no children")

        # make solid
        solid = oceShape_Geant4_Tessellated(name, shape, greg, meshQuality[0], meshQuality[1])

        if solid is None:
            return None
        else:
            # make logicalVolume
            logicalVolume = oceShape_Geant4_LogicalVolume(name, solid, material, greg)

            return logicalVolume

    elif shapeTool.IsShape(label) and label.NbChildren() != 0:
        # print("Shape with children", label.NbChildren())

        # make assembly (TODO might require multi union if overlapping)

        try:
            return greg.logicalVolumeDict[name]
        except:
            assembly = oceShape_Geant4_Assembly(name, greg)

        # Loop over children
        for i in range(1, label.NbChildren() + 1, 1):
            b, child = label.FindChild(i, False)
            logicalVolume = _oce2Geant4_traverse(
                shapeTool,
                child,
                greg,
                materialMap,
                labelToSkipList,
                meshQualityMap,
                badCADLabels,
                addBoundingSolids,
            )

            if not logicalVolume:  # logical could be None
                continue

            ax = _pyoce.gp.gp_XYZ()
            an = 0

            childShape = shapeTool.GetShape(child)
            childLoc = childShape.Location()

            trsf = childLoc.Transformation()

            scale = trsf.ScaleFactor()
            trans = trsf.TranslationPart()
            b, ax, an = trsf.GetRotation(ax, an)

            trans = _pyoce.pythonHelpers.gp_XYZ_numpy(trans)
            ax = _pyoce.pythonHelpers.gp_XYZ_numpy(ax)
            rot = _transformation.axisangle2tbxyz(ax, -an)

            physicalVolume = _g4.PhysicalVolume(
                list(rot),
                list(trans),
                logicalVolume,
                logicalVolume.name + "_pv",
                assembly,
                greg,
            )

        return assembly

    else:
        print(name, "missing compound 2")


def oce2Geant4(
    shapeTool, shapeName, materialMap={}, labelToSkipList=[], meshQualityMap={}, oceName=False
):
    """
    Convert CAD geometry starting from shapeName

    :param shapeTool: OpenCascade TopoDS_Shape
    :type shapeTool: pyoce.TopoDS_Shape
    :param shapeName: Name of the shape in the CAD file
    :type shapeName: str
    :param materialMap: dictionary to map shape name to material shapeName:materialName or shapeName:Material
    :type materialMap: dict
    :param meshQualityMap: dictionary to map shape name to meshing quality str:[LinDef,AngDef]
    :type meshQualityMap: dict
    """
    greg = _g4.Registry()

    label = _pyoce.pythonHelpers.findOCCShapeByName(shapeTool, shapeName)
    if label is None:
        fsl = _pyoce.TDF.TDF_LabelSequence()
        shapeTool.GetFreeShapes(fsl)

        freeShapeLabel = fsl.Value(1)
        label = _pyoce.pythonHelpers.findOCCShapeByTreeNode(freeShapeLabel, shapeName)

    # traverse cad and make geant4 geometry
    av = _oce2Geant4_traverse(
        shapeTool,
        label,
        greg,
        materialMap,
        labelToSkipList,
        meshQualityMap,
        badCADLabels=["COMPOUND", "SOLID"],
        oceName=oceName,
    )

    # convert to LV and make world
    av.makeWorldVolume()

    return greg
