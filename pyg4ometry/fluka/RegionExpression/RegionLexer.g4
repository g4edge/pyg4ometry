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
    : ('*'|'#') {self.column == 1}? ~[\r\n]*
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
    : [A-Za-z] {self.column == 1}? [A-Za-z0-9_]+
    ;

BodyName
    : [A-Za-z] [A-Za-z0-9_]+
    ;

Plus : '+' ;
Minus : '-' ;
Bar : '|' ;
LParen : '(' ;
RParen : ')' ;
