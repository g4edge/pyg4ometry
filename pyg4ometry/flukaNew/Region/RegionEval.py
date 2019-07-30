#!/usr/bin/env python

import sys

from antlr4 import *

from RegionLexer import GdmlExpressionLexer
from RegionParser import GdmlExpressionParser
from RegionVisitor import GdmlExpressionVisitor

import math

from IPython import embed
import traceback

class RegionEvalVisitor(RegionVisitor):
    def __init__(self):
        self.defines = {}

    def visitSignbody(self, ctx):
        name = ctx.BODYNAME().getText();
        sign = -1 if ctx.MINUS() else 1

        return self.defines[name]

    def visitSubzone(self, ctx):
        value = self.visit(ctx.expression)
        sign = -1 if ctx.MINUS() else 1
        # Maybe something like:
        # if sign < 0:
        # return Invert(value)

        return sign*value

    def visitExpression(self, ctx):
        pass


    def visitRegion(self, ctx):
        pass


class RegionEvaluator(object):
    def __init__(self):
        self.visitor = RegionEvalVisitor()
        self.defines_dict = {}

    def parse(self, input):
        # Make a char stream out of the input
        istream = InputStream(input) # Can do directly as a string?
        # tokenise character stream
        lexer = RegionLexer(istream)
        # Create a buffer of tokens from lexer
        tokens= CommonTokenStream(lexer)
        # create a parser that reads from stream of tokens
        parser = RegionParser(tokens)

        parse_tree = parser.region()

        return parse_tree

    def evaluate(self, parse_tree, define_dict={}):
        # Update the defines dict for every evaluation
        self.visitor.defines = define_dict
        result = self.visitor.visit(parse_tree)

        return result
