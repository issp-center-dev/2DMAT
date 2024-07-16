import py2dmat
import py2dmat.algorithm.min_search
import leed

params = {
    "base": {
        "dimension": 2,
        "output_dir": "output",
    },
    "solver": {
        "config": {
            "path_to_solver": "./leedsatl/satl2.exe",
        },
        "reference": {
            "path_to_base_dir": "./base",
        },
    },
    "algorithm": {
        "label_list": ["z1", "z2"],
        "param": {
            "min_list": [-0.5, -0.5],
            "max_list": [0.5, 0.5],
            "initial_list": [-0.1, 0.1],
        },
         
    },
}

info = py2dmat.Info(params)

solver = leed.Solver(info)
runner = py2dmat.Runner(solver, info)
alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
alg.main()
