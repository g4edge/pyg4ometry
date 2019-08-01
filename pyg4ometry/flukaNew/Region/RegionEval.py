#!/usr/bin/env python

import sys

from antlr4 import *

from RegionLexer import RegionLexer
from RegionParser import RegionParser
from RegionVisitor import RegionVisitor

import math

from IPython import embed
import traceback

class RegionEvalVisitor(RegionVisitor):
    def __init__(self):
        self.defines = {}

    def visitSignbody(self, ctx):
        name = ctx.BODYNAME().getText();
        sign = "-" if ctx.MINUS() else "+"
        value = self.defines[name]
        return "{}{}".format(sign, value)

    def visitSubzone(self, ctx):
        value = self.visit(ctx.expression())
        sign = "-" if ctx.MINUS() else "+"

        return "{}({})".format(sign, value)

    def visitExpression(self, ctx):

        result = ""
        for ch in ctx.children:
            result += self.visit(ch)
        return result

    def visitRegion(self, ctx):
        left = self.visit(ctx.expression(0))

        for i in range(len(ctx.BAR())):
            right = self.visit(ctx.expression(i+1))
            left += " | {}".format(right)

        return left


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

def main():
    ev = RegionEvaluator()

    defines = {
        "a" : "A",
        "b" : "B",
        "c" : "C",
        "d" : "D",
        "e" : "E",
        "h" : "H",
        "f" : "F",
        "g" : "G",
        "i" : "I",
        "j" : "J",
        "x" : "X",
        "y" : "Y",
        "z" : "Z",
        "jj" : "JJ",
        "zz" : "ZZ",
    }

    #test = "+a +b +c -d -e" # 01_body_only_exp
    #test = "+a -(+b +c +d -e -f)" # 02_paran_only_expression.inp
    #test = "+a -(+b +c +d -e -f) -g" # 03_body_paran_expression.inp
    test = "+(+a +b) -(+c +d +e) -(+f +g -h) | +zz +(+i +j) -jj | +x +y +z" # 10_bigup.inp

    parse_tree = ev.parse(test)
    output = ev.evaluate(parse_tree, defines)

    print output

if __name__ == "__main__":
    main()
