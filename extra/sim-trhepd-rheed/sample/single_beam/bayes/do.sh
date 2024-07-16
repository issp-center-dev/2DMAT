#!/bin/sh

sh prepare.sh

./bulk.exe

time py2dmat-sim-trhepd-rheed input.toml

echo diff output/BayesData.txt ref_BayesData.txt
res=0
diff output/BayesData.txt ref_BayesData.txt || res=$?
if [ $res -eq 0 ]; then
  echo TEST PASS
  true
else
  echo TEST FAILED: BayesData.txt.txt and ref_BayesData.txt.txt differ
  false
fi

