import sys
from optparse import OptionParser
import pyg4ometry as _pyg4
import numpy as _np


def _loadFile(fileName):
    reg, wl = None, None
    if fileName.find(".gdml") != -1:
        r = _pyg4.gdml.Reader(fileName)
        reg = r.getRegistry()
        wl = reg.getWorldVolume()
    elif fileName.find(".root") != -1:
        r = _pyg4.io.ROOTTGeo.Reader(fileName)
        reg = r.getRegistry()
        wl = reg.getWorldVolume()
    elif fileName.find(".inp") != -1:
        r = _pyg4.fluka.Reader(fileName)
        reg = _pyg4.convert.fluka2Geant4(r.getRegistry())
        wl = reg.getWorldVolume()
    elif fileName.find(".stl") != -1:
        reg = _pyg4.geant4.Registry()
        r = _pyg4.stl.Reader(fileName, registry=reg)
        s = r.getSolid()

        stl_log = _pyg4.geant4.LogicalVolume(s, "G4_Ag", "stl_log", reg)
        stl_ext = _np.array(stl_log.extent(True))
        stl_dext = stl_ext[1] - stl_ext[0]
        stl_cext = (stl_ext[1] + stl_ext[0]) / 2

        ws = _pyg4.geant4.solid.Box("ws", stl_dext[0], stl_dext[1], stl_dext[2], reg)
        wl = _pyg4.geant4.LogicalVolume(ws, "G4_Galactic", "wl", reg)
        stl_phy = _pyg4.geant4.PhysicalVolume(
            [0, 0, 0], list(-stl_cext), stl_log, "stl_phy", wl, reg
        )

        reg.setWorld(wl)
    elif fileName.find(".stp") != -1:
        errMsg = ".stp file loading not yet implement in command line interface"
        raise NotImplementedError(errMsg)
    else:
        errMsg = "unknown format: '" + fileName.split(".")[-1] + "'"
        raise OSError(errMsg)

    return reg, wl


def _writeFile(fileName, reg):
    if fileName.find(".gdml") != -1:
        ow = _pyg4.gdml.Writer(fileName)
        ow.addDetector(reg)
        ow.write(fileName)
    elif fileName.find(".inp") != -1:
        freg = _pyg4.convert.geant4Reg2FlukaReg(reg)
        ow = _pyg4.fluka.Writer()
        ow.addDetector(freg)
        ow.write(fileName)
    elif fileName.find(".usd") != -1:
        errMsg = ".usd file writing not yet implement in command line interface"
        raise NotImplementedError(errMsg)
    else:
        errMsg = "unknown format: '" + fileName.split(".")[-1] + "'"
        raise OSError(errMsg)


def _parseStrMultipletAsFloat(strTriplet):
    return list(map(float, strTriplet.split(",")))


def _parseStrPythonAsSolid(reg, strPython):
    locals = {}
    solid = exec(
        "s = _pyg4.geant4.solid." + strPython,
        {"reg": reg, "_pyg4": _pyg4, "_np": _np},
        locals,
    )

    # get solid name
    # solidName = str(strPython.split("(")[1].split(",")[0]).replace("'", "")
    return locals["s"]


def _parseStrPythonAsDict(strPython):
    locals = {}
    exec("d= " + strPython, globals(), locals)
    return locals["d"]


def _printCitation():
    print("https://zenodo.org/doi/10.5281/zenodo.10449301")


def cli(
    inputFileName=None,
    view=False,
    bounding=False,
    checkOverlaps=False,
    analysis=False,
    nullMeshException=False,
    compareFileName=None,
    appendFileName=None,
    lvName=None,
    info=None,
    exchangeLvName=None,
    clip=None,
    solid=None,
    translation=None,
    rotation=None,
    materials=None,
    outputFileName=None,
    planeCutterData=None,
    planeCutterOutputFileName=None,
    featureData=None,
    featureDataOutputFileName=None,
    gltfScale=None,
    verbose=None,
):
    print("pyg4 - command line interface")

    # switch on file type
    if not inputFileName:
        print("pyg4> need input file name")

    try:
        open(inputFileName)
    except FileNotFoundError:
        print("pyg4> input file not found")
        return

    if nullMeshException:
        _pyg4.config.meshingNullException = not nullMeshException

    reg, wl = _loadFile(inputFileName)

    # extract lv in new registry etc
    if lvName is not None:
        lv = reg.logicalVolumeDict[lvName]
        reg1 = _pyg4.geant4.Registry()
        reg1.addVolumeRecursive(lv)
        reg = reg1
        reg.setWorld(lv)
        lw = reg.getWorldVolume()

    if bounding:
        bbExtent = _np.array(wl.extent())
        bbDExtent = bbExtent[1] - bbExtent[0]
        bbCentre = bbExtent[0] + bbExtent[1]

        print("pyg4> extent        ", bbExtent)
        print("pyg4> extent size   ", bbDExtent)
        print("pyg4> extent centre ", bbCentre)

    if info:
        if info == "reg":
            print("pyg4> registry defines")
            print(list(reg.defineDict.keys()))
            print("pyg4> registry materials")
            print(list(reg.materialDict.keys()))
            print("pyg4> registry solids")
            print(list(reg.solidDict.keys()))
            print("pyg4> registry logical volumes")
            print(list(reg.logicalVolumeDict.keys()))
            print("pyg4> registry assembly volumes")
            print(list(reg.assemblyVolumeDict.keys()))
            print("pyg4> registry physical volumes")
            print(list(reg.physicalVolumeDict.keys()))
            print("pyg4> registry optical surfaces")
            print(list(reg.surfaceDict.keys()))
        elif info == "tree":
            _pyg4.geant4.DumpGeometryStructureTree(wl, 0)
        elif info == "instances":
            print("pyg4> Not yet implemented")

    if checkOverlaps:
        print("pyg4> checkoverlaps")
        wl.checkOverlaps(True)

    if analysis:
        print("pyg4> analysis")
        a = _pyg4.geant4.AnalyseGeometryComplexity(reg.getWorldVolume())
        a.printSummary()

    if compareFileName is not None:
        creg, cwl = _loadFile(compareFileName)
        comparision = _pyg4.compare.geometry(wl, cwl, _pyg4.compare.Tests(), False)
        print("pyg4> compare")
        comparision.print()

    if appendFileName is not None:
        reg1, wl1 = _loadFile(appendFileName)
        wp1 = _pyg4.geant4.PhysicalVolume(rotation, translation, wl1, "l1_pv", wl, reg)
        print("pyg4> append")
        reg.addVolumeRecursive(wp1)

    # parse solid
    newSolid = None
    if solid is not None:
        newSolid = _parseStrPythonAsSolid(reg, solid)

    if exchangeLvName is not None:
        lvToChange = reg.logicalVolumeDict[exchangeLvName]
        lvToChange.replaceSolid(newSolid, rotation=rotation, position=translation)
        lvToChange.reMesh()

    if clip is not None:
        wl.clipGeometry(wl.solid, (0, 0, 0), (0, 0, 0))

    if materials is not None:
        errMsg = "materials flag is not implemented yet"
        raise NotImplementedError(errMsg)

    if outputFileName is not None:
        if outputFileName.find(".gl") != -1:
            v = _pyg4.visualisation.VtkViewerColouredMaterialNew()
            v.addLogicalVolume(reg.getWorldVolume())
            v.removeInvisible()
            if gltfScale is not None:
                v.scaleScene(float(gltfScale))
            v.buildPipelinesAppend()
            v.exportGLTFScene(outputFileName)
        if outputFileName.find(".html") != -1:
            v = _pyg4.visualisation.VtkViewerColouredMaterialNew()
            v.addLogicalVolume(reg.getWorldVolume())
            v.removeInvisible()
            if gltfScale is not None:
                v.scaleScene(float(gltfScale))
            v.buildPipelinesAppend()
            v.exportThreeJSScene(outputFileName.split(".")[0])
        else:
            _writeFile(outputFileName, reg)

    if view:
        v = _pyg4.visualisation.VtkViewerColouredMaterialNew()
        v.addLogicalVolume(reg.getWorldVolume())
        v.removeInvisible()
        v.buildPipelinesAppend()

        if bounding:
            v.addAxes(_pyg4.visualisation.axesFromExtents(bbExtent)[0])
        v.view(interactive=True)

    if planeCutterData is not None:
        if planeCutterOutputFileName is None:
            print("pyg4> must specify -P or --planeCutterOutput file")
            exit(1)
        # up the quality of meshes
        _pyg4.config.setGlobalMeshSliceAndStack(56)
        v = _pyg4.visualisation.VtkViewerColouredMaterialNew()
        v.addLogicalVolume(wl)
        o = planeCutterData[:3]
        n = planeCutterData[3:]
        v.addCutter("cli-cutter", o, n)
        v.buildPipelinesAppend()
        v.exportCutter("cli-cutter", planeCutterOutputFileName)
        print(
            "pyg4> cutter with " + str(o) + ", " + str(n) + " written to: ",
            planeCutterOutputFileName,
        )

    if featureData is not None or featureDataOutputFileName is not None:
        errMsg = "feature data has not yet been implemented in the command line interface"
        raise NotImplementedError(errMsg)
        # TBC!!!


def main():
    parser = OptionParser()
    parser.add_option(
        "-a",
        "--analysis",
        help="geometry information",
        action="store_true",
        dest="analysis",
    )
    parser.add_option(
        "-b",
        "--bounding",
        help="calculate bounding box",
        action="store_true",
        dest="bounding",
    )
    parser.add_option(
        "-c",
        "--checkoverlaps",
        help="check overlaps",
        dest="checkOverlaps",
        action="store_true",
    )
    parser.add_option(
        "-C",
        "--clip",
        help="clip to mother world solid. Or exchanged solid if specified",
        action="store_true",
        dest="clip",
    )
    parser.add_option(
        "-d",
        "--compare",
        help="comp(a)re geometry",
        dest="compareFileName",
        metavar="COMPAREFILE",
    )
    parser.add_option(
        "-e",
        "--append",
        help="app(e)nd geometry",
        dest="appendFileName",
        metavar="APPENDFILE",
    )
    parser.add_option(
        "-f",
        "--feature",
        help="feature extraction from simple geometry (planeQuality,circumference)",
        dest="featureData",
    )
    parser.add_option(
        "-F",
        "--featureExtractOutput",
        help="feature extract output",
        dest="featureExtactOutputFileName",
        metavar="FEATUREFILE",
    )
    parser.add_option(
        "-i",
        "--file",
        dest="inputFileName",
        help="(i)nput file (gdml, stl, inp, step)",
        metavar="INFILE",
    )
    parser.add_option(
        "-I",
        "--info",
        help="information on geometry (tree, reg, instance)",
        dest="info",
    )
    parser.add_option(
        "-l",
        "--logical",
        help="extract logical LVNAME",
        dest="lvName",
        metavar="LVNAME",
    )
    parser.add_option(
        "-m",
        "--material",
        help='material dictionary ("lvname":"nist")',
        dest="material",
    )
    parser.add_option(
        "-n",
        "--nullmesh",
        help="disable null mesh exception",
        action="store_true",
        dest="nullmesh",
    )
    parser.add_option(
        "-o",
        "--output",
        dest="outputFileName",
        help="(o)utout file (gdml, inp, usd, vtp)",
        metavar="OUTFILE",
    )
    parser.add_option(
        "-p",
        "--planeCutter",
        help="add (p)plane cutter -p x,y,z,nx,ny,nz",
        dest="planeCutter",
    )
    parser.add_option(
        "-P",
        "--planeCutterOutput",
        help="plane cutter output file",
        dest="planeCutterOutputFileName",
        metavar="CUTTERFILE",
    )
    parser.add_option(
        "-r",
        "--rotation",
        help="rotation (Tait-Bryan) tx,ty,tz (used with append/exchange)",
        dest="rotation",
        metavar="TX,TY,TZ",
    )
    parser.add_option(
        "-s",
        "--solid",
        help="solid in python constructor syntax (used with exchange). Registry must be reg and _np used for numpy",
        dest="solidCode",
        metavar="PYTHONSOLID",
    )
    parser.add_option(
        "-S",
        "--gltfScale",
        help="scale factor for gltf conversion",
        dest="gltfScale",
        metavar="SCALE",
    )
    parser.add_option(
        "-t",
        "--translation",
        help="translation x,y,z (used with append/exchange)",
        dest="translation",
        metavar="X,Y,Z",
    )
    parser.add_option("-v", "--view", help="view geometry", action="store_true", dest="view")
    parser.add_option("-V", "--verbose", help="verbose script", dest="verbose", action="store_true")
    parser.add_option(
        "-x",
        "--exchange",
        help="replace solid for logical volume, LVNAME is logical volume name",
        dest="exchangeLvName",
        metavar="LVNAME",
    )
    parser.add_option(
        "-z", "--citation", help="print citation text", dest="citation", action="store_true"
    )

    # features
    (options, args) = parser.parse_args()

    verbose = options.__dict__["verbose"]
    if verbose:
        print("pyg4> options")
        print(options)

    if options.__dict__["citation"]:
        _printCitation()
        exit(0)

    # absolutely need a file name
    if options.__dict__["inputFileName"] is None:
        print("pyg4> need an input file")
        exit(1)

    # parse plane
    planeData = options.__dict__["planeCutter"]
    if planeData is not None:
        planeData = _parseStrMultipletAsFloat(planeData)
        print("pyg4> clipper plane data", planeData)

    # parse translation
    translation = options.__dict__["translation"]
    if translation is not None:
        translation = _parseStrMultipletAsFloat(translation)
        if verbose:
            print("pyg4> translation ", translation)

    # parse rotation
    rotation = options.__dict__["rotation"]
    if rotation is not None:
        rotation = _parseStrMultipletAsFloat(rotation)
        if verbose:
            print("pyg4> rotation ", rotation)

    # parse solid
    # this must be done when we have a registry

    # parse feature data
    featureData = options.__dict__["featureData"]
    if featureData is not None:
        featureData = _parseStrMultipletAsFloat(featureData)
        if verbose:
            print("pyg4> feature data", featureData)

    # parse gltf scale
    gltfScale = options.__dict__["gltfScale"]
    if gltfScale is not None:
        gltfScale = _parseStrMultipletAsFloat(gltfScale)

    cli(
        inputFileName=options.__dict__["inputFileName"],
        view=options.__dict__["view"],
        bounding=options.__dict__["bounding"],
        checkOverlaps=options.__dict__["checkOverlaps"],
        analysis=options.__dict__["analysis"],
        nullMeshException=options.__dict__["nullmesh"],
        info=options.__dict__["info"],
        lvName=options.__dict__["lvName"],
        compareFileName=options.__dict__["compareFileName"],
        appendFileName=options.__dict__["appendFileName"],
        solid=options.__dict__["solidCode"],
        exchangeLvName=options.__dict__["exchangeLvName"],
        clip=options.__dict__["clip"],
        translation=translation,
        rotation=rotation,
        outputFileName=options.__dict__["outputFileName"],
        planeCutterData=planeData,
        planeCutterOutputFileName=options.__dict__["planeCutterOutputFileName"],
        featureData=featureData,
        featureDataOutputFileName=options.__dict__["featureExtactOutputFileName"],
        gltfScale=options.__dict__["gltfScale"],
        verbose=verbose,
    )


if __name__ == "__main__":
    main()
