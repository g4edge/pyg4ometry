import pyg4ometry
import pyg4ometry.geant4 as _g4


def Test(printOut=False):
    # make 2 copies independently so we can have degenerate names, which we couldn't
    # have in just 1 registry
    r1 = _g4.Registry()
    r2 = _g4.Registry()

    tests = pyg4ometry.compare.Tests()

    galactic1 = _g4.MaterialPredefined("G4_Galactic", r1)
    copper1 = _g4.MaterialPredefined("G4_Cu", r1)
    galactic2 = _g4.MaterialPredefined("G4_Galactic", r1)
    copper2 = _g4.MaterialPredefined("G4_Cu", r2)

    # ctdeltaphi = pyg4ometry.gdml.Constant("deltaphi","2*pi",r1)
    ts1 = _g4.solid.Tubs("ts", 0, 50, 100, 0, "2*pi", r1)
    tl1 = _g4.LogicalVolume(ts1, copper1, "tl1_lv", r1)
    ts2 = _g4.solid.Tubs("ts", 0, 50, 100, 0, "2*pi", r2)
    tl2 = _g4.LogicalVolume(ts2, copper2, "tl1_lv", r2)
    tl2b = _g4.LogicalVolume(ts2, galactic2, "tl1b_lv", r2)

    # same lvs
    comp1 = pyg4ometry.compare.logicalVolumes(tl1, tl1, tests)
    if printOut:
        comp1.print()
    assert len(comp1) == 0

    # same lvs, different registry
    comp2 = pyg4ometry.compare.logicalVolumes(tl1, tl2, tests)
    if printOut:
        comp2.print()
    assert len(comp2) == 0

    # different material
    comp3 = pyg4ometry.compare.logicalVolumes(tl1, tl2b, tests)
    if printOut:
        comp3.print()
    assert len(comp3) > 0

    miniBox1 = _g4.solid.Box("mb1", 1, 2, 3, r1)
    miniBox1LV = _g4.LogicalVolume(miniBox1, galactic1, "mb1_lv", r1)
    miniBox2 = _g4.solid.Box("mb2", 1, 2, 3, r1)
    miniBox2LV = _g4.LogicalVolume(miniBox1, galactic1, "mb2_lv", r1)
    miniBox3 = _g4.solid.Box("mb3", 3, 2, 1, r1)
    miniBox3LV = _g4.LogicalVolume(miniBox1, galactic1, "mb3_lv", r1)
    miniBox1PV1 = _g4.PhysicalVolume([0, 0.1, 0], [-1, 0, -10], miniBox1LV, "mb1_pv1", tl1, r1)
    miniBox1PV2 = _g4.PhysicalVolume([0, -0.1, 0], [5, 0, 10], miniBox1LV, "mb1_pv2", tl1, r1)
    miniBox1PV3 = _g4.PhysicalVolume(
        [0.1, -0.1, 3.14159265],
        [-5, 0, 30],
        miniBox1LV,
        "mb1_pv3",
        tl1,
        r1,
        copyNumber=3,
        scale=[1, 1, -1],
    )

    # same daughters
    comp4 = pyg4ometry.compare.logicalVolumes(
        tl1, tl1, tests, recursive=True
    )  # recursive = check daughter placements
    if printOut:
        comp4.print()
    assert len(comp4) == 0

    # make it all again in reg2 (adding "pointer" to end of lv and pv names)
    miniBox12 = _g4.solid.Box("mb1", 1, 2, 3, r2)
    miniBox12LV = _g4.LogicalVolume(miniBox12, galactic2, "mb1_lv0x1234567", r2)
    miniBox22 = _g4.solid.Box("mb2", 1, 2, 3, r2)
    miniBox22LV = _g4.LogicalVolume(miniBox12, galactic2, "mb2_lv0x1234567", r2)
    miniBox32 = _g4.solid.Box("mb3", 3, 2, 1, r2)
    miniBox32LV = _g4.LogicalVolume(miniBox12, galactic2, "mb3_lv0x1234567", r2)
    miniBox12PV1 = _g4.PhysicalVolume(
        [0, 0.1, 0], [-1, 0, -10], miniBox12LV, "mb1_pv10x1234567", tl2, r2
    )
    miniBox12PV2 = _g4.PhysicalVolume(
        [0, -0.1, 0], [5, 0, 10], miniBox12LV, "mb1_pv20x1234567", tl2, r2
    )
    miniBox12PV3 = _g4.PhysicalVolume(
        [0.1, -0.1, -3.14159265],
        [-5, 0, 30],
        miniBox12LV,
        "mb1_pv30x1234567",
        tl2,
        r2,
        copyNumber=3,
        scale=[1, 1, -1],
    )
    # NOTE rotation of -pi vs pi in miniBox1PV3 - it is equivalent so should not result in an error

    # same daughters
    tests.names = False  # disable exact name matching
    comp5 = pyg4ometry.compare.logicalVolumes(tl1, tl2, tests, recursive=True)
    if printOut:
        comp5.print()
    assert len(comp5) == 0

    # extra placement in 2nd one now
    miniBox12PV4 = _g4.PhysicalVolume([0, 0, 0], [-5, 0, 40], miniBox12LV, "mb1_pv4", tl2, r2)
    comp6 = pyg4ometry.compare.logicalVolumes(tl1, tl2, tests, recursive=True)
    if printOut:
        comp6.print()
    assert len(comp6) > 0

    # different copyNumber
    miniBox1PV5 = _g4.PhysicalVolume(
        [0, 0, 0], [0, 10, 40], miniBox1LV, "mb1_pv5", tl1, r1, copyNumber=2
    )
    miniBox12PV5 = _g4.PhysicalVolume(
        [0, 0, 0], [0, 10, 40], miniBox12LV, "mb1_pv5", tl2, r2, copyNumber=3
    )
    comp7 = pyg4ometry.compare.logicalVolumes(tl1, tl2, tests, recursive=True)
    if printOut:
        comp7.print()
    assert len(comp7.test["copyNumber"]) > 0

    # different scale
    miniBox1PV6 = _g4.PhysicalVolume(
        [0, 0, 0], [0, -10, 40], miniBox1LV, "mb1_pv6", tl1, r1, scale=[1, 1, 1]
    )
    miniBox12PV6 = _g4.PhysicalVolume(
        [0, 0, 0], [0, -10, 40], miniBox12LV, "mb1_pv6", tl2, r2, scale=[1, 1, -1]
    )
    comp8 = pyg4ometry.compare.logicalVolumes(tl1, tl2, tests, recursive=True)
    if printOut:
        comp8.print()
    assert len(comp8.test["scale"]) > 0

    # equivalent volume but different solids
    # NOTE solids go with LogicalVolumes in pyg4ometry, not solids
    r3 = _g4.Registry()
    boxA = _g4.solid.Box("box_a", 10, 20, 50, r3)
    boxALV = _g4.LogicalVolume(boxA, copper1, "boxA_lv", r3)
    r4 = _g4.Registry()
    boxB_A = _g4.solid.Box("box_b_a", 10, 30, 100, r3)
    boxB_B = _g4.solid.Box("box_b_b", 10, 20, 50, r3)
    boxB = _g4.solid.Intersection("box_b", boxB_A, boxB_B, [[0, 0, 0], [0, 0, 0]], r3)
    boxBLV = _g4.LogicalVolume(boxB, copper1, "boxB_lv", r3)
    testVolumeAreaOnly = pyg4ometry.compare.Tests("shapeVolume", "shapeArea")
    comp9 = pyg4ometry.compare.logicalVolumes(boxALV, boxBLV, testVolumeAreaOnly)
    if printOut:
        comp9.print()
    assert len(comp9) == 0

    # update the shape of one solid and convince ourselves the area and volume checks work
    boxB_B.pY = 12
    boxBLV.reMesh()
    comp10 = pyg4ometry.compare.logicalVolumes(boxALV, boxBLV, testVolumeAreaOnly)
    if printOut:
        comp10.print()
    assert len(comp10) == 2

    # return {"teststatus": True}


if __name__ == "__main__":
    Test()
