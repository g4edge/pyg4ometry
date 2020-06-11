import sympy

import antlr4

from . import vector
from . import region
from . import reader
from .RegionExpression import RegionParserVisitor, RegionParser, RegionLexer
from . import fluka_registry

def zoneToDNFZones(zone):
    dnf = sympy.to_dnf(toAlgebraicExpression(zone))

    zones = []
    for arg in dnf.args:
        arg = str(arg)
        arg = arg.replace("& ~", "-")
        arg = arg.replace("& ", "+")

        # Hack to use the existing region parser...  fix this.
        expr = f"dummy 5 {arg}"

        istream = antlr4.InputStream(expr)
        lexed_input = RegionLexer(istream)
        tokens = antlr4.CommonTokenStream(lexed_input)
        parser = RegionParser(tokens)
        tree = parser.region()
        freg = fluka_registry.FlukaRegistry()
        zone.allBodiesToRegistry(freg)
        vis = reader.RegionVisitor(freg)
        vis.visit(tree)

        zones.append(freg.regionDict["dummy"].zones[0])

    return zones

def toAlgebraicExpression(regzone): # region or zone
    s = regzone.flukaFreeString()
    s = s.strip()
    s = s.lstrip("+")
    s = s.replace("-", "& ~")
    s = s.replace("( +", "(")
    s = s.replace(" +", " & ")
    bodyNames = set(b.name for b in regzone.bodies())
    namespace = {name: sympy.Symbol(name) for name in bodyNames}
    return sympy.sympify(s, locals=namespace)

def pruneZone(zone, aabb=None):
    from IPython import embed; embed()
    mesh0 = zone.intersections[0].body.mesh()
    aabb0 = vector.AABB.fromMesh(mesh0)
    result = aabb0

    filtered_intersections = []
    for body in zone.intersections[1:]:
        mesh = body.body.mesh(aabb=aabb)
        if mesh.isNull():
            from IPython import embed; embed()
            continue
        bodyAABB = vector.AABB.fromMesh(mesh)
        if result.intersects(bodyAABB):
            filtered_intersections.append(body)
        else:
            from IPython import embed; embed()

    filtered_subtractions = []
    for body in zone.subtractions:
        mesh = body.body.mesh(aabb=aabb)
        if mesh.isNull():
            from IPython import embed; embed()
        bodyAABB = vector.AABB.fromMesh(mesh)
        if result.intersects(bodyAABB):
            filtered_subtractions.append(body)
    from IPython import embed; embed()
