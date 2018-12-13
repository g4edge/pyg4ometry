# Generated from GdmlExpression.g4 by ANTLR 4.7.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\35h\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write(u"\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4")
        buf.write(u"\16\t\16\4\17\t\17\3\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\7")
        buf.write(u"\3\'\n\3\f\3\16\3*\13\3\3\4\3\4\3\4\3\4\7\4\60\n\4\f")
        buf.write(u"\4\16\4\63\13\4\3\5\3\5\3\6\3\6\3\7\3\7\3\7\7\7<\n\7")
        buf.write(u"\f\7\16\7?\13\7\3\b\3\b\3\b\3\b\3\b\3\b\5\bG\n\b\3\t")
        buf.write(u"\3\t\3\t\3\t\3\t\3\t\3\t\5\tP\n\t\3\n\3\n\3\13\3\13\3")
        buf.write(u"\f\3\f\3\r\3\r\3\r\3\r\3\r\7\r]\n\r\f\r\16\r`\13\r\3")
        buf.write(u"\r\3\r\3\16\3\16\3\17\3\17\3\17\2\2\20\2\4\6\b\n\f\16")
        buf.write(u"\20\22\24\26\30\32\34\2\7\3\2\16\17\3\2\20\21\3\2\30")
        buf.write(u"\32\3\2\3\13\3\2\22\24\2c\2\36\3\2\2\2\4\"\3\2\2\2\6")
        buf.write(u"+\3\2\2\2\b\64\3\2\2\2\n\66\3\2\2\2\f8\3\2\2\2\16F\3")
        buf.write(u"\2\2\2\20O\3\2\2\2\22Q\3\2\2\2\24S\3\2\2\2\26U\3\2\2")
        buf.write(u"\2\30W\3\2\2\2\32c\3\2\2\2\34e\3\2\2\2\36\37\5\4\3\2")
        buf.write(u"\37 \5\34\17\2 !\5\4\3\2!\3\3\2\2\2\"(\5\6\4\2#$\5\b")
        buf.write(u"\5\2$%\5\6\4\2%\'\3\2\2\2&#\3\2\2\2\'*\3\2\2\2(&\3\2")
        buf.write(u"\2\2()\3\2\2\2)\5\3\2\2\2*(\3\2\2\2+\61\5\f\7\2,-\5\n")
        buf.write(u"\6\2-.\5\f\7\2.\60\3\2\2\2/,\3\2\2\2\60\63\3\2\2\2\61")
        buf.write(u"/\3\2\2\2\61\62\3\2\2\2\62\7\3\2\2\2\63\61\3\2\2\2\64")
        buf.write(u"\65\t\2\2\2\65\t\3\2\2\2\66\67\t\3\2\2\67\13\3\2\2\2")
        buf.write(u"8=\5\16\b\29:\7\27\2\2:<\5\16\b\2;9\3\2\2\2<?\3\2\2\2")
        buf.write(u"=;\3\2\2\2=>\3\2\2\2>\r\3\2\2\2?=\3\2\2\2@A\7\16\2\2")
        buf.write(u"AG\5\16\b\2BC\7\17\2\2CG\5\16\b\2DG\5\30\r\2EG\5\20\t")
        buf.write(u"\2F@\3\2\2\2FB\3\2\2\2FD\3\2\2\2FE\3\2\2\2G\17\3\2\2")
        buf.write(u"\2HP\5\22\n\2IP\5\26\f\2JP\5\24\13\2KL\7\f\2\2LM\5\4")
        buf.write(u"\3\2MN\7\r\2\2NP\3\2\2\2OH\3\2\2\2OI\3\2\2\2OJ\3\2\2")
        buf.write(u"\2OK\3\2\2\2P\21\3\2\2\2QR\7\34\2\2R\23\3\2\2\2ST\t\4")
        buf.write(u"\2\2T\25\3\2\2\2UV\7\33\2\2V\27\3\2\2\2WX\5\32\16\2X")
        buf.write(u"Y\7\f\2\2Y^\5\4\3\2Z[\7\25\2\2[]\5\4\3\2\\Z\3\2\2\2]")
        buf.write(u"`\3\2\2\2^\\\3\2\2\2^_\3\2\2\2_a\3\2\2\2`^\3\2\2\2ab")
        buf.write(u"\7\r\2\2b\31\3\2\2\2cd\t\5\2\2d\33\3\2\2\2ef\t\6\2\2")
        buf.write(u"f\35\3\2\2\2\b(\61=FO^")
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
    RULE_operatorAddSub = 3
    RULE_operatorMulDiv = 4
    RULE_powExpression = 5
    RULE_signedAtom = 6
    RULE_atom = 7
    RULE_scientific = 8
    RULE_constant = 9
    RULE_variable = 10
    RULE_func = 11
    RULE_funcname = 12
    RULE_relop = 13

    ruleNames =  [ u"equation", u"expression", u"multiplyingExpression", 
                   u"operatorAddSub", u"operatorMulDiv", u"powExpression", 
                   u"signedAtom", u"atom", u"scientific", u"constant", u"variable", 
                   u"func", u"funcname", u"relop" ]

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
            self.state = 28
            self.expression()
            self.state = 29
            self.relop()
            self.state = 30
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


        def operatorAddSub(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GdmlExpressionParser.OperatorAddSubContext)
            else:
                return self.getTypedRuleContext(GdmlExpressionParser.OperatorAddSubContext,i)


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
            self.state = 32
            self.multiplyingExpression()
            self.state = 38
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.PLUS or _la==GdmlExpressionParser.MINUS:
                self.state = 33
                self.operatorAddSub()
                self.state = 34
                self.multiplyingExpression()
                self.state = 40
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


        def operatorMulDiv(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GdmlExpressionParser.OperatorMulDivContext)
            else:
                return self.getTypedRuleContext(GdmlExpressionParser.OperatorMulDivContext,i)


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
            self.state = 41
            self.powExpression()
            self.state = 47
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.TIMES or _la==GdmlExpressionParser.DIV:
                self.state = 42
                self.operatorMulDiv()
                self.state = 43
                self.powExpression()
                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class OperatorAddSubContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.OperatorAddSubContext, self).__init__(parent, invokingState)
            self.parser = parser

        def PLUS(self):
            return self.getToken(GdmlExpressionParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(GdmlExpressionParser.MINUS, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_operatorAddSub

        def enterRule(self, listener):
            if hasattr(listener, "enterOperatorAddSub"):
                listener.enterOperatorAddSub(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOperatorAddSub"):
                listener.exitOperatorAddSub(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitOperatorAddSub"):
                return visitor.visitOperatorAddSub(self)
            else:
                return visitor.visitChildren(self)




    def operatorAddSub(self):

        localctx = GdmlExpressionParser.OperatorAddSubContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_operatorAddSub)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            _la = self._input.LA(1)
            if not(_la==GdmlExpressionParser.PLUS or _la==GdmlExpressionParser.MINUS):
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

    class OperatorMulDivContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GdmlExpressionParser.OperatorMulDivContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TIMES(self):
            return self.getToken(GdmlExpressionParser.TIMES, 0)

        def DIV(self):
            return self.getToken(GdmlExpressionParser.DIV, 0)

        def getRuleIndex(self):
            return GdmlExpressionParser.RULE_operatorMulDiv

        def enterRule(self, listener):
            if hasattr(listener, "enterOperatorMulDiv"):
                listener.enterOperatorMulDiv(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOperatorMulDiv"):
                listener.exitOperatorMulDiv(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitOperatorMulDiv"):
                return visitor.visitOperatorMulDiv(self)
            else:
                return visitor.visitChildren(self)




    def operatorMulDiv(self):

        localctx = GdmlExpressionParser.OperatorMulDivContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_operatorMulDiv)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            _la = self._input.LA(1)
            if not(_la==GdmlExpressionParser.TIMES or _la==GdmlExpressionParser.DIV):
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
        self.enterRule(localctx, 10, self.RULE_powExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 54
            self.signedAtom()
            self.state = 59
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.POW:
                self.state = 55
                self.match(GdmlExpressionParser.POW)
                self.state = 56
                self.signedAtom()
                self.state = 61
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
        self.enterRule(localctx, 12, self.RULE_signedAtom)
        try:
            self.state = 68
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GdmlExpressionParser.PLUS]:
                self.enterOuterAlt(localctx, 1)
                self.state = 62
                self.match(GdmlExpressionParser.PLUS)
                self.state = 63
                self.signedAtom()
                pass
            elif token in [GdmlExpressionParser.MINUS]:
                self.enterOuterAlt(localctx, 2)
                self.state = 64
                self.match(GdmlExpressionParser.MINUS)
                self.state = 65
                self.signedAtom()
                pass
            elif token in [GdmlExpressionParser.COS, GdmlExpressionParser.SIN, GdmlExpressionParser.TAN, GdmlExpressionParser.ACOS, GdmlExpressionParser.ASIN, GdmlExpressionParser.ATAN, GdmlExpressionParser.LN, GdmlExpressionParser.LOG, GdmlExpressionParser.SQRT]:
                self.enterOuterAlt(localctx, 3)
                self.state = 66
                self.func()
                pass
            elif token in [GdmlExpressionParser.LPAREN, GdmlExpressionParser.PI, GdmlExpressionParser.EULER, GdmlExpressionParser.I, GdmlExpressionParser.VARIABLE, GdmlExpressionParser.SCIENTIFIC_NUMBER]:
                self.enterOuterAlt(localctx, 4)
                self.state = 67
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
        self.enterRule(localctx, 14, self.RULE_atom)
        try:
            self.state = 77
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GdmlExpressionParser.SCIENTIFIC_NUMBER]:
                self.enterOuterAlt(localctx, 1)
                self.state = 70
                self.scientific()
                pass
            elif token in [GdmlExpressionParser.VARIABLE]:
                self.enterOuterAlt(localctx, 2)
                self.state = 71
                self.variable()
                pass
            elif token in [GdmlExpressionParser.PI, GdmlExpressionParser.EULER, GdmlExpressionParser.I]:
                self.enterOuterAlt(localctx, 3)
                self.state = 72
                self.constant()
                pass
            elif token in [GdmlExpressionParser.LPAREN]:
                self.enterOuterAlt(localctx, 4)
                self.state = 73
                self.match(GdmlExpressionParser.LPAREN)
                self.state = 74
                self.expression()
                self.state = 75
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
        self.enterRule(localctx, 16, self.RULE_scientific)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 79
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
        self.enterRule(localctx, 18, self.RULE_constant)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
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
        self.enterRule(localctx, 20, self.RULE_variable)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
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
        self.enterRule(localctx, 22, self.RULE_func)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.funcname()
            self.state = 86
            self.match(GdmlExpressionParser.LPAREN)
            self.state = 87
            self.expression()
            self.state = 92
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GdmlExpressionParser.COMMA:
                self.state = 88
                self.match(GdmlExpressionParser.COMMA)
                self.state = 89
                self.expression()
                self.state = 94
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 95
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
        self.enterRule(localctx, 24, self.RULE_funcname)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
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
        self.enterRule(localctx, 26, self.RULE_relop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 99
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





