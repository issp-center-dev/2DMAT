time python3 ./minsearch_rev.py \
--dimension 3 \
--llist "z1"  "z2"  "z3" \
--slist 'value_01' 'value_02' 'value_03' \
--inilist 5.25 4.25 3.50 \
--unit_list 1.0 1.0 1.0 \
--minlist -100.0 -100.0 -100.0 \
--maxlist 100.0 100.0 100.0 \
--initial_scale_list 0.25 0.25 0.25 \
--norm "TOTAL" \
--rfactor "A" \
--efirst 1 \
--elast 70 \
--cfirst 5 \
--clast 74 \
--dmax 7.0 \
--rnumber  2 \
--omega 0.5  \
--xtol 0.0001 \
--ftol 0.0001 \
| tee log.txt

