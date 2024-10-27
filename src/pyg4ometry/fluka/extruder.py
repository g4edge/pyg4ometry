from .. import geant4
from ..geant4 import solid
from ..pycgal import CGAL
from ..pycgal import pythonHelpers

from ..pycgal import PolygonProcessing
from ..pycgal import Polygon_2
from ..pycgal import Polygon_with_holes_2
from ..pycgal import Point_2

import functools as _functools
import math as _math
import matplotlib.pyplot as _plt
import numpy as _np


class Extruder(solid.SolidBase):
    def __init__(
        self, name="", length=1000, angle=0.0, regions=None, materials=None, registry=None
    ):
        super().__init__(name, "extruder", registry)

        self.length = length
        self.angle = angle
        self.regions = regions if regions is not None else {}
        self.materials = materials if materials is not None else {}
        self.angle = angle
        self.cgalpolys = {}
        self.extrusions = {}
        self.decomposed = {}
        self.g4_extrusions = {}
        self.g4_decomposed_extrusions = {}
        self.extruders = {}

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
            raise NameError(name + " already in " + self.name)
        if dxdy:
            pointList = [[x + dxdy[0], y + dxdy[1]] for [x, y] in pointList]
        self.materials[name] = material
        if not scale:
            self.regions[name] = pointList
        else:
            # product of +-1 (sign of) scale gives winding order
            winding = int(_functools.reduce(lambda x, y: x * _math.copysign(1.0, y), scale))
            pointListScaled = [[x * scale[0], y * scale[1]] for [x, y] in pointList]
            self.regions[name] = pointListScaled[::winding]

    def addExtruder(self, extruder):
        self.extruders[extruder.name] = extruder

    def addPointToRegion(self, name, pntIndx):
        self.regions[name].append(pntIndx)

    def setRegionToOuterBoundary(self, name):
        self.boundary = name

    def setRegionMaterial(self, name, material):
        self.materials[name] = material

    def getRegionMaterial(self, name):
        return self.materials[name]

    def buildCgalPolygons(self):
        # first loop over extruIders
        for extruderName, extruder in self.extruders.items():
            extruder.buildCgalPolygons()

        # build a CGAL polygon (without holes for each region)
        holes = []

        for region in self.regions:
            if self.polygon_area(self.regions[region]) < 0:
                self.regions[region] = self.regions[region]

            if self.boundary != region:
                self.decomposed[region] = PolygonProcessing.decomposePolygon2d(self.regions[region])
                if len(self.decomposed[region]) == 1:
                    self.decomposed[region] = PolygonProcessing.decomposePolygon2d(
                        list(reversed(self.regions[region]))
                    )
                holes.append(self.regions[region])

        for extruderName, extruder in self.extruders.items():
            holes.append(extruder.regions[extruder.boundary])

        self.decomposed[self.boundary] = PolygonProcessing.decomposePolygon2dWithHoles(
            self.regions[self.boundary], holes
        )

    def buildGeant4Extrusions(self):
        if self.angle == 0:
            self._buildStraightExtrustions()
        else:
            self._buildCurvedExtrusions()

        for extruderName, extruder in self.extruders.items():
            extruder.buildGeant4Extrusions()
            self.g4_extrusions.update(extruder.g4_extrusions)
            self.g4_decomposed_extrusions.update(extruder.g4_decomposed_extrusions)
            self.materials.update(extruder.materials)

    def _buildStraightExtrustions(self):
        # normal geant4 extrusions
        for region in self.regions:
            g4e = solid.ExtrudedSolid(
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
                g4e = solid.ExtrudedSolid(
                    region + "_" + str(idecomp),
                    _np.array(pgon),
                    [[-self.length / 2, [0, 0], 1], [self.length / 2, [0, 0], 1]],
                    self.registry,
                    lunit="mm",
                )
                g4_decomposed_extrusions.append(g4e)

            self.g4_decomposed_extrusions[region] = g4_decomposed_extrusions

    def _buildCurvedExtrusions(self):
        # normal geant4 extrusions
        for region in self.regions:
            g4e = solid.ExtrudedSolid(
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
            print(region)
            for pgon, idecomp in zip(pgonList, range(len(pgonList))):
                g4e = solid.HalfSpace(region + str(idecomp))

                if self.polygon_area(pgon) < 0:
                    pgon = list(reversed(pgon))

                g4e.addPolygon([[v[0], v[1], 0] for v in pgon])
                print(pgon)
                g4_decomposed_extrusions.append(g4e)

            self.g4_decomposed_extrusions[region] = g4_decomposed_extrusions

    def plot(self, decompositions=False):
        f = _plt.figure()

        for region in self.regions:
            region_connect = self.regions[region].copy()
            region_connect.append(region_connect[0])
            region_array = _np.array(region_connect)

            _plt.plot(region_array[:, 0], region_array[:, 1])

        for extruderName, extruder in self.extruders.items():
            extruder.plot(decompositions)

        # break if decompositions are not required
        if not decompositions:
            return

        for dr in self.decomposed:
            for p in self.decomposed[dr]:
                p = _np.array(p)
                _plt.plot(p[:, 0], p[:, 1])

    def polygon_area(self, vertices):
        # Using the shoelace formula
        xy = _np.array(vertices).T
        x = xy[0]
        y = xy[1]
        signed_area = 0.5 * (_np.dot(x, _np.roll(y, 1)) - _np.dot(y, _np.roll(x, 1)))
        return signed_area

    def mesh(self):
        return self.g4_extrusions[self.boundary].mesh()

        # m = pyg4ometry.pycgal.CSG()
        #
        # for bs in self.g4_decomposed_extrusions[self.boundary]:
        #    bsm = bs.mesh()
        #    m = m.union(bsm)
        #
        # return m
