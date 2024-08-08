#!/bin/sh

export PYTHONPATH=../../src:$PYTHONPATH

sh ./prepare.sh

#time python3 simple.py
time mpiexec -np 4 python3 simple.py

resfile=output/ColorMap.txt
reffile=ref_ColorMap.txt

echo diff $resfile $reffile
res=0
diff $resfile $reffile || res=$?
if [ $res -eq 0 ]; then
  echo TEST PASS
  true
else
  echo TEST FAILED: $resfile and $reffile differ
  false
fi

