import os as _os
import pyg4ometry
import pyg4ometry.geant4 as _g4


def test(printOut=False):
    r = _g4.Registry()

    tests = pyg4ometry.compare.Tests()

    galactic1 = _g4.MaterialPredefined("G4_Galactic", r)
    galactic2 = _g4.MaterialPredefined("G4_Galactic", r)

    # predefined materials
    comp1 = pyg4ometry.compare.materials(galactic1, galactic2, tests)
    if printOut:
        comp1.print()
    assert len(comp1) == 0

    # TBC

    # return {"teststatus": True}


if __name__ == "__main__":
    test()
