sh prepare.sh

./bulk.exe

time mpiexec -np 2 python3 ../../../src/2dmat/mapper_mpi.py input.toml

echo diff ColorMap.txt ref_ColorMap.txt
diff ColorMap.txt ref_ColorMap.txt
if [ $? == 0 ]; then
  echo TEST PASS
else
  echo TEST FAILED: ColorMap.txt and ref_ColorMap.txt differ
fi

