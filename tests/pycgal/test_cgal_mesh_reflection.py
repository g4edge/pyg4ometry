import pyg4ometry.pycgal as _cgal


def test_cgal_box_reflection():
    c = _cgal.CSG.cube([1, 1, 1], [1, 1, 1])

    assert _cgal.CGAL.is_outward_oriented(c.sm)

    c.scale([-1, -1, -1])

    assert not _cgal.CGAL.is_outward_oriented(c.sm)

    _cgal.CGAL.reverse_face_orientations(c.sm)

    assert _cgal.CGAL.is_outward_oriented(c.sm)
