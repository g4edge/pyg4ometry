# Generated from Region.g4 by ANTLR 4.7.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2")
        buf.write(u"\13\61\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4")
        buf.write(u"\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\3\2\3\2\3\2\3\2\3\3\6")
        buf.write(u"\3\33\n\3\r\3\16\3\34\3\4\6\4 \n\4\r\4\16\4!\3\5\3\5")
        buf.write(u"\3\6\3\6\3\7\3\7\5\7*\n\7\3\b\3\b\3\t\3\t\3\n\3\n\2\2")
        buf.write(u"\13\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\3\2\4\4")
        buf.write(u"\2\13\13\"\"\6\2\62;C\\aac|\2\63\2\3\3\2\2\2\2\5\3\2")
        buf.write(u"\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2")
        buf.write(u"\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\3\25\3\2\2\2")
        buf.write(u"\5\32\3\2\2\2\7\37\3\2\2\2\t#\3\2\2\2\13%\3\2\2\2\r)")
        buf.write(u"\3\2\2\2\17+\3\2\2\2\21-\3\2\2\2\23/\3\2\2\2\25\26\t")
        buf.write(u"\2\2\2\26\27\3\2\2\2\27\30\b\2\2\2\30\4\3\2\2\2\31\33")
        buf.write(u"\t\3\2\2\32\31\3\2\2\2\33\34\3\2\2\2\34\32\3\2\2\2\34")
        buf.write(u"\35\3\2\2\2\35\6\3\2\2\2\36 \t\3\2\2\37\36\3\2\2\2 !")
        buf.write(u"\3\2\2\2!\37\3\2\2\2!\"\3\2\2\2\"\b\3\2\2\2#$\7-\2\2")
        buf.write(u"$\n\3\2\2\2%&\7/\2\2&\f\3\2\2\2\'*\5\t\5\2(*\5\13\6\2")
        buf.write(u")\'\3\2\2\2)(\3\2\2\2*\16\3\2\2\2+,\7~\2\2,\20\3\2\2")
        buf.write(u"\2-.\7*\2\2.\22\3\2\2\2/\60\7+\2\2\60\24\3\2\2\2\b\2")
        buf.write(u"\32\34\37!)\3\b\2\2")
        return buf.getvalue()


class RegionLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    WHITESPACE = 1
    BODYNAME = 2
    REGIONNAME = 3
    PLUS = 4
    MINUS = 5
    SIGN = 6
    BAR = 7
    LPAREN = 8
    RPAREN = 9

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'+'", u"'-'", u"'|'", u"'('", u"')'" ]

    symbolicNames = [ u"<INVALID>",
            u"WHITESPACE", u"BODYNAME", u"REGIONNAME", u"PLUS", u"MINUS", 
            u"SIGN", u"BAR", u"LPAREN", u"RPAREN" ]

    ruleNames = [ u"WHITESPACE", u"BODYNAME", u"REGIONNAME", u"PLUS", u"MINUS", 
                  u"SIGN", u"BAR", u"LPAREN", u"RPAREN" ]

    grammarFileName = u"Region.g4"

    def __init__(self, input=None, output=sys.stdout):
        super(RegionLexer, self).__init__(input, output=output)
        self.checkVersion("4.7.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


