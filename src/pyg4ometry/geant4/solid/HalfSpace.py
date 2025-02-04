from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg:
    from ...pycsg.core import CSG as _CSG
    from ...pycsg.geom import Vector as _Vector
    from ...pycsg.geom import Vertex as _Vertex
    from ...pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm:
    from ...pycgal.core import CSG as _CSG
    from ...pycgal.geom import Vector as _Vector
    from ...pycgal.geom import Vertex as _Vertex
    from ...pycgal.geom import Polygon as _Polygon

import logging as _log

_log = _log.getLogger(__name__)


class HalfSpace(_SolidBase):
    def __init__(self, name, registry=None):
        super().__init__(name, "HalfSpace", registry)

        self.pgons = []

    def addPolygon(self, pgonVertex):
        self.pgons.append(pgonVertex)

    def mesh(self):
        polygons = []
        for pgon in self.pgons:
            verts = []
            for pgonvert in pgon:
                verts.append(_Vertex(pgonvert))
            polygons.append(_Polygon(verts))

        mesh = _CSG.fromPolygons(polygons)
        return mesh
