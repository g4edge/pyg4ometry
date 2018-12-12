#!/usr/bin/env python

import sys

from antlr4 import *

from GdmlExpressionLexer import GdmlExpressionLexer
from GdmlExpressionParser import GdmlExpressionParser
from GdmlExpressionVisitor import GdmlExpressionVisitor
import math

from IPython import embed

class EvalVisitor(GdmlExpressionVisitor):
    def __init__(self):
        self.defines = {}

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

    def visitMultiplyingExpression(self, ctx):
        left = float(self.visit(ctx.powExpression(0)))
        right = float(self.visit(ctx.powExpression(1)))
        if ctx.op.type == GdmlExpressionParser.TIMES:
            return left * right
        return left / right

    def visitExpression(self, ctx):
        left = float(self.visit(ctx.multiplyingExpression(0)))
        right = float(self.visit(ctx.multiplyingExpression(1)))
        if ctx.op.type == GdmlExpressionParser.PLUS:
            return left + right
        return left - right

    def visitPowExpression(self, ctx):
        left = float(self.visit(ctx.signedAtom(0)))
        right = float(self.visit(ctx.signedAtom(1)))
        return left ** right

    def visitParens(self, ctx):
        return self.visit(ctx.expression())

    def visitSignedAtom(self, ctx):
        sign = -1 if ctx.MINUS() else 1
        if ctx.func():
            value = self.visit(ctx.func())
        elif ctx.atom():
            value = self.visit(ctx.atom())
        elif self.signedAtom():
            value = self.visit(ctx.signedAtom())
        else:
            raise SystemExit("Signed atom done fucked up.")

        return sign*float(value)

    def visitAtom(self, ctx):
        sign = -1 if ctx.MINUS() else 1
        if ctx.func():
            value = self.visit(ctx.func())
        elif ctx.atom():
            value = self.visit(ctx.atom())
        elif self.signedAtom():
            value = self.visit(ctx.signedAtom())
        else:
            raise SystemExit("Signed atom done fucked up.")

        return sign*float(value)

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
    lexer = GdmlExpressionLexer(istream)
    # embed()
    # Create a buffer of tokens from lexer
    tokens= CommonTokenStream(lexer)
    # embed()
    # create a parser that reads from stream of tokens
    parser = GdmlExpressionParser(tokens)

    # Create parsing tree.
    tree = parser.equation()
    # print tree.toStringTree(recog=parser) # print LISP-style tree.
    # embed()

    visitor = EvalVisitor()
    visitor.visit(tree)


if __name__ == '__main__':
    main(sys.argv)
