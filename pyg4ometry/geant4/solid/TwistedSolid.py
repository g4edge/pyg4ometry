from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from TwoVector import TwoVector as _TwoVector
from Layer import Layer as _Layer
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Plane as _Plane
from ...pycsg.geom import Polygon as _Polygon


import numpy as _np

class TwistedSolid(object):
    def makeFaceFromLayer(self, layer):
        pols = []
        l = layer
        for p in [l.p1, l.p2, l.p3, l.p4]:
            pols.append(_Vertex(_Vector(p.x, p.y, l.z), None))
        return _Polygon(pols)

    def makeSide(self, pal, pbl, pau, pbu, zl, zu, nsl):
        """
        p = point
        a = first
        b = second
        u = upper
        l = lower
        """
        pols = []
        for i in range(nsl):
            pll = pal + float(i)     * (pbl - pal) / nsl
            plr = pal + float(i+1)   * (pbl - pal) / nsl
            pul = pau + float(i)     * (pbu - pau) / nsl
            pur = pau + float(i+1)   * (pbu - pau) / nsl

            pol1 = _Polygon([_Vertex(_Vector(pll.x, pll.y, zl), None),
                             _Vertex(_Vector(pul.x, pul.y, zu), None),
                             _Vertex(_Vector(pur.x, pur.y, zu), None)])
            pols.append(pol1)

            pol2 = _Polygon([_Vertex(_Vector(plr.x, plr.y, zl), None),
                             _Vertex(_Vector(pll.x, pll.y, zl), None),
                             _Vertex(_Vector(pur.x, pur.y, zu), None)])
            pols.append(pol2)
        return pols

    def meshFromLayers(self, layers, nsl):
        l = layers #shortcut
        allPolygons = []
        polyTop = []
        polyBottom = []

        bottom = self.makeFaceFromLayer(l[-1])
        allPolygons.append(bottom)

        for zi in range(len(l) - 1):
            ll = l[zi]
            ul = l[zi + 1]

            pols = self.makeSide(ll.p1, ll.p2, ul.p1, ul.p2, ll.z, ul.z, nsl)
            allPolygons.extend(pols)

            pols = self.makeSide(ll.p2, ll.p3, ul.p2, ul.p3, ll.z, ul.z, nsl)
            allPolygons.extend(pols)

            pols = self.makeSide(ll.p3, ll.p4, ul.p3, ul.p4, ll.z, ul.z, nsl)
            allPolygons.extend(pols)

            pols = self.makeSide(ll.p4, ll.p1, ul.p4, ul.p1, ll.z, ul.z, nsl)
            allPolygons.extend(pols)

        top = self.makeFaceFromLayer(l[0])
        allPolygons.append(top)

        self.mesh = _CSG.fromPolygons(allPolygons)


        return self.mesh
