import sys
from optparse import OptionParser
import pyg4ometry as _pyg4
import numpy as _np

def _loadFile(fileName) :
    if fileName.find(".gdml") != -1 :
        r = _pyg4.gdml.Reader(fileName)
        reg = r.getRegistry()
        wl = reg.getWorldVolume()
    elif fileName.find(".root") != -1 :
        r = _pyg4.io.ROOTTGeo.Reader(fileName)
        reg = r.getRegistry()
        wl = reg.getWorldVolume()
    elif fileName.find(".inp") != -1 :
        r = _pyg4.fluka.Reader(fileName)
        reg = _pyg4.convert.fluka2Geant4(r.getRegistry())
        wl = reg.getWorldVolume()
    elif fileName.find(".stl") != -1 :
        reg = _pyg4.geant4.Registry()
        r = _pyg4.stl.Reader(fileName, registry=reg)
        s = r.getSolid()

        stl_log = _pyg4.geant4.LogicalVolume(s,"G4_Ag","stl_log",reg)
        stl_ext = _np.array(stl_log.extent(True))
        stl_dext= stl_ext[1]-stl_ext[0]
        stl_cext= (stl_ext[1]+stl_ext[0])/2

        ws = _pyg4.geant4.solid.Box("ws",stl_dext[0],stl_dext[1],stl_dext[2],reg)
        wl = _pyg4.geant4.LogicalVolume(ws,"G4_Galactic","wl",reg)
        stl_phy = _pyg4.geant4.PhysicalVolume([0,0,0],list(-stl_cext),stl_log,"stl_phy",wl,reg)

        reg.setWorld(wl)
    elif fileName.find(".stp") != -1 :
        pass

    return reg,wl

def _writeFile(fileName, reg) :
    if fileName.find(".gdml") != -1 :
        ow = _pyg4.gdml.Writer(fileName)
        ow.addDetector(reg)
        ow.write(fileName)
    elif fileName.find(".inp") != -1 :
        freg = _pyg4.convert.geant4Reg2FlukaReg(reg)
        ow = _pyg4.fluka.Writer()
        ow.addDetector(freg)
        ow.write(fileName)
    elif fileName.find(".usd") != -1 :
        pass



def cli(inputFileName = None,
        view = False,
        bounding = False,
        checkOverlaps = False,
        analysis = False,
        compareFileName = None,
        outputFileName = None):

    print("pyg4 - command line interface")

    # switch on file type
    if not inputFileName :
        print("pyg4> need input file name")

    try :
        open(inputFileName)
    except FileNotFoundError :
        print("pyg4> input file not found")
        return

    reg, wl = _loadFile(inputFileName)

    if bounding :
        bbExtent = wl.extent()
        print("pyg4> extent",bbExtent)

    if checkOverlaps :
        wl.checkOverlaps(True)

    if analysis :
        a = _pyg4.geant4.AnalyseGeometryComplexity(reg.getWorldVolume())
        a.printSummary()

    if compareFileName is not None :
        creg, cwl = _loadFile(compareFileName)
        comparision = _pyg4.compare.geometry(wl, cwl, _pyg4.compare.Tests(), False)
        comparision.print()

    if outputFileName is not None :
        _writeFile(outputFileName, reg)

    if view :
        v = _pyg4.visualisation.PubViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        if bounding :
            v.addAxes(_pyg4.visualisation.axesFromExtents(bbExtent)[0])
        v.view(interactive=True)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-v", "--view", help="view geometry", action = "store_true", dest = "view")
    parser.add_option("-b", "--bounding", help="calculate bounding box", action = "store_true", dest = "bounding")
    parser.add_option("-a", "--analysis", help="geometry information", action = "store_true", dest="analysis")
    parser.add_option("-c", "--checkoverlaps", help="check overlaps", dest="checkOverlaps", action = "store_true")
    parser.add_option("-n", "--nullmesh", help="disable null mesh exception", dest="nullmesh")
    parser.add_option("-f", "--file", dest="inputFileName",help="input file (gdml, stl, inp, step)", metavar="INFILE")
    parser.add_option("-o", "--output", dest="outputFileName", help="(o)utout file (gdml, inp, usd, vtp)", metavar="OUTFILE")
    parser.add_option("-m","--compare", help="co(m)pare geometry", dest="compareFileName", metavar="COMPAREFILE")
    parser.add_option("-p", "--planeCutter", help="add (p)plane cutter -p x,y,z,nx,ny,nz", dest="planeCutter")
    parser.add_option("-e", "--append", help="add(e)nd geometry", dest="appendFileName", metavar="APPENDFILE")
    # parser.add_option("")

    # features
    (options, args) = parser.parse_args()

    cli(inputFileName=options.__dict__['inputFileName'],
        view=options.__dict__['view'],
        bounding=options.__dict__['bounding'],
        checkOverlaps=options.__dict__['checkOverlaps'],
        analysis=options.__dict__['analysis'],
        compareFileName=options.__dict__['compareFileName'],
        outputFileName=options.__dict__['outputFileName'])
    
