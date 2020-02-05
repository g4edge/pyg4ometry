parser grammar RegionParser;

options {
tokenVocab=RegionLexer;
language=Python2;
}

regions
    : region+
    ;

region
    : RegionName Integer zone         # simpleRegion
    | RegionName Integer zoneUnion    # complexRegion
    ;

zoneUnion
    : Bar zone (Bar zone)+      # multipleUnion
    | Bar zone                  # singleUnion
    | zone Bar (zone Bar)* zone # multipleUnion2
    ;

zone
    : BodyName? expr       # zoneExpr
    | BodyName? subZone    # zoneSubZone
    | BodyName             # zoneBody
    ;

expr
    : unaryExpression         # singleUnary
    | unaryExpression expr    # unaryAndBoolean
    | subZone expr            # unaryAndSubZone
    | subZone                 # oneSubZone
    ;

subZone
    : (Minus | Plus) LParen BodyName? expr RParen
    ;

unaryExpression
    : (Minus | Plus) BodyName
    ;
