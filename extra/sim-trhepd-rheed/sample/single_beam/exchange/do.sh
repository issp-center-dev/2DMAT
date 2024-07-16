#!/bin/sh

sh prepare.sh

./bulk.exe

time mpiexec --oversubscribe -np 4 py2dmat-sim-trhepd-rheed input.toml

echo diff output/best_result.txt ref.txt
res=0
diff output/best_result.txt ref.txt || res=$?
if [ $res -eq 0 ]; then
  echo TEST PASS
  true
else
  echo TEST FAILED: best_result.txt and ref.txt differ
  false
fi

