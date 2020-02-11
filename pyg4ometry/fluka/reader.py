from collections import OrderedDict
from copy import deepcopy
from operator import mul, add
import sys
from warnings import warn

import antlr4
import numpy as np

from . import body
from .card import freeFormatStringSplit, Card
from .directive import Transform, RotoTranslation, RecursiveRotoTranslation
from .fluka_registry import FlukaRegistry
from .lattice import Lattice
from . preprocessor import preprocess
from .region import Zone, Region
from pyg4ometry.fluka.RegionExpression import (RegionParserVisitor,
                                               RegionParser,
                                               RegionLexer)
from .vector import Three
from pyg4ometry.exceptions import FLUKAError, FLUKAInputError



_BODY_NAMES = {"RPP",
               "BOX",
               "SPH",
               "RCC",
               "REC",
               "TRC",
               "ELL",
               "WED", "RAW",
               "ARB",
               "XYP", "XZP", "YZP",
               "PLA",
               "XCC", "YCC", "ZCC",
               "XEC", "YEC", "ZEC",
               "QUA"}


class Reader(object):
    """
    Class to read a FLUKA file.
    """

    def __init__(self, filename) :
        self.filename = filename
        self.flukaregistry = FlukaRegistry()
        self.cards = []

        self._load()

    def _load(self):
        """Load the FLUKA input file"""

        # parse file
        self._lines, self._raw_lines = preprocess(self.filename)
        self._findLines()
        self.cards = self._parseCards()
        self._parseRotDefinis()
        self._parseBodies()
        self._parseRegions()
        self._material_assignments = self._parseMaterialAssignments()
        self._parseLattice()
        self._assignMaterials()

    def _findLines(self) :
        # find geo(begin/end) lines and bodies/region ends
        found_geobegin = False
        found_geoend = False
        found_first_end = False
        found_second_end = False
        in_geo = False
        for i, line in enumerate(self._lines) :
            if line.startswith("GEOBEGIN"):
                found_geobegin = in_geo = True
                self.geobegin = i
                self.bodiesbegin = i + 2
            elif line.startswith("GEOEND"):
                found_geoend = True
                in_geo = False
                self.geoend = i
                break
            elif line.startswith("END") and in_geo:
                if found_first_end:
                    found_second_end = True
                    self.regionsend = i
                    self.latticebegin = i + 1
                else:
                    self.bodiesend = i
                    self.regionsbegin = i + 1
                    found_first_end = True

        if not found_geobegin:
            raise FLUKAError("Missing GEOBEGIN card in input.")
        if not found_geoend:
            raise FLUKAError("Missing GEOEND card in input.")
        if not found_first_end:
            raise FLUKAError("Missing both END cards within geometry section.")
        if not found_second_end:
            raise FLUKAError("Missing second END card within geometry section.")

    def _parseBodies(self) :
        bodies_block = self._lines[self.bodiesbegin:self.bodiesend+1]

        # there can only be one of each directive used at a time, and
        # the order in which they are nested is irrelevant to the
        # order of application so no need for a stack.
        expansion_stack = []
        translation_stack = []
        transform_stack = []

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
                    _make_body(body_parts,
                               expansion_stack,
                               translation_stack,
                               transform_stack,
                               self.flukaregistry)
                body_parts = line_parts
                in_body = True
            elif first_bit.startswith("$"): # geometry directive
                if in_body: # build the body we have accrued...
                    _make_body(body_parts,
                               expansion_stack,
                               translation_stack,
                               transform_stack,
                               self.flukaregistry)
                self._parseGeometryDirective(line_parts,
                                             expansion_stack,
                                             translation_stack,
                                             transform_stack)
                in_body = False
            elif first_bit == "END": # finished parsing bodies
                if in_body: # one last body to make
                    _make_body(body_parts,
                               expansion_stack,
                               translation_stack,
                               transform_stack,
                               self.flukaregistry)
                break
            elif in_body: # continue appending bits to the body_parts list.
                body_parts.extend(line_parts)
            else:
                raise RuntimeError(
                    "Failed to parse FLUKA input line: {}".format(line))
        else: # we should always break out of the above loop with END.
            raise RuntimeError("Unable to parse FLUKA bodies.")

    def _parseRegions(self) :
        regions_block = self._lines[self.regionsbegin:self.regionsend]
        regions_block = "\n".join(regions_block) # turn back into 1 big string

        # Create ANTLR4 char stream from processed regions_block string
        istream = antlr4.InputStream(regions_block)
        # tokenize
        lexed_input = RegionLexer(istream)
        lexed_input.removeErrorListeners()
        lexed_input.addErrorListener(SensitiveErrorListener())

        # Create a buffer of tokens from lexer
        tokens = antlr4.CommonTokenStream(lexed_input)

        # Create a parser that reads from stream of tokens
        parser = RegionParser(tokens)
        parser.removeErrorListeners()
        parser.addErrorListener(SensitiveErrorListener())

        tree = parser.regions() # build the tree

        visitor = RegionVisitor(self.flukaregistry)
        visitor.visit(tree)  # walk the tree, populating flukaregistry

    def _parseCards(self):
        fixed = True # start off parsing as fixed, i.e. not free format.
        cards = []
        # Parse everything except the bodies and the regions as cards:
        lines = self._lines[:self.geobegin] + self._lines[self.latticebegin:]
        inTitle = False
        for line in lines:
            if inTitle: # Special treatment for the title line.
                self.title = line
                inTitle = False
                kw = None
            elif fixed:
                cards.append(Card.fromFixed(line))
                kw = cards[-1].keyword
            else: # must be free format
                cards.append(Card.fromFree(line))
                kw = cards[-1].keyword

            if kw == "TITLE":
                inTitle = True
            if kw == "GLOBAL": # See manual
                if cards[-1].what4 == 2.0:
                    fixed = False
            elif kw != "FREE" and kw != "FIXED":
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
            rotdefi = RotoTranslation.fromCard(card)
            name = rotdefi.name
            self.flukaregistry.addRotoTranslation(rotdefi)

    def _parseGeometryDirective(self, line_parts,
                                expansion_stack,
                                translation_stack,
                                transform_stack):

        directive = line_parts[0].lower()
        if directive == "$start_translat":
            # CONVERTING TO MILLIMETRES HERE
            translation_stack.append(
                Three([10*float(x) for x in line_parts[1:4]]))
        elif directive == "$end_translat":
            translation_stack.pop()
        elif directive == "$start_expansion":
            expansion_stack.append(float(line_parts[1]))
        elif directive == "$end_expansion":
            expansion_stack.pop()
        elif directive == "$start_transform":
            transform_name = line_parts[1]
            inverse = False
            if transform_name.startswith("-"):
                transform_name = transform_name[1:]
                inverse = True
            transform = self.flukaregistry.rotoTranslations[transform_name]
            transform_stack.append((transform, inverse))
        elif directive == "$end_transform":
            transform_stack.pop()
        else:
            raise ValueError("Unknown geometry directive: {}.".format(directive))

    def _parseMaterialAssignments(self):
        material_assignments = dict()
        regions = self.flukaregistry.regionDict
        # Need to make a list of the keys to account for index-based
        # material assignments.
        regionlist = self.flukaregistry.regionDict.keys()
        for card in self.cards:
            if card.keyword != "ASSIGNMA" and card.keyword != "ASSIGNMAT":
                continue

            material_name = card.what1
            region_lower = card.what2
            region_upper = card.what3
            step = card.what4

            # WHAT1 is the material name or index
            if material_name is None:
                material_name = 1
            elif (not isinstance(material_name, basestring)
                    and int(material_name) <= 0.0):
                material_name = 1

            # WHAT2 is either the lower region name or index.
            if isinstance(region_lower, basestring):
                if region_lower not in regionlist:
                    continue
                start = regionlist.index(region_lower)
            elif material_name is None:
                start = 2
            else:
                start = int(card.what1)

            # WHAT3 is the upper region name or index.
            if isinstance(region_upper, basestring):
                if region_upper not in regionlist:
                    msg = ("Region {} referred to in WHAT3 of ASSIGNMA"
                           " has not been defined.".format(region_upper))
                    raise ValueError(msg)
                stop = regionlist.index(region_upper)
            elif region_upper is None:
                stop = start
            else:
                stop = int(region_upper)
            stop += 1

            # WHAT4 is the step length in assigning indices
            if step is None or step == 0.0:
                step = 1
            else:
                step = int(step)

            # Add 1 to index as the bound is open on the upper bound
            # in python, but closed in the ASSIGMA case of fluka.
            for region_name in regionlist[start:stop+1:step]:
                material_assignments[region_name] = material_name
        return material_assignments

    def _assignMaterials(self):
        for region_name in self.flukaregistry.regionDict.iterkeys():
            try:
                material = self._material_assignments[region_name]
            except KeyError:
                # if there's no material assigned to a LATTICE cell
                # then it doesn't matter because the material is not
                # used in such circumstances anyway.
                if region_name not in self.flukaregistry.latticeDict:
                    warn("No material assigned to Region {}.".format(
                        region_name))
                continue

            # Don't crash on assigning a material to a region that
            # haven't been defined.
            try:
                self.flukaregistry.regionDict[region_name].material = material
            except KeyError:
                continue

    def _parseLattice(self):
        for card in self.cards:
            if card.keyword != "LATTICE":
                continue
            cellName = card.what1

            if card.what2 is not None:
                msg = "Unable to parse LATTICE with non-default WHAT2."
                raise ValueError(msg)

            transformName = card.sdum
            badPrefixes1 = ("ROT", "Rot", "rot")
            badPrefixes2 = ("RO", "Ro", "ro")
            failmsg = "Currently can't parse LATTICE 'SDUM with '{}' prefixes"
            if transformName.startswith(badPrefixes1):
                try:
                    transformIndex = int(transformName[3:])
                    raise FLUKAError(failmsg.format(", ".join(badPrefix1)))
                except ValueError:
                    pass
            if transformName.startswith(badPrefixes2):
                try:
                    transformIndex = int(transformName[2:])
                    raise FLUKAError(failmsg.format(", ".join(badPrefixes2)))
                except ValueError:
                    pass

            rotoTranslation = self.flukaregistry.rotoTranslations[transformName]

            # Deal with inverse rotation notation
            invert = False
            if transformName[0] == "-":
                invert = True

            cellRegion = self.flukaregistry.regionDict[cellName]
            lattice = Lattice(cellRegion, rotoTranslation,
                              invertRotoTranslation=invert)
            # It's a LATTICE region which we store in the latticeDict,
            # not the regionDict.  Now we know that the region read in
            # previously is a LATTICE cell we don't store it in there
            # any more.
            del self.flukaregistry.regionDict[cellRegion.name]
            self.flukaregistry.addLattice(lattice)


def _make_body(body_parts,
               expansion_stack, translation_stack, transform_stack, flukareg):
    # definition is string of the entire definition as written in the file.
    body_type = body_parts[0]
    name = body_parts[1]
    # WE ARE CONVERTING FROM CENTIMETRES TO MILLIMETRES HERE.
    p = [float(p)*10. for p in body_parts[2:]] # p = parameters

    # Note that we have to reverse the transform stack to match FLUKA
    # here, because it seems that FLUKA applys nested transforms
    # outside first, rather than inside first.

    # deepcopies because otherwise when we pop from the stacks, we
    transform_stack = deepcopy(transform_stack[::-1])
    rotoTranslations = [x[0] for x in transform_stack]
    inversion_stack = [x[1] for x in transform_stack]
    transform = Transform(expansion=deepcopy(expansion_stack),
                          translation=deepcopy(translation_stack),
                          rotoTranslation=rotoTranslations,
                          invertRotoTranslation=inversion_stack)

    if body_type == "RPP":
        b = body.RPP(name, *p, flukaregistry=flukareg, transform=transform)
    elif body_type == "RCC":
        b = body.RCC(name, p[0:3], p[3:6], p[6], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "XYP":
        b = body.XYP(name, p[0], flukaregistry=flukareg, transform=transform)
    elif body_type == "XZP":
        b = body.XZP(name, p[0], flukaregistry=flukareg, transform=transform)
    elif body_type == "YZP":
        b = body.YZP(name, p[0], flukaregistry=flukareg, transform=transform)
    elif body_type == "PLA":
        b = body.PLA(name, p[0:3], p[3:6], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "XCC":
        b = body.XCC(name, p[0], p[1], p[2], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "YCC":
        b = body.YCC(name, p[0], p[1], p[2], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "ZCC":
        b = body.ZCC(name, p[0], p[1], p[2], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "XEC":
        b = body.XEC(name, p[0], p[1], p[2], p[3], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "YEC":
        b = body.YEC(name, p[0], p[1], p[2], p[3], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "ZEC":
        b = body.ZEC(name, p[0], p[1], p[2], p[3], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "TRC":
        b = body.TRC(name, p[0:3], p[3:6], p[6], p[7], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "SPH":
        b = body.SPH(name, p[0:3], p[3], flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "REC":
        b = body.REC(name, p[0:3], p[3:6], p[6:9], p[9:12],
                     flukaregistry=flukareg, transform=transform)
    elif body_type == "ELL":
        b = body.ELL(name, p[0:3], p[3:6], p[6],
                     flukaregistry=flukareg, transform=transform)
    elif body_type == "BOX":
        b = body.BOX(name, p[0:3], p[3:6], p[6:9], p[9:12],
                     flukaregistry=flukareg, transform=transform)
    elif body_type == "WED":
        b = body.WED(name, p[0:3], p[3:6], p[6:9], p[9:12],
                     flukaregistry=flukareg, transform=transform)
    elif body_type == "RAW":
        b = body.RAW(name, p[0:3], p[3:6], p[6:9], p[9:12],
                     flukaregistry=flukareg, transform=transform)
    elif body_type == "ARB":
        vertices = [p[0:3], p[3:6], p[6:9], p[9:12],
                    p[12:15], p[15:18], p[18:21], p[21:24]]
        facenumbers = p[24:]
        # Remember we converted to param to millimetres blindly above, well,
        # facenumbers are not dimensions, but indices, so we convert
        # back to "centimetres" here:
        facenumbers = [f/10. for f in facenumbers]
        b = body.ARB(name, vertices, facenumbers,
                     flukaregistry=flukareg,
                     transform=transform)
    elif body_type == "QUA":
        b = body.QUA(name, *p, flukaregistry=flukareg, transform=transform)
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
        if isinstance(right_solid, tuple):
            right_solid = [right_solid]

        return left_solid + right_solid

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
            if not isinstance(sub_zone, list):
                sub_zone = [sub_zone]
            return sub_zone + expr
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

        if ctx.BodyName():
            body = self.flukaregistry.bodyDict[ctx.BodyName().getText()]
            z.addIntersection(body)

        for op, body in solids:
            if op == "+":
                z.addIntersection(body)
            else:
                z.addSubtraction(body)
        return (operator, z)

    def visitZoneExpr(self, ctx):
        opsAndBooleans= self.visit(ctx.expr())

        if not ctx.BodyName():
            return opsAndBooleans

        bodyName = ctx.BodyName().getText()
        body = self.flukaregistry.bodyDict[bodyName]
        boolean = [("+", body)] # implicit intersection
        boolean.extend(opsAndBooleans)
        return boolean

    def visitZoneSubZone(self, ctx):
        opsAndBooleans= self.visit(ctx.subZone())

        if not ctx.BodyName():
            return opsAndBooleans

        bodyName = ctx.BodyName().getText()
        body = self.flukaregistry.bodyDict[bodyName]
        boolean = [("+", body)] # implict intersection
        boolean.extend(opsAndBooleans)
        return boolean

    def visitZoneBody(self, ctx):
        bodyName = ctx.BodyName().getText()
        body = self.flukaregistry.bodyDict[bodyName]
        return [("+", body)] # implicit intersection

class SensitiveErrorListener(antlr4.error.ErrorListener.ErrorListener):
    """ANTLR4 by default is very passive regarding parsing errors, it will
    just carry on parsing and potentially build a nonsense-tree. This
    is not ideal as pyfluka has a very convoluted syntax; we want to
    be very strict about what our parser can and can't do.  For that
    reason this is a very sensitive error listener, throwing
    exceptions readily.

    """
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        msg = ("At ({}, {}), Error: {}.  Warning:  The provided line and"
               " column numbers may be deceptive.").format(line, column, msg)
        raise antlr4.error.Errors.ParseCancellationException(msg)

def main(filein):
    r = Reader(filein)

if __name__ == '__main__':
    main(sys.argv[1])
