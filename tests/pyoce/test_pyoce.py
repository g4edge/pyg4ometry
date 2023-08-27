import pyg4ometry as _pyg4


def commonCode(fileName, mats={}, skip=[], mesh={}):
    r = _pyg4.pyoce.Reader(str(fileName))
    ls = r.freeShapes()
    worldName = _pyg4.pyoce.pythonHelpers.get_TDataStd_Name_From_Label(ls.Value(1))

    # test traversal
    r.traverse(ls.Value(1))

    # python helpers
    _pyg4.pyoce.pythonHelpers.get_TDataStd_Name_From_Label(ls.Value(1))

    # test conversion
    reg = _pyg4.convert.oce2Geant4(r.shapeTool, worldName, mats, skip, mesh)
    wa = reg.logicalVolumeDict[worldName]

    return r


def test_1_BasicSolids_Bodies(testdata):
    commonCode(testdata["step/1_BasicSolids_Bodies.step"])


def test_2_BasicSolids_Components(testdata):
    commonCode(testdata["step/2_BasicSolids_Components.step"])


def test_3_BasicSolids_Components_Copied(testdata):
    commonCode(testdata["step/3_BasicSolids_Components_Copied.step"])


def test_4_BasicSolids_Components_ManyBodies(testdata):
    commonCode(testdata["step/4_BasicSolids_Components_ManyBodies.step"])


def test_5_BasicSolids_Components_NestedComponents(testdata):
    commonCode(testdata["step/5_BasicSolids_Components_NestedComponents.step"])


def test_6_SolidFromSketch(testdata):
    commonCode(testdata["step/6_SolidFromSketch.step"])


def test_7_Booleans(testdata):
    commonCode(testdata["step/7_Booleans.step"])


def test_8_rotationTest(testdata):
    commonCode(testdata["step/8_rotationTest.step"])


def test_9_AshTray(testdata):
    commonCode(testdata["step/9_AshTray.step"])


def test_10_SectorBendSmall(testdata):
    commonCode(testdata["step/10_SectorBendSmall.step"])


def test_11_Material(testdata):
    mats = {"0:1:1:1:1": "G4_H", "0:1:1:1:4": "G4_He"}
    commonCode(testdata["step/10_SectorBendSmall.step"], mats=mats)


def test_12_Skip(testdata):
    skip = ["0:1:1:1:4"]
    commonCode(testdata["step/10_SectorBendSmall.step"], skip=skip)


def test_13_Mesh(testdata):
    mesh = {"0:1:1:1:2": (0.05, 0.05)}
    commonCode(testdata["step/10_SectorBendSmall.step"], mesh=mesh)


def test_14_MonolithicConversion(testdata):
    r = _pyg4.pyoce.Reader(str(testdata["step/1_BasicSolids_Bodies.step"]))
    ls = r.freeShapes()
    worldName = _pyg4.pyoce.pythonHelpers.get_TDataStd_Name_From_Label(ls.Value(1))
    worldShape = r.shapeTool.GetShape(ls.Value(1))
    greg = _pyg4.geant4.Registry()
    _pyg4.convert.oceShape_Geant4_Tessellated("world", worldShape, greg)


def test_15_xcaf(testdata):
    # create application
    app = _pyg4.pyoce.XCAFApp.XCAFApp_Application.GetApplication()

    # create new document
    doc = app.NewDocument(_pyg4.pyoce.TCollection.TCollection_ExtendedString("MDTV-CAF"))

    # top label
    top_label = doc.Main()

    # shape tool
    shape_tool = _pyg4.pyoce.XCAFDoc.XCAFDoc_DocumentTool.ShapeTool(top_label)

    # add some childen
    child1_label = _pyg4.pyoce.TDF.TDF_TagSource.NewChild(top_label)
    child2_label = _pyg4.pyoce.TDF.TDF_TagSource.NewChild(top_label)

    # w = _pyg4.pyoce.STEPCAFControl.STEPCAFControl_Writer()
    # w.Transfer(doc)
    # w.WriteFile("output.step")


def test_16_CurveAndSurface_Extraction(testdata):
    from pyg4ometry.pyoce.TopAbs import TopAbs_ShapeEnum
    from pyg4ometry.pyoce.TopExp import TopExp_Explorer
    from pyg4ometry.pyoce.BRep import BRep_Tool
    from pyg4ometry.pyoce.TopLoc import TopLoc_Location
    from pyg4ometry.pyoce.TopoDS import TopoDSClass
    from pyg4ometry.pyoce.Poly import Poly_MeshPurpose

    if type(testdata) is not str:
        r = commonCode(testdata["step/1_BasicSolids_Bodies.step"])
    else:
        r = commonCode(testdata)
    # root label
    freeShapeLabels = r.freeShapes()

    # recursive shape decent
    def extractSurfacesAndCurvesFromShape(shape):
        print(shape.ShapeType())

        # set up explorer
        e = None
        if shape.ShapeType() == TopAbs_ShapeEnum.TopAbs_COMPOUND:
            e = TopExp_Explorer(
                shape,
                TopAbs_ShapeEnum.TopAbs_SOLID,
                TopAbs_ShapeEnum.TopAbs_FACE,
            )
        elif shape.ShapeType() == TopAbs_ShapeEnum.TopAbs_SOLID:
            e = TopExp_Explorer(
                shape,
                TopAbs_ShapeEnum.TopAbs_FACE,
                TopAbs_ShapeEnum.TopAbs_VERTEX,
            )
        elif shape.ShapeType() == TopAbs_ShapeEnum.TopAbs_FACE:
            e = TopExp_Explorer(
                shape,
                TopAbs_ShapeEnum.TopAbs_WIRE,
                TopAbs_ShapeEnum.TopAbs_VERTEX,
            )
            location = TopLoc_Location()
            face = TopoDSClass.Face(shape)
            surface = BRep_Tool.Surface(face, location)
            mesh = BRep_Tool.Triangulation(face, location, Poly_MeshPurpose.Poly_MeshPurpose_NONE)
            print(surface, location, mesh)
        elif shape.ShapeType() == TopAbs_ShapeEnum.TopAbs_WIRE:
            e = TopExp_Explorer(
                shape,
                TopAbs_ShapeEnum.TopAbs_EDGE,
                TopAbs_ShapeEnum.TopAbs_VERTEX,
            )
        elif shape.ShapeType() == TopAbs_ShapeEnum.TopAbs_EDGE:
            e = TopExp_Explorer(
                shape,
                TopAbs_ShapeEnum.TopAbs_VERTEX,
                TopAbs_ShapeEnum.TopAbs_FACE,
            )
        if e is None:
            return

        # loop over shapes
        while e.More():
            currentShape = e.Current()
            extractSurfacesAndCurvesFromShape(currentShape)
            e.Next()

    # loop over free shapes
    for freeShapeLabel in freeShapeLabels:
        shape = r.shapeTool.GetShape(freeShapeLabel)

        print(freeShapeLabel, shape, shape.ShapeType())
        extractSurfacesAndCurvesFromShape(shape)
