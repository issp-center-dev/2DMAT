sh prepare.sh

./bulk.exe

time mpiexec -np 2 python3 ../../../src/2dmat/mapper_mpi.py \
  --dimension 3 \
  --llist "z1" "z2" "z3" \
  --slist "value_01" "value_02" "value_03" \
  --efirst 1 \
  --elast 70 \
  --cfirst 5 \
  --clast 74 \
  --dmax 7.0 \
  --rnumber 2 \
  | tee log.txt

echo diff ColorMap.txt ref_ColorMap.txt
diff ColorMap.txt ref_ColorMap.txt
if [ $? == 0 ]; then
  echo TEST PASS
else
  echo TEST FAILED: ColorMap.txt and ref_ColorMap.txt differ
fi

