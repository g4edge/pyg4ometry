import numpy as np
import pytest

from pyg4ometry import convert, fluka, geant4


def _meshExtent(solid):
    verts = np.array(solid.mesh().toVerticesAndPolygons()[0])
    return verts.min(axis=0), verts.max(axis=0)


@pytest.mark.parametrize(
    ("bodyClass", "semiAxes", "transverse"),
    [
        (fluka.XEC, (10, 5), (1, 2)),  # (y, z) semi-axes
        (fluka.YEC, (10, 5), (2, 0)),  # (z, x) semi-axes
        (fluka.ZEC, (10, 5), (0, 1)),  # (x, y) semi-axes
    ],
)
def test_infinite_elliptical_cylinder_geant4_size(bodyClass, semiAxes, transverse):
    # The Geant4 EllipticalTube takes semi-axes, so the converted solid must match the
    # FLUKA semi-axes and not twice them. The solid is meshed in its local frame where the
    # cylinder axis is z, so the rotation of each body is applied to the extent here.
    freg = fluka.FlukaRegistry()
    body = bodyClass("EC", 0, 0, *semiAxes, flukaregistry=freg)
    solid = body.geant4Solid(geant4.Registry())
    _, hi = _meshExtent(solid)
    rot = body.rotation()
    globalHi = np.abs(rot @ hi)
    assert globalHi[transverse[0]] == pytest.approx(semiAxes[0])
    assert globalHi[transverse[1]] == pytest.approx(semiAxes[1])


def test_rec_geant4_size():
    # REC with semi-axes 10 and 5 along x and y and a height of 20 along z.
    freg = fluka.FlukaRegistry()
    body = fluka.REC("R", [0, 0, 0], [0, 0, 20], [10, 0, 0], [0, 5, 0], flukaregistry=freg)
    lo, hi = _meshExtent(body.geant4Solid(geant4.Registry()))
    assert hi == pytest.approx([10, 5, 10])
    assert lo == pytest.approx([-10, -5, -10])
    assert list(body.centre()) == pytest.approx([0, 0, 10])


def test_rec_region_geant4_extent():
    # Full conversion of a REC region including placement, so the solid should span the
    # face to the face plus the direction vector.
    freg = fluka.FlukaRegistry()
    body = fluka.REC("R", [0, 0, 0], [0, 0, 20], [10, 0, 0], [0, 5, 0], flukaregistry=freg)
    zone = fluka.Zone()
    zone.addIntersection(body)
    region = fluka.Region("REG")
    region.addZone(zone)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)
    lo, hi = greg.getWorldVolume().extent()
    # Tolerance allows for the length safety applied in the conversion.
    assert lo == pytest.approx([-10, -5, 0], abs=1e-5)
    assert hi == pytest.approx([10, 5, 20], abs=1e-5)


def test_geant4_elliptical_tube_to_fluka_rec():
    # Geant4 EllipticalTube semi-axes 10, 25 mm and half-length 20 mm should give a REC
    # with semi-axes of 1 and 2.5 cm and a height of 4 cm, centred on the origin.
    reg = geant4.Registry()
    solid = geant4.solid.EllipticalTube("es", 10, 25, 20, reg)
    freg = fluka.FlukaRegistry()
    fregion, _ = convert.geant42Fluka.geant4EllipticalTube2Fluka(0, solid, flukaRegistry=freg)
    rec = next(iter(fregion.zones[0].intersections)).body

    assert rec.semiminor.length() == pytest.approx(1)
    assert rec.semimajor.length() == pytest.approx(2.5)
    assert rec.direction.length() == pytest.approx(4)
    assert list(rec.centre()) == pytest.approx([0, 0, 0])
