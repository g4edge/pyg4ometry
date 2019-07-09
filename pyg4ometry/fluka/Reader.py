
"""Load Fluka files."""
import os.path
import collections
import warnings
import textwrap

import antlr4

from . import FlukaLexer
from . import FlukaParser
from . import materials
from .model import Model
from .FlukaParserVisitor import FlukaParserVisitor
from .FlukaParserListener import FlukaParserListener

class Reader(object):
    def __init__(self, filename, fluka_g4_material_map=None):
        self.filename = filename
        self.fluka_model = Model()
        # get the syntax tree and defined cards
        ast, self.cards = get_geometry_ast_and_cards(filename)

        self._readBodies(ast)
        self._readRegions(ast)



    def _read_before_geometry(self):
        pass

    def _read_after_geometry(self):
        pass

    def _read_not_geometry(self):
        pass

    def _readBodies(self, ast):
        """Return a tuple of bodies, region scale, and a count of bodies by
        type.

        """
        body_listener = FlukaBodyListener()
        walker = antlr4.ParseTreeWalker()
        walker.walk(body_listener, ast)
        body_freq_map = body_listener.body_freq_map
        bodies = body_listener.bodies
        self.fluka_model.bodies = bodies

    def _readRegions(self, tree):
    # def _regions_from_tree(self, tree):
        visitor = FlukaRegionVisitor(self.fluka_model.bodies)
        visitor.visit(tree)
        self.regions = visitor.regions

    def _assignMaterialsToRegions(self, fluka_g4_material_map):
        fluka_region_materials = self.readMaterials()

        regions_and_materials = materials.get_region_material_pairs(
            self.regions.keys(),
            self.cards)


        # Assign the materials if provided with a FLUKA->G4 material map.
        # Circular dependencies means we can't do this until after the regions
        # are defined: Material assignments depend on the order in which the
        # regions are defined, which we get from the region definitions, which
        # in turn nominally depend on the material assignments.  To get around
        # this we set the material to G4_Galactic at region initialisation and
        # then reassign immediately afterwards here.
        self._assignMaterialsToRegions(fluka_g4_material_map)

        if fluka_g4_material_map:
            # Always set BLCKHOLE to None.  We always omit regions with material
            # BLCKHOLE.
            fluka_g4_material_map["BLCKHOLE"] = None
            for region_name, region in self.regions.iteritems():
                fluka_material = regions_and_materials[region_name]
                try:
                    g4_material = fluka_g4_material_map[fluka_material]
                    region.material = g4_material
                except KeyError:
                    msg = ("Missing material \"{}\"from"
                           " FLUKA->G4 material map!").format(fluka_material)
                    warnings.warn(msg)

        else: # If no material map, we still want to omit BLCKHOLE
            # regions from viewing/conversion.
            msg = '\n'.join(textwrap.wrap(
                "No FLUKA->G4 material map provided.  All converted regions"
                " will be \"G4_Galactic\" by default, but BLCKHOLE regions"
                " will still be omitted from both conversion and viewing."))
            print(msg, '\n')

            for region_name, region in self.regions.iteritems():
                fluka_material = regions_and_materials.get(region_name)
                if fluka_material == "BLCKHOLE":
                    fluka_material = None
                else:
                    fluka_material = "G4_Galactic"
                region.material = fluka_material



        # regions = _readRegions
        # self.regions = self._regions_from_tree(tree)


        pass

    def readMaterials(self):
        return

    # def readConfiguation(self):
    #     pass

# # FIRST I MUST UNDERSTAND HOW INCLUDES ARE DONE IN FLUPIX.  Does a
# # define in the current file affect the file included?
# # ALSO What does "#define x 0" do?  does it actually affect the definition?

# class _Preprocessor(object):
#     def __init__(self, path):
#         if not os.path.exists(path):
#             raise IOError("File not found: %s" % path)
#         self.path = path
#         self.defined_names = set()
#         self.if_stack = [] # [(name, defined?), ...]
#         self.elif_stack = [] # [(name, defined?), ...]

#     def preprocess(self):
#         with open(self.path, 'r') as f:
#             for line in f:
#                 if (self.skip_to_end_of_conditional
#                     and not line.startswith(("#elif", "#endif"))):
#                     continue
#                 elif line.startswith("#"):
#                     self._preprocess_line(line)
#                 else:
#                     yield line

#     def _define(self, line):
#         name = line.split()[1]
#         self.defined_names.add(name)

#     def _undef(self, line):
#         name = line.split()[1]
#         try:
#             self.defined_names.remove(name)
#         except KeyError: # it wasn't defined.  allow this.
#             pass

#     def _if(self, line):
#         name = line.split()[1]
#         self.if_stack.append((name, name in self.defined_names))

#     def _elif(self, line):
#         name = linesplit()[1]
#         self.elif_stack.append((name, name in self.defined_names))

#     def _endif(self, line):
#         self.elif
#         self.if_stack.pop()

#     def _include(self, line):
#         path = line.split()[1]
#         new_pp = _PreProcessor(path)
#         yield new_pp.preprocess()

#     def _preprocess_line(self, line):
#         try:
#             pp_type = line.split()[0][1:] # "define", "if", etc..
#             getattr(self, "_{}".format(pp_type)
#         except AttributeError, IndexError:
#             raise ValueError("Not a preprocessor line: {}".format(line))

# # def preprocess(path):

# #     with open(path, 'r') as f:
# #         for line in f:
# #             if skip_to_next_conditional is True:
# #                 continue
# #             elif line.startswith('#'):
# #                 _dispatch_preprocessor_line(line, defined_names, if_stack)


# # FIRST I MUST UNDERSTAND HOW INCLUDES ARE DONE IN FLUPIX.  Does a
# # define in the current file affect the file included?
# # ALSO What does "#define x 0" do?  does it actually affect the definition?

# class _Preprocessor(object):
#     def __init__(self, path):
#         if not os.path.exists(path):
#             raise IOError("File not found: %s" % path)
#         self.path = path
#         self.defined_names = set()
#         self.if_stack = [] # [(name, defined?), ...]
#         self.elif_stack = [] # [(name, defined?), ...]

#     def preprocess(self):
#         with open(self.path, 'r') as f:
#             for line in f:
#                 if (self.skip_to_end_of_conditional
#                     and not line.startswith(("#elif", "#endif"))):
#                     continue
#                 elif line.startswith("#"):
#                     self._preprocess_line(line)
#                 else:
#                     yield line

#     def _define(self, line):
#         name = line.split()[1]
#         self.defined_names.add(name)

#     def _undef(self, line):
#         name = line.split()[1]
#         try:
#             self.defined_names.remove(name)
#         except KeyError: # it wasn't defined.  allow this.
#             pass

#     def _if(self, line):
#         name = line.split()[1]
#         self.if_stack.append((name, name in self.defined_names))

#     def _elif(self, line):
#         name = linesplit()[1]
#         self.elif_stack.append((name, name in self.defined_names))

#     def _endif(self, line):
#         self.elif
#         self.if_stack.pop()

#     def _include(self, line):
#         path = line.split()[1]
#         new_pp = _PreProcessor(path)
#         yield new_pp.preprocess()

#     def _preprocess_line(self, line):
#         try:
#             pp_type = line.split()[0][1:] # "define", "if", etc..
#             getattr(self, "_{}".format(pp_type)
#         except AttributeError, IndexError:
#             raise ValueError("Not a preprocessor line: {}".format(line))

# # def preprocess(path):

# #     with open(path, 'r') as f:
# #         for line in f:
# #             if skip_to_next_conditional is True:
# #                 continue
# #             elif line.startswith('#'):
# #                 _dispatch_preprocessor_line(line, defined_names, if_stack)


def get_geometry_ast_and_cards(path):
    """Return the antlr4 syntax tree for the given file."""
    if not os.path.exists(path):
        raise IOError("File not found: %s" % path)

    with open(path, 'r') as fluka_file:
        lines = fluka_file.readlines()

    not_geometry, geometry = _separate_geometry(lines)

    # Create ANTLR4 char stream from processed model string
    # geometry is a list of strings here, so join as single string.
    istream = antlr4.InputStream(''.join(geometry))

    # Tokenise character stream
    lexed_input = FlukaLexer.FlukaLexer(istream)
    lexed_input.removeErrorListeners()
    lexed_input.addErrorListener(SensitiveErrorListener())

    # Create a buffer of tokens from lexer
    tokens = antlr4.CommonTokenStream(lexed_input)

    # Create a parser that reads from stream of tokens
    parser = FlukaParser.FlukaParser(tokens)
    parser.removeErrorListeners()
    parser.addErrorListener(SensitiveErrorListener())

    # Create syntax tree
    tree = parser.geocards()

    # Blindly assume all lines in not_geometry are of fixed format.  Will be OK
    # for now.
    not_geometry = map(Card.from_fixed_line, not_geometry)
    return tree, not_geometry


def _separate_geometry(lines):
    """Separate the model into two parts, lines describing the
    geometry, and lines describing what is not the geometry.  In both
    cases, the other is commented out rather than removed.  This is
    useful as the line numbering is retained.

    """
    # Get the two indices of geobegin and geoend
    try:
        geo_begin_index = (i for i, line in enumerate(lines)
                           if line.startswith("GEOBEGIN")).next()
        geo_end_index = (i for i, line in enumerate(lines)
                         if line.startswith("GEOEND")).next()
    except StopIteration:
        msg = "GEOBEGIN and/or GEOEND cards not found and/or malformed!"
        raise IOError(msg)

    body_types = ["ARB", "BOX", "ELL", "PLA", "QUA", "RAW",
                  "RCC", "REC", "RPP", "SPH", "TRC", "WED",
                  "XCC", "XEC", "XYP", "XZP", "YCC", "YEC",
                  "YZP", "ZCC", "ZEC"]
    # Check if line after geobegin is a body definition, if not then
    # it is part of the GEOBEGIN card, and move begin_index onwards one.
    for body_type in body_types:
        if lines[geo_begin_index + 1].startswith(body_type):
            break
    else: # no break
        geo_begin_index += 1

    # Split the model into 3 parts
    before_geometry = lines[:geo_begin_index + 1]
    geometry = lines[geo_begin_index + 1:geo_end_index]
    after_geometry = lines[geo_end_index:]

    # Create list of equal length of commented lines to preserve line numbers
    commented_before_geometry = len(before_geometry) * ["*\n"]
    commented_after_geometry = len(after_geometry) * ["*\n"]
    # Assemble and return the two sets:
    geometry = commented_before_geometry + geometry + commented_after_geometry
    not_geometry = before_geometry + after_geometry

    return _strip_comments(not_geometry), geometry


def _strip_comments(lines):
    return [line for line in lines if not line.startswith('*')]

class Card(collections.namedtuple("Card",
                                  ["keyword", "what1", "what2", "what3",
                                   "what4", "what5", "what6", "sdum"])):

    @classmethod
    def from_fixed_line(cls, line):
        # Don't know if this is actually necessary but just in case..
        if len(line) > 80:
            raise TypeError("Line too long!  Maximum line length is 80.")
        line = line.rstrip('\n')
        # column positions are multiples of 10 up to 80 inclusive.
        positions = [10 * x for x in range(9)]
        # Split the line into a list of strings according to the positions
        columns = [line[start:stop]
                   for start, stop in zip(positions, positions[1:])]
        # remove trailing/leading whitepace
        columns = [column.strip() for column in columns]
        # Empty strings -> None
        columns = [column if column != "" else None for column in columns]
        columns = [Card._attempt_float_coercion(column) for column in columns]
        return cls(*columns)

    @classmethod
    def from_free_line(cls, line, sep=None):
        pass

    def warn_not_supported(self, supported_fields):
        """User provides an iterable of SUPPORTED fields of the form
        ["what1", "what2", "sdum"], and warnings will be raised once if
        there are any fields which are not None which do not feature in fields.

        """
        for field in self._fields:
            if (getattr(self, field) is not None
                    and field not in supported_fields):
                warnings.simplefilter('once', UserWarning)
                msg = ("{} not supported for card \"{}\"."
                       "  This field will be ignored.".format(field.upper(),
                                                              self.keyword))
                warnings.warn(msg)

    @staticmethod
    def _attempt_float_coercion(string):
        try:
            return float(string)
        # (Not a coercable string, not a coercable type)
        except (ValueError, TypeError):
            return string


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


class FlukaBodyListener(FlukaParserListener):
    """
    This class is for getting simple, declarative  information about
    the geometry model.  In no particular order:

    - Body definitions, including surrounding geometry directives
    - Stats like names and frequencies for body types and regions.

    """
    def __init__(self):
        self.bodies = dict()

        self.body_freq_map = dict()
        self.unique_body_names = set()
        self.used_bodies_by_type = list()

        self.current_translat = None
        self.current_expansion = None

    def enterBodyDefSpaceDelim(self, ctx):
        # This is where we get the body definitions and instantiate
        # them with the relevant pyfuka.bodies classes.
        body_name = ctx.ID().getText()
        body_type = ctx.BodyCode().getText()
        body_parameters = FlukaBodyListener._get_floats(ctx)
        # Apply any expansions:
        body_parameters = self.apply_expansions(body_parameters)

        # Try and construct the body, if it's not implemented then
        # warn and continue.
        try:
            self.bodies[body_name] = _make_body(body_type, body_name,
                                                body_parameters,
                                                self.current_translat)
        except ValueError:
            warnings.simplefilter('once', UserWarning)
            msg = ("""Body type "{}" not supported.  All bodies of
this type will be omitted.  If bodies of this type are used in
regions, viewing and conversion will most likely fail.""".format(body_type))
            warnings.warn(msg)

    def enterUnaryExpression(self, ctx):
        body_name = ctx.ID().getText()
        # used, then record its name and type.
        if body_name not in self.unique_body_names:
            self.unique_body_names.add(body_name)
            body_type = type(self.bodies[body_name]).__name__
            self.used_bodies_by_type.append(body_type)

    def enterTranslat(self, ctx):
        translation = FlukaBodyListener._get_floats(ctx)
        if self.current_translat is not None:
            # Nested translations are not supported.
            raise FLUKAInputError("Nested translations are forbidden.")
        self.current_translat = pyfluka.vector.Three(translation)

    def exitTranslat(self, ctx):
        self.current_translat = None

    def enterExpansion(self, ctx):
        self.current_expansion = float(ctx.Float().getText())

    def exitExpansion(self, ctx):
        self.current_expansion = None

    def apply_expansions(self, parameters):
        """
        Method for applying the current expansion to the parameters.

        """
        factor = self.current_expansion
        if factor is not None:
            return [factor * x for x in parameters]
        return parameters

    @staticmethod
    def _get_floats(ctx):
        '''
        Gets the Float tokens associated with the rule and returns
        them as an array of python floats.
        '''
        float_strings = [i.getText() for i in ctx.Float()]
        floats = map(float, float_strings)
        # Converting centimetres to millimetres!!!
        floats = [10 * x for x in floats]
        return floats

    def exitGeocards(self, ctx):
        # When we've finished walking the geometry, count the bodies.
        self.body_freq_map = collections.Counter(self.used_bodies_by_type)
        del self.used_bodies_by_type


class FlukaRegionVisitor(pyfluka.FlukaParserVisitor.FlukaParserVisitor):
    """
    A visitor class for accumulating the region definitions.  The body
    instances are provided at instatiation, and then these are used
    when traversing the tree to build up a dictionary of region name
    and pyfluka.geometry.Region instances.

    """
    def __init__(self, bodies):
        self.bodies = bodies
        self.regions = collections.OrderedDict()

    def visitSimpleRegion(self, ctx):
        # Simple in the sense that it consists of no unions of Zones.
        region_defn = self.visitChildren(ctx)
        # Build a zone from the list of bodies or single body:
        zone = [pyfluka.geometry.Zone(region_defn)]
        region_name = ctx.RegionName().getText()
        # temporarily G4_Galactic
        self.regions[region_name] = pyfluka.geometry.Region(region_name, zone,
                                                            "G4_Galactic")

    def visitComplexRegion(self, ctx):
        # Complex in the sense that it consists of the union of
        # multiple zones.

        # Get the list of tuples of operators and bodies/zones
        region_defn = self.visitChildren(ctx)
        # Construct zones out of these:
        zones = [pyfluka.geometry.Zone(defn) for defn in region_defn]
        region_name = ctx.RegionName().getText()
        region = pyfluka.geometry.Region(region_name, zones, "G4_Galactic")
        self.regions[region_name] = region

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
        zone = pyfluka.geometry.Zone(solids)
        return (operator, zone)


class FLUKAInputError(RuntimeError):
    def __init__(self, message):
        super(RuntimeError, self).__init__(self.message)

def _make_body(body_type, name, parameters, translation):
    """Given a body type, "REC", "XYP", etc, and a list of the parameters
    in the correct order as written in an input file, return the
    correct Body instance.

    """

    try:
        ctor = getattr(pyfluka.geometry, body_type)
    except AttributeError:
        raise ValueError("Body type not supported")

    if body_type in {"XZP", "XYP", "YZP",
                     "XCC", "YCC", "ZCC",
                     "XEC", "YEC", "ZEC"}:
        return ctor(name, *parameters, translation=translation)
    elif body_type == "PLA":
        return ctor(name, parameters[0:3], parameters[3:6],
                    translation=translation)
    elif body_type == "RCC":
        return ctor(name, parameters[0:3], parameters[3:6], parameters[6],
                    translation=translation)
    elif body_type == "RPP":
        return ctor(name,
                    [parameters[0], parameters[2], parameters[4]],
                    [parameters[1], parameters[3], parameters[5]],
                    translation=translation)
    elif body_type == "TRC":
        return ctor(name, parameters[0:3], parameters[3:6],
                    parameters[6], parameters[7], translation=translation)
    elif body_type == "SPH":
        return ctor(name, parameters[0:3], parameters[3],
                    translation=translation)
