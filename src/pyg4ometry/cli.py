import sys
import logging
from optparse import OptionParser, OptParseError
import pyg4ometry as _pyg4
import numpy as _np


class OptionParserTestable(OptionParser):
    """
    This class wraps the general OptionParser and if the flag
    for noExit is set to True, then it throws an exception instead
    of the default sys.exit(). This allows testing of the parser.
    """

    def __init__(self, *args, noExit=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.noExit = noExit

    def exit(self, status=0, msg=None):
        if msg:
            sys.stderr.write(msg)
        if self.noExit:
            msg2 = f"Status:{status}  {msg}"
            raise OptParseError(msg2)
        else:
            sys.exit(status)

    def error(self, msg):
        self.print_usage(sys.stderr)
        msg2 = f"Status:2 {self.get_prog_name()}: error: {msg}\n"
        if self.noExit:
            raise OptParseError(msg2)
        else:
            self.exit(2, msg2)


def _loadFile(fileName):
    # convert to string for possible pathlib path object from testing data
    if type(fileName) != str:
        fileName = str(fileName)
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
    elif fileName.find(".stp") != -1 or fileName.find(".step") != -1:
        r = _pyg4.pyoce.Reader(str(fileName))
        ls = r.freeShapes()
        worldName = _pyg4.pyoce.pythonHelpers.get_TDataStd_Name_From_Label(ls.Value(1))
        mats, skip, mesh = {}, [], {}
        reg = _pyg4.convert.oce2Geant4(r.shapeTool, worldName, mats, skip, mesh)
        wl = reg.logicalVolumeDict[worldName]
    else:
        errMsg = "unknown format: '" + fileName.split(".")[-1] + "'"
        raise OSError(errMsg)

    return reg, wl


def _writeFile(fileName, reg):
    # this assumes we have always converted to Geant4 beforehand.
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
        # TODO
        errMsg = ".usd file writing not yet implement in command line interface"
        raise NotImplementedError(errMsg)
    else:
        errMsg = "unknown format: '" + fileName.split(".")[-1] + "'"
        raise OSError(errMsg)


def _parseStrMultipletAsFloat(strTriplet):
    def evalulate(str):
        reg = _pyg4.geant4.Registry()
        e = _pyg4.gdml.Expression("temp", str, reg)
        return e.eval()

    return list(map(evalulate, strTriplet.split(",")))


def _parseStrPythonAsSolid(reg, strPython):
    # TODO = finish locals
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
    print("https://zenodo.org/doi/10.5281/zenodo.10449301")  # noqa: T201


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
    testing=False,
):
    logging.basicConfig()

    print("pyg4 - command line interface")  # noqa: T201

    # switch on file type
    if not inputFileName:
        print("pyg4> need input file name")  # noqa: T201

    try:
        if str(inputFileName).startswith("g4edgetestdata/"):
            try:
                import g4edgetestdata

                d = g4edgetestdata.G4EdgeTestData()
                inputFileName = d[inputFileName.replace("g4edgetestdata/", "")]
            except ImportError:
                print("pyg4> g4edgetestdata package not available - install with pip")  # noqa: T201
        f = open(inputFileName)
        f.close()
    except FileNotFoundError:
        errMsg = "pyg4> input file not found"
        raise FileNotFoundError(errMsg)

    if nullMeshException:
        _pyg4.config.meshingNullException = not nullMeshException

    reg, wl = _loadFile(inputFileName)

    if bounding:
        bbExtent = _np.array(wl.extent())
        bbDExtent = bbExtent[1] - bbExtent[0]
        bbCentre = bbExtent[0] + bbExtent[1]
        print("pyg4> extent        ", bbExtent)  # noqa: T201
        print("pyg4> extent size   ", bbDExtent)  # noqa: T201
        print("pyg4> extent centre ", bbCentre)  # noqa: T201

    # these are not used on their own but possibly as part of other commands in multiple places
    r = rotation if rotation else [0, 0, 0]
    t = translation if translation else [0, 0, 0]

    if info:
        if info == "reg":
            print("pyg4> registry defines")  # noqa: T201
            print(list(reg.defineDict.keys()))  # noqa: T201
            print("pyg4> registry materials")  # noqa: T201
            print(list(reg.materialDict.keys()))  # noqa: T201
            print("pyg4> registry solids")  # noqa: T201
            print(list(reg.solidDict.keys()))  # noqa: T201
            print("pyg4> registry logical volumes")  # noqa: T201
            print(list(reg.logicalVolumeDict.keys()))  # noqa: T201
            print("pyg4> registry assembly volumes")  # noqa: T201
            print(list(reg.assemblyVolumeDict.keys()))  # noqa: T201
            print("pyg4> registry physical volumes")  # noqa: T201
            print(list(reg.physicalVolumeDict.keys()))  # noqa: T201
            print("pyg4> registry optical surfaces")  # noqa: T201
            print(list(reg.surfaceDict.keys()))  # noqa: T201
        elif info == "tree":
            _pyg4.geant4.DumpGeometryStructureTree(wl, 0)
        elif info == "instances":
            print("pyg4> Not yet implemented")  # noqa: T201
        else:
            errMsg = "Accepted info keys are 'reg', 'tree', 'instances'"
            raise ValueError(errMsg)

    if checkOverlaps:
        print("pyg4> checkoverlaps")  # noqa: T201
        wl.checkOverlaps(True)

    if analysis:
        print("pyg4> analysis")  # noqa: T201
        a = _pyg4.geant4.AnalyseGeometryComplexity(reg.getWorldVolume())
        a.printSummary()

    if compareFileName is not None:
        creg, cwl = _loadFile(compareFileName)
        comparision = _pyg4.compare.geometry(wl, cwl, _pyg4.compare.Tests(), False)
        print("pyg4> compare")  # noqa: T201
        comparision.print()

    if appendFileName is not None:
        reg1, wl1 = _loadFile(appendFileName)
        wp1 = _pyg4.geant4.PhysicalVolume(r, t, wl1, "l1_pv", wl, reg)
        print("pyg4> append")  # noqa: T201
        reg.addVolumeRecursive(wp1)

    # extract lv in new registry etc
    if lvName is not None:
        lv = reg.logicalVolumeDict[lvName]
        reg1 = _pyg4.geant4.Registry()
        reg1.addVolumeRecursive(lv)
        reg = reg1
        reg.setWorld(lv)
        wl = reg.getWorldVolume()

    if solid is not None:
        newSolid = _parseStrPythonAsSolid(reg, solid)
        if exchangeLvName is None:
            errMsg = "pyg4> must specify the LV with -x to exchange the solid in."
            raise ValueError(errMsg)
        lvToChange = reg.logicalVolumeDict[exchangeLvName]
        lvToChange.replaceSolid(newSolid, r, t)
        lvToChange.reMesh()

    if clip is not None:
        if len(clip) != 3:
            errMsg = "pyg4> clip must be supplied with exactly 3 numbers"
            raise ValueError(errMsg)
        clipBoxes = _pyg4.misc.NestedBoxes(
            "clipper", clip[0], clip[1], clip[2], reg, "mm", 1e-3, 1e-3, 1e-3, wl.depth()
        )
        wl.clipGeometry(clipBoxes, r, t)

    if materials is not None:
        # TODO - implement
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
        elif outputFileName.find(".html") != -1:
            v = _pyg4.visualisation.VtkViewerColouredMaterialNew()
            v.addLogicalVolume(reg.getWorldVolume())
            v.removeInvisible()
            if gltfScale is not None:
                v.scaleScene(float(gltfScale))
            v.buildPipelinesAppend()
            try:
                v.exportThreeJSScene(str(outputFileName).split(".")[0])
            except ModuleNotFoundError:
                errMsg = (
                    "pyg4> html export requires the jinja2 package that is not a formal dependency"
                )
                raise ModuleNotFoundError(errMsg)
        else:
            _writeFile(outputFileName, reg)

    if view:
        v = _pyg4.visualisation.VtkViewerColouredMaterialNew()
        v.addLogicalVolume(reg.getWorldVolume())
        v.removeInvisible()
        v.buildPipelinesAppend()

        if bounding:
            v.addAxes(_pyg4.visualisation.axesFromExtents(bbExtent)[0])
        interactive = not testing
        v.view(interactive=interactive)

    if planeCutterData is not None:
        if planeCutterOutputFileName is None:
            errMsg = "pyg4> must specify -P or --planeCutterOutput file"
            raise ValueError(errMsg)
        # up the quality of meshes
        _pyg4.config.setGlobalMeshSliceAndStack(56)
        v = _pyg4.visualisation.VtkViewerColouredMaterialNew()
        v.addLogicalVolume(wl)
        o = planeCutterData[:3]
        n = planeCutterData[3:]
        v.addCutter("cli-cutter", o, n)
        v.buildPipelinesAppend()
        v.exportCutter("cli-cutter", planeCutterOutputFileName)
        print(  # noqa: T201
            "pyg4> cutter with " + str(o) + ", " + str(n) + " written to: ",
            planeCutterOutputFileName,
        )

    if featureData is not None or featureDataOutputFileName is not None:
        errMsg = "feature data has not yet been implemented in the command line interface"
        raise NotImplementedError(errMsg)
        # TODO


def mainNoExceptions(testArgs=None, testing=False):
    """A separate function to nicely wrap exception catching in one place."""
    try:
        main(testArgs, testing)
    except Exception as ex:
        print(*ex.args)  # noqa: T201
        exit(1)


def main(testArgs=None, testing=False):
    parser = OptionParserTestable(noExit=testing)
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
        help="clip to a box of full widths px,py,pz in mm",
        dest="clip",
        metavar="CLIP",
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
        help="append geometry",
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
    (options, args) = parser.parse_args(args=testArgs)

    verbose = options.__dict__["verbose"]
    if verbose:
        print("pyg4> options")  # noqa: T201
        print(options)  # noqa: T201

    if options.__dict__["citation"]:
        _printCitation()
        exit(0)

    # absolutely need a file name
    if options.__dict__["inputFileName"] is None:
        print("pyg4> need an input file")  # noqa: T201
        exit(1)

    # parse plane
    planeData = options.__dict__["planeCutter"]
    if planeData is not None:
        planeData = _parseStrMultipletAsFloat(planeData)
        if verbose:
            print("pyg4> clipper plane data", planeData)  # noqa: T201

    # parse translation
    translation = options.__dict__["translation"]
    if translation is not None:
        translation = _parseStrMultipletAsFloat(translation)
        if verbose:
            print("pyg4> translation ", translation)  # noqa: T201

    # parse rotation
    rotation = options.__dict__["rotation"]
    if rotation is not None:
        rotation = _parseStrMultipletAsFloat(rotation)
        if verbose:
            print("pyg4> rotation ", rotation)  # noqa: T201

    # parse clip box
    clipbox = options.__dict__["clip"]
    if clipbox is not None:
        clipbox = _parseStrMultipletAsFloat(clipbox)
        if verbose:
            print("pyg4> clip ", clipbox)  # noqa: T201

    # parse solid
    # this must be done when we have a registry
    solid = options.__dict__["solidCode"]
    if solid is not None:
        errMsg = "pyg4> solid is not implemented yet"
        raise NotImplementedError(errMsg)

    # parse feature data
    featureData = options.__dict__["featureData"]
    if featureData is not None:
        featureData = _parseStrMultipletAsFloat(featureData)
        if verbose:
            print("pyg4> feature data", featureData)  # noqa: T201

    # parse gltf scale
    gltfScale = options.__dict__["gltfScale"]
    if gltfScale is not None:
        gltfScale = _parseStrMultipletAsFloat(gltfScale)[0]

    cli(
        inputFileName=options.__dict__["inputFileName"],
        view=options.__dict__["view"],
        bounding=options.__dict__["bounding"],
        checkOverlaps=options.__dict__["checkOverlaps"],
        analysis=options.__dict__["analysis"],
        nullMeshException=options.__dict__["nullmesh"],
        compareFileName=options.__dict__["compareFileName"],
        appendFileName=options.__dict__["appendFileName"],
        lvName=options.__dict__["lvName"],
        info=options.__dict__["info"],
        exchangeLvName=options.__dict__["exchangeLvName"],
        clip=clipbox,
        solid=options.__dict__["solidCode"],
        translation=translation,
        rotation=rotation,
        materials=options.__dict__["material"],
        outputFileName=options.__dict__["outputFileName"],
        planeCutterData=planeData,
        planeCutterOutputFileName=options.__dict__["planeCutterOutputFileName"],
        featureData=featureData,
        featureDataOutputFileName=options.__dict__["featureExtactOutputFileName"],
        gltfScale=gltfScale,
        verbose=verbose,
        testing=testing,
    )
