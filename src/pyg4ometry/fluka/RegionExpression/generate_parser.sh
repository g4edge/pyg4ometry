#!/bin/sh

# If you don't have /usr/local/lib/antlr-4.7-complete.jar then you
# should get it via http://www.antlr.org.

ANTLRJAR=/usr/local/lib/antlr-4.9-complete.jar

# Grep for string "language=Python3" -> it's a python3 target:
grep -q 'language=Python3' *.g4
if [ "$?" -eq 0 ]
then
    echo "Compiling parser with python3 as target."
    java -jar $ANTLRJAR RegionLexer.g4 -Dlanguage=Python3 -visitor;
    java -jar $ANTLRJAR RegionParser.g4 -Dlanguage=Python3 -visitor;
    exit 0;
fi

# Grep for string "language=Java" -> it's a Java target
grep -q 'language=Java' *.g4
if [ "$?" -eq 0 ]
then
    echo "Compiling parser with Java as target."
    java -jar $ANTLRJAR RegionLexer.g4 -Dlanguage=Java -visitor;
    java -jar $ANTLRJAR RegionParser.g4 -Dlanguage=Java -visitor;
    javac *.java;
    exit 0;
fi

echo "Unable to decide correct target for parser!"
exit(1)

