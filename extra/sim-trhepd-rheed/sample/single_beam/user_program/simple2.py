import numpy as np

import py2dmat
import py2dmat.algorithm.min_search
import sim_trhepd_rheed

params = {
    "base": {
        "dimension": 3,
        "output_dir": "output",
    },
    "solver": {
        "run_scheme": "subprocess",
        "generate_rocking_curve": True,
        "config": {
            "cal_number": [1],
        },
        "param": {
            "string_list": ["value_01", "value_02", "value_03"],
        },
        "reference": {
            "path": "experiment.txt",
            "exp_number": [1],
        },
        "post": {
            "normalization": "TOTAL",
        },
    },
    "algorithm": {
        "label_list": ["z1", "z2", "z3"],
        "param": {
            "min_list": [ 0.0, 0.0, 0.0 ],
            "max_list": [ 10.0, 10.0, 10.0 ],
            "initial_list": [ 5.25, 4.25, 3.50],
        },
    },
}

info = py2dmat.Info(params)

solver = sim_trhepd_rheed.Solver(info)

runner = py2dmat.Runner(solver, info)

alg = py2dmat.algorithm.min_search.Algorithm(info, runner)

alg.main()
