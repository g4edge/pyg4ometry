grammar GdmlExpression;

expr: ID '(' expr (COMMA expr)* ')' # FunCall
    |  expr op=('*'|'/') expr       # MultDiv
    |  expr op=('+'|'-') expr       # AddSub 
    |  NUM                          # number
    |  ID                           # id 
    |  '(' expr ')'                 # Parens
    ;

ID      : [a-zA-Z] [A-Za-z0-9_]* ;
COMMA   : ',';
WS      : [ \t]+ -> skip; 

NUM : ('+' | '-'?)
      (
      	   DIGIT+ '.'? DIGIT* ('E'|'e')? ('+'|'-')? DIGIT*
      |
	   '.' DIGIT+ 	
      )
    ;

fragment
DIGIT : [0-9];
MUL : '*';
DIV : '/';
ADD : '+';
SUB : '-';
POW : '^';



