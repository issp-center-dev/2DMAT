#!/usr/bin/env python3

import os.path

def load_best(filename="best_result.txt"):
    res = {}
    with open(filename) as f:
        for line in f:
            words = line.split("=")
            res[words[0].strip()] = words[1].strip()
    return res


param = load_best()
nprocs = int(param["nprocs"])

Ts = []
results = {}
dim = 0
for rank in range(nprocs):
    with open(os.path.join(str(rank), "result.txt")) as f:
        f.readline()
        line = f.readline()
        words = line.split()
        T = float(words[1])
        Ts.append(T)
        results[T] = []
        dim = len(words) - 3

for rank in range(nprocs):
    with open(os.path.join(str(rank), "result.txt")) as f:
        f.readline()
        for line in f:
            words = line.split()
            T = float(words[1])
            fx = float(words[2])
            res = [float(words[i+3]) for i in range(dim)]
            results[T].append((fx, res))

for i, T in enumerate(Ts):
    with open(f"result_T{i}.dat", "w") as f:
        f.write(f"# T = {T}\n")
        for fx, res in results[T]:
            f.write(f"{fx} ")
            for x in res:
                f.write(f"{x} ")
            f.write("\n")
