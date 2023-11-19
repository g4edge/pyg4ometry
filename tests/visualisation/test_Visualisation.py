import pyg4ometry as _pyg4


def test_VtkViewer(testdata):
    r = _pyg4.gdml.Reader(testdata["gdml/001_box.gdml"])
    v = _pyg4.visualisation.VtkViewer()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())
    v.view(interactive=False)


def test_VtkViewerNew(testdata, tmptestdir):
    r = _pyg4.gdml.Reader(testdata["gdml/001_box.gdml"])
    v = _pyg4.visualisation.VtkViewerNew()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())

    v.addAxes()
    v.addAxesWidget()

    v.addCutter("c1", [0, 0, 0], [0, 0, 1])

    v.buildPipelinesAppend()

    v.setCutter("c1", [0, 0, 0], [0, 0, 1])
    v.exportCutter("c1", tmptestdir / "cutter.vtp")
    v.getCutterPolydata("c1")

    v.view(interactive=False)
    v.exportGLTFScene(tmptestdir / "test.gltf")
