import pyg4ometry.geant4
import pyg4ometry.geant4.solid
import pyg4ometry.pycgal.CGAL
import pyg4ometry.pycgal.pythonHelpers

from ..pycgal import Polygon_2
from ..pycgal import Polygon_with_holes_2
from ..pycgal import Point_2
import matplotlib.pyplot as _plt
import numpy as _np


class Extruder(pyg4ometry.geant4.solid.SolidBase):
    def __init__(self, name="", length=1000, regions={}, registry=None):
        super().__init__(name, "extruder", registry)

        self.length = length
        self.regions = regions
        self.cgalpolys = {}
        self.extrusions = {}
        self.decomposed = {}
        self.g4_extrusions = {}
        self.g4_decomposed_extrusions = {}

    def add_region(self, name):
        self.regions[name] = []
        return self.regions[name]

    def add_point_to_region(self, name, pntIndx):
        self.regions[name].append(pntIndx)

    def set_region_to_outer_boundary(self, name):
        self.boundary = name

    def build_cgal_polygons(self):
        # build a CGAL polygon (without holes for each region)

        for region in self.regions:
            self.cgalpolys[region] = Polygon_2.Polygon_2_EPECK()

            for point in self.regions[region]:
                self.cgalpolys[region].push_back(
                    Point_2.Point_2_EPECK(point[0], point[1])
                )

        outer_polygon = self.cgalpolys[self.boundary]
        outer_polygon_hole = (
            pyg4ometry.pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK()
        )

        for region in self.regions:
            if self.boundary != region:
                pyg4ometry.pycgal.CGAL.difference(
                    outer_polygon, self.cgalpolys[region], outer_polygon_hole
                )
                outer_polygon = outer_polygon_hole[0]
                self.decomposed[
                    region
                ] = pyg4ometry.pycgal.CGAL.PolygonDecomposition_2_wrapped(
                    self.cgalpolys[region]
                )
        self.decomposed[
            self.boundary
        ] = pyg4ometry.pycgal.CGAL.PolygonWithHolesConvexDecomposition_2_wrapped(
            outer_polygon_hole[0]
        )

    def build_geant4_extrusions(self):
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

            for pgon, idecomp in zip(pgonList, range(0, len(pgonList))):
                g4e = pyg4ometry.geant4.solid.ExtrudedSolid(
                    region + "_" + str(idecomp),
                    pyg4ometry.pycgal.pythonHelpers.polygon_to_numpy(pgon),
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
                pyg4ometry.pycgal.pythonHelpers.draw_polygon_2(p)

    def mesh(self):
        return self.g4_extrusions[self.boundary].mesh()

        # m = pyg4ometry.pycgal.CSG()
        #
        # for bs in self.g4_decomposed_extrusions[self.boundary]:
        #    bsm = bs.mesh()
        #    m = m.union(bsm)
        #
        # return m
