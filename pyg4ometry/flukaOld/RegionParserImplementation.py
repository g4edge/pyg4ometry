import antlr4

from .RegionParserVisitor import RegionParserVisitor
from .RegionLexer import RegionLexer
from .RegionParser import RegionParser

def parse_single_region(region_string):
    """given a FLUKA region string, return the antlr4 abstract syntax tree"""
    istream = antlr4.InputStream(region_string)
    lexed_input = RegionLexer(istream)
    tokens = antlr4.CommonTokenStream(lexed_input)
    parser = RegionParser(tokens)

    # syntax tree from single region:
    tree = parser.region()
    return tree

def region_string_to_region_instance(region_string):
    region_tree = parse_single_region(region_string)
    bodies = {} # obviously this should contain some actual bodies.
    region_visitor = RegionVisitor(bodies)
    region_visitor.visit(region_tree)
    return region_vistitor.region

class RegionVisitor(RegionParserVisitor):
    def __init__(self, bodies):
        self.bodies = bodies

    def visitSimpleRegion(self, ctx):
        # Simple in the sense that it consists of no unions of Zones.
        region_defn = self.visitChildren(ctx)
        # Build a zone from the list of bodies or single body:
        zone = [geometry.Zone(region_defn)]
        region_name = ctx.RegionName().getText()
        # temporarily G4_Galactic
        self.region = geometry.Region(region_name, zone, "G4_Galactic")

    def visitComplexRegion(self, ctx):
        # Complex in the sense that it consists of the union of
        # multiple zones.

        # Get the list of tuples of operators and bodies/zones
        region_defn = self.visitChildren(ctx)
        # Construct zones out of these:
        zones = [geometry.Zone(defn) for defn in region_defn]
        region_name = ctx.RegionName().getText()
        region = geometry.Region(region_name, zones, "G4_Galactic")
        self.region = region


    def visitUnaryAndBoolean(self, ctx):
        left_solid = self.visit(ctx.unaryExpression())
        right_solid = self.visit(ctx.expr())

        # If both are tuples (i.e. operator, body/zone pairs):
        if (isinstance(left_solid, tuple)
                and isinstance(right_solid, tuple)):
            return [left_solid, right_solid]
        elif (isinstance(left_solid, tuple)
              and isinstance(right_solid, list)):
            right_solid.append(left_solid)
            return right_solid
        else:
            raise RuntimeError("dunno what's going on here")

    def visitUnaryExpression(self, ctx):
        body_name = ctx.ID().getText()
        body = self.bodies[body_name]
        if ctx.Plus():
            return  ('+', body)
        elif ctx.Minus():
            return ('-', body)
        return None

    def visitUnaryAndSubZone(self, ctx):
        sub_zone = self.visit(ctx.subZone())
        expr = self.visit(ctx.expr())
        # If expr is already a list, append to it rather than building
        # up a series of nested lists.  This is to keep it flat, with
        # the only nesting occuring in Zones.
        if isinstance(expr, list):
            return [sub_zone] + expr
        return [sub_zone, expr]

    def visitSingleUnion(self, ctx):
        zone = [(self.visit(ctx.zone()))]
        return zone

    def visitMultipleUnion(self, ctx):
        # Get the zones:
        zones = [self.visit(zone) for zone in ctx.zone()]
        return zones

    def visitMultipleUnion2(self, ctx):
        # This rule exists because of the three ways of expressing a
        # union:
        # - | +x +y (union with nothing)
        # -   +x | +y (infix union operator)
        # - | +x | +y (infix union operator with leading union op)
        # The latter two are identical, hence this method simply calling
        # the other.
        return self.visitMultipleUnion(ctx)

    def visitSubZone(self, ctx):
        if ctx.Plus():
            operator = '+'
        elif ctx.Minus():
            operator = '-'
        solids = self.visit(ctx.expr())
        zone = geometry.Zone(solids)
        return (operator, zone)
