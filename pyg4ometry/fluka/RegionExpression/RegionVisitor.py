# Generated from Region.g4 by ANTLR 4.7.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by RegionParser.

class RegionVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RegionParser#region.
    def visitRegion(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#subzone.
    def visitSubzone(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegionParser#signbody.
    def visitSignbody(self, ctx):
        return self.visitChildren(ctx)


