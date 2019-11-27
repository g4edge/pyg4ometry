# Generated from RegionLexer.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2")
        buf.write(u"\rT\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t")
        buf.write(u"\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write(u"\3\2\3\2\3\2\3\2\3\3\3\3\7\3\"\n\3\f\3\16\3%\13\3\3\3")
        buf.write(u"\3\3\3\4\3\4\3\4\7\4,\n\4\f\4\16\4/\13\4\3\4\3\4\3\5")
        buf.write(u"\5\5\64\n\5\3\5\3\5\3\5\3\5\3\6\5\6;\n\6\3\6\6\6>\n\6")
        buf.write(u"\r\6\16\6?\3\7\3\7\3\b\3\b\3\b\6\bG\n\b\r\b\16\bH\3\t")
        buf.write(u"\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\2\2\16\3\3\5\4")
        buf.write(u"\7\5\t\6\13\7\r\2\17\b\21\t\23\n\25\13\27\f\31\r\3\2")
        buf.write(u"\b\4\2\13\13\"\"\4\2\f\f\17\17\4\2%%,,\3\2\62;\4\2C\\")
        buf.write(u"c|\6\2\62;C\\aac|\2X\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2")
        buf.write(u"\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2")
        buf.write(u"\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2")
        buf.write(u"\2\3\33\3\2\2\2\5\37\3\2\2\2\7(\3\2\2\2\t\63\3\2\2\2")
        buf.write(u"\13:\3\2\2\2\rA\3\2\2\2\17C\3\2\2\2\21J\3\2\2\2\23L\3")
        buf.write(u"\2\2\2\25N\3\2\2\2\27P\3\2\2\2\31R\3\2\2\2\33\34\t\2")
        buf.write(u"\2\2\34\35\3\2\2\2\35\36\b\2\2\2\36\4\3\2\2\2\37#\7#")
        buf.write(u"\2\2 \"\n\3\2\2! \3\2\2\2\"%\3\2\2\2#!\3\2\2\2#$\3\2")
        buf.write(u"\2\2$&\3\2\2\2%#\3\2\2\2&\'\b\3\2\2\'\6\3\2\2\2()\t\4")
        buf.write(u"\2\2)-\6\4\2\2*,\n\3\2\2+*\3\2\2\2,/\3\2\2\2-+\3\2\2")
        buf.write(u"\2-.\3\2\2\2.\60\3\2\2\2/-\3\2\2\2\60\61\b\4\2\2\61\b")
        buf.write(u"\3\2\2\2\62\64\7\17\2\2\63\62\3\2\2\2\63\64\3\2\2\2\64")
        buf.write(u"\65\3\2\2\2\65\66\7\f\2\2\66\67\3\2\2\2\678\b\5\3\28")
        buf.write(u"\n\3\2\2\29;\7/\2\2:9\3\2\2\2:;\3\2\2\2;=\3\2\2\2<>\5")
        buf.write(u"\r\7\2=<\3\2\2\2>?\3\2\2\2?=\3\2\2\2?@\3\2\2\2@\f\3\2")
        buf.write(u"\2\2AB\t\5\2\2B\16\3\2\2\2CD\t\6\2\2DF\6\b\3\2EG\t\7")
        buf.write(u"\2\2FE\3\2\2\2GH\3\2\2\2HF\3\2\2\2HI\3\2\2\2I\20\3\2")
        buf.write(u"\2\2JK\7-\2\2K\22\3\2\2\2LM\7/\2\2M\24\3\2\2\2NO\7~\2")
        buf.write(u"\2O\26\3\2\2\2PQ\7*\2\2Q\30\3\2\2\2RS\7+\2\2S\32\3\2")
        buf.write(u"\2\2\t\2#-\63:?H\4\b\2\2\2\3\2")
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
    Plus = 7
    Minus = 8
    Bar = 9
    LParen = 10
    RParen = 11

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'+'", u"'-'", u"'|'", u"'('", u"')'" ]

    symbolicNames = [ u"<INVALID>",
            u"Whitespace", u"InLineComment", u"LineComment", u"Newline", 
            u"Integer", u"RegionName", u"Plus", u"Minus", u"Bar", u"LParen", 
            u"RParen" ]

    ruleNames = [ u"Whitespace", u"InLineComment", u"LineComment", u"Newline", 
                  u"Integer", u"Digit", u"RegionName", u"Plus", u"Minus", 
                  u"Bar", u"LParen", u"RParen" ]

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
                return getCharPositionInLine() == 1
         

    def RegionName_sempred(self, localctx, predIndex):
            if predIndex == 1:
                return getCharPositionInLine() == 1
         


