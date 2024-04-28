from ..visualisation import VtkViewerNew as _VtkViewerNew
from ..visualisation.Convert import vtkPolyDataToNumpy as _vtkPolyDataToNumpy
from ..gdml import Reader as _GdmlReader
from .flukaData import Usrdump as _Usrdump
import matplotlib.pyplot as _plt
import numpy as _np


def plotEventSections():
    pass


def plotEventSection(geometryFile, flukaFile=None, bdsimFile=None):
    pass


def plotScoringMeshSection(
    geometryFile, planeAxis=1, flukaFile=None, flukaBin=None, bdsimFile=None, bdsimHisto=None
):
    v = _VtkViewerNew()
    r = _GdmlReader(geometryFile)
    l = r.getRegistry().getWorldVolume()
    v.addCutter("c1", [0, 0, 0], [0, 1, 0])
    v.addLogicalVolume(l)
    v.buildPipelinesSeparate()
    v.view()
    cut = _vtkPolyDataToNumpy(v.getCutterPolydata("c1"))

    coords = _np.array([0, 1, 2])
    for s in cut:
        s = s[:, coords != planeAxis]

        _plt.plot(s[:, 0], s[:, 1])

    return (cut, v)


def flukaEventDisplay(gdmlFile, dumpFile, iEvent, nEventToRead=1000000):
    r = _GdmlReader(gdmlFile)
    v = _VtkViewerNew()
    v.addLogicalVolume(r.getRegistry().getWorldVolume())
    v.buildPipelinesAppend()

    fd = open(dumpFile, "rb")
    ud = _Usrdump(fd, nEventToRead)
    ud.read_event(fd, iEvent)

    pd = ud.trackDataToPolydata()
    v.addTracks(pd)

    v.addAxes()
    v.view()
