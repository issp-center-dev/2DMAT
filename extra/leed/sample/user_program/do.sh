#!/bin/sh

sh ./prepare.sh

time python3 ./simple.py
#time python3 ./simple2.py


result=output/res.txt
reference=ref.txt

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

