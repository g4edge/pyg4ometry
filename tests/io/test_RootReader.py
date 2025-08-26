import pytest
import os as _os

import pyg4ometry as _pyg4ometry

pytestmark = pytest.mark.xfail(run=True, reason="requires PyROOT")


def gdml2ROOT(gdmlFileName, rootFileName):
    import ROOT as _ROOT

    _ROOT.TGeoManager.SetVerboseLevel(0)
    tgm = _ROOT.TGeoManager.Import(_os.path.join(_os.path.dirname(__file__), gdmlFileName))
    tgm.Export(_os.path.join(_os.path.dirname(__file__), rootFileName))


def loadROOTFile(rootFileName):
    r = _pyg4ometry.io.ROOTTGeo.Reader(_os.path.join(_os.path.dirname(__file__), rootFileName))
    return r


def deleteROOTFile(rootFileName):
    _os.remove(_os.path.join(_os.path.dirname(__file__), rootFileName))


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def visGeometry(wl, vis, interactive):
    extentBB = wl.extent(includeBoundingSolid=True)

    if vis:
        v = _pyg4ometry.visualisation.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_pyg4ometry.visualisation.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
        return v


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T001Box(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T001_Box.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T002Tubs(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T002_Tubs.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T003CutTubs(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T003_CutTubs.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T004Cons(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T004_Cons.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T005Para(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T005_Para.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T006Trd(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T006_Trd.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T007Trap(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T007_Trap.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T008Sphere(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T008_Sphere.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T009Orb(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T009_Orb.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T010Torus(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T010_Torus.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T011Polycone(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T011_Polycone.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


# Generic polycone does not exist in ROOT


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T013Polyhedra(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T013_Polyhedra.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


# Generic polyheda does not exist in ROOT


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T015EllipticalTube(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T015_EllipticalTube.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


# Ellipsoid used scaled and boolean
@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T016Ellipsoid(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T016_Ellipsoid.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


# phi range does not exist for ROOT Cons
@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T017EllipticalCone(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T017_EllipticalCone.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T018Paraboloid(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T018_Paraboloid.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T019Hyperboloid(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T019_Hyperboloid.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


# Tet does not exist


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T021ExtrudedSolid(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T021_ExtrudedSolid.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


# Twisted don't exist

# Generic trap does not exist either


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T028Union(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T028_Union.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(r.getRegistry().getWorldVolume(), vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T029Subtraction(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T029_Subtraction.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T030Intersection(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T030_Intersection.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


# Multiunion does not exist
# def test_ROOT_T031MultiUnion(vis = False, interactive = False):
#    gdml2ROOT("T031_MultiUnion.gdml","T031_MultiUnion.root")
#    r = loadROOTFile("T031_MultiUnion.root")
#    l = r.getRegistry().getWorldVolume()
#    v = visGeometry(l, vis, interactive)
#    return {"testStatus": True, "logicalVolume":l, "vtkViewer":v}

# Scaled cannot be read by ROOT?


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T033TessellatedSolid(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T033_TessellatedSolid.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T101PhysicalLogical(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T101_physical_logical.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T102OverlapNone(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T102_overlap_none.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T103OverlapCopl(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T103_overlap_copl.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T900LHT(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/lht.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)


@pytest.mark.parametrize("vis", [False])
@pytest.mark.parametrize("interactive", [False])
def test_ROOT_T901BoxPlacement(testdata, vis, interactive):
    r = loadROOTFile(testdata["root/T001_geant4Box2Fluka.root"])
    l = r.getRegistry().getWorldVolume()
    v = visGeometry(l, vis, interactive)
