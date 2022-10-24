# Generated from RegionParser.g4 by ANTLR 4.7
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by RegionParser.

class RegionParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RegionParser#regions.
    def visitRegions(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#simpleRegion.
    def visitSimpleRegion(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#complexRegion.
    def visitComplexRegion(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#multipleUnion.
    def visitMultipleUnion(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#singleUnion.
    def visitSingleUnion(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#multipleUnion2.
    def visitMultipleUnion2(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#zoneExpr.
    def visitZoneExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#zoneSubZone.
    def visitZoneSubZone(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#zoneBody.
    def visitZoneBody(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#singleUnary.
    def visitSingleUnary(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#unaryAndBoolean.
    def visitUnaryAndBoolean(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#unaryAndSubZone.
    def visitUnaryAndSubZone(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#oneSubZone.
    def visitOneSubZone(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#subZone.
    def visitSubZone(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#unaryExpression.
    def visitUnaryExpression(self, ctx):
        return self.visitChildren(ctx)


