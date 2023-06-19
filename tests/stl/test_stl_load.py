from pyg4ometry import geant4
from pyg4ometry import stl
from pyg4ometry.visualisation import Convert
from pyg4ometry.visualisation import Writer


def LoadStl(fileName):
    reg = geant4.Registry()
    r = stl.Reader(fileName, registry=reg)
    s = r.getSolid()
    return True, s


def test_StlLoad_Dog(testdata):
    LoadStl(testdata["stl/dog.stl"])


def test_StlLoad_Dragon(testdata):
    LoadStl(testdata["stl/dragon.stl"])


def test_StlLoad_Robot(testdata):
    # robot.stl is in binary format
    LoadStl(testdata["stl/robot.stl"])


def test_StlLoad_Teapot(testdata):
    LoadStl(testdata["stl/utah_teapot.stl"])


def test_StlWrite_T001_Box(testdata, tmptestdir, simple_box):
    r = simple_box
    lv = r["logicalVolume"]
    m = lv.daughterVolumes[0].logicalVolume.mesh.localmesh
    pd = Convert.pycsgMeshToVtkPolyData(m)
    Writer.writeVtkPolyDataAsSTLFile(str(tmptestdir / "T001_Box.stl"), [pd])
