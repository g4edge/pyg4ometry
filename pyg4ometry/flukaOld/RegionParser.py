# Generated from RegionParser.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\16E\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write(u"\3\2\3\2\3\2\3\2\3\2\3\2\5\2\25\n\2\3\3\3\3\3\3\3\3\6")
        buf.write(u"\3\33\n\3\r\3\16\3\34\3\3\3\3\3\3\3\3\3\3\3\3\3\3\7\3")
        buf.write(u"&\n\3\f\3\16\3)\13\3\3\3\3\3\5\3-\n\3\3\4\3\4\5\4\61")
        buf.write(u"\n\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\5\5;\n\5\3\6\3\6")
        buf.write(u"\3\6\3\6\3\6\3\7\3\7\3\7\3\7\2\2\b\2\4\6\b\n\f\2\3\3")
        buf.write(u"\2\n\13\2G\2\24\3\2\2\2\4,\3\2\2\2\6\60\3\2\2\2\b:\3")
        buf.write(u"\2\2\2\n<\3\2\2\2\fA\3\2\2\2\16\17\7\5\2\2\17\20\7\6")
        buf.write(u"\2\2\20\25\5\6\4\2\21\22\7\5\2\2\22\23\7\6\2\2\23\25")
        buf.write(u"\5\4\3\2\24\16\3\2\2\2\24\21\3\2\2\2\25\3\3\2\2\2\26")
        buf.write(u"\27\7\f\2\2\27\32\5\6\4\2\30\31\7\f\2\2\31\33\5\6\4\2")
        buf.write(u"\32\30\3\2\2\2\33\34\3\2\2\2\34\32\3\2\2\2\34\35\3\2")
        buf.write(u"\2\2\35-\3\2\2\2\36\37\7\f\2\2\37-\5\6\4\2 !\5\6\4\2")
        buf.write(u"!\'\7\f\2\2\"#\5\6\4\2#$\7\f\2\2$&\3\2\2\2%\"\3\2\2\2")
        buf.write(u"&)\3\2\2\2\'%\3\2\2\2\'(\3\2\2\2(*\3\2\2\2)\'\3\2\2\2")
        buf.write(u"*+\5\6\4\2+-\3\2\2\2,\26\3\2\2\2,\36\3\2\2\2, \3\2\2")
        buf.write(u"\2-\5\3\2\2\2.\61\5\b\5\2/\61\5\n\6\2\60.\3\2\2\2\60")
        buf.write(u"/\3\2\2\2\61\7\3\2\2\2\62;\5\f\7\2\63\64\5\f\7\2\64\65")
        buf.write(u"\5\b\5\2\65;\3\2\2\2\66\67\5\n\6\2\678\5\b\5\28;\3\2")
        buf.write(u"\2\29;\5\n\6\2:\62\3\2\2\2:\63\3\2\2\2:\66\3\2\2\2:9")
        buf.write(u"\3\2\2\2;\t\3\2\2\2<=\t\2\2\2=>\7\r\2\2>?\5\b\5\2?@\7")
        buf.write(u"\16\2\2@\13\3\2\2\2AB\t\2\2\2BC\7\b\2\2C\r\3\2\2\2\b")
        buf.write(u"\24\34\',\60:")
        return buf.getvalue()


class RegionParser ( Parser ):

    grammarFileName = "RegionParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"'+'", u"'-'", u"'|'", u"'('", u"')'" ]

    symbolicNames = [ u"<INVALID>", u"Whitespace", u"Newline", u"RegionName", 
                      u"Integer", u"Float", u"ID", u"Delim", u"Plus", u"Minus", 
                      u"Bar", u"LParen", u"RParen" ]

    RULE_region = 0
    RULE_zoneUnion = 1
    RULE_zone = 2
    RULE_expr = 3
    RULE_subZone = 4
    RULE_unaryExpression = 5

    ruleNames =  [ u"region", u"zoneUnion", u"zone", u"expr", u"subZone", 
                   u"unaryExpression" ]

    EOF = Token.EOF
    Whitespace=1
    Newline=2
    RegionName=3
    Integer=4
    Float=5
    ID=6
    Delim=7
    Plus=8
    Minus=9
    Bar=10
    LParen=11
    RParen=12

    def __init__(self, input, output=sys.stdout):
        super(RegionParser, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



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
        self.enterRule(localctx, 0, self.RULE_region)
        try:
            self.state = 18
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                localctx = RegionParser.SimpleRegionContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 12
                self.match(RegionParser.RegionName)
                self.state = 13
                self.match(RegionParser.Integer)
                self.state = 14
                self.zone()
                pass

            elif la_ == 2:
                localctx = RegionParser.ComplexRegionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 15
                self.match(RegionParser.RegionName)
                self.state = 16
                self.match(RegionParser.Integer)
                self.state = 17
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
        self.enterRule(localctx, 2, self.RULE_zoneUnion)
        self._la = 0 # Token type
        try:
            self.state = 42
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                localctx = RegionParser.MultipleUnionContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 20
                self.match(RegionParser.Bar)
                self.state = 21
                self.zone()
                self.state = 24 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 22
                    self.match(RegionParser.Bar)
                    self.state = 23
                    self.zone()
                    self.state = 26 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==RegionParser.Bar):
                        break

                pass

            elif la_ == 2:
                localctx = RegionParser.SingleUnionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 28
                self.match(RegionParser.Bar)
                self.state = 29
                self.zone()
                pass

            elif la_ == 3:
                localctx = RegionParser.MultipleUnion2Context(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 30
                self.zone()
                self.state = 31
                self.match(RegionParser.Bar)
                self.state = 37
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 32
                        self.zone()
                        self.state = 33
                        self.match(RegionParser.Bar) 
                    self.state = 39
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

                self.state = 40
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
        self.enterRule(localctx, 4, self.RULE_zone)
        try:
            self.state = 46
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 44
                self.expr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 45
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
        self.enterRule(localctx, 6, self.RULE_expr)
        try:
            self.state = 56
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                localctx = RegionParser.SingleUnaryContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 48
                self.unaryExpression()
                pass

            elif la_ == 2:
                localctx = RegionParser.UnaryAndBooleanContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 49
                self.unaryExpression()
                self.state = 50
                self.expr()
                pass

            elif la_ == 3:
                localctx = RegionParser.UnaryAndSubZoneContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 52
                self.subZone()
                self.state = 53
                self.expr()
                pass

            elif la_ == 4:
                localctx = RegionParser.OneSubZoneContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 55
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
        self.enterRule(localctx, 8, self.RULE_subZone)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 58
            _la = self._input.LA(1)
            if not(_la==RegionParser.Plus or _la==RegionParser.Minus):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 59
            self.match(RegionParser.LParen)
            self.state = 60
            self.expr()
            self.state = 61
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

        def ID(self):
            return self.getToken(RegionParser.ID, 0)

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
        self.enterRule(localctx, 10, self.RULE_unaryExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            _la = self._input.LA(1)
            if not(_la==RegionParser.Plus or _la==RegionParser.Minus):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 64
            self.match(RegionParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





