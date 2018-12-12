#!/usr/bin/env python

import sys

from antlr4 import *

from GdmlExpressionLexer import GdmlExpressionLexer
from GdmlExpressionParser import GdmlExpressionParser
from GdmlExpressionVisitor import GdmlExpressionVisitor
import math

from IPython import embed
import traceback

class EvalVisitor(GdmlExpressionVisitor):
    def __init__(self):
        self.defines = {}

    def visitAssign(self, ctx):
        name = ctx.ID().getText();
        value = self.visit(ctx.expr())
        self.memory[name] = value
        return value

    def visitVariable(self, ctx):
        name = ctx.VARIABLE().getText();
        value = self.defines.get(name, "1.5")
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

    def visitScientific(self, ctx):
        return float(ctx.SCIENTIFIC_NUMBER().getText())

    def visitMultiplyingExpression(self, ctx):
        left = float(self.visit(ctx.powExpression(0)))
        # Perform all defined multiplications/divisions
        # TODO: Super dumb and slow way of getting the order, rewrite
        ops = [char for char in ctx.getText() if char=="*" or char=="/"]
        for i in range(len(ctx.powExpression())-1):
            print i
            right = float(self.visit(ctx.powExpression(i+1)))
            if ops[i] == "*":
                left  *= right
            else:
                left  /= right
        return left

    def visitExpression(self, ctx):
        left = float(self.visit(ctx.multiplyingExpression(0)))

        # Perform all defined addtions/subtractions
        # TODO: Super dumb and slow way of getting the order, rewrite
        ops = [char for char in ctx.getText() if char=="+" or char=="-"]
        for i in range(len(ctx.multiplyingExpression())-1):
            right = float(self.visit(ctx.multiplyingExpression(i+1)))
            if ops[i] == "+":
                left += right
            else:
                left -= right
        print left
        return left

    def visitPowExpression(self, ctx):
        base = float(self.visit(ctx.signedAtom(0)))
        for i in range(len(ctx.POW())):
            power = float(self.visit(ctx.signedAtom(i+1)))
            base = base ** power

        return base

    def visitParens(self, ctx):
        return self.visit(ctx.expression())

    def visitSignedAtom(self, ctx):
        sign = -1 if ctx.MINUS() else 1
        value = 0
        if ctx.func():
            value = self.visit(ctx.func())
        elif ctx.atom():
            value = self.visit(ctx.atom())
        elif ctx.signedAtom():
            value = self.visit(ctx.signedAtom())
        #else:
        #    raise SystemExit("Invalid signed atom.") ##DEBUG####

        return sign*float(value)

    def visitAtom(self, ctx):
        if ctx.constant():
            value =  getattr(math, ctx.constant())
        elif ctx.variable():
            value = self.visit(ctx.variable())
        elif ctx.expression(): # This handles expr with and without parens
            value = self.visit(ctx.expression())
        elif ctx.scientific():
            value = self.visit(ctx.scientific())
        else:
            raise SystemExit("Invalid atom.") ##DEBUG####

        return float(value)

    def visitFunc(self, ctx):
        function_name = str(self.visit(ctx.funcname()))
        function = getattr(math, function_name)
        arguments = [self.visit(expr) for expr in ctx.expression()]
        return function(*arguments)

    def visitFuncname(self, ctx):
        #TODO: fix this
        return "cos"

def main(argv):
    # create a CharStream that reads from standard input
    if len(sys.argv) > 1:
        istream = FileStream(argv[1])
    else:
        input_str = sys.stdin.read()
        istream = InputStream(input_str)

    print "Input expression: ", str(istream)

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
