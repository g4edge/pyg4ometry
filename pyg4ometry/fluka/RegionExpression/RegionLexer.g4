lexer grammar RegionLexer;

Whitespace
    : [ \t]
	->skip
    ;

InLineComment
    : '!' ~[\r\n]*
	-> skip
    ;

// Skip preprocessor directives.
LineComment
    : ('*'|'#') {getCharPositionInLine() == 1}? ~[\r\n]*
	-> skip
    ;

Newline
    : '\r'? '\n'
	-> channel(HIDDEN)
    ;

Integer
    : '-'? Digit+
    ;


fragment
Digit
    : [0-9]
    ;

RegionName
    : [A-Za-z] {getCharPositionInLine() == 1}? [A-Za-z0-9_]+
    ;

Plus : '+' ;
Minus : '-' ;
Bar : '|' ;
LParen : '(' ;
RParen : ')' ;
