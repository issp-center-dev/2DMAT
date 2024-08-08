#!/bin/sh

#CMD=py2dmat-leed
CMD="python3 ../../src/main.py"

sh ./prepare.sh

time mpiexec -np 4 $CMD input.toml


result=output/ColorMap.txt
reference=ref_ColorMap.txt

echo diff $result $reference
res=0
diff $result $reference || res=$?
if [ $res -eq 0 ]; then
  echo TEST PASS
  true
else
  echo TEST FAILED: $result and $reference differ
  false
fi

