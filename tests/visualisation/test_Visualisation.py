import pyg4ometry as _pyg4
import platform as _platform
import pytest


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


def _usd_meshes(path):
    """Every mesh on a stage, with its face count and its points in world coordinates."""
    from pxr import Usd, UsdGeom
    import numpy as np

    stage = Usd.Stage.Open(str(path))
    cache = UsdGeom.XformCache()
    meshes = []
    for prim in stage.Traverse(Usd.TraverseInstanceProxies()):
        if not prim.IsA(UsdGeom.Mesh):
            continue
        mesh = UsdGeom.Mesh(prim)
        points = np.array(mesh.GetPointsAttr().Get())
        xform = np.array(cache.GetLocalToWorldTransform(prim))
        meshes.append(
            (
                mesh,
                len(mesh.GetFaceVertexCountsAttr().Get()),
                points @ xform[:3, :3] + xform[3, :3],
            )
        )
    return stage, meshes


def test_UsdViewer_stage(testdata, tmptestdir):
    """The stage says what units it is in, which way is up, and what to place."""
    pytest.importorskip("pxr")

    from pxr import Usd, UsdGeom

    r = _pyg4.gdml.Reader(testdata["gdml/001_box.gdml"])
    out = tmptestdir / "stage.usd"
    v = _pyg4.visualisation.UsdViewer(str(out))
    v.traverseHierarchy(r.getRegistry().getWorldVolume())
    v.save()

    stage, meshes = _usd_meshes(out)
    assert UsdGeom.GetStageMetersPerUnit(stage) == 1
    assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z
    assert stage.GetDefaultPrim()
    # a usdz package needs exactly one root, so the materials live below the geometry
    assert len(stage.GetPseudoRoot().GetChildren()) == 1
    assert meshes
    for mesh, _, _ in meshes:
        # a solid is a polyhedron, not the cage of a smooth surface
        assert mesh.GetSubdivisionSchemeAttr().Get() == "none"


def test_UsdViewer_usdz(testdata, tmptestdir):
    """A .usdz suffix writes a package, and leaves no loose layer behind."""
    pytest.importorskip("pxr")

    import zipfile

    r = _pyg4.gdml.Reader(testdata["gdml/001_box.gdml"])
    out = tmptestdir / "package.usdz"
    v = _pyg4.visualisation.UsdViewer(str(out))
    v.traverseHierarchy(r.getRegistry().getWorldVolume())
    v.save()

    assert out.exists()
    assert not out.with_suffix(".usdc").exists()
    assert zipfile.is_zipfile(out)
    with zipfile.ZipFile(out) as z:
        assert z.infolist()[0].filename.endswith((".usdc", ".usda", ".usd"))


def test_UsdViewer_mergeByMaterial(testdata, tmptestdir):
    """Merging gives fewer meshes holding the same triangles in the same places."""
    pytest.importorskip("pxr")

    import numpy as np

    r = _pyg4.gdml.Reader(testdata["gdml/ChargeExchangeMC/lht.gdml"])

    outputs = {}
    for merge in (False, True):
        out = tmptestdir / f"merge_{merge}.usd"
        v = _pyg4.visualisation.UsdViewer(str(out), mergeByMaterial=merge)
        v.traverseHierarchy(r.getRegistry().getWorldVolume())
        v.save()
        _, meshes = _usd_meshes(out)
        outputs[merge] = (
            len(meshes),
            sum(n for _, n, _ in meshes),
            np.concatenate([p for _, _, p in meshes]),
        )

    plain, merged = outputs[False], outputs[True]
    assert merged[0] < plain[0], "merging should leave fewer meshes"
    assert merged[1] == plain[1], "merging should keep every face"
    assert np.allclose(merged[2].min(0), plain[2].min(0))
    assert np.allclose(merged[2].max(0), plain[2].max(0))


def test_RenderWriter(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/ChargeExchangeMC/lht.gdml"])
    reg = r.getRegistry()
    v = _pyg4.visualisation.RenderWriter()
    v.addLogicalVolumeRecursive(reg.getWorldVolume())
    v.write(str(tmptestdir))
