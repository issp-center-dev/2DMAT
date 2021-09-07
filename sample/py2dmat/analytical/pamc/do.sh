python3 ../../../../src/py2dmat_main.py input.toml

for i in `seq 0 10`; do
  python3 ../plot_himmel.py --xcol=4 --ycol=5 --skip=20 --format="o" --output=output/res_T${i}.png output/0/result_T${i}.txt
done
