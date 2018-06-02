#!/bin/sh

# If you don't have /usr/local/lib/antlr-4.7-complete.jar then you
# should get it via http://www.antlr.org.

# Grep for string "language=Python2" -> it's a python2 target:
grep -q 'language=Python2' *.g4
if [ "$?" -eq 0 ]
then
    echo "Compiling parser with python2 as target."
    java -jar /usr/local/lib/antlr-4.7-complete.jar FlukaLexer.g4 \
	 -Dlanguage=Python2 -visitor;
    java -jar /usr/local/lib/antlr-4.7-complete.jar FlukaParser.g4 \
	 -Dlanguage=Python2 -visitor;
    exit 0;
fi

# Grep for string "language=Java" -> it's a Java target
grep -q 'language=Java' *.g4
if [ "$?" -eq 0 ]
then
    echo "Compiling parser with Java as target."
    java -jar /usr/local/lib/antlr-4.7-complete.jar FlukaLexer.g4 \
	 -Dlanguage=Java -visitor;
    java -jar /usr/local/lib/antlr-4.7-complete.jar FlukaParser.g4 \
	 -Dlanguage=Java -visitor;
    javac *.java;
    exit 0;
fi

echo "Unable to decide correct target for parser!"
exit(1)
