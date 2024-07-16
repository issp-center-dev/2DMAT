#!/bin/sh

sh prepare.sh

time py2dmat-sxrd input.toml

echo diff output/res.txt ref_res.txt
res=0
diff output/res.txt ref_res.txt || res=$?
if [ $res -eq 0 ]; then
  echo TEST PASS
  true
else
  echo TEST FAILED: res.txt and ref_res.txt differ
  false
fi
