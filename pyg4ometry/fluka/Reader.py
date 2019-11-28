import sys
import re as _re
from . import Body
from .Region import Zone, Region
from FlukaRegistry import FlukaRegistry
from BodyTransform import BodyTransform
from copy import deepcopy
from pyg4ometry.fluka.RegionExpression import (RegionParserVisitor,
                                               RegionParser,
                                               RegionLexer)
import antlr4

_BODY_NAMES = {"RPP",
               "BOX",
               "SPH",
               "RCC",
               "REC",
               "TRC",
               "ELL",
               "WED", "RAW",
               "ARB ",
               "XYP", "XZP", "YZP",
               "PLA",
               "XCC", "YCC", "ZCC",
               "XEC", "YEC", "ZEC",
               "QUA"}

def _freeform_split(string):
    """Method to split a string in FLUKA FREE format into its components"""
    # Split the string along non-black separators [,;:/\]
    partial_split = _re.split(';|,|\\/|:|\\\|\n', r"{}".format(string))

    # Populate zeros between consequtive non-blank separators as per the FLUKA manual
    is_blank  = lambda s : not set(s) or set(s) == {" "}
    noblanks_split = [chunk if not is_blank(chunk) else '0.0' for chunk in partial_split]

    # Split along whitespaces now for complete result
    components = []
    for chunk in noblanks_split:
        components += chunk.split()

    return components

class Reader(object):
    def __init__(self, filename) :
        self.fileName = filename
        self.flukaregistry = FlukaRegistry()
        self.load()

    def load(self) :

        # read file
        flukaFile = open(self.fileName)
        self.fileLines = flukaFile.readlines()
        flukaFile.close()

        # strip comments
        fileLinesStripped = []
        for l in self.fileLines :
            fileLineStripped = l.lstrip()

            # if there is nothing on  the line
            if len(fileLineStripped) == 0 :
                continue
            # skip comment
            if fileLineStripped[0] != '*' :
                fileLinesStripped.append(l.rstrip())
        self.fileLines = fileLinesStripped

        # parse file
        self.findLines()
        self.parseBodies()
        self.parseRegions()
        self.parseMaterials()
        self.parseMaterialAssignment()
        self.parseLattice()
        self.parseCards()

    def findLines(self) :
        # find geo(begin/end) lines and bodies/region ends
        firstEND = True
        for i, line in enumerate(self.fileLines) :
            if "GEOBEGIN" in line:
                self.geobegin = i
            elif "GEOEND" in line:
                self.geoend = i
            elif "END" in line:
                if firstEND:
                    self.bodiesend = i
                    firstEND = False
                else:
                    self.regionsend = i

        print self.geobegin, self.fileLines[self.geobegin]
        print self.bodiesend, self.fileLines[self.bodiesend]
        print self.regionsend, self.fileLines[self.regionsend]
        print self.geoend,self.fileLines[self.geoend]

    def parseBodyTransform(self, line):
        sline = _freeform_split(line)
        trans_type = sline[0].split("_")[1]
        transcount = len(self.flukaregistry.bodyTransformDict)
        name = "bodytransform_{}".format(transcount+1)
        value = sline[1:]
        trans = BodyTransform(name, trans_type, value, self.flukaregistry)

        return trans

    def parseBodies(self) :
        bodies_block = self.fileLines[self.geobegin+2:self.bodiesend+1]

        # there can only be one of each directive used at a time, and
        # the order in which they are nested is irrelevant to the
        # order of application so no need for a stack.
        expansion = None
        translation = None
        transform = None

        # type, name, parameters, etc.,  may be accumulated
        # over many lines, each part is a string in the list in order.
        body_parts = []
        in_body = False # flag to tell us if we are currently in a body defn
        for line in bodies_block:
            print line
            # split the line into chunks according to the FLUKA delimiter rules.
            line_parts = _freeform_split(line)
            # Get the first bit of the line, which determines what we do next.
            first_bit = line_parts[0]
            if first_bit in _BODY_NAMES: # start of body definition
                if in_body: # already in body, build the previous one.
                    _make_body(body_parts, expansion, translation, transform,
                               self.flukaregistry)
                body_parts = line_parts
                in_body = True
            elif first_bit.startswith("$"): # geometry directive
                if in_body: # build the body we have accrued...
                    _make_body(body_parts, expansion, translation, transform,
                               self.flukaregistry)
                expansion, translation, transform = _parseGeometryDirective(
                    line_parts, expansion, translation, transform)
                in_body = False
            elif first_bit == "END": # finished parsing bodies
                if in_body: # one last body to make
                    _make_body(body_parts, expansion, translation, transform,
                               self.flukaregistry)
                break
            elif in_body: # continue appending bits to the body_parts list.
                body_parts.append(line_parts)
            else:
                raise RuntimeError(
                    "Failed to parse FLUKA input line: {}".format(line))
        else: # we should always break out of the above loop with END.
            raise RuntimeError("Unable to parse FLUKA bodies.")

    def parseRegions(self) :
        regions_block = self.fileLines[self.bodiesend+1:self.regionsend]
        regions_block = "\n".join(regions_block) # turn back into 1 big string

        # Create ANTLR4 char stream from processed regions_block string
        istream = antlr4.InputStream(regions_block)
        # tokenize
        lexed_input = RegionLexer(istream)
        lexed_input.removeErrorListeners()

        # Create a buffer of tokens from lexer
        tokens = antlr4.CommonTokenStream(lexed_input)

        # Create a parser that reads from stream of tokens
        parser = RegionParser(tokens)
        parser.removeErrorListeners()

        tree = parser.regions() # build the tree

        visitor = RegionVisitor(self.flukaregistry)
        visitor.visit(tree)  # walk the tree, populating flukaregistry

    def parseMaterials(self) :
        pass

    def parseMaterialAssignment(self) :
        pass

    def parseCards(self) :
        pass

    def parseLattice(self) :
        pass

def _parseGeometryDirective(line_parts, expansion, translation, transform):
    directive = line_parts[0].lower()
    if directive == "$start_translat":
        translation = map(float, line_parts[1:3])
    elif directive == "$start_expansion":
        expansion = float(line_parts[1])
    elif directive == "$start_transform":
        transform = line_parts[1]
    elif directive == "$end_translat":
        translation = None
    elif directive == "$end_expansion":
        expansion = None
    elif directive == "$end_transform":
        expansion = None
    else:
        raise ValueError("Unknown geometry directive: {}.".format(directive))

    return expansion, translation, transform

def _make_body(body_parts, expansion, translation, transform, flukareg):
    # definition is string of the entire definition as written in the file.
    body_type = body_parts[0]
    name = body_parts[1]
    # we are converting from centimetres to millimetres here!!!
    param = [float(p)*10. for p in body_parts[2:]]
    transforms = {"expansion": expansion,
                  "translation": translation,
                  "transform": transform}

    if body_type == "RPP":
        b = Body.RPP(name, *param, flukaregistry=flukareg, **transforms)
    elif body_type == "BOX":
        b = Body.BOX(name, param[0:3], param[3:6], param[6:9],
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "ELL":
        b = Body.ELL(name, param[0:3], param[3:6], param[7],
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "RCC":
        b = Body.RCC(name, param[0:3], param[3:6], param[6],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "SPH":
        b = Body.SPH(name, param[0:3], param[3],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "REC":
        b = Body.REC(name, param[0:3], param[3:6], param[6:9], param[9:12],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "WED":
        b = Body.WED(name, param[0:3], param[3:6], param[6:9], param[9:12],
                       flukaregistry=flukareg, **transforms)
    elif body_type == "RAW":
        b = Body.RAW(name, param[0:3], param[3:6], param[6:9], param[9:12],
                       flukaregistry=flukareg, **transforms)
    elif body_type == "ARB":
        vertices = [param[0:3], param[3:6], param[6:9], param[9:12],
                    param[12:15], param[15:18], param[18:21], param[21:24]]
        facenumbers = param[24:]
        b = Body.ARB(name, vertices, facenumbers,
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "XYP":
        b = Body.XYP(name, param[0], flukaregistry=flukareg, **transforms)
    elif body_type == "XZP":
        b = Body.XZP(name, param[0], flukaregistry=flukareg, **transforms)
    elif body_type == "YZP":
        b = Body.YZP(name, param[0], flukaregistry=flukareg, **transforms)
    elif body_type == "PLA":
        b = Body.PLA(name, param[0:3], param[3:6], flukaregistry=flukareg,
                       **transforms)
    elif body_type == "XCC":
        b = Body.XCC(name, param[0], param[1], param[2],
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "YCC":
        b = Body.YCC(name, param[0], param[1], param[2],
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "ZCC":
        b = Body.ZCC(name, param[0], param[1], param[2],
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "XEC":
        b = Body.XEC(name, param[0], param[1], param[2], param[3],
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "YEC":
        b = Body.YEC(name, param[0], param[1], param[2], param[3],
                       flukaregistry=flukareg,
                       **transforms)
    elif body_type == "ZEC":
        b = Body.ZEC(name, param[0], param[1], param[2], param[3],
                       flukaregistry=flukareg,
                       **transforms)
    else:
        raise TypeError("Body type {} not supported".format(body_type))
    return b


class RegionVisitor(RegionParserVisitor):
    """
    A visitor class for accumulating the region definitions.  The body
    instances are provided at instatiation, and then these are used
    when traversing the tree to build up a dictionary of region name
    and pyfluka.geometry.Region instances.

    """
    def __init__(self, flukaregistry):
        self.flukaregistry = flukaregistry
        self.current_region = None

    def visitSimpleRegion(self, ctx):
        # Simple in the sense that it consists of no unions of Zones.
        region_name = ctx.RegionName().getText()
        region_defn = self.visitChildren(ctx)
        # Build a zone from the list of bodies or single body:

        zone = Zone(name="{}_zone".format(region_name))
        for operator, body in region_defn:
            if operator == "+":
                zone.addIntersection(body)
            else:
                zone.addSubtraction(body)

        region = Region(region_name)
        region.addZone(zone)
        self.flukaregistry.addRegion(region)

    def visitComplexRegion(self, ctx):
        # Complex in the sense that it consists of the union of
        # multiple zones.
        region_name = ctx.RegionName().getText()
        region = Region(region_name)
        # Get the list of tuples of operators and bodies/zones
        region_defn = self.visitChildren(ctx)

        # Construct zones out of these nested lists.
        for i, z in enumerate(region_defn):
            zone = Zone(name="{}_zone{}".format(region_name, i))
            for operator, body in z:
                if operator == "+":
                    zone.addIntersection(body)
                else:
                    zone.addSubtraction(body)
            region.addZone(zone)
        self.flukaregistry.addRegion(region)

    def visitUnaryAndBoolean(self, ctx):
        left_solid = self.visit(ctx.unaryExpression())
        right_solid = self.visit(ctx.expr())
        right_solid.extend(left_solid)
        return right_solid

    def visitUnaryExpression(self, ctx):
        body_name = ctx.BodyName().getText()
        body = self.flukaregistry.bodyDict[body_name]
        if ctx.Plus():
            return  [('+', body)]
        elif ctx.Minus():
            return [('-', body)]
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
        zone = pyfluka.geometry.Zone(solids)
        return (operator, zone)

def main(filein):
    r = Reader(filein)

if __name__ == '__main__':
    main(sys.argv[1])
