import pytest

from . import T001_geant4Box2Fluka
from . import T002_geant4Tubs2Fluka
from . import T003_geant4CutTubs2Fluka
from . import T004_geant4Cons2Fluka
from . import T005_geant4Para2Fluka
from . import T006_geant4Trd2Fluka
from . import T007_geant4Trap2Fluka
from . import T008_geant4Sphere2Fluka
from . import T009_geant4Orb2Fluka
from . import T010_geant4Torus2Fluka
from . import T011_geant4Polycone2Fluka
from . import T012_geant4GenericPolycone2Fluka
from . import T013_geant4Polyhedra2Fluka
from . import T014_geant4GenericPolyhedra2Fluka
from . import T015_geant4EllipticalTube2Fluka
from . import T016_geant4Ellipsoid2Fluka
from . import T017_geant4EllipticalCone2Fluka
from . import T018_geant4Paraboloid2Fluka
from . import T019_geant4Hyperboloid2Fluka
from . import T020_geant4Tet2Fluka
from . import T021_geant4ExtrudedSolid2Fluka
from . import T026_geant4GenericTrap2Fluka

from . import T028_geant4Union2Fluka
from . import T029_geant4Subtraction2Fluka
from . import T030_geant4Intersection2Fluka

from . import T105_geant4Assembly2Fluka
from . import T106_geant4ReplicaX2Fluka
from . import T107_geant4ReplicaY2Fluka
from . import T108_geant4ReplicaZ2Fluka
from . import T109_geant4ReplicaPhi2Fluka
from . import T110_geant4ReplicaRho2Fluka


def test_Geant42FlukaConversion_T001_Box(tmptestdir):
    T001_geant4Box2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T002_Tubs(tmptestdir):
    T002_geant4Tubs2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T003_CutTubs(tmptestdir):
    T003_geant4CutTubs2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T004_Cons(tmptestdir):
    T004_geant4Cons2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T005_Para(tmptestdir):
    T005_geant4Para2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T006_Tdr(tmptestdir):
    T006_geant4Trd2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T007_Trap(tmptestdir):
    T007_geant4Trap2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T008_Sphere(tmptestdir):
    T008_geant4Sphere2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T009_Orb(tmptestdir):
    T009_geant4Orb2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T010_Torus(tmptestdir):
    T010_geant4Torus2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T011_Polycone(tmptestdir):
    T011_geant4Polycone2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T012_GenericPolycone(tmptestdir):
    T012_geant4GenericPolycone2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T013_Polyhedra(tmptestdir):
    T013_geant4Polyhedra2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T014_GenericPolyhedra(tmptestdir):
    T014_geant4GenericPolyhedra2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T015_EllipticalTube(tmptestdir):
    T015_geant4EllipticalTube2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T016_Ellipsoid(tmptestdir):
    T016_geant4Ellipsoid2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T017_EllipticalCone(tmptestdir):
    T017_geant4EllipticalCone2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T018_Paraboloid(tmptestdir):
    T018_geant4Paraboloid2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T019_Hyperboloid(tmptestdir):
    T019_geant4Hyperboloid2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T020_Tet(tmptestdir):
    T020_geant4Tet2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T021_ExtrudedSolid(tmptestdir):
    T021_geant4ExtrudedSolid2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


#    def test_Geant42FlukaConversion_T026_GenericTrap(tmptestdir):
#        T026_geant4GenericTrap2Fluka.Test(False,False,True)


def test_Geant42FlukaConversion_T028_Union(tmptestdir):
    T028_geant4Union2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T029_Subtraction(tmptestdir):
    T029_geant4Subtraction2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T030_Intersection(tmptestdir):
    T030_geant4Intersection2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T105_Assembly(tmptestdir):
    T105_geant4Assembly2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T106_replica_x(tmptestdir):
    T106_geant4ReplicaX2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T107_replica_y(tmptestdir):
    T107_geant4ReplicaY2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T108_replica_z(tmptestdir):
    T108_geant4ReplicaZ2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T109_replica_phi(tmptestdir):
    T109_geant4ReplicaPhi2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)


def test_Geant42FlukaConversion_T110_replica_rho(tmptestdir):
    T110_geant4ReplicaRho2Fluka.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)
