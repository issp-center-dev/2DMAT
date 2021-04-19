mpiexec -np 4 --oversubscribe python3 ../../../src/py2dmat_main.py input.toml
python3 ../../../script/separateT.py output

for i in 0 1 2 3; do
  python3 ../plot_himmel.py --xcol=3 --ycol=4 --skip=20 --format="o" --output=output/res_T${i}.png output/result_T${i}.txt
done
