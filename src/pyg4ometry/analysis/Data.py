import logging
import numpy as _np
import matplotlib.pyplot as _plt
from ..analysis.flukaData import FlukaBdxData as _FlukaBdxData
from ..analysis.flukaData import FlukaBinData as _FlukaBinData

_import_failed = []
try:
    from pybdsim.Data import TH1 as _TH1
    from pybdsim.Data import TH2 as _TH2
    from pybdsim.Data import TH3 as _TH3
except ImportError:
    _import_failed.append("pybdsim")

try:
    from ROOT import TH1D as _TH1D
    from ROOT import TH2D as _TH2D
    from ROOT import TH3D as _TH3D
    from ROOT import TH1F as _TH1F
    from ROOT import TH2F as _TH2F
    from ROOT import TH3F as _TH3F
except ImportError:
    _import_failed.append("ROOT")

_log = logging.getLogger(__name__)


def _warn_import_failed():
    global _import_failed
    if _import_failed != []:
        msg = f"Failed to import {_import_failed}"
        _log.warning(msg)
        _import_failed = []


class TH1:
    def __init__(self, data, nPrimary=1, flukaBdxVariable="energy"):
        self.name = None
        self.nPrimary = nPrimary
        self.contents = None
        self.errors = None
        self.xnbins = None
        self.xcentres = None
        self.xedges = None
        self.xlowedges = None
        self.xhighedges = None

        _warn_import_failed()

        if type(data) is _FlukaBdxData:
            print("flukaBdxData")
            self.name = data.name.strip()
            if flukaBdxVariable == "angle":
                self.contents = data.data.sum(0)  # integrate over energy
                self.xnbins = data.na
                self.xedges = _np.linspace(data.alow, data.ahigh, data.na + 1)
            elif flukaBdxVariable == "energy":
                self.contents = data.data.sum(1)  # integrate over angle
                self.xnbins = data.ne
                self.xedges = _np.linspace(data.elow, data.ehigh, data.ne + 1)

            self.xcentres = _np.convolve(self.xedges, [0.5, 0.5])[1:-1]
            self.xlowedge = self.xedges[0:-1]
            self.xhighedge = self.xedges[1:]
            self.xwidth = self.xhighedge - self.xlowedge

            self.contents = self.contents * self.nPrimary / self.xwidth

            # self.errors =

        elif type(data) is _TH1:
            print("pybdsim data")
            self.name = data.name
            self.nPrimary = nPrimary
            self.contents = data.contents
            self.errors = data.errors
            self.xnbins = data.nbinsx
            self.xcentres = data.xcentres
            self.xedges = data.xedges
            self.xlowedge = data.xlowedge
            self.xhighedge = data.xhighedge
            self.xwidths = data.xwidths
            self.contents = self.contents / self.xwidths

        elif type(data) is _TH1D:
            print("ROOT data")

    def __getitem__(self, slice):
        print(slice)

    def plot(self, ms="."):
        _plt.plot(self.xcentres, self.contents, ms)


class TH2:
    def __init__(self, data, nPrimary=1):
        _warn_import_failed()

        if type(data) is _TH2:
            self.name = data.name
            self.nPrimary = nPrimary

            self.contents = data.contents
            self.errors = data.errors

            self.xnbins = data.nbinsx
            self.ynbins = data.nbinsy

            self.xcentres = data.xcentres
            self.ycentres = data.ycentres

            self.xedges = data.xedges
            self.yedges = data.yedges

            self.xlowedge = data.xlowedge
            self.ylowedge = data.ylowedge

            self.xhighedge = data.xhighedge
            self.yhighedge = data.yhighedge

            self.xwidths = data.xwidths
            self.ywidths = data.ywidths

    def __getitem__(self, slice):
        print(slice)

    def plot(self):
        pass


class TH3:
    def __init__(self, data, nPrimary=1):
        _warn_import_failed()

        if type(data) is _FlukaBinData:
            self.name = data.name.strip()
            self.nPrimary = data

            self.contents = data.data
            try:
                self.errors = data.errors
            except AttributeError:
                self.errors = None

            self.xnbins = data.e1n
            self.ynbins = data.e2n
            self.znbins = data.e3n

            self.xedges = _np.linspace(data.e1low, data.e1high, data.e1n + 1)
            self.yedges = _np.linspace(data.e2low, data.e2high, data.e2n + 1)
            self.zedges = _np.linspace(data.e3low, data.e3high, data.e3n + 1)

            self.xcentres = _np.convolve(self.xedges, [0.5, 0.5])[1:-1]
            self.ycentres = _np.convolve(self.yedges, [0.5, 0.5])[1:-1]
            self.zcentres = _np.convolve(self.zedges, [0.5, 0.5])[1:-1]

            self.xlowedge = self.xedges[0:-1]
            self.ylowedge = self.yedges[0:-1]
            self.zlowedge = self.zedges[0:-1]

            self.xhighedge = self.xedges[1:]
            self.yhighedge = self.yedges[1:]
            self.zhighedge = self.zedges[1:]

            self.xwidth = self.xhighedge - self.xlowedge
            self.ywidth = self.yhighedge - self.ylowedge
            self.zwidth = self.zhighedge - self.zlowedge

        elif type(data) is _TH3:
            self.name = data.name
            self.nPrimary = nPrimary

            self.contents = data.contents
            self.errors = data.errors

            self.xnbins = data.nbinsx
            self.ynbins = data.nbinsy
            self.znbins = data.nbinsz

            self.xcentres = data.xcentres
            self.ycentres = data.ycentres
            self.zcentres = data.zcentres

            self.xedges = data.xedges
            self.yedges = data.yedges
            self.zedges = data.zedges

            self.xlowedge = data.xlowedge
            self.ylowedge = data.ylowedge
            self.zlowedge = data.zlowedge

            self.xhighedge = data.xhighedge
            self.yhighedge = data.yhighedge
            self.zhighedge = data.zhighedge

            self.xwidths = data.xwidths
            self.ywidths = data.ywidths
            self.zwidths = data.zwidths

    def __getitem__(self, slice):
        print(slice)

    def plot(self):
        pass

    def plot3Projections(self):
        import matplotlib.pyplot as _plt

        _plt.subplot(2, 2, 1)
        _plt.imshow(_np.log10(self.contents[:, :, 30]))

        _plt.subplot(2, 2, 2)
        _plt.imshow(_np.log10(self.contents[:, 30, :]))

        _plt.subplot(2, 2, 3)
        _plt.imshow(_np.log10(self.contents[30, :, :]))

        _plt.colorbar()
