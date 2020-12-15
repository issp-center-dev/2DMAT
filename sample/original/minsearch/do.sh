sh ./prepare.sh

time python3 ../../../src/py2dmat/main.py input.toml | tee log.txt
tail -n3 log.txt > res.dat

echo diff res.dat ref.dat
diff res.dat ref.dat
if [ $? == 0 ]; then
  echo Test PASS
else
  echo Test FAILED: res.dat and ref.dat differ
fi
