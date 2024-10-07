import pytest
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd


@pytest.fixture
def registry():
    return _g4.Registry()


@pytest.fixture
def two_materials(registry):
    def _two_materials(nist_materials=False):
        if nist_materials:
            wm = _g4.nist_material_2geant4Material("G4_Galactic", registry)
            sm = _g4.nist_material_2geant4Material("G4_Au", registry)
        else:
            wm = _g4.MaterialPredefined("G4_Galactic")
            sm = _g4.MaterialPredefined("G4_Au")

        return {"wm": wm, "sm": sm}

    return _two_materials


@pytest.fixture
def geant4_world(registry):
    wx = _gd.Constant("wx", "100", registry, True)
    wy = _gd.Constant("wy", "100", registry, True)
    wz = _gd.Constant("wz", "100", registry, True)

    ws = _g4.solid.Box("ws", wx, wy, wz, registry, "mm")

    return ws


@pytest.fixture
def geant4_box(registry):
    bx = _gd.Constant("bx", "10", registry, True)
    by = _gd.Constant("by", "10", registry, True)
    bz = _gd.Constant("bz", "10", registry, True)

    bs = _g4.solid.Box("bs", bx, by, bz, registry, "mm")

    return bs


@pytest.fixture
def geant4_tubs(registry):
    trmin = _gd.Constant("trmin", "2.5", registry, True)
    trmax = _gd.Constant("trmax", "10.0", registry, True)
    tz = _gd.Constant("tz", "50", registry, True)
    tstartphi = _gd.Constant("startphi", "0", registry, True)
    tdeltaphi = _gd.Constant("deltaphi", "1.5*pi", registry, True)

    tstartphi_deg = _gd.Constant("startphi_deg", "0", registry, True)
    tdeltaphi_deg = _gd.Constant("deltaphi_deg", "270", registry, True)

    ts = _g4.solid.Tubs(
        "ts", trmin, trmax, tz, tstartphi, tdeltaphi, registry, "mm", "rad", nslice=16
    )

    return ts


@pytest.fixture
def geant4_cuttubs(registry):
    ctrmin = _gd.Constant("trmin", "2.5", registry, True)
    ctrmax = _gd.Constant("trmax", "10.0", registry, True)
    ctz = _gd.Constant("tz", "50", registry, True)
    ctstartphi = _gd.Constant("startphi", "0", registry, True)
    ctdeltaphi = _gd.Constant("deltaphi", "1.5*pi", registry, True)
    ctlowx = _gd.Constant("ctlowx", "-1", registry, True)
    ctlowy = _gd.Constant("ctlowy", "-1", registry, True)
    ctlowz = _gd.Constant("ctlowz", "-1", registry, True)
    cthighx = _gd.Constant("cthighx", "1", registry, True)
    cthighy = _gd.Constant("cthighy", "1", registry, True)
    cthighz = _gd.Constant("cthighz", "1", registry, True)

    cts = _g4.solid.CutTubs(
        "ts",
        ctrmin,
        ctrmax,
        ctz,
        ctstartphi,
        ctdeltaphi,
        [ctlowx, ctlowy, ctlowz],
        [cthighx, cthighy, cthighz],
        registry,
        "mm",
        "rad",
        nslice=16,
    )
    return cts


@pytest.fixture
def geant4_cons(registry):
    crmin1 = _gd.Constant("crmin1", "6", registry, True)
    crmax1 = _gd.Constant("crmax1", "20", registry, True)
    crmin2 = _gd.Constant("crmin2", "5", registry, True)
    crmax2 = _gd.Constant("crmax2", "10", registry, True)
    cz = _gd.Constant("cz", "100", registry, True)
    cdp = _gd.Constant("cdp", "1.5*pi", registry, True)
    zero = _gd.Constant("zero", "0.0", registry, False)

    cdp_deg = _gd.Constant("cdp_deg", "270", registry, True)

    cs = _g4.solid.Cons(
        "cs",
        crmin1,
        crmax1,
        crmin2,
        crmax2,
        cz,
        zero,
        cdp,
        registry,
        "mm",
        "rad",
        nslice=16,
    )

    return cs


@pytest.fixture
def geant4_para(registry):
    px = _gd.Constant("px", "10", registry, True)
    py = _gd.Constant("py", "20", registry, True)
    pz = _gd.Constant("pz", "30", registry, True)
    pAlpha = _gd.Constant("pAlpha", "0.2", registry, True)
    pTheta = _gd.Constant("pTheta", "0.3", registry, True)
    pPhi = _gd.Constant("pPhi", "0.4", registry, True)

    pAlpha_deg = _gd.Constant("pAlpha_deg", "0.2/pi*180", registry, True)
    pTheta_deg = _gd.Constant("pTheta_deg", "0.3/pi*180", registry, True)
    pPhi_deg = _gd.Constant("pPhi_deg", "0.4/pi*180", registry, True)

    ps = _g4.solid.Para("ps", px, py, pz, pAlpha, pTheta, pPhi, registry, "mm", "rad")

    return ps


@pytest.fixture
def geant4_trd(registry):
    tx1 = _gd.Constant("tx1", "20", registry, True)
    ty1 = _gd.Constant("ty1", "25", registry, True)
    tx2 = _gd.Constant("tx2", "5", registry, True)
    ty2 = _gd.Constant("ty2", "7.5", registry, True)
    tz = _gd.Constant("tz", "10.0", registry, True)

    ts = _g4.solid.Trd("ts", tx1, tx2, ty1, ty2, tz, registry, "mm")

    return ts


@pytest.fixture
def geant4_trap(registry):
    tx1 = _gd.Constant("tx1", "5", registry, True)
    tx2 = _gd.Constant("tx2", "5", registry, True)
    tx3 = _gd.Constant("tx3", "10", registry, True)
    tx4 = _gd.Constant("tx4", "10", registry, True)

    ty1 = _gd.Constant("ty1", "5", registry, True)
    ty2 = _gd.Constant("ty2", "7.5", registry, True)

    tz = _gd.Constant("tz", "10.0", registry, True)

    ttheta = _gd.Constant("ttheta", "0.6", registry, True)
    tphi = _gd.Constant("tphi", "0.0", registry, True)
    talp1 = _gd.Constant("talp1", "0.0", registry, True)
    talp2 = _gd.Constant("talp2", "0.0", registry, True)

    ttheta_deg = _gd.Constant("ttheta_deg", "0.6/pi*180", registry, True)
    tphi_deg = _gd.Constant("tphi_deg", "0.0", registry, True)
    talp1_deg = _gd.Constant("talp1_deg", "0.0", registry, True)
    talp2_deg = _gd.Constant("talp2_deg", "0.0", registry, True)

    ts = _g4.solid.Trap(
        "ts",
        tz,
        ttheta,
        tphi,
        ty1,
        tx1,
        tx2,
        talp1,
        ty2,
        tx3,
        tx4,
        talp2,
        registry,
        "mm",
        "rad",
    )

    return ts


@pytest.fixture
def geant4_sphere(registry):
    srmin = _gd.Constant("rmin", "8", registry, True)
    srmax = _gd.Constant("rmax", "10", registry, True)
    ssphi = _gd.Constant("sphi", "0", registry, True)
    sdphi = _gd.Constant("dphi", "1.75*pi", registry, True)
    sstheta = _gd.Constant("stheta", "0", registry, True)
    sdtheta = _gd.Constant("dtheta", "0.75*pi", registry, True)

    ss = _g4.solid.Sphere(
        "ss",
        srmin,
        srmax,
        ssphi,
        sdphi,
        sstheta,
        sdtheta,
        registry,
        "mm",
        "rad",
        nslice=16,
        nstack=16,
    )

    return ss


@pytest.fixture
def geant4_structure():
    def _geant4_structure(solid, registry, two_materials, geant4_world):
        wl = _g4.LogicalVolume(geant4_world, two_materials()["wm"], "wl", registry)
        sl = _g4.LogicalVolume(solid, two_materials()["sm"], "sl", registry)
        sp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], sl, "spv1", wl, registry)

        # set world volume
        registry.setWorld(wl.name)

        return registry

    return _geant4_structure


def test_geant4_box(geant4_box, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_box, registry, two_materials, geant4_world)
    # vertex count, poly count, area, volume, minEdge, maxEdge


def test_geant4_tubs(geant4_tubs, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_tubs, registry, two_materials, geant4_world)


def test_geant4_cuttubs(geant4_cuttubs, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_cuttubs, registry, two_materials, geant4_world)


def test_geant4_cons(geant4_cons, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_cons, registry, two_materials, geant4_world)


def test_geant4_para(geant4_para, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_para, registry, two_materials, geant4_world)


def test_geant4_trd(geant4_trd, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_trd, registry, two_materials, geant4_world)


def test_geant4_trap(geant4_trap, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_trap, registry, two_materials, geant4_world)


def test_geant4_sphere(geant4_sphere, registry, two_materials, geant4_world, geant4_structure):
    reg = geant4_structure(geant4_sphere, registry, two_materials, geant4_world)
