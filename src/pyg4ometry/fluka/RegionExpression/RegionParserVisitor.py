# Generated from RegionParser.g4 by ANTLR 4.13.1
from antlr4 import *

if "." in __name__:
    from .RegionParser import RegionParser
else:
    from RegionParser import RegionParser

# This class defines a complete generic visitor for a parse tree produced by RegionParser.


class RegionParserVisitor(ParseTreeVisitor):
    # Visit a parse tree produced by RegionParser#regions.
    def visitRegions(self, ctx: RegionParser.RegionsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#simpleRegion.
    def visitSimpleRegion(self, ctx: RegionParser.SimpleRegionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#complexRegion.
    def visitComplexRegion(self, ctx: RegionParser.ComplexRegionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#multipleUnion.
    def visitMultipleUnion(self, ctx: RegionParser.MultipleUnionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#singleUnion.
    def visitSingleUnion(self, ctx: RegionParser.SingleUnionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#multipleUnion2.
    def visitMultipleUnion2(self, ctx: RegionParser.MultipleUnion2Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#zoneExpr.
    def visitZoneExpr(self, ctx: RegionParser.ZoneExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#zoneSubZone.
    def visitZoneSubZone(self, ctx: RegionParser.ZoneSubZoneContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#zoneBody.
    def visitZoneBody(self, ctx: RegionParser.ZoneBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#singleUnary.
    def visitSingleUnary(self, ctx: RegionParser.SingleUnaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#unaryAndBoolean.
    def visitUnaryAndBoolean(self, ctx: RegionParser.UnaryAndBooleanContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#unaryAndSubZone.
    def visitUnaryAndSubZone(self, ctx: RegionParser.UnaryAndSubZoneContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#oneSubZone.
    def visitOneSubZone(self, ctx: RegionParser.OneSubZoneContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#subZone.
    def visitSubZone(self, ctx: RegionParser.SubZoneContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RegionParser#unaryExpression.
    def visitUnaryExpression(self, ctx: RegionParser.UnaryExpressionContext):
        return self.visitChildren(ctx)


del RegionParser
