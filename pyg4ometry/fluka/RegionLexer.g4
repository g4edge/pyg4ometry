lexer grammar RegionLexer;

Whitespace
    : [ \t]
	->skip
    ;

Newline
    : '\r'? '\n'
	-> channel(HIDDEN)
    ;

RegionName
    : [A-Za-z] {self.column == 1}? [A-Za-z0-9_]+
    ;

Integer
    : '-'? Digit+
    ;

Float
    : ('+' | '-'?)
	( // (1.3 | 1. | 1E5 | 1.E5 | 0041E5 | 1.14E+04
	    Digit+ '.'? Digit* 'E'? ('+'|'-')? Digit*
	|
	    '.' Digit+  // .123
	)
    ;

fragment
Digit
    : [0-9]
    ;

// A GeoID does not start at the beginning of the line.
ID
    : [A-Za-z] {self.column != 1}? [A-Za-z0-9_-]*
    ;

Delim
    : [,:;/]
	-> skip
    ;

Plus : '+' ;
Minus  : '-' ;
Bar   : '|' ;
LParen       : '(' ;
RParen       : ')' ;
