#!/bin/sh

grep -q 'self.column' *.g4
if [ "$?" -eq 0 ]
then
    echo "Switching to Java predicates..."
    sed -ie 's/language=Python2/language=Java/g' *.g4;
    sed -ie 's/self.column/getCharPositionInLine()/g' *.g4 ;
    exit 0;
fi

grep -q 'getCharPositionInLine()' *.g4
if [ "$?" -eq 0 ]
then
    echo "Switching to Python predicates..."
    sed -ie 's/language=Java/language=Python2/g' *.g4;
    sed -ie 's/getCharPositionInLine()/self.column/g' *.g4;
    exit 0;
fi
