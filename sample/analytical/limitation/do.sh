mpiexec -np 10 --oversubscribe python3 ../../../src/py2dmat_main.py input.toml

python3 hist2d_limitation_sample.py -p 10 -i input.toml -b 0.1
