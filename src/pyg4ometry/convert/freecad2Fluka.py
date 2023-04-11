import pyg4ometry.fluka as _fluka

def freecadDoc2Fluka(fcd) :
    freg = _fluka.FlukaRegistry()


    # loop over parts
    for obj in fcd.doc.Objects:
        if obj.TypeId == "Part::Feature":
            pass


def part2Region(obj, trfm, fgreg, meshDeviation = 0.05) :

    ################################
    # Tessellate object
    ################################
    mesh = list(obj.Shape.tessellate(meshDeviation))

    # create list of surfaces

    # determine surfaces which are cut surfaces

    # (set of surfaces strictly on one side of cut surface)

    # optimize cut surfaces

    # compile list output zones

    # create region



