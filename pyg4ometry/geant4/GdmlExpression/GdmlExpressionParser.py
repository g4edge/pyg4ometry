# Generated from GdmlExpression.g4 by ANTLR 4.7.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\35^\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write(u"\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\3")
        buf.write(u"\2\3\2\3\2\3\2\3\3\3\3\3\3\7\3\"\n\3\f\3\16\3%\13\3\3")
        buf.write(u"\4\3\4\3\4\7\4*\n\4\f\4\16\4-\13\4\3\5\3\5\3\5\7\5\62")
        buf.write(u"\n\5\f\5\16\5\65\13\5\3\6\3\6\3\6\3\6\3\6\3\6\5\6=\n")
        buf.write(u"\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7\5\7F\n\7\3\b\3\b\3\t\3")
        buf.write(u"\t\3\n\3\n\3\13\3\13\3\13\3\13\3\13\7\13S\n\13\f\13\16")
        buf.write(u"\13V\13\13\3\13\3\13\3\f\3\f\3\r\3\r\3\r\2\2\16\2\4\6")
        buf.write(u"\b\n\f\16\20\22\24\26\30\2\7\3\2\16\17\3\2\20\21\3\2")
        buf.write(u"\30\32\3\2\3\13\3\2\22\24\2[\2\32\3\2\2\2\4\36\3\2\2")
        buf.write(u"\2\6&\3\2\2\2\b.\3\2\2\2\n<\3\2\2\2\fE\3\2\2\2\16G\3")
        buf.write(u"\2\2\2\20I\3\2\2\2\22K\3\2\2\2\24M\3\2\2\2\26Y\3\2\2")
        buf.write(u"\2\30[\3\2\2\2\32\33\5\4\3\2\33\34\5\30\r\2\34\35\5\4")
        buf.write(u"\3\2\35\3\3\2\2\2\36#\5\6\4\2\37 \t\2\2\2 \"\5\6\4\2")
        buf.write(u"!\37\3\2\2\2\"%\3\2\2\2#!\3\2\2\2#$\3\2\2\2$\5\3\2\2")
        buf.write(u"\2%#\3\2\2\2&+\5\b\5\2\'(\t\3\2\2(*\5\b\5\2)\'\3\2\2")
        buf.write(u"\2*-\3\2\2\2+)\3\2\2\2+,\3\2\2\2,\7\3\2\2\2-+\3\2\2\2")
        buf.write(u".\63\5\n\6\2/\60\7\27\2\2\60\62\5\n\6\2\61/\3\2\2\2\62")
        buf.write(u"\65\3\2\2\2\63\61\3\2\2\2\63\64\3\2\2\2\64\t\3\2\2\2")
        buf.write(u"\65\63\3\2\2\2\66\67\7\16\2\2\67=\5\n\6\289\7\17\2\2")
        buf.write(u"9=\5\n\6\2:=\5\24\13\2;=\5\f\7\2<\66\3\2\2\2<8\3\2\2")
        buf.write(u"\2<:\3\2\2\2<;\3\2\2\2=\13\3\2\2\2>F\5\16\b\2?F\5\22")
        buf.write(u"\n\2@F\5\20\t\2AB\7\f\2\2BC\5\4\3\2CD\7\r\2\2DF\3\2\2")
        buf.write(u"\2E>\3\2\2\2E?\3\2\2\2E@\3\2\2\2EA\3\2\2\2F\r\3\2\2\2")
        buf.write(u"GH\7\34\2\2H\17\3\2\2\2IJ\t\4\2\2J\21\3\2\2\2KL\7\33")
        buf.write(u"\2\2L\23\3\2\2\2MN\5\26\f\2NO\7\f\2\2OT\5\4\3\2PQ\7\25")
        buf.write(u"\2\2QS\5\4\3\2RP\3\2\2\2SV\3\2\2\2TR\3\2\2\2TU\3\2\2")
        buf.write(u"\2UW\3\2\2\2VT\3\2\2\2WX\7\r\2\2X\25\3\2\2\2YZ\t\5\2")
        buf.write(u"\2Z\27\3\2\2\2[\\\t\6\2\2\\\31\3\2\2\2\b#+\63<ET")
        return buf.getvalue()


class GdmlExpressionParser ( Parser ):

    grammarFileName = "GdmlExpression.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'cos'", u"'sin'", u"'tan'", u"'acos'", 
                     u"'asin'", u"'atan'", u"'ln'", u"'log'", u"'sqrt'", 
                     u"'('", u"')'", u"'+'", u"'-'", u"'*'", u"'/'", u"'>'", 
                     u"'<'", u"'='", u"','", u"'.'", u"'^'", u"'pi'", u"<INVALID>", 
                     u"'i'" ]

    symbolicNames = [ u"<INVALID>", u"COS", u"SIN", u"TAN", u"ACOS", u"ASIN", 
                      u"ATAN", u"LN", u"LOG", u"SQRT", u"LPAREN", u"RPAREN", 
                      u"PLUS", u"MINUS", u"TIMES", u"DIV", u"GT", u"LT", 
                      u"EQ", u"COMMA", u"POINT", u"POW", u"PI", u"EULER", 
                      u"I", u"VARIABLE", u"SCIENTIFIC_NUMBER", u"WS" ]

    RULE_equation = 0
    RULE_expression = 1
    RULE_multiplyingExpression = 2
    RULE_powExpression = 3
    RULE_signedAtom = 4
    RULE_atom = 5
    RULE_scientific = 6
    RULE_constant = 7
    RULE_variable = 8
    RULE_func = 9
    RULE_funcname = 10
    RULE_relop = 11

    ruleNames =  [ u"equation", u"expression", u"multiplyingExpression", 
                   u"powExpression", u"signedAtom", u"atom", u"scientific", 
                   u"constant", u"variable", u"func", u"funcname", u"relop" ]

    EOF = Token.EOF
    COS=1
    SIN=2
    TAN=3
    ACOS=4
    ASIN=5
    ATAN=6
    LN=7
    LOG=8
    SQRT=9
    LPAREN=10
    RPAREN=11
    PLUS=12
    MINUS=13
    TIMES=14
    DIV=15
    GT=16
    LT=17
    EQ=18
    COMMA=19
    POINT=20
    POW=21
    PI=22
    EULER=23
    I=24
    VARIABLE=25
    SCIENTIFIC_NUMBER=26
    WS=27

    def __init__(self, input, output=sys.stdout):
        super(GdmlExpressionParser, self).__init__(input, output=output)
        self.checkVersion("4.7.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class EquationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.EquationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GdmlExpressionParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(GdmlExpressionParser.ExpressionContext,i)


        def relop(self):
            return self.getTypedRuleContext(GdmlExpressionParser.RelopContext,0)


        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_equation

        def enterRule(self, listener):
            if hasattr(listener, "enterEquation"):
                listener.enterEquation(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitEquation"):
                listener.exitEquation(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitEquation"):
                return visitor.visitEquation(self)
            else:
                return visitor.visitChildren(self)




    def equation(self):

        localctx = GdmlExpressionParser.EquationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_equation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self.expression()
            self.state = 25
            self.relop()
            self.state = 26
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.ExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def multiplyingExpression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GdmlExpressionParser.MultiplyingExpressionContext)
            else:
                return self.getTypedRuleContext(GdmlExpressionParser.MultiplyingExpressionContext,i)


        def PLUS(self, i=None):
            if i is None:
                return self.getTokens(GdmlExpressionParser.PLUS)
            else:
                return self.getToken(GdmlExpressionParser.PLUS, i)

        def MINUS(self, i=None):
            if i is None:
                return self.getTokens(GdmlExpressionParser.MINUS)
            else:
                return self.getToken(GdmlExpressionParser.MINUS, i)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_expression

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

        localctx = GdmlExpressionParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.multiplyingExpression()
            self.state = 33
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.PLUS or _la==GdmlExpressionParser.MINUS:
                self.state = 29
                _la = self._input.LA(1)
                if not(_la==GdmlExpressionParser.PLUS or _la==GdmlExpressionParser.MINUS):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 30
                self.multiplyingExpression()
                self.state = 35
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class MultiplyingExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.MultiplyingExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def powExpression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GdmlExpressionParser.PowExpressionContext)
            else:
                return self.getTypedRuleContext(GdmlExpressionParser.PowExpressionContext,i)


        def TIMES(self, i=None):
            if i is None:
                return self.getTokens(GdmlExpressionParser.TIMES)
            else:
                return self.getToken(GdmlExpressionParser.TIMES, i)

        def DIV(self, i=None):
            if i is None:
                return self.getTokens(GdmlExpressionParser.DIV)
            else:
                return self.getToken(GdmlExpressionParser.DIV, i)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_multiplyingExpression

        def enterRule(self, listener):
            if hasattr(listener, "enterMultiplyingExpression"):
                listener.enterMultiplyingExpression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMultiplyingExpression"):
                listener.exitMultiplyingExpression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMultiplyingExpression"):
                return visitor.visitMultiplyingExpression(self)
            else:
                return visitor.visitChildren(self)




    def multiplyingExpression(self):

        localctx = GdmlExpressionParser.MultiplyingExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_multiplyingExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
            self.powExpression()
            self.state = 41
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.TIMES or _la==GdmlExpressionParser.DIV:
                self.state = 37
                _la = self._input.LA(1)
                if not(_la==GdmlExpressionParser.TIMES or _la==GdmlExpressionParser.DIV):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 38
                self.powExpression()
                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PowExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.PowExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def signedAtom(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GdmlExpressionParser.SignedAtomContext)
            else:
                return self.getTypedRuleContext(GdmlExpressionParser.SignedAtomContext,i)


        def POW(self, i=None):
            if i is None:
                return self.getTokens(GdmlExpressionParser.POW)
            else:
                return self.getToken(GdmlExpressionParser.POW, i)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_powExpression

        def enterRule(self, listener):
            if hasattr(listener, "enterPowExpression"):
                listener.enterPowExpression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPowExpression"):
                listener.exitPowExpression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitPowExpression"):
                return visitor.visitPowExpression(self)
            else:
                return visitor.visitChildren(self)




    def powExpression(self):

        localctx = GdmlExpressionParser.PowExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_powExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.signedAtom()
            self.state = 49
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.POW:
                self.state = 45
                self.match(GdmlExpressionParser.POW)
                self.state = 46
                self.signedAtom()
                self.state = 51
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SignedAtomContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.SignedAtomContext, self).__init__(parent, invokingState)
            self.parser = parser

        def PLUS(self):
            return self.getToken(GdmlExpressionParser.PLUS, 0)

        def signedAtom(self):
            return self.getTypedRuleContext(GdmlExpressionParser.SignedAtomContext,0)


        def MINUS(self):
            return self.getToken(GdmlExpressionParser.MINUS, 0)

        def func(self):
            return self.getTypedRuleContext(GdmlExpressionParser.FuncContext,0)


        def atom(self):
            return self.getTypedRuleContext(GdmlExpressionParser.AtomContext,0)


        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_signedAtom

        def enterRule(self, listener):
            if hasattr(listener, "enterSignedAtom"):
                listener.enterSignedAtom(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSignedAtom"):
                listener.exitSignedAtom(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSignedAtom"):
                return visitor.visitSignedAtom(self)
            else:
                return visitor.visitChildren(self)




    def signedAtom(self):

        localctx = GdmlExpressionParser.SignedAtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_signedAtom)
        try:
            self.state = 58
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GdmlExpressionParser.PLUS]:
                self.enterOuterAlt(localctx, 1)
                self.state = 52
                self.match(GdmlExpressionParser.PLUS)
                self.state = 53
                self.signedAtom()
                pass
            elif token in [GdmlExpressionParser.MINUS]:
                self.enterOuterAlt(localctx, 2)
                self.state = 54
                self.match(GdmlExpressionParser.MINUS)
                self.state = 55
                self.signedAtom()
                pass
            elif token in [GdmlExpressionParser.COS, GdmlExpressionParser.SIN, GdmlExpressionParser.TAN, GdmlExpressionParser.ACOS, GdmlExpressionParser.ASIN, GdmlExpressionParser.ATAN, GdmlExpressionParser.LN, GdmlExpressionParser.LOG, GdmlExpressionParser.SQRT]:
                self.enterOuterAlt(localctx, 3)
                self.state = 56
                self.func()
                pass
            elif token in [GdmlExpressionParser.LPAREN, GdmlExpressionParser.PI, GdmlExpressionParser.EULER, GdmlExpressionParser.I, GdmlExpressionParser.VARIABLE, GdmlExpressionParser.SCIENTIFIC_NUMBER]:
                self.enterOuterAlt(localctx, 4)
                self.state = 57
                self.atom()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AtomContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.AtomContext, self).__init__(parent, invokingState)
            self.parser = parser

        def scientific(self):
            return self.getTypedRuleContext(GdmlExpressionParser.ScientificContext,0)


        def variable(self):
            return self.getTypedRuleContext(GdmlExpressionParser.VariableContext,0)


        def constant(self):
            return self.getTypedRuleContext(GdmlExpressionParser.ConstantContext,0)


        def LPAREN(self):
            return self.getToken(GdmlExpressionParser.LPAREN, 0)

        def expression(self):
            return self.getTypedRuleContext(GdmlExpressionParser.ExpressionContext,0)


        def RPAREN(self):
            return self.getToken(GdmlExpressionParser.RPAREN, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_atom

        def enterRule(self, listener):
            if hasattr(listener, "enterAtom"):
                listener.enterAtom(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitAtom"):
                listener.exitAtom(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitAtom"):
                return visitor.visitAtom(self)
            else:
                return visitor.visitChildren(self)




    def atom(self):

        localctx = GdmlExpressionParser.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_atom)
        try:
            self.state = 67
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GdmlExpressionParser.SCIENTIFIC_NUMBER]:
                self.enterOuterAlt(localctx, 1)
                self.state = 60
                self.scientific()
                pass
            elif token in [GdmlExpressionParser.VARIABLE]:
                self.enterOuterAlt(localctx, 2)
                self.state = 61
                self.variable()
                pass
            elif token in [GdmlExpressionParser.PI, GdmlExpressionParser.EULER, GdmlExpressionParser.I]:
                self.enterOuterAlt(localctx, 3)
                self.state = 62
                self.constant()
                pass
            elif token in [GdmlExpressionParser.LPAREN]:
                self.enterOuterAlt(localctx, 4)
                self.state = 63
                self.match(GdmlExpressionParser.LPAREN)
                self.state = 64
                self.expression()
                self.state = 65
                self.match(GdmlExpressionParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ScientificContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.ScientificContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SCIENTIFIC_NUMBER(self):
            return self.getToken(GdmlExpressionParser.SCIENTIFIC_NUMBER, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_scientific

        def enterRule(self, listener):
            if hasattr(listener, "enterScientific"):
                listener.enterScientific(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitScientific"):
                listener.exitScientific(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitScientific"):
                return visitor.visitScientific(self)
            else:
                return visitor.visitChildren(self)




    def scientific(self):

        localctx = GdmlExpressionParser.ScientificContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_scientific)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            self.match(GdmlExpressionParser.SCIENTIFIC_NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ConstantContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.ConstantContext, self).__init__(parent, invokingState)
            self.parser = parser

        def PI(self):
            return self.getToken(GdmlExpressionParser.PI, 0)

        def EULER(self):
            return self.getToken(GdmlExpressionParser.EULER, 0)

        def I(self):
            return self.getToken(GdmlExpressionParser.I, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_constant

        def enterRule(self, listener):
            if hasattr(listener, "enterConstant"):
                listener.enterConstant(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitConstant"):
                listener.exitConstant(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitConstant"):
                return visitor.visitConstant(self)
            else:
                return visitor.visitChildren(self)




    def constant(self):

        localctx = GdmlExpressionParser.ConstantContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_constant)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GdmlExpressionParser.PI) | (1 << GdmlExpressionParser.EULER) | (1 << GdmlExpressionParser.I))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class VariableContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.VariableContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VARIABLE(self):
            return self.getToken(GdmlExpressionParser.VARIABLE, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_variable

        def enterRule(self, listener):
            if hasattr(listener, "enterVariable"):
                listener.enterVariable(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitVariable"):
                listener.exitVariable(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitVariable"):
                return visitor.visitVariable(self)
            else:
                return visitor.visitChildren(self)




    def variable(self):

        localctx = GdmlExpressionParser.VariableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_variable)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(GdmlExpressionParser.VARIABLE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FuncContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.FuncContext, self).__init__(parent, invokingState)
            self.parser = parser

        def funcname(self):
            return self.getTypedRuleContext(GdmlExpressionParser.FuncnameContext,0)


        def LPAREN(self):
            return self.getToken(GdmlExpressionParser.LPAREN, 0)

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GdmlExpressionParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(GdmlExpressionParser.ExpressionContext,i)


        def RPAREN(self):
            return self.getToken(GdmlExpressionParser.RPAREN, 0)

        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(GdmlExpressionParser.COMMA)
            else:
                return self.getToken(GdmlExpressionParser.COMMA, i)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_func

        def enterRule(self, listener):
            if hasattr(listener, "enterFunc"):
                listener.enterFunc(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFunc"):
                listener.exitFunc(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitFunc"):
                return visitor.visitFunc(self)
            else:
                return visitor.visitChildren(self)




    def func(self):

        localctx = GdmlExpressionParser.FuncContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_func)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 75
            self.funcname()
            self.state = 76
            self.match(GdmlExpressionParser.LPAREN)
            self.state = 77
            self.expression()
            self.state = 82
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.COMMA:
                self.state = 78
                self.match(GdmlExpressionParser.COMMA)
                self.state = 79
                self.expression()
                self.state = 84
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 85
            self.match(GdmlExpressionParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FuncnameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.FuncnameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def COS(self):
            return self.getToken(GdmlExpressionParser.COS, 0)

        def TAN(self):
            return self.getToken(GdmlExpressionParser.TAN, 0)

        def SIN(self):
            return self.getToken(GdmlExpressionParser.SIN, 0)

        def ACOS(self):
            return self.getToken(GdmlExpressionParser.ACOS, 0)

        def ATAN(self):
            return self.getToken(GdmlExpressionParser.ATAN, 0)

        def ASIN(self):
            return self.getToken(GdmlExpressionParser.ASIN, 0)

        def LOG(self):
            return self.getToken(GdmlExpressionParser.LOG, 0)

        def LN(self):
            return self.getToken(GdmlExpressionParser.LN, 0)

        def SQRT(self):
            return self.getToken(GdmlExpressionParser.SQRT, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_funcname

        def enterRule(self, listener):
            if hasattr(listener, "enterFuncname"):
                listener.enterFuncname(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFuncname"):
                listener.exitFuncname(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitFuncname"):
                return visitor.visitFuncname(self)
            else:
                return visitor.visitChildren(self)




    def funcname(self):

        localctx = GdmlExpressionParser.FuncnameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_funcname)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 87
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GdmlExpressionParser.COS) | (1 << GdmlExpressionParser.SIN) | (1 << GdmlExpressionParser.TAN) | (1 << GdmlExpressionParser.ACOS) | (1 << GdmlExpressionParser.ASIN) | (1 << GdmlExpressionParser.ATAN) | (1 << GdmlExpressionParser.LN) | (1 << GdmlExpressionParser.LOG) | (1 << GdmlExpressionParser.SQRT))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RelopContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.RelopContext, self).__init__(parent, invokingState)
            self.parser = parser

        def EQ(self):
            return self.getToken(GdmlExpressionParser.EQ, 0)

        def GT(self):
            return self.getToken(GdmlExpressionParser.GT, 0)

        def LT(self):
            return self.getToken(GdmlExpressionParser.LT, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_relop

        def enterRule(self, listener):
            if hasattr(listener, "enterRelop"):
                listener.enterRelop(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRelop"):
                listener.exitRelop(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRelop"):
                return visitor.visitRelop(self)
            else:
                return visitor.visitChildren(self)




    def relop(self):

        localctx = GdmlExpressionParser.RelopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_relop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GdmlExpressionParser.GT) | (1 << GdmlExpressionParser.LT) | (1 << GdmlExpressionParser.EQ))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





