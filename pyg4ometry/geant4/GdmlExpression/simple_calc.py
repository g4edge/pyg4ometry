#!/usr/bin/env python

import sys

from antlr4 import *

from CalculatorLexer import CalculatorLexer
from CalculatorParser import CalculatorParser
from CalculatorVisitor import CalculatorVisitor
import math

from IPython import embed

class EvalVisitor(CalculatorVisitor):
    def __init__(self):
        self.memory = {}

    def visitAssign(self, ctx):
        name = ctx.ID().getText();
        value = self.visit(ctx.expr())
        self.memory[name] = value
        return value

    def visitPrintExpr(self, ctx):
        value = self.visit(ctx.expr())
        print value
        return 0

    def visitId(self, ctx):
        name = ctx.ID().getText()
        if name in self.memory:
            return self.memory[name]
        return 0

    def visitInt(self, ctx):
        return int(ctx.INT().getText())

    def visitMulDiv(self, ctx):
        left = int(self.visit(ctx.expr(0)))
        right = int(self.visit(ctx.expr(1)))
        if ctx.op.type == CalculatorParser.MUL:
            return left * right
        return left / right

    def visitAddSub(self, ctx):
        left = int(self.visit(ctx.expr(0)))
        right = int(self.visit(ctx.expr(1)))
        if ctx.op.type == CalculatorParser.ADD:
            return left + right
        return left - right

    def visitPow(self, ctx):
        left = int(self.visit(ctx.expr(0)))
        right = int(self.visit(ctx.expr(1)))
        return left ** right

    def visitParens(self, ctx):
        return self.visit(ctx.expr())

    def visitFunCall(self, ctx):
        function_name = ctx.ID().getText()
        function = getattr(math, function_name)
        arguments = [self.visit(expr) for expr in ctx.expr()]
        return function(*arguments)

def main(argv):
    # create a CharStream that reads from standard input
    if len(sys.argv) > 1:
        istream = FileStream(argv[1])
    else:
        input_str = sys.stdin.read()
        istream = InputStream(input_str)

    # tokenise character stream
    lexer = CalculatorLexer(istream)
    # embed()
    # Create a buffer of tokens from lexer
    tokens= CommonTokenStream(lexer)
    # embed()
    # create a parser that reads from stream of tokens
    parser = CalculatorParser(tokens)

    # Create parsing tree.
    tree = parser.prog()
    # print tree.toStringTree(recog=parser) # print LISP-style tree.
    # embed()

    visitor = EvalVisitor()
    visitor.visit(tree)


if __name__ == '__main__':
    main(sys.argv)
