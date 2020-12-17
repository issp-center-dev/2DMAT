sh ./prepare.sh

./bulk.exe

time python3 ../../../src/2dmat/main.py input.toml | tee log.txt
tail -n3 log.txt > res.dat

echo diff res.dat ref.dat
res=0
diff res.dat ref.dat || res=$?
if [ $res -eq 0 ]; then
  echo Test PASS
  true
else
  echo Test FAILED: res.dat and ref.dat differ
  false
fi
