parser grammar FlukaParser ;

options {
tokenVocab=FlukaLexer;
language=Java ;
}

// Geometry:
geocards
    : (body | region | lattice)+
    ;

body
    : geoDirective                     # GeometryDirective
    | BodyCode (ID | Integer) Float+   # BodyDefSpaceDelim
    | BodyCode (Delim (ID|Float)?)*    # BodyDefPunctDelim
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
    : expr
    | subZone
    ;

expr
    : unaryExpression         # singleUnary
    | unaryExpression expr    # unaryAndBoolean
    | subZone expr            # unaryAndSubZone
    | subZone                 # oneSubZone
    ;

subZone
    : (Minus | Plus) LParen expr RParen
    ;

unaryExpression
    : (Minus | Plus) ID
    ;

geoDirective
    : expansion
    | translat
    | transform
    ;

expansion
    : StartExpansion Float body+ EndExpansion
    ;

translat
    : StartTranslat Float Float Float body+ EndTranslat
    ;

transform
    : StartTransform (ID | Integer) body+ EndTransform
    ;

lattice
    : Lattice ID+
    ;
