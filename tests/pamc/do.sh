rm -rf output

time mpiexec --oversubscribe -np 2 python3 -m mpi4py ../../src/py2dmat_main.py input.toml

resfile=output/best_result.txt

echo diff $resfile ref.txt
res=0
diff $resfile ref.txt || res=$?
if [ $res -eq 0 ]; then
  echo TEST PASS
  true
else
  echo TEST FAILED: $resfile and ref.txt differ
  false
fi

