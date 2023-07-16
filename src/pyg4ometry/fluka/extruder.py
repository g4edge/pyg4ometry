import pyg4ometry.pycgal.CGAL
import pyg4ometry.pycgal.pythonHelpers

from ..pycgal import Polygon_2
from ..pycgal import Polygon_with_holes_2
from ..pycgal import Point_2
import matplotlib.pyplot as _plt
import numpy as _np


class Extruder:
    def __init__(self, length=1000):
        self.length = length
        self.points = []
        self.regions = {}
        self.cgalpolys = {}
        self.extrusions = {}
        self.decomposed = {}

    def add_region(self, name):
        self.regions[name] = []
        return self.regions[name]

    def add_point_to_region(self, name, pntIndx):
        self.regions[name].append(pntIndx)

    def set_region_to_outer_boundary(self, name):
        self.boundary = name

    def build_and_test_hierachy(self):
        pass

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
        pass

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
