from .. import geant4 as _g4
from .. import pyoce as _pyoce
from .. import transformation as _transformation
from .ocePrimitiveRecognition import (
    recognise_box_from_shape_vertices as _recognise_box_from_shape_vertices,
)

import numpy as _np

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


def oceShape_Geant4_Tessellated(
    name,
    shape,
    greg,
    linDef=0.01,
    angDef=0.01,
    nativePrimitives=False,
    nativePlacementAvailable=False,
):
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
    # Check if shape is solid
    ##############################################
    shapeTopo = _pyoce.pythonHelpers.shapeTopology(shape)
    if shapeTopo["nSolid"] == 0:
        return None

    ##############################################
    # G4 tessellated solid
    ##############################################
    g4t = _g4.solid.TessellatedSolid(name, None, greg, addRegistry=False)

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
            topoExp.Next()
            continue

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
            topoExp.Next()
            continue

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

    if nativePrimitives:
        primitive = _recognise_box_from_shape_vertices(
            name,
            shape,
            g4t.meshtess[0],
        )

        if primitive is not None:
            local_basis = _np.column_stack(primitive["local_axes"])
            local_centre = _np.asarray(primitive["centre"], dtype=float)

            correction_is_identity = _np.allclose(
                local_basis,
                _np.eye(3),
                atol=1e-12,
                rtol=0.0,
            ) and _np.allclose(
                local_centre,
                _np.zeros(3),
                atol=1e-12,
                rtol=0.0,
            )

            if correction_is_identity or nativePlacementAvailable:
                native = _g4.solid.Box(
                    name,
                    primitive["dimensions"][0],
                    primitive["dimensions"][1],
                    primitive["dimensions"][2],
                    greg,
                    lunit="mm",
                )
                native._oceNativeLocalBasis = local_basis
                native._oceNativeLocalCentre = local_centre
                return native

    greg.addSolid(g4t)
    return g4t


def _apply_native_local_transform(rot, trans, volume):
    local_basis = getattr(volume, "_oceNativeLocalBasis", None)
    local_centre = getattr(volume, "_oceNativeLocalCentre", None)

    if local_basis is None or local_centre is None:
        return rot, trans

    old_rotation = _transformation.tbxyz2matrix(rot)
    new_rotation = _np.asarray(local_basis, dtype=float).T @ old_rotation
    new_translation = old_rotation.T @ _np.asarray(local_centre, dtype=float) + _np.asarray(
        trans, dtype=float
    )

    if not _np.allclose(
        new_rotation.T @ new_rotation,
        _np.eye(3),
        atol=1e-10,
        rtol=0.0,
    ):
        message = "Composed native CAD rotation is not orthonormal."
        raise RuntimeError(message)

    if not _np.isclose(
        _np.linalg.det(new_rotation),
        1.0,
        atol=1e-10,
        rtol=0.0,
    ):
        message = "Composed native CAD rotation is not proper (det != +1)."
        raise RuntimeError(message)

    return (
        _transformation.matrix2tbxyz(new_rotation),
        new_translation,
    )


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
    nativePrimitives=False,
    nativePlacementAvailable=False,
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

    shapeTopo = _pyoce.pythonHelpers.shapeTopology(shape)
    if shapeTopo["nSolid"] > 0:
        print("------------------------------")
        print(
            '"' + name + '"',
            '"' + node.ToCString() + '"',
            '"' + _pyoce.pythonHelpers.get_shapeTypeString(shapeTool, label).strip() + '"',
        )
        print(shapeTopo)

    if shapeTool.IsAssembly(label):
        # print("_oce2Geant4_traverse: Assembly")

        # make assembly
        try:
            return greg.logicalVolumeDict[name]
        except:
            assembly = oceShape_Geant4_Assembly(name, greg)

        # Loop over children
        for i in range(1, label.NbChildren() + 1, 1):
            _b, child = label.FindChild(i, False)
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
                nativePrimitives=nativePrimitives,
                nativePlacementAvailable=False,
            )

            # need to do this after to keep recursion clean (TODO consider move with extra parameter)
            if component:
                component.motherVolume = assembly
                assembly.add(component)

        return assembly

    elif shapeTool.IsComponent(label):
        # print("_oce2Geant4_traverse: Component")

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
            nativePrimitives=nativePrimitives,
            nativePlacementAvailable=True,
        )

        if not logicalVolume:
            return

        ax = _pyoce.gp.gp_XYZ()
        an = 0

        trsf = locShape.Transformation()

        scale = trsf.ScaleFactor()
        trans = trsf.TranslationPart()
        _b, ax, an = trsf.GetRotation(ax, an)

        trans = _pyoce.pythonHelpers.gp_XYZ_numpy(trans)
        ax = _pyoce.pythonHelpers.gp_XYZ_numpy(ax)
        rot = _transformation.axisangle2tbxyz(ax, -an)

        # make physical volume
        rot, trans = _apply_native_local_transform(rot, trans, logicalVolume)
        physicalVolume = _g4.PhysicalVolume(rot, trans, logicalVolume, name, None, greg)

        return physicalVolume

    elif shapeTool.IsShape(label) and label.NbChildren() == 0:
        # print("_oce2Geant4_traverse: Shape with no children")

        # make solid
        solid = oceShape_Geant4_Tessellated(
            name,
            shape,
            greg,
            meshQuality[0],
            meshQuality[1],
            nativePrimitives=nativePrimitives,
            nativePlacementAvailable=nativePlacementAvailable,
        )

        if solid is None:
            return None
        else:
            # make logicalVolume
            logicalVolume = oceShape_Geant4_LogicalVolume(name, solid, material, greg)
            if hasattr(solid, "_oceNativeLocalBasis"):
                logicalVolume._oceNativeLocalBasis = solid._oceNativeLocalBasis
                logicalVolume._oceNativeLocalCentre = solid._oceNativeLocalCentre

            return logicalVolume

    elif shapeTool.IsShape(label) and label.NbChildren() != 0:
        # print("_oce2Geant4_traverse: Shape with children", label.NbChildren())

        # make assembly (TODO might require multi union if overlapping)

        try:
            return greg.logicalVolumeDict[name]
        except:
            assembly = oceShape_Geant4_Assembly(name, greg)

        # Loop over children
        for i in range(1, label.NbChildren() + 1, 1):
            _b, child = label.FindChild(i, False)
            logicalVolume = _oce2Geant4_traverse(
                shapeTool,
                child,
                greg,
                materialMap,
                labelToSkipList,
                meshQualityMap,
                badCADLabels,
                addBoundingSolids,
                nativePrimitives=nativePrimitives,
                nativePlacementAvailable=True,
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
            _b, ax, an = trsf.GetRotation(ax, an)

            trans = _pyoce.pythonHelpers.gp_XYZ_numpy(trans)
            ax = _pyoce.pythonHelpers.gp_XYZ_numpy(ax)
            rot = _transformation.axisangle2tbxyz(ax, -an)

            rot, trans = _apply_native_local_transform(rot, trans, logicalVolume)
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
    shapeTool,
    shapeName,
    materialMap={},
    labelToSkipList=[],
    meshQualityMap={},
    oceName=False,
    nativePrimitives=False,
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
    :param nativePrimitives: conservatively replace supported CAD solids with native Geant4 solids
    :type nativePrimitives: bool
    """
    greg = _g4.Registry()

    label = _pyoce.pythonHelpers.findOCCShapeByName(shapeTool, shapeName)
    if label is None:
        print("oce2Geant4: label not found using tree node")

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
        nativePrimitives=nativePrimitives,
        nativePlacementAvailable=False,
    )

    # convert to LV and make world
    av.makeWorldVolume()

    return greg
