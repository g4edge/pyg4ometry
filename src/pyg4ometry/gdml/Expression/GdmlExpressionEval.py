from antlr4 import *

from .GdmlExpressionLexer import GdmlExpressionLexer
from .GdmlExpressionParser import GdmlExpressionParser
from .GdmlExpressionVisitor import GdmlExpressionVisitor

from ..Units import units as _units

import math
import numpy

#from IPython import embed
#import traceback

class GdmlExpressionEvalVisitor(GdmlExpressionVisitor):
    def __init__(self):
        self.defines = {}

    def visitVariable(self, ctx):
        name = ctx.VARIABLE().getText();

        try:
            value = self.defines[name]
        except KeyError:
            try:
                value = _units[name]
            except KeyError as err:
                msg = "<= Undefined variable : {}".format(name)
                if not err.args:
                    err.args=('',)
                err.args = err.args + (msg,)
                raise

        return value

    def visitPrintExpr(self, ctx):
        value = self.visit(ctx.expr())
        print(value)
        return 0

    def visitScientific(self, ctx):
        return float(ctx.SCIENTIFIC_NUMBER().getText())

    def visitMultiplyingExpression(self, ctx):
        left = float(self.visit(ctx.powExpression(0)))

        for i in range(len(ctx.operatorMulDiv())):
            right = float(self.visit(ctx.powExpression(i+1)))
            if ctx.operatorMulDiv(i).TIMES():
                left  *= right
            else:
                left  /= right
        return left

    def visitExpression(self, ctx):
        left = float(self.visit(ctx.multiplyingExpression(0)))

        for i in range(len(ctx.operatorAddSub())):
            right = float(self.visit(ctx.multiplyingExpression(i+1)))
            if ctx.operatorAddSub(i).PLUS():
                left += right
            else:
                left -= right
        return left

    def visitPowExpression(self, ctx):
        base = float(self.visit(ctx.signedAtom(0)))
        for i in range(len(ctx.POW())):
            power = float(self.visit(ctx.signedAtom(i+1)))
            base = base ** power

        return base

    def visitMatrixElement(self, ctx):
        matrix = self.visit(ctx.variable())
        indices = [int(self.visit(ctx.expression(0)))-1] # at least one index
        for i in range(len(ctx.COMMA())):
            index = int(self.visit(ctx.expression(i+1)))  #only integer access
            indices.append(index-1) # decrement indices to match python 0-indexing
        return matrix.values_asarray[tuple(indices)]


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
            value = self.visit(ctx.constant())
        elif ctx.variable():
            value = self.visit(ctx.variable())
        elif ctx.expression(): # This handles expr with and without parens
            value = self.visit(ctx.expression())
        elif ctx.scientific():
            value = self.visit(ctx.scientific())
        elif ctx.matrixElement():
            value = self.visit(ctx.matrixElement())
        else:
            raise SystemExit("Invalid atom.") ##DEBUG####

        return float(value)

    def visitFunc(self, ctx):
        function_name = str(self.visit(ctx.funcname()))
        if hasattr(math, function_name):
            function = getattr(math, function_name)
        elif hasattr(numpy, function_name):
            function = getattr(numpy, function_name)
        else:
            raise ValueError("Function {} not found in 'numpy' or 'math'"
                             "".format(function_name))
            
        arguments = [self.visit(expr) for expr in ctx.expression()]
        return function(*arguments)

    def visitFuncname(self, ctx):
        funcs = ["SIN", "COS", "TAN", "ACOS",
                 "ASIN", "ATAN", "LOG", "LN",
                 "EXP", "SQRT", "POWER", "ABS"]
        for f in funcs:
            function = getattr(ctx, f)
            if function():
                return function().getText()

    def visitConstant(self, ctx):
        constants = ["PI", "EULER", "I"]
        for c in constants:
            constant = getattr(ctx, c)
            if constant():
                return getattr(math, constant().getText())

class ExpressionParser(object):
    def __init__(self):
        self.visitor = GdmlExpressionEvalVisitor()
        self.defines_dict = {}

    def parse(self, expression):
        # Make a char stream out of the expression
        istream = InputStream(expression) # Can do directly as a string?
        # tokenise character stream
        lexer = GdmlExpressionLexer(istream)
        # Create a buffer of tokens from lexer
        tokens= CommonTokenStream(lexer)
        # create a parser that reads from stream of tokens
        parser = GdmlExpressionParser(tokens)

        parse_tree = parser.expression()

        return parse_tree

    def evaluate(self, parse_tree, define_dict={}):
        # Update the defines dict for every evaluation
        self.visitor.defines = define_dict
        result = self.visitor.visit(parse_tree)

        return result

    def get_variables(self, parse_tree):
        variables = []
        if hasattr(parse_tree, "children"):
            for ch in parse_tree.children:
                if isinstance(ch, GdmlExpressionParser.VariableContext):
                    variables.append(ch.getText())
                else:
                    variables.extend(self.get_variables(ch))

        return variables
