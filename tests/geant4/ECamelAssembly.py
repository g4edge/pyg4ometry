import pyg4ometry.geant4 as _g4


def MakeECamelAssembly(reg, margin=1, separation=1):
    iron = _g4.MaterialPredefined("G4_Fe")

    # solids
    # E shape - go from bottom left around outside edge clockwise
    dx = 30  # width
    dy = 60  # height
    tt = 10  # thickness of each bit
    polygon = [
        [-dx, 0],
        [-dx, dy],
        [0, dy],
        [0, dy - tt],
        [-dx + tt, dy - tt],
        [-dx + tt, 0.5 * (dy + tt)],
        [0, 0.5 * (dy + tt)],
        [0, 0.5 * dy - 0.5 * tt],
        [-dx + tt, 0.5 * dy - 0.5 * tt],
        [-dx + tt, tt],
        [0, tt],
        [0, 0],
    ]
    slices = [[-5, [0, 0], 1.0], [5, [0, 0], 1.0]]

    eSolid = _g4.solid.ExtrudedSolid("e_solid", polygon, slices, reg)

    # now for a camel-like two hump solid to fit 'into' the E tightly but not touching
    # start bottom left corner then go clockwise (so beside bottom right corner of E)
    hx = dx - tt
    ma = margin
    hy = 0.5 * (dy - 3 * tt)
    polygon2 = [
        [0, 0],
        [0, tt + ma],
        [-hx, tt + ma],
        [-hx, tt + hy - ma],
        [0, tt + hy - ma],
        [0, tt + hy + tt + ma],
        [-hx, tt + hy + tt + ma],
        [-hx, dy - tt - ma],
        [0, dy - tt - ma],
        [0, dy],
        [tt, dy],
        [tt, 0],
    ]
    slices2 = [[-5, [0, 0], 1.0], [5, [0, 0], 1.0]]
    camelSolid = _g4.solid.ExtrudedSolid("camel_solid", polygon2, slices2, reg)

    # logicals
    eLV = _g4.LogicalVolume(eSolid, iron, "e_lv", reg)
    camelLV = _g4.LogicalVolume(camelSolid, iron, "camel_lv", reg)

    # structure
    assembly = _g4.AssemblyVolume("assembly1", reg)
    xo = (dx + tt) * 0.5 - tt
    epv = _g4.PhysicalVolume([0, 0, 0], [xo, 0, 0], eLV, "e_pv", assembly, reg)
    cpv = _g4.PhysicalVolume([0, 0, 0], [xo + separation, 0, 0], camelLV, "camel_pv", assembly, reg)

    return assembly
