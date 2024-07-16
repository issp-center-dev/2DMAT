#!/bin/sh

sh ./prepare.sh

./bulk.exe

time py2dmat-sim-trhepd-rheed input.toml | tee log.txt

echo diff output/res.txt ref.txt
res=0
diff output/res.txt ref.txt || res=$?
if [ $res -eq 0 ]; then
  echo Test PASS
  true
else
  echo Test FAILED: res.txt and ref.txt differ
  false
fi
