#!/bin/sh

sh ./prepare.sh

./bulk.exe

time python3 simple.py
#time python3 simple2.py

result=output/res.txt
reference=ref.txt

echo diff $result $reference
res=0
diff $result $reference || res=$?
if [ $res -eq 0 ]; then
  echo Test PASS
  true
else
  echo Test FAILED: $result and $reference differ
  false
fi

