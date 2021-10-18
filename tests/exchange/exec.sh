rm -rf output

# time mpiexec --oversubscribe -np 2 python3 ../../src/py2dmat_main.py input.toml
mpiexec -np 1 python3 ../../src/py2dmat_main.py input2.toml
