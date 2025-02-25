import pyg4ometry as _pyg4
import platform as _platform


def test_VtkViewer(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T104_overlap_volu.gdml"])
    l = r.getRegistry().getWorldVolume()
    l.checkOverlaps()

    v = _pyg4.visualisation.VtkViewer()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())
    v.addAxes(20, (0, 0, 0))

    # individual actors
    v.setOpacity(0, 0)
    v.setWireframe(0)
    v.setSurface(0)
    v.setOpacityOverlap(0, 0)
    v.setOpacityOverlap(-1, 0)
    v.setWireframeOverlap(0)
    v.setWireframeOverlap(-1)

    # set random colours
    v.setRandomColours()

    # cutter settings
    v.setCutterOrigin("x", (0, 0, 0))
    v.setCutterOrigin("y", (0, 0, 0))
    v.setCutterOrigin("z", (0, 0, 0))
    v.setCutterNormal("x", (0, 0, 1))
    v.setCutterNormal("y", (0, 1, 0))
    v.setCutterNormal("z", (1, 0, 0))

    # camera
    v.setCameraFocusPosition([0, 0, 0], [100, 100, 100])

    # export 3d
    v.exportOBJScene(fileName=str(tmptestdir / "test.obj"))
    v.exportVRMLScene(fileName=str(tmptestdir / "temp.vrml"))
    v.exportGLTFScene(fileName=str(tmptestdir / "temp.gltf"))
    v.exportVTPScene(fileName=str(tmptestdir / "temp.vtp"))

    # export screenshots
    # v.exportScreenShot(fileName=str(tmptestdir / "test.bmp"))
    # v.exportScreenShot(fileName=str(tmptestdir / "test.jpg"))
    # v.exportScreenShot(fileName=str(tmptestdir / "test.pnm"))
    # v.exportScreenShot(fileName=str(tmptestdir / "test.ps"))

    # v.view(interactive=False)


def test_VtkViewer_replica(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T106_replica_x.gdml"])
    reg = r.getRegistry()
    v = _pyg4.visualisation.VtkViewer()
    v.addLogicalVolumeRecursive(reg.getWorldVolume())


def test_VtkViewer_division(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/124_division_box_x.gdml"])
    reg = r.getRegistry()
    v = _pyg4.visualisation.VtkViewer()
    v.addLogicalVolumeRecursive(reg.getWorldVolume())


def test_VtkViewer_param(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T111_parameterised_box.gdml"])
    reg = r.getRegistry()
    v = _pyg4.visualisation.VtkViewer()
    v.addLogicalVolumeRecursive(reg.getWorldVolume())


def test_VtkViewer_addSolid(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T001_Box.gdml"])
    reg = r.getRegistry()
    s = reg.solidDict["bs"]
    v = _pyg4.visualisation.VtkViewer()
    v.addSolid(s)


def test_VtkViewer_overlap(testdata, tmptestdir):

    r = _pyg4.gdml.Reader(testdata["gdml/T104_overlap_volu.gdml"])
    reg = r.getRegistry()
    wl = reg.getWorldVolume()
    wl.checkOverlaps(recursive=True)
    v = _pyg4.visualisation.VtkViewer()
    v.addLogicalVolume(wl)


def test_VtkViewer_addBooleanSolidRecursive(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T028_Union.gdml"])
    reg = r.getRegistry()
    u = reg.solidDict["us"]
    v = _pyg4.visualisation.VtkViewer()
    v.addBooleanSolidRecursive(u)


def test_VtkViewerColoured(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T104_overlap_volu.gdml"])
    l = r.getRegistry().getWorldVolume()
    l.checkOverlaps()

    v = _pyg4.visualisation.VtkViewerColoured()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())
    v.addAxes(20, (0, 0, 0))


def test_VtkViewerColoured_setColour(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"])
    reg = r.getRegistry()
    coil = reg.logicalVolumeDict["m3_coil_lv0x7fc499f68a00"]
    coil.setColour("f5ee2f")  # yellow
    yoke = reg.logicalVolumeDict["m6_yoke_lv0x7fc49c0168c0"]
    yoke.setColour(
        [0.9607843137254902, 0.9333333333333333, 0.1843137254901961]
    )  # yellow but rgb normalised

    v = _pyg4.visualisation.VtkViewerColoured()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())


def test_VtkViewerColouredMaterial(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T104_overlap_volu.gdml"])
    l = r.getRegistry().getWorldVolume()
    l.checkOverlaps()

    v = _pyg4.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())
    v.addAxes(20, (0, 0, 0))


def test_VtkViewerNewAppend(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T001_Box.gdml"])
    v = _pyg4.visualisation.VtkViewerNew()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())

    v.addAxes()
    v.addAxesWidget()

    v.addCutter("c1", [0, 0, 0], [0, 0, 1])

    v.buildPipelinesAppend()

    v.setCutter("c1", [0, 0, 0], [0, 0, 1])
    v.exportCutter("c1", tmptestdir / "cutter.vtp")
    v.getCutterPolydata("c1")

    # v.view(interactive=False)
    v.exportGLTFScene(tmptestdir / "test.gltf")


def test_VtkViewerColouredNewAppend(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T001_Box.gdml"])
    v = _pyg4.visualisation.VtkViewerColouredNew()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())

    v.buildPipelinesAppend()


def test_VtkViewerColouredMaterialNewAppend(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/T001_Box.gdml"])
    v = _pyg4.visualisation.VtkViewerColouredNew()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())

    v.buildPipelinesAppend()


def test_UsdViewer(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/ChargeExchangeMC/lht.gdml"])
    reg = r.getRegistry()
    try:
        v = _pyg4.visualisation.UsdViewer(str(tmptestdir / "temp.usd"))
        v.traverseHierarchy(reg.getWorldVolume())
        v.save()
    except:
        pass


def test_RenderWriter(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/ChargeExchangeMC/lht.gdml"])
    reg = r.getRegistry()
    v = _pyg4.visualisation.RenderWriter()
    v.addLogicalVolumeRecursive(reg.getWorldVolume())
    v.write(str(tmptestdir))
