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
    : ('*'|'#') {getCharPositionInLine() == 1}? ~[\r\n]*
	-> skip
    ;

Newline
    : '\r'? '\n'
	-> channel(HIDDEN)
    ;

End
    : 'E' {getCharPositionInLine() == 1}? 'ND'
    -> skip
    ;

BodyCode
    : [A-Z] {getCharPositionInLine() == 1}? [A-Z] [A-Z]
    ;

Lattice
    : 'L' {getCharPositionInLine() == 1}? 'ATTICE'
    ;

RegionName
    : [A-Za-z] {getCharPositionInLine() == 1}? [A-Za-z0-9_]+
    ;

// Geometry directives:
StartExpansion
    : '$' {getCharPositionInLine() == 1}? [sS] 'tart_expansion'
    ;

StartTranslat
    :  '$' {getCharPositionInLine() == 1}? [sS] 'tart_translat'
    ;

StartTransform
    : '$' {getCharPositionInLine() == 1}? [sS] 'tart_transform'
    ;

EndExpansion
    : '$' {getCharPositionInLine() == 1}? [eE] 'nd_expansion'
    ;

EndTranslat
    : '$' {getCharPositionInLine() == 1}? [eE] 'nd_translat'
    ;

EndTransform
    :'$' {getCharPositionInLine() == 1}? [eE] 'nd_transform'
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
    : [A-Za-z] {getCharPositionInLine() != 1}? [A-Za-z0-9_-]*
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
