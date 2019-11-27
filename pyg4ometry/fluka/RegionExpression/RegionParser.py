# Generated from RegionParser.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\rL\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4")
        buf.write(u"\b\t\b\3\2\6\2\22\n\2\r\2\16\2\23\3\3\3\3\3\3\3\3\3\3")
        buf.write(u"\3\3\5\3\34\n\3\3\4\3\4\3\4\3\4\6\4\"\n\4\r\4\16\4#\3")
        buf.write(u"\4\3\4\3\4\3\4\3\4\3\4\3\4\7\4-\n\4\f\4\16\4\60\13\4")
        buf.write(u"\3\4\3\4\5\4\64\n\4\3\5\3\5\5\58\n\5\3\6\3\6\3\6\3\6")
        buf.write(u"\3\6\3\6\3\6\3\6\5\6B\n\6\3\7\3\7\3\7\3\7\3\7\3\b\3\b")
        buf.write(u"\3\b\3\b\2\2\t\2\4\6\b\n\f\16\2\3\3\2\t\n\2N\2\21\3\2")
        buf.write(u"\2\2\4\33\3\2\2\2\6\63\3\2\2\2\b\67\3\2\2\2\nA\3\2\2")
        buf.write(u"\2\fC\3\2\2\2\16H\3\2\2\2\20\22\5\4\3\2\21\20\3\2\2\2")
        buf.write(u"\22\23\3\2\2\2\23\21\3\2\2\2\23\24\3\2\2\2\24\3\3\2\2")
        buf.write(u"\2\25\26\7\b\2\2\26\27\7\7\2\2\27\34\5\b\5\2\30\31\7")
        buf.write(u"\b\2\2\31\32\7\7\2\2\32\34\5\6\4\2\33\25\3\2\2\2\33\30")
        buf.write(u"\3\2\2\2\34\5\3\2\2\2\35\36\7\13\2\2\36!\5\b\5\2\37 ")
        buf.write(u"\7\13\2\2 \"\5\b\5\2!\37\3\2\2\2\"#\3\2\2\2#!\3\2\2\2")
        buf.write(u"#$\3\2\2\2$\64\3\2\2\2%&\7\13\2\2&\64\5\b\5\2\'(\5\b")
        buf.write(u"\5\2(.\7\13\2\2)*\5\b\5\2*+\7\13\2\2+-\3\2\2\2,)\3\2")
        buf.write(u"\2\2-\60\3\2\2\2.,\3\2\2\2./\3\2\2\2/\61\3\2\2\2\60.")
        buf.write(u"\3\2\2\2\61\62\5\b\5\2\62\64\3\2\2\2\63\35\3\2\2\2\63")
        buf.write(u"%\3\2\2\2\63\'\3\2\2\2\64\7\3\2\2\2\658\5\n\6\2\668\5")
        buf.write(u"\f\7\2\67\65\3\2\2\2\67\66\3\2\2\28\t\3\2\2\29B\5\16")
        buf.write(u"\b\2:;\5\16\b\2;<\5\n\6\2<B\3\2\2\2=>\5\f\7\2>?\5\n\6")
        buf.write(u"\2?B\3\2\2\2@B\5\f\7\2A9\3\2\2\2A:\3\2\2\2A=\3\2\2\2")
        buf.write(u"A@\3\2\2\2B\13\3\2\2\2CD\t\2\2\2DE\7\f\2\2EF\5\n\6\2")
        buf.write(u"FG\7\r\2\2G\r\3\2\2\2HI\t\2\2\2IJ\7\b\2\2J\17\3\2\2\2")
        buf.write(u"\t\23\33#.\63\67A")
        return buf.getvalue()


class RegionParser ( Parser ):

    grammarFileName = "RegionParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"'+'", u"'-'", 
                     u"'|'", u"'('", u"')'" ]

    symbolicNames = [ u"<INVALID>", u"Whitespace", u"InLineComment", u"LineComment", 
                      u"Newline", u"Integer", u"RegionName", u"Plus", u"Minus", 
                      u"Bar", u"LParen", u"RParen" ]

    RULE_regions = 0
    RULE_region = 1
    RULE_zoneUnion = 2
    RULE_zone = 3
    RULE_expr = 4
    RULE_subZone = 5
    RULE_unaryExpression = 6

    ruleNames =  [ u"regions", u"region", u"zoneUnion", u"zone", u"expr", 
                   u"subZone", u"unaryExpression" ]

    EOF = Token.EOF
    Whitespace=1
    InLineComment=2
    LineComment=3
    Newline=4
    Integer=5
    RegionName=6
    Plus=7
    Minus=8
    Bar=9
    LParen=10
    RParen=11

    def __init__(self, input, output=sys.stdout):
        super(RegionParser, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class RegionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.RegionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def region(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(RegionParser.RegionContext)
            else:
                return self.getTypedRuleContext(RegionParser.RegionContext,i)


        def getRuleIndex(self):
            return RegionParser.RULE_regions

        def enterRule(self, listener):
            if hasattr(listener, "enterRegions"):
                listener.enterRegions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRegions"):
                listener.exitRegions(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRegions"):
                return visitor.visitRegions(self)
            else:
                return visitor.visitChildren(self)




    def regions(self):

        localctx = RegionParser.RegionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_regions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 14
                self.region()
                self.state = 17 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==RegionParser.RegionName):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RegionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.RegionContext, self).__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegionParser.RULE_region

     
        def copyFrom(self, ctx):
            super(RegionParser.RegionContext, self).copyFrom(ctx)



    class ComplexRegionContext(RegionContext):

        def __init__(self, parser, ctx): # actually a RegionParser.RegionContext)
            super(RegionParser.ComplexRegionContext, self).__init__(parser)
            self.copyFrom(ctx)

        def RegionName(self):
            return self.getToken(RegionParser.RegionName, 0)
        def Integer(self):
            return self.getToken(RegionParser.Integer, 0)
        def zoneUnion(self):
            return self.getTypedRuleContext(RegionParser.ZoneUnionContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterComplexRegion"):
                listener.enterComplexRegion(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitComplexRegion"):
                listener.exitComplexRegion(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitComplexRegion"):
                return visitor.visitComplexRegion(self)
            else:
                return visitor.visitChildren(self)


    class SimpleRegionContext(RegionContext):

        def __init__(self, parser, ctx): # actually a RegionParser.RegionContext)
            super(RegionParser.SimpleRegionContext, self).__init__(parser)
            self.copyFrom(ctx)

        def RegionName(self):
            return self.getToken(RegionParser.RegionName, 0)
        def Integer(self):
            return self.getToken(RegionParser.Integer, 0)
        def zone(self):
            return self.getTypedRuleContext(RegionParser.ZoneContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterSimpleRegion"):
                listener.enterSimpleRegion(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSimpleRegion"):
                listener.exitSimpleRegion(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSimpleRegion"):
                return visitor.visitSimpleRegion(self)
            else:
                return visitor.visitChildren(self)



    def region(self):

        localctx = RegionParser.RegionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_region)
        try:
            self.state = 25
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                localctx = RegionParser.SimpleRegionContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 19
                self.match(RegionParser.RegionName)
                self.state = 20
                self.match(RegionParser.Integer)
                self.state = 21
                self.zone()
                pass

            elif la_ == 2:
                localctx = RegionParser.ComplexRegionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 22
                self.match(RegionParser.RegionName)
                self.state = 23
                self.match(RegionParser.Integer)
                self.state = 24
                self.zoneUnion()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ZoneUnionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.ZoneUnionContext, self).__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegionParser.RULE_zoneUnion

     
        def copyFrom(self, ctx):
            super(RegionParser.ZoneUnionContext, self).copyFrom(ctx)



    class MultipleUnion2Context(ZoneUnionContext):

        def __init__(self, parser, ctx): # actually a RegionParser.ZoneUnionContext)
            super(RegionParser.MultipleUnion2Context, self).__init__(parser)
            self.copyFrom(ctx)

        def zone(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(RegionParser.ZoneContext)
            else:
                return self.getTypedRuleContext(RegionParser.ZoneContext,i)

        def Bar(self, i=None):
            if i is None:
                return self.getTokens(RegionParser.Bar)
            else:
                return self.getToken(RegionParser.Bar, i)

        def enterRule(self, listener):
            if hasattr(listener, "enterMultipleUnion2"):
                listener.enterMultipleUnion2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMultipleUnion2"):
                listener.exitMultipleUnion2(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMultipleUnion2"):
                return visitor.visitMultipleUnion2(self)
            else:
                return visitor.visitChildren(self)


    class MultipleUnionContext(ZoneUnionContext):

        def __init__(self, parser, ctx): # actually a RegionParser.ZoneUnionContext)
            super(RegionParser.MultipleUnionContext, self).__init__(parser)
            self.copyFrom(ctx)

        def Bar(self, i=None):
            if i is None:
                return self.getTokens(RegionParser.Bar)
            else:
                return self.getToken(RegionParser.Bar, i)
        def zone(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(RegionParser.ZoneContext)
            else:
                return self.getTypedRuleContext(RegionParser.ZoneContext,i)


        def enterRule(self, listener):
            if hasattr(listener, "enterMultipleUnion"):
                listener.enterMultipleUnion(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMultipleUnion"):
                listener.exitMultipleUnion(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMultipleUnion"):
                return visitor.visitMultipleUnion(self)
            else:
                return visitor.visitChildren(self)


    class SingleUnionContext(ZoneUnionContext):

        def __init__(self, parser, ctx): # actually a RegionParser.ZoneUnionContext)
            super(RegionParser.SingleUnionContext, self).__init__(parser)
            self.copyFrom(ctx)

        def Bar(self):
            return self.getToken(RegionParser.Bar, 0)
        def zone(self):
            return self.getTypedRuleContext(RegionParser.ZoneContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterSingleUnion"):
                listener.enterSingleUnion(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSingleUnion"):
                listener.exitSingleUnion(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSingleUnion"):
                return visitor.visitSingleUnion(self)
            else:
                return visitor.visitChildren(self)



    def zoneUnion(self):

        localctx = RegionParser.ZoneUnionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_zoneUnion)
        self._la = 0 # Token type
        try:
            self.state = 49
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                localctx = RegionParser.MultipleUnionContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 27
                self.match(RegionParser.Bar)
                self.state = 28
                self.zone()
                self.state = 31 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 29
                    self.match(RegionParser.Bar)
                    self.state = 30
                    self.zone()
                    self.state = 33 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==RegionParser.Bar):
                        break

                pass

            elif la_ == 2:
                localctx = RegionParser.SingleUnionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 35
                self.match(RegionParser.Bar)
                self.state = 36
                self.zone()
                pass

            elif la_ == 3:
                localctx = RegionParser.MultipleUnion2Context(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 37
                self.zone()
                self.state = 38
                self.match(RegionParser.Bar)
                self.state = 44
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 39
                        self.zone()
                        self.state = 40
                        self.match(RegionParser.Bar) 
                    self.state = 46
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                self.state = 47
                self.zone()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ZoneContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.ZoneContext, self).__init__(parent, invokingState)
            self.parser = parser

        def expr(self):
            return self.getTypedRuleContext(RegionParser.ExprContext,0)


        def subZone(self):
            return self.getTypedRuleContext(RegionParser.SubZoneContext,0)


        def getRuleIndex(self):
            return RegionParser.RULE_zone

        def enterRule(self, listener):
            if hasattr(listener, "enterZone"):
                listener.enterZone(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitZone"):
                listener.exitZone(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitZone"):
                return visitor.visitZone(self)
            else:
                return visitor.visitChildren(self)




    def zone(self):

        localctx = RegionParser.ZoneContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_zone)
        try:
            self.state = 53
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 51
                self.expr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 52
                self.subZone()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExprContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.ExprContext, self).__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegionParser.RULE_expr

     
        def copyFrom(self, ctx):
            super(RegionParser.ExprContext, self).copyFrom(ctx)



    class UnaryAndBooleanContext(ExprContext):

        def __init__(self, parser, ctx): # actually a RegionParser.ExprContext)
            super(RegionParser.UnaryAndBooleanContext, self).__init__(parser)
            self.copyFrom(ctx)

        def unaryExpression(self):
            return self.getTypedRuleContext(RegionParser.UnaryExpressionContext,0)

        def expr(self):
            return self.getTypedRuleContext(RegionParser.ExprContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterUnaryAndBoolean"):
                listener.enterUnaryAndBoolean(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnaryAndBoolean"):
                listener.exitUnaryAndBoolean(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnaryAndBoolean"):
                return visitor.visitUnaryAndBoolean(self)
            else:
                return visitor.visitChildren(self)


    class OneSubZoneContext(ExprContext):

        def __init__(self, parser, ctx): # actually a RegionParser.ExprContext)
            super(RegionParser.OneSubZoneContext, self).__init__(parser)
            self.copyFrom(ctx)

        def subZone(self):
            return self.getTypedRuleContext(RegionParser.SubZoneContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterOneSubZone"):
                listener.enterOneSubZone(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOneSubZone"):
                listener.exitOneSubZone(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitOneSubZone"):
                return visitor.visitOneSubZone(self)
            else:
                return visitor.visitChildren(self)


    class UnaryAndSubZoneContext(ExprContext):

        def __init__(self, parser, ctx): # actually a RegionParser.ExprContext)
            super(RegionParser.UnaryAndSubZoneContext, self).__init__(parser)
            self.copyFrom(ctx)

        def subZone(self):
            return self.getTypedRuleContext(RegionParser.SubZoneContext,0)

        def expr(self):
            return self.getTypedRuleContext(RegionParser.ExprContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterUnaryAndSubZone"):
                listener.enterUnaryAndSubZone(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnaryAndSubZone"):
                listener.exitUnaryAndSubZone(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnaryAndSubZone"):
                return visitor.visitUnaryAndSubZone(self)
            else:
                return visitor.visitChildren(self)


    class SingleUnaryContext(ExprContext):

        def __init__(self, parser, ctx): # actually a RegionParser.ExprContext)
            super(RegionParser.SingleUnaryContext, self).__init__(parser)
            self.copyFrom(ctx)

        def unaryExpression(self):
            return self.getTypedRuleContext(RegionParser.UnaryExpressionContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterSingleUnary"):
                listener.enterSingleUnary(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSingleUnary"):
                listener.exitSingleUnary(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSingleUnary"):
                return visitor.visitSingleUnary(self)
            else:
                return visitor.visitChildren(self)



    def expr(self):

        localctx = RegionParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_expr)
        try:
            self.state = 63
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                localctx = RegionParser.SingleUnaryContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 55
                self.unaryExpression()
                pass

            elif la_ == 2:
                localctx = RegionParser.UnaryAndBooleanContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 56
                self.unaryExpression()
                self.state = 57
                self.expr()
                pass

            elif la_ == 3:
                localctx = RegionParser.UnaryAndSubZoneContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 59
                self.subZone()
                self.state = 60
                self.expr()
                pass

            elif la_ == 4:
                localctx = RegionParser.OneSubZoneContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 62
                self.subZone()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SubZoneContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.SubZoneContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LParen(self):
            return self.getToken(RegionParser.LParen, 0)

        def expr(self):
            return self.getTypedRuleContext(RegionParser.ExprContext,0)


        def RParen(self):
            return self.getToken(RegionParser.RParen, 0)

        def Minus(self):
            return self.getToken(RegionParser.Minus, 0)

        def Plus(self):
            return self.getToken(RegionParser.Plus, 0)

        def getRuleIndex(self):
            return RegionParser.RULE_subZone

        def enterRule(self, listener):
            if hasattr(listener, "enterSubZone"):
                listener.enterSubZone(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSubZone"):
                listener.exitSubZone(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSubZone"):
                return visitor.visitSubZone(self)
            else:
                return visitor.visitChildren(self)




    def subZone(self):

        localctx = RegionParser.SubZoneContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_subZone)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            _la = self._input.LA(1)
            if not(_la==RegionParser.Plus or _la==RegionParser.Minus):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 66
            self.match(RegionParser.LParen)
            self.state = 67
            self.expr()
            self.state = 68
            self.match(RegionParser.RParen)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class UnaryExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.UnaryExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def RegionName(self):
            return self.getToken(RegionParser.RegionName, 0)

        def Minus(self):
            return self.getToken(RegionParser.Minus, 0)

        def Plus(self):
            return self.getToken(RegionParser.Plus, 0)

        def getRuleIndex(self):
            return RegionParser.RULE_unaryExpression

        def enterRule(self, listener):
            if hasattr(listener, "enterUnaryExpression"):
                listener.enterUnaryExpression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnaryExpression"):
                listener.exitUnaryExpression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnaryExpression"):
                return visitor.visitUnaryExpression(self)
            else:
                return visitor.visitChildren(self)




    def unaryExpression(self):

        localctx = RegionParser.UnaryExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_unaryExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            _la = self._input.LA(1)
            if not(_la==RegionParser.Plus or _la==RegionParser.Minus):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 71
            self.match(RegionParser.RegionName)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





