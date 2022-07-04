import sys
from optparse import OptionParser
import pyg4ometry as _pyg4

def cli(inputFileName = None,
        view = False,
        bounding = False):

    print("pyg4 - command line interface")

    # switch on file type
    if not inputFileName :
        print("pyg4> need input file name")

    try :
        open(inputFileName)
    except FileNotFoundError :
        print("pyg4> input file not found")
        return

    if inputFileName.find(".gdml") :
        r = _pyg4.gdml.Reader(inputFileName)
        reg = r.getRegistry()
        wl = reg.getWorldVolume()
    elif inputFileName.find(".root") :
        r = _pyg4.io.ROOTTGeo.Reader(inputFileName)
        reg = r.getRegistry()
        wl = reg.getWorldVolume()

    if bounding :
        bbExtent = wl.extent()
        print("pyg4> extent",bbExtent)

    if view :
        v = _pyg4.visualisation.PubViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        if bounding :
            v.addAxes(_pyg4.visualisation.axesFromExtents(bbExtent)[0])
        v.view(interactive=True)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="inputFileName",
                      help="input file (gdml, stl, inp, step)", metavar="FILE")
    parser.add_option("-v", "--view", help="view geometry", action = "store_true", dest = "view")
    parser.add_option("-b", "--bounding", help="calculate bounding box", action = "store_true", dest = "bounding")
    parser.add_option("-o", "--output", dest="outputFileName",
                      help="input file (gdml, stl, inp, step)", metavar="FILE")

    (options, args) = parser.parse_args()

    cli(inputFileName=options.__dict__['inputFileName'],
        view=options.__dict__['view'],
        bounding=options.__dict__['bounding'])
    
