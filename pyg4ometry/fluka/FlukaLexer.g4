lexer grammar FlukaLexer;

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

End
    : 'E' {self.column == 1}? 'ND'
    -> skip
    ;

BodyCode
    : [A-Z] {self.column == 1}? [A-Z] [A-Z]
    ;

Lattice
    : 'L' {self.column == 1}? 'ATTICE'
    ;

RegionName
    : [A-Za-z] {self.column == 1}? [A-Za-z0-9_]+
    ;

// Geometry directives:
StartExpansion
    : '$' {self.column == 1}? [sS] 'tart_expansion'
    ;

StartTranslat
    :  '$' {self.column == 1}? [sS] 'tart_translat'
    ;

StartTransform
    : '$' {self.column == 1}? [sS] 'tart_transform'
    ;

EndExpansion
    : '$' {self.column == 1}? [eE] 'nd_expansion'
    ;

EndTranslat
    : '$' {self.column == 1}? [eE] 'nd_translat'
    ;

EndTransform
    :'$' {self.column == 1}? [eE] 'nd_transform'
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
