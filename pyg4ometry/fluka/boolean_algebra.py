from collections import namedtuple as _namedtuple

import antlr4 as _antlr4
import numpy as _np
import sympy as _sympy

from . import vector as _vector
from . import region as _region
from . import reader as _reader
from .RegionExpression import RegionParserVisitor, RegionParser, RegionLexer
from . import fluka_registry

def expressionToZone(zone, zoneExpr):
    zoneExpr = str(zoneExpr)
    zoneExpr = zoneExpr.replace("& ~", "-")
    zoneExpr = zoneExpr.replace("& ", "+")

    # Hack to use the existing region parser...  fix this.
    expr = f"dummy 5 {zoneExpr}"

    istream = _antlr4.InputStream(expr)
    lexed_input = RegionLexer(istream)
    tokens = _antlr4.CommonTokenStream(lexed_input)
    parser = RegionParser(tokens)
    tree = parser._region()
    freg = fluka_registry.FlukaRegistry()
    zone.allBodiesToRegistry(freg)
    vis = _reader.RegionVisitor(freg)
    vis.visit(tree)

    return freg.regionDict["dummy"].zones[0]

def zoneToDNFZones(zone):
    dnf = _sympy.to_dnf(zoneToAlgebraicExpression(zone))
    zones = []
    if isinstance(dnf, _sympy.And):
        zones.append(expressionToZone(zone, dnf))
        return zones

    assert isinstance(dnf, _sympy.Or)

    for arg in dnf.args:
        arg = _sympy.simplify_logic(arg) # trivially solve a & ~a, etc..
        if not arg:
            continue
        zones.append(expressionToZone(zone, arg))

    return zones

def regionToAlgebraicExpression(region): # region or zone
    result = []
    for z in region.zones:
        result.append(zoneToAlgebraicExpression(z))
    return _sympy.Or(*result)

def zoneToAlgebraicExpression(zone):
    s = zone.dumps()
    s = s.strip()
    s = s.lstrip("+")
    s = s.replace("-", "& ~")
    s = s.replace("( +", "(")
    s = s.replace(" +", " & ")
    bodyNames = set(b.name for b in zone.bodies())
    namespace = {name: _sympy.Symbol(name) for name in bodyNames}
    return _sympy.sympify(s, locals=namespace)

def _getMeshAndAABB(body, aabb=None):
    mesh = body.mesh(aabb=aabb)
    return mesh, _vector.AABB.fromMesh(mesh)

def pruneRegion(reg, aabb=None):
    result = _region.Region(reg.name)
    for zone in reg.zones:
        prunedZone = pruneZone(zone)
        if prunedZone.intersections: # and not prunedZone.isNull(aabb=aabb):
            result.addZone(prunedZone)
    return result

def isZoneContradiction(zone):
    intNames = {b.body.name for b in zone.intersections}
    subNames = {b.body.name for b in zone.subtractions}
    return bool(intNames.intersection(subNames))

def pruneZone(zone, aabb0=None, aabb=None):
    if not zone.isDNF():
        raise ValueError("Zone must be in DNF")

    intersections = zone.intersections

    result = _region.Zone()

    if isZoneContradiction(zone):
        return result

    if aabb0 is None:
        first = intersections[0].body
        mesh0 = first.mesh()
        aabb0 = _vector.AABB.fromMesh(mesh0)
        intersections = intersections[1:]
        result.addIntersection(first)

    for intersect in intersections:
        body = intersect.body

        _, thisAABB = _getMeshAndAABB(body, aabb=aabb)
        if thisAABB.coplanarIntersects(aabb0):
            aabb0 = thisAABB.intersect(aabb0)
            result.addIntersection(body)
        else:
            result.intersections = []
            return result

    for sub in zone.subtractions:
        body = sub.body
        _, thisAABB = _getMeshAndAABB(body, aabb=aabb)
        if thisAABB.coplanarIntersects(aabb0):
            result.addSubtraction(body)

    return result

def squashDegenerateBodies(zone, bodystore=None):
    if bodystore is None:
        bodystore = fluka_registry.FlukaBodyStore()
    result = _region.Zone()
    for b in zone.intersections:
        body = b.body
        if isinstance(body, _region.Zone):
            result.addIntersection(
                squashDegenerateBodies(body, bodystore=bodystore)
            )
        else:
            result.addIntersection(bodystore.getDegenerateBody(body))

    for b in zone.subtractions:
        body = b.body
        if isinstance(body, _region.Zone):
            result.addSubtraction(
                squashDegenerateBodies(body, bodystore=bodystore)
            )
        else:
            result.addSubtraction(bodystore.getDegenerateBody(body))

    return result


_MeshedZoneInfo = _namedtuple("MeshedZoneInfo", ["zone", "mesh", "volume"])

def simplifyRegion(region):
    if not _region.isDNF():
        raise ValueError("Must be DNF to simplify region")

    zoneData = []
    for zone in region.zones:
        mesh = zone.mesh()
        zoneInfo = _MeshedZoneInfo(zone, mesh, mesh.volume())
        zoneData.append(zoneInfo)

    zoneData = _filterRedunantZonesSymbollicaly(zoneData)
    zoneData = _filterRedundantZonesMetricCheck(zoneData)

    region.zones = [zd.zone for zd in zoneData]

def _filterRedunantZonesSymbollicaly(zoneData):
    zoneData.sort(key=lambda x: x.volume, reverse=True)

    largestZone = zoneData[0].zone
    intersectionNamesLargestZone = set(b.body.name
                                       for b in largestZone.intersections)
    subtractionNamesLargestZone = set(b.body.name
                                      for b in largestZone.subtractions)

    resultZoneData = [zoneData[0]]
    for zone, mesh, volume in zoneData[1:]:
        zoneIntersectionNames = set(b.body.name for b in zone.intersections)
        zoneSubtractionNames = set(b.body.name for b in zone.subtractions)

        # Filter trivial "A & ~A"
        if isZoneContradiction(zone):
            continue

        # This zone is a subset of the larger zone.
        if zoneIntersectionNames.issuperset(
            intersectionNamesLargestZone
        ) and zoneSubtractionNames.issuperset(subtractionNamesLargestZone):
            continue

        resultZoneData.append(_MeshedZoneInfo(zone, mesh, volume))

    return resultZoneData

def _filterRedundantZonesMetricCheck(zoneData):
    largestZoneData = zoneData[0]
    runningRegionMesh = largestZoneData.mesh
    runningRegionVolume = largestZoneData.volume

    resultZoneData = [largestZoneData]
    for zone, mesh, volume in zoneData[1:]:
        if _np.isclose(volume, 0.0):
            continue
        # clone to prevent possible excessive corefinement on the
        # reference mesh resulting in huge slowdown.
        mesh0 = runningRegionMesh.clone()
        unionMesh = mesh0.union(mesh)
        unionVolume = unionMesh.volume()
        if _np.isclose(runningRegionVolume, unionVolume):
            continue
        else:
            runningRegionMesh = unionMesh
            runningRegionVolume = unionVolume

        resultZoneData.append(_MeshedZoneInfo(zone, mesh, volume))

    return resultZoneData

def nTermsDNF(expr):
    # expr is a Zone instance or a Region instance
    try:
        return sum(_nTermsDNFZone(e) for e in expr.zones)
    except AttributeError:
        return _nTermsDNFZone(expr)

def _nTermsDNFZone(zone):
    total = 1
    for arg in zone.subtractions:
        if not isinstance(arg.body, _region.Zone):
            continue
        total *= len(zone.intersections + zone.subtractions)

    return total
