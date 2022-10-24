# Generated from GdmlExpression.g4 by ANTLR 4.7.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by GdmlExpressionParser.

class GdmlExpressionVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by GdmlExpressionParser#equation.
    def visitEquation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#multiplyingExpression.
    def visitMultiplyingExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#operatorAddSub.
    def visitOperatorAddSub(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#operatorMulDiv.
    def visitOperatorMulDiv(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#powExpression.
    def visitPowExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#signedAtom.
    def visitSignedAtom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#atom.
    def visitAtom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#scientific.
    def visitScientific(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#matrixElement.
    def visitMatrixElement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#constant.
    def visitConstant(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#variable.
    def visitVariable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#func.
    def visitFunc(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#funcname.
    def visitFuncname(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GdmlExpressionParser#relop.
    def visitRelop(self, ctx):
        return self.visitChildren(ctx)


