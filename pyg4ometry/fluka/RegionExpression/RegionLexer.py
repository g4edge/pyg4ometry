# Generated from RegionLexer.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2")
        buf.write(u"\16\\\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write(u"\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t")
        buf.write(u"\r\4\16\t\16\3\2\3\2\3\2\3\2\3\3\3\3\7\3$\n\3\f\3\16")
        buf.write(u"\3\'\13\3\3\3\3\3\3\4\3\4\3\4\7\4.\n\4\f\4\16\4\61\13")
        buf.write(u"\4\3\4\3\4\3\5\5\5\66\n\5\3\5\3\5\3\5\3\5\3\6\5\6=\n")
        buf.write(u"\6\3\6\6\6@\n\6\r\6\16\6A\3\7\3\7\3\b\3\b\3\b\6\bI\n")
        buf.write(u"\b\r\b\16\bJ\3\t\3\t\6\tO\n\t\r\t\16\tP\3\n\3\n\3\13")
        buf.write(u"\3\13\3\f\3\f\3\r\3\r\3\16\3\16\2\2\17\3\3\5\4\7\5\t")
        buf.write(u"\6\13\7\r\2\17\b\21\t\23\n\25\13\27\f\31\r\33\16\3\2")
        buf.write(u"\b\4\2\13\13\"\"\4\2\f\f\17\17\4\2%%,,\3\2\62;\4\2C\\")
        buf.write(u"c|\6\2\62;C\\aac|\2a\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2")
        buf.write(u"\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2")
        buf.write(u"\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2")
        buf.write(u"\2\2\33\3\2\2\2\3\35\3\2\2\2\5!\3\2\2\2\7*\3\2\2\2\t")
        buf.write(u"\65\3\2\2\2\13<\3\2\2\2\rC\3\2\2\2\17E\3\2\2\2\21L\3")
        buf.write(u"\2\2\2\23R\3\2\2\2\25T\3\2\2\2\27V\3\2\2\2\31X\3\2\2")
        buf.write(u"\2\33Z\3\2\2\2\35\36\t\2\2\2\36\37\3\2\2\2\37 \b\2\2")
        buf.write(u"\2 \4\3\2\2\2!%\7#\2\2\"$\n\3\2\2#\"\3\2\2\2$\'\3\2\2")
        buf.write(u"\2%#\3\2\2\2%&\3\2\2\2&(\3\2\2\2\'%\3\2\2\2()\b\3\2\2")
        buf.write(u")\6\3\2\2\2*+\t\4\2\2+/\6\4\2\2,.\n\3\2\2-,\3\2\2\2.")
        buf.write(u"\61\3\2\2\2/-\3\2\2\2/\60\3\2\2\2\60\62\3\2\2\2\61/\3")
        buf.write(u"\2\2\2\62\63\b\4\2\2\63\b\3\2\2\2\64\66\7\17\2\2\65\64")
        buf.write(u"\3\2\2\2\65\66\3\2\2\2\66\67\3\2\2\2\678\7\f\2\289\3")
        buf.write(u"\2\2\29:\b\5\3\2:\n\3\2\2\2;=\7/\2\2<;\3\2\2\2<=\3\2")
        buf.write(u"\2\2=?\3\2\2\2>@\5\r\7\2?>\3\2\2\2@A\3\2\2\2A?\3\2\2")
        buf.write(u"\2AB\3\2\2\2B\f\3\2\2\2CD\t\5\2\2D\16\3\2\2\2EF\t\6\2")
        buf.write(u"\2FH\6\b\3\2GI\t\7\2\2HG\3\2\2\2IJ\3\2\2\2JH\3\2\2\2")
        buf.write(u"JK\3\2\2\2K\20\3\2\2\2LN\t\6\2\2MO\t\7\2\2NM\3\2\2\2")
        buf.write(u"OP\3\2\2\2PN\3\2\2\2PQ\3\2\2\2Q\22\3\2\2\2RS\7-\2\2S")
        buf.write(u"\24\3\2\2\2TU\7/\2\2U\26\3\2\2\2VW\7~\2\2W\30\3\2\2\2")
        buf.write(u"XY\7*\2\2Y\32\3\2\2\2Z[\7+\2\2[\34\3\2\2\2\n\2%/\65<")
        buf.write(u"AJP\4\b\2\2\2\3\2")
        return buf.getvalue()


class RegionLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    Whitespace = 1
    InLineComment = 2
    LineComment = 3
    Newline = 4
    Integer = 5
    RegionName = 6
    BodyName = 7
    Plus = 8
    Minus = 9
    Bar = 10
    LParen = 11
    RParen = 12

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'+'", u"'-'", u"'|'", u"'('", u"')'" ]

    symbolicNames = [ u"<INVALID>",
            u"Whitespace", u"InLineComment", u"LineComment", u"Newline", 
            u"Integer", u"RegionName", u"BodyName", u"Plus", u"Minus", u"Bar", 
            u"LParen", u"RParen" ]

    ruleNames = [ u"Whitespace", u"InLineComment", u"LineComment", u"Newline", 
                  u"Integer", u"Digit", u"RegionName", u"BodyName", u"Plus", 
                  u"Minus", u"Bar", u"LParen", u"RParen" ]

    grammarFileName = u"RegionLexer.g4"

    def __init__(self, input=None, output=sys.stdout):
        super(RegionLexer, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


    def sempred(self, localctx, ruleIndex, predIndex):
        if self._predicates is None:
            preds = dict()
            preds[2] = self.LineComment_sempred
            preds[6] = self.RegionName_sempred
            self._predicates = preds
        pred = self._predicates.get(ruleIndex, None)
        if pred is not None:
            return pred(localctx, predIndex)
        else:
            raise Exception("No registered predicate for:" + str(ruleIndex))

    def LineComment_sempred(self, localctx, predIndex):
            if predIndex == 0:
                return self.column == 1
         

    def RegionName_sempred(self, localctx, predIndex):
            if predIndex == 1:
                return self.column == 1
         


