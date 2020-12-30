sh prepare.sh

time mpiexec --oversubscribe -np 4 python3 ../../../src/py2dmat_main.py input.toml

echo diff output/best_result.txt ref.txt
res=0
diff output/best_result.txt ref.txt || res=$?
if [ $res -eq 0 ]; then
  echo TEST PASS
  true
else
  echo TEST FAILED: output/best_result.txt and ref.txt differ
  false
fi

