import pyg4ometry
import pyg4ometry.geant4 as _g4


def test(printOut=False):
    r = _g4.Registry()
    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")
    ws = _g4.solid.Box("ws", 1000, 1000, 1000, r)
    bs = _g4.solid.Box("bs", 100, 100, 100, r)
    mbs = _g4.solid.Box("mbs", 800, 100, 100, r)
    wl = _g4.LogicalVolume(ws, wm, "wl", r)
    bl = _g4.LogicalVolume(bs, bm, "bl", r)
    ml = _g4.LogicalVolume(mbs, wm, "ml", r)
    mbl = _g4.ReplicaVolume("mbl", bl, ml, _g4.ReplicaVolume.Axis.kXAxis, 8, 100, 0, r)

    tests = pyg4ometry.compare.Tests()

    comp1 = pyg4ometry.compare.replicaVolumes(mbl, mbl, tests)
    if printOut:
        comp1.print()
    assert len(comp1) == 0

    # different number of replicas
    r2 = _g4.Registry()
    mbl2 = _g4.ReplicaVolume("mbl", bl, ml, _g4.ReplicaVolume.Axis.kXAxis, 7, 100, 0, r2)
    comp2 = pyg4ometry.compare.replicaVolumes(mbl, mbl2, tests)
    if printOut:
        comp2.print()
    assert len(comp2) == 1

    # different axis
    r3 = _g4.Registry()
    mbl3 = _g4.ReplicaVolume("mbl", bl, ml, _g4.ReplicaVolume.Axis.kYAxis, 8, 100, 0, r3)
    comp3 = pyg4ometry.compare.replicaVolumes(mbl, mbl3, tests)
    if printOut:
        comp3.print()
    assert len(comp3) == 1

    # return {"teststatus": True}


if __name__ == "__main__":
    test()
