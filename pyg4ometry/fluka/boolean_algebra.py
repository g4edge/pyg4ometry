import sympy

import antlr4

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
