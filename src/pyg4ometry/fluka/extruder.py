import pyg4ometry.geant4
import pyg4ometry.geant4.solid
import pyg4ometry.pycgal.CGAL
import pyg4ometry.pycgal.pythonHelpers

from ..pycgal import PolygonProcessing
from ..pycgal import Polygon_2
from ..pycgal import Polygon_with_holes_2
from ..pycgal import Point_2
import functools as _functools
import math as _math
import matplotlib.pyplot as _plt
import numpy as _np


class Extruder(pyg4ometry.geant4.solid.SolidBase):
    def __init__(self, name, length, regions=None, materials=None, registry=None):
        super().__init__(name, "extruder", registry)

        self.length = length
        self.regions = regions if regions is not None else dict()
        self.materials = materials if materials is not None else dict()
        self.cgalpolys = {}
        self.extrusions = {}
        self.decomposed = {}
        self.g4_extrusions = {}
        self.g4_decomposed_extrusions = {}

    def addRegion(self, name, material=None):
        self.regions[name] = []
        self.materials[name] = material
        return self.regions[name]

    def addRegionComplete(self, name, pointList, material=None, scale=None, dxdy=None):
        """
        :param name: Unique name of region.
        :type name: str
        :param pointList: list of x,y pairs.
        :type pointList: list([float, float], [float, float]...)
        :param material: material to assign to that region.
        :type material: pyg4ometry.geant4._Material.Material
        :param scale: List of reflections.
        :type scale: None, [float, float, float]
        :param dxdy: optional offset in x,y for a given region.
        :type dxdy: None, [float, float]
        """
        if name in self.regions:
            raise NameError(name+" already in "+self.name)
        if dxdy:
            pointList = [[x + dxdy[0], y + dxdy[1]] for [x, y] in pointList]
        self.materials[name] = material
        if not scale:
            self.regions[name] = pointList
        else:
            # product of +-1 (sign of) scale gives winding order
            winding = int(_functools.reduce(lambda x, y: x*_math.copysign(1.0, y), scale))
            pointListScaled = [[x*scale[0], y*scale[1]] for [x,y] in pointList]
            self.regions[name] = pointListScaled[::winding]

    def addPointToRegion(self, name, pntIndx):
        self.regions[name].append(pntIndx)

    def setRegionToOuterBoundary(self, name):
        self.boundary = name

    def setRegionMaterial(self, name, material):
        self.materials[name] = material

    def getRegionMaterial(self, name):
        return self.materials[name]

    def buildCgalPolygons(self):
        # build a CGAL polygon (without holes for each region)

        holes = []

        for region in self.regions:
            if self.boundary != region:
                self.decomposed[region] = PolygonProcessing.decomposePolygon2d(self.regions[region])
                holes.append(self.regions[region])

        self.decomposed[self.boundary] = PolygonProcessing.decomposePolygon2dWithHoles(
            self.regions[self.boundary], holes
        )

    def buildGeant4Extrusions(self):
        # normal geant4 extrusions
        for region in self.regions:
            g4_extrusions = []

            g4e = pyg4ometry.geant4.solid.ExtrudedSolid(
                region,
                self.regions[region],
                [[-self.length / 2, [0, 0], 1], [self.length / 2, [0, 0], 1]],
                self.registry,
                lunit="mm",
            )

            self.g4_extrusions[region] = g4e

        # decomposed geant4 extrusions
        for region in self.regions:
            g4_decomposed_extrusions = []

            pgonList = self.decomposed[region]

            for pgon, idecomp in zip(pgonList, range(len(pgonList))):
                g4e = pyg4ometry.geant4.solid.ExtrudedSolid(
                    region + "_" + str(idecomp),
                    _np.array(pgon),
                    [[-self.length / 2, [0, 0], 1], [self.length / 2, [0, 0], 1]],
                    self.registry,
                    lunit="mm",
                )
                g4_decomposed_extrusions.append(g4e)

            self.g4_decomposed_extrusions[region] = g4_decomposed_extrusions

    def plot(self, decompositions=False):
        f = _plt.figure()

        for region in self.regions:
            region_connect = self.regions[region].copy()
            region_connect.append(region_connect[0])
            region_array = _np.array(region_connect)

            _plt.plot(region_array[:, 0], region_array[:, 1])

        # break if decompositions are not required
        if not decompositions:
            return

        for dr in self.decomposed:
            for p in self.decomposed[dr]:
                p = _np.array(p)
                _plt.plot(p[:, 0], p[:, 1])

    def mesh(self):
        return self.g4_extrusions[self.boundary].mesh()

        # m = pyg4ometry.pycgal.CSG()
        #
        # for bs in self.g4_decomposed_extrusions[self.boundary]:
        #    bsm = bs.mesh()
        #    m = m.union(bsm)
        #
        # return m
