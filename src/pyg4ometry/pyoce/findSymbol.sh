#!/bin/bash
# NOTE : Quote it else use array to avoid problems #
FILES="/opt/local/lib/libTK*dylib"
for f in $FILES
do
  echo "Processing $f file..."
  # take action on each file. $f store current file name
  nm $f | grep StlAPI_Writer
done
