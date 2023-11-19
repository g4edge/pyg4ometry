# Generated from GdmlExpression.g4 by ANTLR 4.13.1
from antlr4 import *

if "." in __name__:
    from .GdmlExpressionParser import GdmlExpressionParser
else:
    from GdmlExpressionParser import GdmlExpressionParser

# This class defines a complete generic visitor for a parse tree produced by GdmlExpressionParser.


class GdmlExpressionVisitor(ParseTreeVisitor):
    # Visit a parse tree produced by GdmlExpressionParser#equation.
    def visitEquation(self, ctx: GdmlExpressionParser.EquationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#expression.
    def visitExpression(self, ctx: GdmlExpressionParser.ExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#multiplyingExpression.
    def visitMultiplyingExpression(self, ctx: GdmlExpressionParser.MultiplyingExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#operatorAddSub.
    def visitOperatorAddSub(self, ctx: GdmlExpressionParser.OperatorAddSubContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#operatorMulDiv.
    def visitOperatorMulDiv(self, ctx: GdmlExpressionParser.OperatorMulDivContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#powExpression.
    def visitPowExpression(self, ctx: GdmlExpressionParser.PowExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#signedAtom.
    def visitSignedAtom(self, ctx: GdmlExpressionParser.SignedAtomContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#atom.
    def visitAtom(self, ctx: GdmlExpressionParser.AtomContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#scientific.
    def visitScientific(self, ctx: GdmlExpressionParser.ScientificContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#matrixElement.
    def visitMatrixElement(self, ctx: GdmlExpressionParser.MatrixElementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#constant.
    def visitConstant(self, ctx: GdmlExpressionParser.ConstantContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#variable.
    def visitVariable(self, ctx: GdmlExpressionParser.VariableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#func.
    def visitFunc(self, ctx: GdmlExpressionParser.FuncContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#funcname.
    def visitFuncname(self, ctx: GdmlExpressionParser.FuncnameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GdmlExpressionParser#relop.
    def visitRelop(self, ctx: GdmlExpressionParser.RelopContext):
        return self.visitChildren(ctx)


del GdmlExpressionParser
