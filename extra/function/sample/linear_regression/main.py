import numpy as np

import py2dmat
#import py2dmat.algorithm.mapper_mpi as mapper
import py2dmat.algorithm.min_search as min_search
from function import LinearRegression
import py2dmat.domain

data = np.loadtxt("data.txt")

info = py2dmat.Info.from_file("input.toml")
solver = LinearRegression(info, xdata=data[:,0], ydata=data[:,1])
runner = py2dmat.Runner(solver, info)

region = py2dmat.domain.Region(param={"min_list": [-1,-1,-1], "max_list": [1,1,1]})

alg = min_search.Algorithm(info, runner, region)
alg.main()
