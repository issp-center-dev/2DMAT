time mpiexec -np 1 python ../../../src/original/mapper_mpi_py2.py \
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
