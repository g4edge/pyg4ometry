import pytest
import pyg4ometry
import pyg4ometry.geant4 as _g4


@pytest.mark.parametrize("printOut", [False])
def test(printOut):
    r = _g4.Registry()

    tests = pyg4ometry.compare.Tests()

    box1 = _g4.solid.Box("box1", 100, 80, 60, r)

    # solid with itself
    comp1 = pyg4ometry.compare.solids(box1, box1, tests)
    if printOut:
        comp1.print()
    assert len(comp1) == 0

    wx = pyg4ometry.gdml.Constant("wx", 10, r)
    box2 = _g4.solid.Box("box2", "1*wx", 0.8 * wx, 0.6 * wx, r, lunit="cm")

    # solid with itself - using expressions
    comp2 = pyg4ometry.compare.solids(box2, box2, tests)
    if printOut:
        comp2.print()
    assert len(comp2) == 0

    # box with numbers vs box with expressions but equivalent
    # only name should be different
    comp3 = pyg4ometry.compare.solids(box1, box2, tests)
    if printOut:
        comp3.print()
    assert len(comp3) == 2  # 2 name tests

    testsNoName = pyg4ometry.compare.Tests()
    testsNoName.names = False
    comp4 = pyg4ometry.compare.solids(
        box1, box2, testsNoName, "maintest", includeAllTestResults=True
    )
    if printOut:
        comp4.print()
    assert len(comp4) > 0  # because we include all tests

    # test a solid where a parameter is potentially a list or not just a number
    p1x = pyg4ometry.gdml.Constant("p1x", "-20", r, True)
    p1y = pyg4ometry.gdml.Constant("p1y", "-20", r, True)
    z1, x1, y1, s1 = -20, 5, 5, 1
    z2, x2, y2, s2 = 0, -5, -5, 1
    z3, x3, y3, s3 = 20, 0, 0, 2
    polygon = [
        [p1x, p1y],
        [-20, 20],
        [20, 20],
        [20, 10],
        [-10, 10],
        [-10, 10],
        [20, -10],
        [20, -20],
    ]
    slices = [[z1, [x1, y1], s1], [z2, [x2, y2], s2], [z3, [x3, y3], s3]]
    xs = _g4.solid.ExtrudedSolid("xs", polygon, slices, r)

    # complex solid with other with simple values
    comp5 = pyg4ometry.compare.solids(box1, xs, tests)
    if printOut:
        comp5.print()
    assert len(comp5) > 0

    comp6 = pyg4ometry.compare.solids(xs, xs, tests)
    if printOut:
        comp6.print()
    assert len(comp6) == 0

    # one number deep inside that's slightly different
    polygon2 = [
        [p1x, p1y],
        [-20, 20],
        [30, 20],
        [20, 10],
        [-10, 10],
        [-10, 10],
        [20, -10],
        [20, -20],
    ]
    slices2 = [[z1, [6, y1], s1], [z2, [x2, y2], s2], [z3, [x3, y3], s3]]
    xs2 = _g4.solid.ExtrudedSolid("xs2", polygon2, slices2, r)
    comp7 = pyg4ometry.compare.solids(xs, xs2, tests)
    if printOut:
        comp7.print()
    assert len(comp7) > 0

    # different units
    polygon3 = [[-2, -2], [-2, 2], [2, 2], [2, 1], [-1, 1], [-1, 1], [2, -1], [2, -2]]
    slices3 = [[-2, [0.5, 0.5], 1], [0, [-0.5, -0.5], 1], [2, [0, 0], 2]]
    xs3 = _g4.solid.ExtrudedSolid("xs3", polygon3, slices3, r, lunit="cm")
    comp8 = pyg4ometry.compare.solids(xs, xs3, tests)
    if printOut:
        comp8.print()
    assert len(comp8) == 2  # 2 name tests

    # return {"teststatus": True}


if __name__ == "__main__":
    test()
