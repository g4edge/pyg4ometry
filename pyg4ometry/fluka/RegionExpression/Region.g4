grammar Region;

WHITESPACE : [ \t] ->skip ;

BODYNAME : ([a-z] | [A-Z] | [0-9] | '_' )+ ;

REGIONNAME : ([a-z] | [A-Z] | [0-9] | '_' )+ ;

PLUS   : '+' ;
MINUS  : '-' ;
SIGN   : (PLUS | MINUS);
BAR    : '|' ;
LPAREN : '(' ;
RPAREN : ')' ;

region : expression (BAR expression+)*;

/* zone : expression+; */

expression :  signbody+ subzone+ signbody+ | signbody+ subzone+ | subzone+ signbody+ | subzone+ | signbody+  ;

subzone : (MINUS | PLUS) LPAREN expression RPAREN;

signbody : (MINUS | PLUS) BODYNAME;





