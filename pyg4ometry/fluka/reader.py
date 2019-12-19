import sys
from collections import OrderedDict

import numpy as np


from . import body
from .region import Zone, Region
from .fluka_registry import FlukaRegistry
from copy import deepcopy
from pyg4ometry.fluka.RegionExpression import (RegionParserVisitor,
                                               RegionParser,
                                               RegionLexer)
from .card import freeFormatStringSplit, Card

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


class Reader(object):
    """
    Class to read FLUKA filie
    """

    def __init__(self, filename) :
        self.filename = filename
        self.flukaregistry = FlukaRegistry()
        self.cards = []
        self.transforms = OrderedDict()

        self._load()

    def _load(self):
        """Load the FLUKA input file"""
        with open(self.filename, "r") as f:
            self._lines = f.readlines()

        # strip comments
        strippedLines = []
        for l in self._lines :
            strippedLine = l.lstrip()

            # if there is nothing on  the line
            if len(strippedLine) == 0 :
                continue
            # skip comment
            if strippedLine[0] != '*':
                strippedLines.append(l.rstrip())

        self._lines = strippedLines

        # parse file
        self._findLines()
        self.cards = self._parseCards()
        self._parseRotDefinis()
        self._parseBodies()
        self._parseRegions()


    def _findLines(self) :
        # find geo(begin/end) lines and bodies/region ends
        firstEND = True
        for i, line in enumerate(self._lines) :
            if "GEOBEGIN" in line:
                self.geobegin = i
                self.bodiesbegin = i + 2
            elif "GEOEND" in line:
                self.geoend = i
            elif "END" in line:
                if firstEND:
                    self.bodiesend = i
                    self.regionsbegin = i + 1
                    firstEND = False
                else:
                    self.regionsend = i

    def _parseBodies(self) :
        bodies_block = self._lines[self.bodiesbegin:self.bodiesend+1]

        # there can only be one of each directive used at a time, and
        # the order in which they are nested is irrelevant to the
        # order of application so no need for a stack.
        expansion = 1.0
        translation = None
        transform = None

        # type, name, parameters, etc.,  may be accumulated
        # over many lines, each part is a string in the list in order.
        body_parts = []
        in_body = False # flag to tell us if we are currently in a body defn
        for line in bodies_block:
            # split the line into chunks according to the FLUKA delimiter rules.
            line_parts = freeFormatStringSplit(line)
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
                expansion, translation, transform = self._parseGeometryDirective(
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

    def _parseRegions(self) :
        regions_block = self._lines[self.regionsbegin:self.regionsend+1]
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

    def _parseCards(self):
        fixed = True # start off parsing as fixed, i.e. not free format.
        cards = []
        for line in self._lines[:self.geobegin] + self._lines[self.geoend:]:
            if fixed:
                cards.append(Card.fromFixed(line))
                kw = cards[-1].keyword
            else: # must be free format
                cards.append(Card.fromFree(line))
                kw = cards[-1].keyword

            if kw != "FREE" and kw != "FIXED":
                continue
            elif kw == "FREE":
                fixed = False
            else:
                fixed = True
        return cards

    def _parseRotDefinis(self):
        for card in self.cards:
            if card.keyword != "ROT-DEFI":
                continue
            name, matrix = _parseRotDefiniCard(card)

            if name in self.transforms:
                # if already defined (i.e. it is defined recursively)
                # then left multiply it with the existing transform
                # definition.
                existing = self.transforms[name]
                self.transforms[name] = matrix.dot(existing)
            else:
                self.transforms[name] = matrix

    def _parseGeometryDirective(self,
                                line_parts, expansion, translation, transform):

        directive = line_parts[0].lower()
        if directive == "$start_translat":
            # CONVERTING TO MILLIMETRES HERE
            translation = [10*float(x) for x in line_parts[1:4]]
        elif directive == "$end_translat":
            translation = None
        elif directive == "$start_expansion":
            expansion = float(line_parts[1])
        elif directive == "$end_expansion":
            expansion = 1.0
        elif directive == "$start_transform":
            transform = self.transforms[line_parts[1]]
        elif directive == "$end_transform":
            transform = None
        else:
            raise ValueError("Unknown geometry directive: {}.".format(directive))

        return expansion, translation, transform

def _make_body(body_parts, expansion, translation, transform, flukareg):
    # definition is string of the entire definition as written in the file.
    body_type = body_parts[0]
    name = body_parts[1]
    # WE ARE CONVERTING FROM CENTIMETRES TO MILLIMETRES HERE.
    param = [float(p)*10. for p in body_parts[2:]]
    transforms = {"expansion": expansion,
                  "translation": translation,
                  "transform": transform}

    if body_type == "RPP":
        b = body.RPP(name, *param, flukaregistry=flukareg, **transforms)
    elif body_type == "BOX":
        b = body.BOX(name, param[0:3], param[3:6], param[6:9],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "ELL":
        b = body.ELL(name, param[0:3], param[3:6], param[6],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "RCC":
        b = body.RCC(name, param[0:3], param[3:6], param[6],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "SPH":
        b = body.SPH(name, param[0:3], param[3],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "REC":
        b = body.REC(name, param[0:3], param[3:6], param[6:9], param[9:12],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "WED":
        b = body.WED(name, param[0:3], param[3:6], param[6:9], param[9:12],
                     flukaregistry=flukareg, **transforms)
    elif body_type == "RAW":
        b = body.RAW(name, param[0:3], param[3:6], param[6:9], param[9:12],
                     flukaregistry=flukareg, **transforms)
    elif body_type == "ARB":
        vertices = [param[0:3], param[3:6], param[6:9], param[9:12],
                    param[12:15], param[15:18], param[18:21], param[21:24]]
        facenumbers = param[24:]
        b = body.ARB(name, vertices, facenumbers,
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "XYP":
        b = body.XYP(name, param[0], flukaregistry=flukareg, **transforms)
    elif body_type == "XZP":
        b = body.XZP(name, param[0], flukaregistry=flukareg, **transforms)
    elif body_type == "YZP":
        b = body.YZP(name, param[0], flukaregistry=flukareg, **transforms)
    elif body_type == "PLA":
        b = body.PLA(name, param[0:3], param[3:6], flukaregistry=flukareg,
                     **transforms)
    elif body_type == "XCC":
        b = body.XCC(name, param[0], param[1], param[2],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "YCC":
        b = body.YCC(name, param[0], param[1], param[2],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "ZCC":
        b = body.ZCC(name, param[0], param[1], param[2],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "XEC":
        b = body.XEC(name, param[0], param[1], param[2], param[3],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "YEC":
        b = body.YEC(name, param[0], param[1], param[2], param[3],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "ZEC":
        b = body.ZEC(name, param[0], param[1], param[2], param[3],
                     flukaregistry=flukareg,
                     **transforms)
    elif body_type == "TRC":
        b = body.TRC(name, param[0:3], param[3:6], param[6], param[7],
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
        # Purely so we can give nested subzones meaningful names:
        self.region_name = None
        self.subzone_counter = 0

    def visitSimpleRegion(self, ctx):
        # Simple in the sense that it consists of no unions of Zones.
        self.region_name = ctx.RegionName().getText()
        self.subzone_counter = 0
        region_defn = self.visitChildren(ctx)
        # Build a zone from the list of bodies or single body:

        zone = Zone(name="{}_zone".format(self.region_name))
        for operator, body in region_defn:
            if operator == "+":
                zone.addIntersection(body)
            else:
                zone.addSubtraction(body)

        region = Region(self.region_name)
        region.addZone(zone)
        self.flukaregistry.addRegion(region)

    def visitComplexRegion(self, ctx):
        # Complex in the sense that it consists of the union of
        # multiple zones.
        self.region_name = ctx.RegionName().getText()
        self.subzone_counter = 0
        region = Region(self.region_name)
        # Get the list of tuples of operators and bodies/zones
        region_defn = self.visitChildren(ctx)

        # Construct zones out of these nested lists.
        for i, z in enumerate(region_defn):
            zone = Zone(name="{}_zone{}".format(self.region_name, i))
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
        operator = '-'
        if ctx.Plus():
            operator = '+'
        self.subzone_counter += 1
        solids = self.visit(ctx.expr())
        z = Zone(name="{}_subzone{}".format(self.region_name,
                                            self.subzone_counter))
        for op, body in solids:
            if op == "+":
                z.addIntersection(body)
            else:
                z.addSubtraction(body)
        return [(operator, z)]


def _parseRotDefiniCard(card):
    # This only is indended to work for transforms applied to
    # geometries.  It may or may not be useful for the other
    # applications of ROT-DEFInis.
    if card.keyword != "ROT-DEFI":
        raise ValueError("Not a ROT-DEFI card.")

    what1 = float(card.what1)

    if what1 > 1000.:
        i = what1 // 1000
        j = int(str(what1)[-1])
    elif what1 > 100. and what1 < 1000.:
        i = int(str(what1)[-1])
        j = what1 // 100
    elif what1 > 0 and what1 <= 100:
        i = int(what1)
        j = 0
    elif what1 == 0:
        # If left empty (i.e. 0), then this is a translation
        # about the z-axis.  But I don't know what that means for i.
        i = what1
        j = 0
    else:
        raise ValueError("Unable to parse ROT-DEFI transformation index.")

    # XXX: I think this is the correct way to deal with a ROT-DEFINI
    # without a name, this may be wrong.
    name = card.sdum
    if name is None:
        name = i

    # rotation angles, converting from degrees to radians:
    theta = np.pi * card.what2 / 180 # polar angle
    phi = np.pi * card.what3 / 180  # azimuthal angle


    # the translation coordinates
    tx, ty, tz = card.what4, card.what5, card.what6

    # CONVERTING TO MILLIMETRES!!
    tx *= 10
    ty *= 10
    tz *= 10

    # From note 4 of the ROT-DEFI entry of the manual (page 253 for
    # me):
    # Note I have turned these into transformation matrices, so that
    # transforms can be easily combined.
    ct = np.cos(theta)
    cp = np.cos(phi)
    st = np.sin(theta)
    sp = np.sin(phi)
    if j == 1: # x
        r1 = np.array([[ ct, st, 0, 0],
                       [-st, ct, 0, 0],
                       [ 0,   0, 1, 0],
                       [ 0,   0, 0, 1]])
        r2 = np.array([[1,  0,   0,             tx],
                       [0,  cp, sp,  ty*cp + tz*sp],
                       [0, -sp, cp,  tz*cp - ty*sp],
                       [0,   0,  0,              1]])

    elif j == 2: # y
        r1 = np.array([[1,   0,  0, 0],
                       [0,  ct, st, 0],
                       [0, -st, ct, 0],
                       [0,   0,  0, 1]])
        r2 = np.array([[cp, 0, -sp, tx*cp - tz*sp],
                       [0,  1,   0,            ty],
                       [sp, 0,  cp, tx*sp + tz*cp],
                       [0,  0,   0,             1]])
    elif j == 3 or j == 0: # z
        r1 = np.array([[ct, 0, -st, 0],
                       [0,  1,  0,  0,],
                       [st, 0,  ct, 0],
                       [0,  0,  0,  1]])
        r2 = np.array([[cp,  sp, 0, tx*cp + ty*sp],
                       [-sp, cp, 0, ty*cp - tx*sp],
                       [  0,  0, 1,            tz],
                       [  0,  0, 0,             1]])

    matrix = r1.dot(r2)

    return name, matrix

def main(filein):
    r = Reader(filein)

if __name__ == '__main__':
    main(sys.argv[1])
