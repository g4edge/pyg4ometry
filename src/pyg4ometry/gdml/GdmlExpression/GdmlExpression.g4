/*
BSD License

Copyright (c) 2013, Tom Everett
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of Tom Everett nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

antlr4 -Dlanguage=Python3 -no-listener -visitor GdmlExpression.g4

*/

grammar GdmlExpression;

equation
   : expression relop expression
   ;

expression
   : multiplyingExpression (operatorAddSub multiplyingExpression)*
   ;

multiplyingExpression
   : powExpression (operatorMulDiv powExpression)*
   ;

operatorAddSub : PLUS | MINUS;

operatorMulDiv : TIMES | DIV;

powExpression
   : signedAtom (POW signedAtom)*
   ;

signedAtom
   : PLUS signedAtom
   | MINUS signedAtom
   | func
   | atom
   ;

atom
   : scientific
   | matrixElement
   | variable
   | constant
   | LPAREN expression RPAREN
   ;


scientific
   : SCIENTIFIC_NUMBER
   ;

matrixElement
   : variable LBRACKET expression (COMMA expression)* RBRACKET
   ;

constant
   : PI
   | EULER
   | I
   ;

variable
   : VARIABLE
   ;

func
   : funcname LPAREN expression (COMMA expression)* RPAREN
   ;

funcname
   : COS
   | TAN
   | SIN
   | ACOS
   | ATAN
   | ASIN
   | LOG
   | LN
   | EXP
   | SQRT
   | POWER
   | ABS
   | MIN
   | MAX
   ;

relop
   : EQ
   | GT
   | LT
   ;


COS
   : 'cos'
   ;


SIN
   : 'sin'
   ;


TAN
   : 'tan'
   ;


ACOS
   : 'acos'
   ;


ASIN
   : 'asin'
   ;


ATAN
   : 'atan'
   ;


LN
   : 'log'
   ;


LOG
   : 'log10'
   ;


SQRT
   : 'sqrt'
   ;

EXP
   : 'exp'
   ;

POWER
   : 'pow'
   ;

ABS
   : 'abs'
   ;

LPAREN
   : '('
   ;


RPAREN
   : ')'
   ;

LBRACKET
   : '['
   ;


RBRACKET
   : ']'
   ;


PLUS
   : '+'
   ;


MINUS
   : '-'
   ;


TIMES
   : '*'
   ;


DIV
   : '/'
   ;


GT
   : '>'
   ;


LT
   : '<'
   ;


EQ
   : '='
   ;


COMMA
   : ','
   ;


POINT
   : '.'
   ;


POW
   : '^'
   ;


PI
   : 'pi'
   ;


EULER
   : E2
   ;


I
   : 'i'
   ;

MIN
   : 'min'
   ;

MAX
   : 'max'
   ;

VARIABLE
   : VALID_ID_START VALID_ID_CHAR*
   ;


fragment VALID_ID_START
   : ('a' .. 'z') | ('A' .. 'Z') | '_'
   ;


fragment VALID_ID_CHAR
   : VALID_ID_START | ('0' .. '9')
   ;


SCIENTIFIC_NUMBER
   : NUMBER ((E1 | E2) SIGN? NUMBER)?
   ;


fragment NUMBER
   : POINT ('0' .. '9')+
   | ('0' .. '9')+ POINT
   | ('0' .. '9')+ POINT ('0' .. '9')+
   | ('0' .. '9')+
   ;


fragment E1
   : 'E'
   ;


fragment E2
   : 'e'
   ;


fragment SIGN
   : ('+' | '-')
   ;


WS
   : [ \r\n\t] + -> skip
   ;
