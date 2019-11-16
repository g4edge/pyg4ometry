# Generated from Region.g4 by ANTLR 4.7.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\13N\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\3\2\3\2\6\2")
        buf.write(u"\16\n\2\r\2\16\2\17\7\2\22\n\2\f\2\16\2\25\13\2\3\3\6")
        buf.write(u"\3\30\n\3\r\3\16\3\31\3\3\6\3\35\n\3\r\3\16\3\36\3\3")
        buf.write(u"\6\3\"\n\3\r\3\16\3#\3\3\6\3\'\n\3\r\3\16\3(\3\3\6\3")
        buf.write(u",\n\3\r\3\16\3-\3\3\6\3\61\n\3\r\3\16\3\62\3\3\6\3\66")
        buf.write(u"\n\3\r\3\16\3\67\3\3\6\3;\n\3\r\3\16\3<\3\3\6\3@\n\3")
        buf.write(u"\r\3\16\3A\5\3D\n\3\3\4\3\4\3\4\3\4\3\4\3\5\3\5\3\5\3")
        buf.write(u"\5\2\2\6\2\4\6\b\2\3\3\2\6\7\2X\2\n\3\2\2\2\4C\3\2\2")
        buf.write(u"\2\6E\3\2\2\2\bJ\3\2\2\2\n\23\5\4\3\2\13\r\7\t\2\2\f")
        buf.write(u"\16\5\4\3\2\r\f\3\2\2\2\16\17\3\2\2\2\17\r\3\2\2\2\17")
        buf.write(u"\20\3\2\2\2\20\22\3\2\2\2\21\13\3\2\2\2\22\25\3\2\2\2")
        buf.write(u"\23\21\3\2\2\2\23\24\3\2\2\2\24\3\3\2\2\2\25\23\3\2\2")
        buf.write(u"\2\26\30\5\b\5\2\27\26\3\2\2\2\30\31\3\2\2\2\31\27\3")
        buf.write(u"\2\2\2\31\32\3\2\2\2\32\34\3\2\2\2\33\35\5\6\4\2\34\33")
        buf.write(u"\3\2\2\2\35\36\3\2\2\2\36\34\3\2\2\2\36\37\3\2\2\2\37")
        buf.write(u"!\3\2\2\2 \"\5\b\5\2! \3\2\2\2\"#\3\2\2\2#!\3\2\2\2#")
        buf.write(u"$\3\2\2\2$D\3\2\2\2%\'\5\b\5\2&%\3\2\2\2\'(\3\2\2\2(")
        buf.write(u"&\3\2\2\2()\3\2\2\2)D\3\2\2\2*,\5\6\4\2+*\3\2\2\2,-\3")
        buf.write(u"\2\2\2-+\3\2\2\2-.\3\2\2\2.D\3\2\2\2/\61\5\b\5\2\60/")
        buf.write(u"\3\2\2\2\61\62\3\2\2\2\62\60\3\2\2\2\62\63\3\2\2\2\63")
        buf.write(u"\65\3\2\2\2\64\66\5\6\4\2\65\64\3\2\2\2\66\67\3\2\2\2")
        buf.write(u"\67\65\3\2\2\2\678\3\2\2\28D\3\2\2\29;\5\6\4\2:9\3\2")
        buf.write(u"\2\2;<\3\2\2\2<:\3\2\2\2<=\3\2\2\2=?\3\2\2\2>@\5\b\5")
        buf.write(u"\2?>\3\2\2\2@A\3\2\2\2A?\3\2\2\2AB\3\2\2\2BD\3\2\2\2")
        buf.write(u"C\27\3\2\2\2C&\3\2\2\2C+\3\2\2\2C\60\3\2\2\2C:\3\2\2")
        buf.write(u"\2D\5\3\2\2\2EF\t\2\2\2FG\7\n\2\2GH\5\4\3\2HI\7\13\2")
        buf.write(u"\2I\7\3\2\2\2JK\t\2\2\2KL\7\4\2\2L\t\3\2\2\2\16\17\23")
        buf.write(u"\31\36#(-\62\67<AC")
        return buf.getvalue()


class RegionParser ( Parser ):

    grammarFileName = "Region.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"'+'", u"'-'", u"<INVALID>", u"'|'", u"'('", u"')'" ]

    symbolicNames = [ u"<INVALID>", u"WHITESPACE", u"BODYNAME", u"REGIONNAME", 
                      u"PLUS", u"MINUS", u"SIGN", u"BAR", u"LPAREN", u"RPAREN" ]

    RULE_region = 0
    RULE_expression = 1
    RULE_subzone = 2
    RULE_signbody = 3

    ruleNames =  [ u"region", u"expression", u"subzone", u"signbody" ]

    EOF = Token.EOF
    WHITESPACE=1
    BODYNAME=2
    REGIONNAME=3
    PLUS=4
    MINUS=5
    SIGN=6
    BAR=7
    LPAREN=8
    RPAREN=9

    def __init__(self, input, output=sys.stdout):
        super(RegionParser, self).__init__(input, output=output)
        self.checkVersion("4.7.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class RegionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.RegionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(RegionParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RegionParser.ExpressionContext,i)


        def BAR(self, i=None):
            if i is None:
                return self.getTokens(RegionParser.BAR)
            else:
                return self.getToken(RegionParser.BAR, i)

        def getRuleIndex(self):
            return RegionParser.RULE_region

        def enterRule(self, listener):
            if hasattr(listener, "enterRegion"):
                listener.enterRegion(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRegion"):
                listener.exitRegion(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRegion"):
                return visitor.visitRegion(self)
            else:
                return visitor.visitChildren(self)




    def region(self):

        localctx = RegionParser.RegionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_region)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self.expression()
            self.state = 17
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==RegionParser.BAR:
                self.state = 9
                self.match(RegionParser.BAR)
                self.state = 11 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 10
                    self.expression()
                    self.state = 13 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==RegionParser.PLUS or _la==RegionParser.MINUS):
                        break

                self.state = 19
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.ExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def signbody(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(RegionParser.SignbodyContext)
            else:
                return self.getTypedRuleContext(RegionParser.SignbodyContext,i)


        def subzone(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(RegionParser.SubzoneContext)
            else:
                return self.getTypedRuleContext(RegionParser.SubzoneContext,i)


        def getRuleIndex(self):
            return RegionParser.RULE_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterExpression"):
                listener.enterExpression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExpression"):
                listener.exitExpression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitExpression"):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = RegionParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_expression)
        try:
            self.state = 65
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 21 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 20
                        self.signbody()

                    else:
                        raise NoViableAltException(self)
                    self.state = 23 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

                self.state = 26 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 25
                        self.subzone()

                    else:
                        raise NoViableAltException(self)
                    self.state = 28 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                self.state = 31 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 30
                        self.signbody()

                    else:
                        raise NoViableAltException(self)
                    self.state = 33 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 36 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 35
                        self.signbody()

                    else:
                        raise NoViableAltException(self)
                    self.state = 38 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 41 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 40
                        self.subzone()

                    else:
                        raise NoViableAltException(self)
                    self.state = 43 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 46 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 45
                        self.signbody()

                    else:
                        raise NoViableAltException(self)
                    self.state = 48 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

                self.state = 51 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 50
                        self.subzone()

                    else:
                        raise NoViableAltException(self)
                    self.state = 53 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 56 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 55
                        self.subzone()

                    else:
                        raise NoViableAltException(self)
                    self.state = 58 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

                self.state = 61 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 60
                        self.signbody()

                    else:
                        raise NoViableAltException(self)
                    self.state = 63 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SubzoneContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.SubzoneContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(RegionParser.LPAREN, 0)

        def expression(self):
            return self.getTypedRuleContext(RegionParser.ExpressionContext,0)


        def RPAREN(self):
            return self.getToken(RegionParser.RPAREN, 0)

        def MINUS(self):
            return self.getToken(RegionParser.MINUS, 0)

        def PLUS(self):
            return self.getToken(RegionParser.PLUS, 0)

        def getRuleIndex(self):
            return RegionParser.RULE_subzone

        def enterRule(self, listener):
            if hasattr(listener, "enterSubzone"):
                listener.enterSubzone(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSubzone"):
                listener.exitSubzone(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSubzone"):
                return visitor.visitSubzone(self)
            else:
                return visitor.visitChildren(self)




    def subzone(self):

        localctx = RegionParser.SubzoneContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_subzone)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            _la = self._input.LA(1)
            if not(_la==RegionParser.PLUS or _la==RegionParser.MINUS):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 68
            self.match(RegionParser.LPAREN)
            self.state = 69
            self.expression()
            self.state = 70
            self.match(RegionParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SignbodyContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(RegionParser.SignbodyContext, self).__init__(parent, invokingState)
            self.parser = parser

        def BODYNAME(self):
            return self.getToken(RegionParser.BODYNAME, 0)

        def MINUS(self):
            return self.getToken(RegionParser.MINUS, 0)

        def PLUS(self):
            return self.getToken(RegionParser.PLUS, 0)

        def getRuleIndex(self):
            return RegionParser.RULE_signbody

        def enterRule(self, listener):
            if hasattr(listener, "enterSignbody"):
                listener.enterSignbody(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSignbody"):
                listener.exitSignbody(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSignbody"):
                return visitor.visitSignbody(self)
            else:
                return visitor.visitChildren(self)




    def signbody(self):

        localctx = RegionParser.SignbodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_signbody)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            _la = self._input.LA(1)
            if not(_la==RegionParser.PLUS or _la==RegionParser.MINUS):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 73
            self.match(RegionParser.BODYNAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





