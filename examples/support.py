import os as _os

import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vis
import numpy as _np

lengthSafety = 1e-8


def SupportMagnet(
    name="supportMagnet",
    shape="polygonal",
    parameters={
        "nface": 3,
        "thickness": 10,
        "angles": [-45, 0, 45],
        "distances": [300, 300, 300],
    },
):

    pass


def SupportTable(
    name="support",
    length=4,
    width=2.0,
    height=1.5,
    thickness=0.05,
    nSupport=4,
    sectionSize=0.1,
    sectionThickness=0.005,
    horizontalPad=0.90,
    verticalPad=0.90,
    reg=None,
    vis=False,
    interactive=False,
):

    if reg == None:
        reg = _g4.Registry()

    # variables
    vLength = _gd.Constant("length", length, reg, True)
    vWidth = _gd.Constant("wigth", width, reg, True)
    vHeight = _gd.Constant("height", height, reg, True)

    vSectionSize = _gd.Constant("sectionSize", sectionSize, reg, True)
    vSectionThickness = _gd.Constant("sectionThickness", sectionThickness, reg, True)

    # table top face
    tableX = _gd.Constant("tableX", width, reg, True)
    tableY = _gd.Constant("tableY", thickness, reg, True)
    tableZ = _gd.Constant("tableZ", length, reg, True)

    supportSolid = _g4.solid.Box(
        name + "_Solid", tableX * 1.0, height * 1.0, tableZ * 1.0, reg, lunit="m"
    )
    supportMaterial = _g4.MaterialPredefined("G4_AIR")
    supportLogical = _g4.LogicalVolume(supportSolid, supportMaterial, name + "_Loical", reg)

    tableTopSolid = _g4.solid.Box(name + "_tableTopSolid", tableX, tableY, tableZ, reg, lunit="m")
    tableTopMaterial = _g4.MaterialPredefined("G4_STAINLESS-STEEL")
    tableTopLogical = _g4.LogicalVolume(
        tableTopSolid, tableTopMaterial, name + "_tableTopLogical", reg
    )
    tableTopPhysical = _g4.PhysicalVolume(
        [0, 0, 0],
        [0, vHeight / 2, 0, "m"],
        tableTopLogical,
        name + "_tableTopPhysical",
        supportLogical,
        reg,
    )

    # build support
    supportZ = horizontalPad * vLength - lengthSafety
    supportZSectionOuter = _g4.solid.Box(
        name + "_supportZOuter", vSectionSize, vSectionSize, supportZ, reg, lunit="m"
    )
    supportZSectionInner = _g4.solid.Box(
        name + "_supportZInner",
        vSectionSize - vSectionThickness,
        vSectionSize - vSectionThickness,
        supportZ - vSectionThickness,
        reg,
        lunit="m",
    )
    supportZSection = _g4.solid.Subtraction(
        name + "_supportZSection",
        supportZSectionOuter,
        supportZSectionInner,
        [[0, 0, 0], [0, 0, 0]],
        reg,
    )
    supportZSectionMaterial = _g4.MaterialPredefined("G4_STAINLESS-STEEL")
    supportZSectionLogical = _g4.LogicalVolume(
        supportZSection, supportZSectionMaterial, name + "_supportZSectionLogical", reg
    )

    supportX = horizontalPad * vWidth - 3 * vSectionSize - lengthSafety
    supportXSectionOuter = _g4.solid.Box(
        name + "_supportXOuter", vSectionSize, vSectionSize, supportX, reg, lunit="m"
    )
    supportXSectionInner = _g4.solid.Box(
        name + "_supportXInner",
        vSectionSize - vSectionThickness,
        vSectionSize - vSectionThickness,
        supportX - vSectionThickness,
        reg,
        lunit="m",
    )
    supportXSection = _g4.solid.Subtraction(
        name + "_supportXSection",
        supportXSectionOuter,
        supportXSectionInner,
        [[0, 0, 0], [0, 0, 0]],
        reg,
    )
    supportXSectionMaterial = _g4.MaterialPredefined("G4_STAINLESS-STEEL")
    supportXSectionLogical = _g4.LogicalVolume(
        supportXSection, supportXSectionMaterial, name + "_supportXSectionLogical", reg
    )

    supportY = verticalPad * vHeight - 3 * vSectionSize - lengthSafety
    supportYSectionOuter = _g4.solid.Box(
        name + "_supportYOuter", vSectionSize, vSectionSize, supportY, reg, lunit="m"
    )
    supportYSectionInner = _g4.solid.Box(
        name + "_supportYInner",
        vSectionSize - vSectionThickness,
        vSectionSize - vSectionThickness,
        supportY - vSectionThickness,
        reg,
        lunit="m",
    )
    supportYSection = _g4.solid.Subtraction(
        name + "_supportYSection",
        supportYSectionOuter,
        supportYSectionInner,
        [[0, 0, 0], [0, 0, 0]],
        reg,
    )
    supportYSectionMaterial = _g4.MaterialPredefined("G4_STAINLESS-STEEL")
    supportYSectionLogical = _g4.LogicalVolume(
        supportYSection, supportYSectionMaterial, name + "_supportYSectionLogical", reg
    )

    supportZSectionPhysical1 = _g4.PhysicalVolume(
        [0, 0, 0],
        [
            horizontalPad * vWidth / 2 - vSectionSize,
            verticalPad * vHeight / 2 - vSectionSize,
            0,
            "m",
        ],
        supportZSectionLogical,
        name + "_supportZSectionPhysical1",
        supportLogical,
        reg,
    )
    supportZSectionPhysical2 = _g4.PhysicalVolume(
        [0, 0, 0],
        [
            horizontalPad * vWidth / 2 - vSectionSize,
            -(verticalPad * vHeight / 2 - vSectionSize),
            0,
            "m",
        ],
        supportZSectionLogical,
        name + "_supportZSectionPhysical2",
        supportLogical,
        reg,
    )
    supportZSectionPhysical3 = _g4.PhysicalVolume(
        [0, 0, 0],
        [
            -(horizontalPad * vWidth / 2 - vSectionSize),
            verticalPad * vHeight / 2 - vSectionSize,
            0,
            "m",
        ],
        supportZSectionLogical,
        name + "_supportZSectionPhysical3",
        supportLogical,
        reg,
    )
    supportZSectionPhysical4 = _g4.PhysicalVolume(
        [0, 0, 0],
        [
            -(horizontalPad * vWidth / 2 - vSectionSize),
            -(verticalPad * vHeight / 2 - vSectionSize),
            0,
            "m",
        ],
        supportZSectionLogical,
        name + "_supportZSectionPhysical4",
        supportLogical,
        reg,
    )

    for iSupport in range(0, nSupport, 1):
        z = iSupport * (supportZ - sectionSize) / (nSupport - 1) - (supportZ - sectionSize) / 2.0
        supportXSectionPhysical1 = _g4.PhysicalVolume(
            [0, _np.pi / 2.0, 0],
            [0, verticalPad * vHeight / 2 - vSectionSize, z, "m"],
            supportXSectionLogical,
            name + "_supportXSectionPhysical1_" + str(iSupport),
            supportLogical,
            reg,
        )
        supportXSectionPhysical2 = _g4.PhysicalVolume(
            [0, _np.pi / 2.0, 0],
            [0, -(verticalPad * vHeight / 2 - vSectionSize), z, "m"],
            supportXSectionLogical,
            name + "_supportXSectionPhysical2_" + str(iSupport),
            supportLogical,
            reg,
        )

        supportYSectionPhysical1 = _g4.PhysicalVolume(
            [_np.pi / 2.0, 0, 0],
            [horizontalPad * vWidth / 2 - vSectionSize, 0, z, "m"],
            supportYSectionLogical,
            name + "_supportYSectionPhysical1_" + str(iSupport),
            supportLogical,
            reg,
        )
        supportYSectionPhysical2 = _g4.PhysicalVolume(
            [_np.pi / 2.0, 0, 0],
            [-(horizontalPad * vWidth / 2 - vSectionSize), 0, z, "m"],
            supportYSectionLogical,
            name + "_supportYSectionPhysical2_" + str(iSupport),
            supportLogical,
            reg,
        )

    # set world volume
    reg.setWorld(supportLogical.name)

    ################################
    # visualisation
    ################################
    if vis:
        v = _vis.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.view(interactive=interactive)

    return {"logical": supportLogical}


def Test(vis=False, interactive=False):

    reg = _g4.Registry()

    table = SupportTable(reg=reg, vis=vis, interactive=interactive)

    ################################
    # write gdml
    ################################
    w = _gd.Writer()
    w.addDetector(reg)
    w.write("support.gdml")
