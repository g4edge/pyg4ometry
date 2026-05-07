import pyg4ometry
import numpy as _np

# set the number of polygon points on cylinders to be 2x the 16 default
pyg4ometry.config.SolidDefaults.Tubs.nslice = 32
pyg4ometry.config.SolidDefaults.CutTubs.nslice = 32


def HepDetector(siBarrel=True, siEndcaps=True, ecalBarrel=True, solenoid=True):
    reg = pyg4ometry.geant4.Registry()

    twopi = pyg4ometry.gdml.Constant("twopi", "2.0*pi", reg)
    halfpi = pyg4ometry.gdml.Constant("halfpi", "0.5*pi", reg)
    safety = pyg4ometry.gdml.Constant("safety", 1e-3, reg)
    constants = {"twopi": twopi, "safety": safety, "halfpi": halfpi}

    siBarrelLength = pyg4ometry.gdml.Constant("siBarrelLength", 1600, reg)
    ecalBInnerRadius = pyg4ometry.gdml.Constant("ecalBInnerRadius", 590, reg)
    ecalBOuterRadius = pyg4ometry.gdml.Constant("ecalBOuterRadius", 900, reg)
    ecalBLength = pyg4ometry.gdml.Constant("ecalBLength", 2500, reg)
    solenoidInnerRadius = pyg4ometry.gdml.Constant(
        "solenoidInnerRadius", ecalBOuterRadius + 50, reg
    )
    solenoidThickness = pyg4ometry.gdml.Constant("solenoidThickness", 50, reg)
    solenoidLength = pyg4ometry.gdml.Constant("solenoidLength", 1.1 * ecalBLength, reg)
    endcapLayerSeparation = pyg4ometry.gdml.Constant("encapLayerSeparation", 50, reg)

    worldSolid = pyg4ometry.geant4.solid.Box("world_solid", 10000, 10000, 10000, reg, "mm")
    worldLV = pyg4ometry.geant4.LogicalVolume(worldSolid, "G4_Galactic", "worldLV", reg)

    # silicon barrel
    if siBarrel:
        siBarrelContainerLV = SiBarrelTracker(reg)
        siBarrelPV = pyg4ometry.geant4.PhysicalVolume(
            [0, 0, 0], [0, 0, 0], siBarrelContainerLV, "silicon_barrel_pv", worldLV, reg
        )

    # end caps
    if siEndcaps:
        endcapLV = SiTrackerEndcapLayer(reg=reg)
        for i in range(4):
            zOffset = 0.5 * siBarrelLength * 1.02 + (i * endcapLayerSeparation)
            pyg4ometry.geant4.PhysicalVolume(
                [0, 0, 0],
                [0, 0, zOffset],
                endcapLV,
                "endcap_" + str(i) + "_left_pv",
                worldLV,
                reg,
            )
            pyg4ometry.geant4.PhysicalVolume(
                [0, 0, 0],
                [0, 0, -zOffset],
                endcapLV,
                "endcap_" + str(i) + "_right_pv",
                worldLV,
                reg,
            )

    # ecalBarrel
    if ecalBarrel:
        ecalBarrelLV = ECALBarrel(
            ecalBInnerRadius.eval(),
            ecalBOuterRadius.eval(),
            ecalBLength.eval(),
            16,
            41,
            constants,
            reg,
        )
        ecalBarrelPV = pyg4ometry.geant4.PhysicalVolume(
            [0, 0, 0], [0, 0, 0], ecalBarrelLV, "ecal_barrel_pv", worldLV, reg
        )

    # solenoid
    if solenoid:
        solenoidLV = Solenoid(
            solenoidInnerRadius, solenoidThickness, solenoidLength, constants, reg
        )
        solenoidPV = pyg4ometry.geant4.PhysicalVolume(
            [0, 0, 0], [0, 0, 0], solenoidLV, "solenoid_pv", worldLV, reg
        )

    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    pbw0Vis = pyg4ometry.visualisation.VisualisationOptions()
    pbw0Vis.colour = [0.8, 0.8, 0.95]
    pbw0Vis.alpha = 0.1
    v.addMaterialVisOption("lead_tungstate", pbw0Vis)
    v.addLogicalVolume(worldLV)
    v.view()

    # gdml output
    reg.setWorld(worldLV)
    w = pyg4ometry.gdml.Writer()
    w.addDetector(reg)
    w.write("HepDetector.gdml")


def SiBarrelTracker(reg=None):
    reg = pyg4ometry.geant4.Registry() if reg is None else reg

    worldBox = pyg4ometry.geant4.solid.Box("worldBox", 10000, 10000, 10000, reg, "mm")
    siBarrelWorldLV = pyg4ometry.geant4.LogicalVolume(
        worldBox, "G4_Galactic", "siBarrelWorldLV", reg
    )

    siTrackerTubs = pyg4ometry.geant4.solid.Tubs(
        "siBarrelTrackerTubs", 100, 500, 1650, 0, 2 * _np.pi, reg, "mm", "rad"
    )
    siTrackerLv = pyg4ometry.geant4.LogicalVolume(siTrackerTubs, "G4_Galactic", "siTrackerLv", reg)
    siTrackerPv = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, 0], [0, 0, 0], siTrackerLv, "siTrackerPv", siBarrelWorldLV, reg
    )

    siTrackerModuleAv = SiTrackerBarrelModule(reg=reg)

    siTrackerLayer1Av = SiTrackerBarrelLayer(
        name="barrelAv1", moduleAv=siTrackerModuleAv, radius=0.15, nAzimuth=15, reg=reg
    )
    siTrackerLayer1Pv = pyg4ometry.geant4.PhysicalVolume(
        [_np.pi / 2.0, 0, 0],
        [0, 0, 0],
        siTrackerLayer1Av,
        "siTrackerLayer1Pv",
        siTrackerLv,
        reg,
    )

    siTrackerLayer2Av = SiTrackerBarrelLayer(
        name="barrelAv2",
        moduleAv=siTrackerModuleAv,
        radius=0.30,
        nAzimuth=int(0.3 / 0.15 * 15),
        reg=reg,
    )
    siTrackerLayer2Pv = pyg4ometry.geant4.PhysicalVolume(
        [_np.pi / 2.0, 0, 0],
        [0, 0, 0],
        siTrackerLayer2Av,
        "siTrackerLayer2Pv",
        siTrackerLv,
        reg,
    )

    siTrackerLayer3Av = SiTrackerBarrelLayer(
        name="barrelAv3",
        moduleAv=siTrackerModuleAv,
        radius=0.45,
        nAzimuth=int(0.45 / 0.15 * 15),
        reg=reg,
    )
    siTrackerLayer3Pv = pyg4ometry.geant4.PhysicalVolume(
        [_np.pi / 2.0, 0, 0],
        [0, 0, 0],
        siTrackerLayer3Av,
        "siTrackerLayer3Pv",
        siTrackerLv,
        reg,
    )

    return siTrackerLv


def SiTrackerBarrelLayer(
    name="barrelAv",
    moduleAv=None,
    length=1.6,
    radius=0.25,
    sensorSize=0.08,
    nAzimuth=25,
    tiltAngleDeg=11,
    reg=None,
):

    reg = pyg4ometry.geant4.Registry() if reg is None else reg

    tiltAngleRad = pyg4ometry.transformation.deg2rad(tiltAngleDeg)

    sitbmLv = moduleAv

    barrelAv = pyg4ometry.geant4.AssemblyVolume(name, reg, True)

    nLength = int(length / (2 * sensorSize))

    for i in range(0, nLength, 1):
        z = i * 2 * sensorSize - length / 2.0 + sensorSize

        for j in range(0, nAzimuth, 1):
            phi = 2 * _np.pi / nAzimuth * j
            modulePv = pyg4ometry.geant4.PhysicalVolume(
                [0, phi + _np.pi / 2 + tiltAngleRad, 0],
                [radius * _np.cos(phi), z, radius * _np.sin(phi), "m"],
                sitbmLv,
                name + "_modulePv" + str(i) + "_" + str(j),
                barrelAv,
                reg,
            )

    return barrelAv


def SiTrackerBarrelModule(
    sensorSize=0.08,
    sensorGap=3e-3,
    pcbLength=0.015,
    pcbGap=0.005,
    tiltAngleDeg=5,
    reg=None,
):
    reg = pyg4ometry.geant4.Registry() if reg is None else reg

    tiltAngleRad = pyg4ometry.transformation.deg2rad(tiltAngleDeg)

    moduleAv = pyg4ometry.geant4.AssemblyVolume("barrelModuleAv", reg, True)

    sensorLv = SiTrackerBarrelSensor(
        sensorSize=sensorSize, sensorThickness=300e-6, nstrip=512, reg=reg
    )
    sensorPv1 = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, 0],
        [0, -sensorSize / 2, sensorGap / 2, "m"],
        sensorLv,
        "sensorBarrelPv1",
        moduleAv,
        reg,
    )
    sensorPv2 = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, 0],
        [0, sensorSize / 2, sensorGap / 2, "m"],
        sensorLv,
        "sensorBarrelPv2",
        moduleAv,
        reg,
    )
    sensorPv3 = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, tiltAngleRad],
        [
            -sensorSize / 2 * _np.sin(tiltAngleRad),
            -sensorSize / 2 * _np.cos(tiltAngleRad),
            -sensorGap / 2,
            "m",
        ],
        sensorLv,
        "sensorPv3",
        moduleAv,
        reg,
    )
    sensorPv4 = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, tiltAngleRad],
        [
            sensorSize / 2 * _np.sin(tiltAngleRad),
            sensorSize / 2 * _np.cos(tiltAngleRad),
            -sensorGap / 2,
            "m",
        ],
        sensorLv,
        "sensorPv4",
        moduleAv,
        reg,
    )

    pcbSolid = pyg4ometry.geant4.solid.Box("pcbSolid", sensorSize, pcbLength, 2e-3, reg, "m")
    pcbLv = pyg4ometry.geant4.LogicalVolume(pcbSolid, "G4_Si", "pcbLV", reg, True)
    pcbPv = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, 0], [0, -pcbLength / 2, pcbGap, "m"], pcbLv, "sensorPv1", moduleAv, reg
    )

    return moduleAv


def SiTrackerBarrelSensor(sensorSize=0.05, sensorThickness=300e-6, nstrip=512, reg=None):
    reg = pyg4ometry.geant4.Registry() if reg is None else reg

    sensor = pyg4ometry.geant4.solid.Box(
        "sensorBarrrelSolid", sensorSize, sensorSize, sensorThickness, reg, "m", True
    )
    sensorLv = pyg4ometry.geant4.LogicalVolume(sensor, "G4_Si", "sensorBarrelLV", reg, True)

    return sensorLv


def SiTrackerEndcapLayer(
    name="endcapAv",
    innerRadius=0.3,
    outerRadius=0.56,
    nAzimuth=30,
    phiPetal=0.6,
    moduleGap=0.005,
    reg=None,
):
    reg = pyg4ometry.geant4.Registry() if reg is None else reg

    moduleLv = SiTrackerEndcapModule(
        innerRadius=innerRadius, outerRadius=outerRadius, sensorSize=phiPetal, reg=reg
    )

    dAzimuth = 2 * _np.pi / nAzimuth

    siTrackerECTubs = pyg4ometry.geant4.solid.Tubs(
        name + "_siTrackerECTubs",
        innerRadius,
        outerRadius,
        0.025,
        0,
        2 * _np.pi,
        reg,
        "m",
        "rad",
    )
    siTrackerECLv = pyg4ometry.geant4.LogicalVolume(
        siTrackerECTubs, "G4_Galactic", "siTrackerECLv", reg
    )

    rMid = (innerRadius + outerRadius) / 2.0

    for i in range(0, nAzimuth, 1):
        azimuth = i * dAzimuth
        x = rMid * _np.cos(azimuth + _np.pi / 2.0)
        y = rMid * _np.sin(azimuth + _np.pi / 2.0)
        z = -moduleGap if (i % 2 == 0) else moduleGap

        modulePv = pyg4ometry.geant4.PhysicalVolume(
            [_np.pi / 2.0, azimuth, 0],
            [x, y, z, "m"],
            moduleLv,
            name + "_modulePv" + str(i),
            siTrackerECLv,
            reg,
        )

    return siTrackerECLv


def SiTrackerEndcapModule(
    innerRadius=0.35, outerRadius=0.56, sensorSize=0.4, sensorGap=3e-3, reg=None
):
    reg = pyg4ometry.geant4.Registry() if reg is None else reg

    moduleAv = pyg4ometry.geant4.AssemblyVolume("endcapModuleAv", reg, True)

    sensorLv = SiTrackerEndcapSensor(
        innerRadius=innerRadius, outerRadius=outerRadius, sensorSize=sensorSize, reg=reg
    )

    sensorPv1 = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, 0],
        [0, sensorGap / 2, 0, "m"],
        sensorLv,
        "sensorEndcapPv1",
        moduleAv,
        reg,
    )
    sensorPv2 = pyg4ometry.geant4.PhysicalVolume(
        [0, 0, 0],
        [0, -sensorGap / 2, 0, "m"],
        sensorLv,
        "sensorEndcapPv2",
        moduleAv,
        reg,
    )

    return moduleAv


def SiTrackerEndcapSensor(
    innerRadius=0.35, outerRadius=0.56, sensorSize=0.4, sensorThickness=300e-6, reg=None
):
    reg = pyg4ometry.geant4.Registry() if reg is None else reg

    dx1 = sensorSize / 2.0 * innerRadius
    dy1 = sensorThickness
    dx2 = sensorSize / 2.0 * outerRadius
    dy2 = sensorThickness
    dz = outerRadius - innerRadius

    sensor = pyg4ometry.geant4.solid.Trd("sensorEndcapSolid", dx1, dx2, dy1, dy2, dz, reg, "m")
    sensorLv = pyg4ometry.geant4.LogicalVolume(sensor, "G4_Si", "sensorEndcapLV", reg, True)

    return sensorLv


def FibreTracker():
    pass


def Solenoid(innerRadius, thickness, length, constants, reg=None):
    """
    Create a big solid aluminium cylinder with embedded NbTi coils.
    """
    reg = pyg4ometry.geant4.Registry() if reg is None else reg
    solenoidSolid = pyg4ometry.geant4.solid.Tubs(
        "solenoid_solid",
        innerRadius,
        innerRadius + thickness,
        length,
        0,
        constants["twopi"],
        reg,
    )
    aluminium = pyg4ometry.geant4.MaterialPredefined("G4_Al")
    solenoidLV = pyg4ometry.geant4.LogicalVolume(solenoidSolid, aluminium, "solenoid_lv", reg)

    coilThickness = 0.25 * thickness
    coilInnerRadius = innerRadius + 0.5 * thickness - 0.5 * coilThickness
    coilOuterRadius = innerRadius + 0.5 * thickness + 0.5 * coilThickness
    coilLengthZ = 0.5 * thickness
    nCoils = int(length.eval() / (2 * coilLengthZ.eval()))
    nCoilsEven = nCoils if (nCoils % 2 == 0) else nCoils - 1
    coilSolid = pyg4ometry.geant4.solid.Tubs(
        "coil_solid",
        coilInnerRadius,
        coilOuterRadius,
        coilLengthZ,
        0,
        constants["twopi"],
        reg,
    )
    nbti = pyg4ometry.geant4.MaterialCompound("nbti", 5.7, 2, reg)
    nbti.set_state("solid")
    nbti.set_temperature(4, "K")
    nbti.add_material(pyg4ometry.geant4.MaterialPredefined("G4_Sn"), 0.3)
    nbti.add_material(pyg4ometry.geant4.MaterialPredefined("G4_Nb"), 0.7)
    coilLV = pyg4ometry.geant4.LogicalVolume(coilSolid, nbti, "solenoid_coil_lv", reg)

    # central coil
    iCoil = 0
    pyg4ometry.geant4.PhysicalVolume(
        [0, 0, 0], [0, 0, 0], coilLV, "coil_" + str(iCoil) + "_pv", solenoidLV, reg
    )
    # one side
    for i in range(1, int(nCoilsEven / 2)):
        zOffset = i * 2 * coilLengthZ
        iCoil += 1
        pyg4ometry.geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, zOffset],
            coilLV,
            "coil_" + str(iCoil) + "_pv",
            solenoidLV,
            reg,
        )
        iCoil += 1
        pyg4ometry.geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, -zOffset],
            coilLV,
            "coil_" + str(iCoil) + "_pv",
            solenoidLV,
            reg,
        )

    return solenoidLV


def ECALBarrel(innerRadius, outerRadius, length, nModulesPhi, nModulesZ, constants, reg):
    # container LV
    ecalBarrelSolid = pyg4ometry.geant4.solid.Tubs(
        "ecal_barrel_solid",
        innerRadius,
        outerRadius,
        length,
        0,
        constants["twopi"],
        reg,
    )
    air = pyg4ometry.geant4.MaterialPredefined("G4_AIR")
    ecalBarrelLV = pyg4ometry.geant4.LogicalVolume(ecalBarrelSolid, air, "ecal_barrel_lv", reg)

    # calculate sizes
    safety = constants["safety"].eval()
    twopi = constants["twopi"].eval()
    halfpi = constants["halfpi"].eval()
    innerR1 = innerRadius + safety  # for the segment container
    segmentAngle = twopi / nModulesPhi
    # inner theoretical radius for modules such that the chord doesn't intercept the arc
    # innerR2 = innerR1 + innerR1 * (1-_np.cos(segmentAngle))
    rGap = outerRadius - innerRadius
    innerR2 = innerR1 + 0.05 * rGap
    outerR1 = outerRadius - safety  # for the segment container
    outerR2 = outerR1 - 0.1 * rGap  # for the modules
    rMid = 0.5 * (outerR1 + innerR2)

    nModulesZ = nModulesZ if (nModulesZ % 2 != 0) else nModulesZ + 1

    # segment container solid
    segmentSolid = pyg4ometry.geant4.solid.Tubs(
        "ecal_barrel_segment_solid",
        innerR1,
        outerR1,
        length - 2 * safety,
        halfpi - 0.5 * segmentAngle,
        segmentAngle,
        reg,
    )
    segmentLV = pyg4ometry.geant4.LogicalVolume(segmentSolid, air, "ecal_barrel_segment_lv", reg)

    # approximate PbW04
    leadTungstate = pyg4ometry.geant4.MaterialCompound("lead_tungstate", 8.28, 3, reg)
    leadTungstate.set_state("solid")
    leadTungstate.set_temperature(293, "K")
    leadTungstate.add_material(pyg4ometry.geant4.MaterialPredefined("G4_Pb"), 0.45)
    leadTungstate.add_material(pyg4ometry.geant4.MaterialPredefined("G4_W"), 0.40)
    leadTungstate.add_material(pyg4ometry.geant4.MaterialPredefined("G4_O"), 0.15)

    # place modules along Z
    iz = -0.5 * length
    dz = length / nModulesZ
    startAngle = halfpi - 0.5 * 0.98 * segmentAngle
    sweepAngle = 0.96 * segmentAngle
    for i in range(nModulesZ):
        iModuleName = "ecal_mod_" + str(i)
        iModule = pyg4ometry.geant4.solid.Tubs(
            iModuleName + "_solid",
            innerR2,
            outerR2,
            0.95 * dz,
            startAngle,
            sweepAngle,
            reg,
        )
        iModuleLV = pyg4ometry.geant4.LogicalVolume(
            iModule, leadTungstate, iModuleName + "_lv", reg
        )
        pyg4ometry.geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, iz + 0.5 * dz],
            iModuleLV,
            iModuleName + "_pv",
            segmentLV,
            reg,
        )
        iz += dz

    # nModulesPhi = 1
    for i in range(nModulesPhi):
        angle = i * segmentAngle
        pyg4ometry.geant4.PhysicalVolume(
            [0, 0, angle],
            [0, 0, 0],
            segmentLV,
            "ecal_segment_" + str(i) + "_pv",
            ecalBarrelLV,
            reg,
        )
    return ecalBarrelLV


def CalorimeterCap(innerRadius=2, outerRadius=2.5):
    pass


if __name__ == "__main__":
    HepDetector()
