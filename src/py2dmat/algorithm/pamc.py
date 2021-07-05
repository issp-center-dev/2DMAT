from typing import List, Dict

from io import open
import copy
import time
import itertools

import numpy as np

import py2dmat
import py2dmat.exception
import py2dmat.algorithm.montecarlo
import py2dmat.util.separateT
import py2dmat.util.resampling

from pprint import pprint


class Algorithm(py2dmat.algorithm.montecarlo.AlgorithmBase):
    """Population annealing Monte Carlo

    Attributes
    ==========
    x: np.ndarray
        current configuration
    fx: np.ndarray
        current "Energy"
    T: float
        current "Temperature"
    istep: int
        current step (or, the number of calculated energies)
    best_x: np.ndarray
        best configuration
    best_fx: float
        best "Energy"
    best_istep: int
        index of best configuration
    comm: MPI.comm
        MPI communicator
    nreplica: int
        The number of replicas (= the number of procs)
    rank: int
        MPI rank
    Ts: list
        List of temperatures
    Tindex: int
        Temperature index
    T2rep: np.ndarray
        Mapping from temperature index to replica index
    exchange_direction: bool
    """

    x: np.ndarray
    xmin: np.ndarray
    xmax: np.ndarray
    xunit: np.ndarray

    numsteps: int
    numsteps_resampling: int

    fx: np.ndarray
    istep: int
    nreplica: int
    Ts: np.ndarray
    Tindex: int

    logQ: np.ndarray

    walker_ancestors: np.ndarray
    populations: np.ndarray
    family_lo: int
    family_hi: int

    Fmeans: np.ndarray
    Ferrs: np.ndarray
    nmeans: np.ndarray
    nstds: np.ndarray

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        time_sta = time.perf_counter()

        info_pamc = info.algorithm["pamc"]
        nwalkers = info_pamc.get("nreplica_per_proc", 1)

        super().__init__(info=info, runner=runner, nwalkers=nwalkers)

        if self.mpicomm is None:
            msg = "ERROR: algorithm.pamc requires mpi4py, but mpi4py cannot be imported"
            raise ImportError(msg)

        self.nreplica = self.mpisize * self.nwalkers
        self.initial_nreplica = self.nreplica

        numsteps = info_pamc.get("numsteps", 0)
        numsteps_resampling = info_pamc.get("numsteps_resampling", 0)
        numT = info_pamc.get("Tnum", 0)

        oks = np.array([numsteps, numsteps_resampling, numT]) > 0
        if np.count_nonzero(oks) != 2:
            msg = "ERROR: Two of 'numsteps', 'numsteps_resampling', and 'Tnum' should be positive in the input file\n"
            msg += "  numsteps = {numsteps}\n"
            msg += "  numsteps_resampling = {numsteps_resampling}\n"
            msg += "  Tnum = {numT}\n"
            raise py2dmat.exception.InputError(msg)

        if numsteps <= 0:
            self.numsteps_for_T = np.full(numT, numsteps_resampling)
        elif numsteps_resampling <= 0:
            nr = numsteps // numT
            self.numsteps_for_T = np.full(numT, nr)
            rem = numsteps - nr * numT
            if rem > 0:
                self.numsteps_for_T[0 : (rem - 1)] += 1
        else:
            ss: List[int] = []
            while numsteps > 0:
                if numsteps > numsteps_resampling:
                    ss.append(numsteps_resampling)
                    numsteps -= numsteps_resampling
                else:
                    ss.append(numsteps)
                    numsteps = 0
            self.numsteps_for_T = np.array(ss)
            numT = len(ss)

        self.Ts = self.read_Ts(info_pamc, numT=numT)
        self.Ts[::-1].sort()  # sort in descending
        self.Tindex = 0

        self.logQ = np.zeros(numT)

        self.Fmeans = np.zeros(numT)
        self.Ferrs = np.zeros(numT)
        self.nmeans = np.zeros(numT)
        self.nstds = np.zeros(numT)

        self.populations = np.zeros((numT, self.nwalkers), dtype=int)
        self.family_lo = self.nwalkers * self.mpirank
        self.family_hi = self.nwalkers * (self.mpirank+1)
        self.walker_ancestors = np.arange(self.family_lo, self.family_hi)
        self.fix_nwalkers = info_pamc.get("fix_num_walkers", True)

        time_end = time.perf_counter()
        self.timer["init"]["total"] = time_end - time_sta

    def _run(self) -> None:
        rank = self.mpirank

        beta = 1.0 / self.Ts[self.Tindex]

        self.istep = 0

        # first step
        self._evaluate()

        file_trial = open("trial_T0.txt", "w")
        file_result = open("result_T0.txt", "w")
        self._write_result_header(file_result)
        self._write_result(file_result)
        self._write_result_header(file_trial)
        self._write_result(file_trial)
        file_trial.close()
        file_result.close()
        self.istep += 1

        minidx = np.argmin(self.fx)
        self.best_x = copy.copy(self.x[minidx, :])
        self.best_fx = np.min(self.fx[minidx])
        self.best_istep = 0
        self.best_iwalker = 0

        for Tindex, T in enumerate(self.Ts):
            self.Tindex = Tindex
            beta = 1.0 / T

            with open(f"ancestors_T{Tindex}.txt", "w") as f:
                f.write("# iwalker ancestor\n")
                for iwalker, ancestor in enumerate(self.walker_ancestors):
                    f.write(f"{iwalker} {ancestor}\n")

            if Tindex > 0:
                file_trial = open(f"trial_T{Tindex}.txt", "w")
                file_result = open(f"result_T{Tindex}.txt", "w")
                self._write_result_header(file_result)
                self._write_result(file_result)
            else:
                file_trial = open(f"trial_T{Tindex}.txt", "a")
                file_result = open(f"result_T{Tindex}.txt", "a")

            for _ in range(self.numsteps_for_T[Tindex]):
                self.local_update(beta, file_trial, file_result)
                self.istep += 1
            file_trial.close()
            file_result.close()

            if Tindex < len(self.Ts) - 1:
                time_sta = time.perf_counter()
                self._resample()
                time_end = time.perf_counter()
                self.timer["run"]["resampling"] += time_end - time_sta
            else:
                res = self._gather_information()
                self._save_stats(res)

        file_result.close()
        file_trial.close()
        if self.mpisize > 1:
            self.mpicomm.barrier()
        print("complete main process : rank {:08d}/{:08d}".format(rank, self.mpisize))

    def _gather_information(self) -> Dict[str, np.ndarray]:
        """

        Returns
        -------
        res: Dict[str, np.ndarray]
            key-value corresponding is the following

            - fxs
                - objective function of each walker over all processes
            - ns
                - number of walkers in each process
            - ancestors
                - ancestor (origin) of each walker
        """
        res = {}
        if self.mpisize > 1:
            fxs_list = self.mpicomm.allgather(self.fx)
            # transform a jagged array to a vector
            res["fxs"] = np.array(list(itertools.chain.from_iterable(fxs_list)))
            res["ns"] = np.array([len(fs) for fs in fxs_list], dtype=int)
            ancestors_list = self.mpicomm.allgather(self.walker_ancestors)
            res["ancestors"] = np.array(
                list(itertools.chain.from_iterable(ancestors_list)),
                dtype=int
            )
        else:
            res["fxs"] = self.fx
            res["ns"] = np.array([self.nwalkers], dtype=int)
            res["ancestors"] = self.walker_ancestors
        return res

    def _save_stats(self, info: Dict[str, np.ndarray], bprint: bool = True) -> None:
        fxs = info["fxs"]
        ns = info["ns"]
        fm = np.mean(fxs)
        ferr = np.sqrt(np.var(fxs) / fxs.size)
        self.Fmeans[self.Tindex] = fm
        self.Ferrs[self.Tindex] = ferr

        nm = np.mean(ns)
        nstd = np.std(ns)
        self.nmeans[self.Tindex] = nm
        self.nstds[self.Tindex] = nstd

        if self.Tindex == len(self.Ts)-1:
            # last step
            dbeta = 0.0
        else:
            dbeta = (1.0 / self.Ts[self.Tindex + 1]) - (1.0 / self.Ts[self.Tindex])
        fx_base = np.min(fxs)
        logQ = np.log(np.mean(np.exp(-dbeta * (fxs-fx_base)))) - dbeta * fx_base
        self.logQ[self.Tindex] = logQ
        mbF = np.sum(self.logQ[0:self.Tindex])

        if bprint and self.mpirank == 0:
            print(f"{self.Ts[self.Tindex]} {fm} {ferr} {nm} {nstd} {mbF} {logQ}")

    def _resample(self) -> None:
        res = self._gather_information()
        self._save_stats(res)
        fxs = res["fxs"]
        if self.fix_nwalkers:
            self._resample_fixed(fxs)
        else:
            self._resample_varied(fxs)

    def _resample_varied(self, fxs: np.ndarray) -> None:
        newbeta = 1.0 / self.Ts[self.Tindex + 1]

        # avoid over/under-flow
        fxs_base = np.min(fxs)
        weights = np.exp((-newbeta) * (fxs - fxs_base))
        weights_sum = np.sum(weights)
        expected_numbers = (
            self.initial_nreplica * np.exp((-newbeta) * (self.fx - fxs_base)) / weights_sum
        )
        next_numbers = self.rng.poisson(expected_numbers)

        if self.iscontinuous:
            new_x = []
            new_fx = []
            new_ancestors = []
            for iwalker in range(self.nwalkers):
                for _ in range(next_numbers[iwalker]):
                    new_x.append(self.x[iwalker, :])
                    new_fx.append(self.fx[iwalker])
                    new_ancestors.append(self.walker_ancestors[iwalker])
            self.x = np.array(new_x)
            self.fx = np.array(new_fx)
            self.walker_ancestors = np.array(new_ancestors)
        else:
            new_inodes = []
            new_fx = []
            new_ancestors = []
            for iwalker in range(self.nwalkers):
                for _ in range(next_numbers[iwalker]):
                    new_inodes.append(self.inodes[iwalker])
                    new_fx.append(self.fx[iwalker])
                    new_ancestors.append(self.walker_ancestors[iwalker])
            self.inode = np.array(new_inodes)
            self.fx = np.array(new_fx)
            self.walker_ancestors = np.array(new_ancestors)
            self.x = self.node_coordinates[self.inode, :]
        self.nwalkers = np.sum(next_numbers)

    def _resample_fixed(self, fxs: np.ndarray) -> None:
        newbeta = 1.0 / self.Ts[self.Tindex + 1]
        fxs_base = np.min(fxs)
        weights = np.exp((-newbeta) * (fxs - fxs_base))
        resampler = py2dmat.util.resampling.WalkerTable(weights)
        new_index = resampler.sample(self.rng, self.nwalkers)

        if self.iscontinuous:
            if self.mpisize > 1:
                xs = np.zeros((self.mpisize, self.nwalkers, self.dimension))
                self.mpicomm.Allgather(self.x, xs)
                xs = xs.reshape(self.nreplica, self.dimension)
                ancestors = np.array(
                    self.mpicomm.allgather(self.walker_ancestors)
                ).flatten()
            else:
                xs = self.x
                ancestors = self.walker_ancestors
            self.x = xs[new_index, :]
            self.walker_ancestors = ancestors[new_index]
        else:
            if self.mpisize > 1:
                inodes = np.array(self.mpicomm.allgather(self.inode)).flatten()
                ancestors = np.array(
                    self.mpicomm.allgather(self.walker_ancestors)
                ).flatten()
            else:
                inodes = self.inode
                ancestors = self.walker_ancestors
            self.inode = inodes[new_index]
            self.walker_ancestors = ancestors[new_index]
            self.x = self.node_coordinates[self.inode, :]

    def _prepare(self) -> None:
        self.timer["run"]["submit"] = 0.0
        self.timer["run"]["resampling"] = 0.0

    def _post(self) -> None:
        for name in ("result", "trial"):
            with open(self.proc_dir / f"{name}.txt", "w") as fout:
                self._write_result_header(fout)
                for Tindex in range(len(self.Ts)):
                    with open(self.proc_dir / f"{name}_T{Tindex}.txt") as fin:
                        for line in fin:
                            if line.startswith("#"):
                                continue
                            fout.write(line)
        best_fx = self.mpicomm.gather(self.best_fx, root=0)
        best_x = self.mpicomm.gather(self.best_x, root=0)
        best_istep = self.mpicomm.gather(self.best_istep, root=0)
        best_iwalker = self.mpicomm.gather(self.best_iwalker, root=0)
        if self.mpirank == 0:
            best_rank = np.argmin(best_fx)
            with open("best_result.txt", "w") as f:
                f.write(f"nprocs = {self.nreplica}\n")
                f.write(f"rank = {best_rank}\n")
                f.write(f"step = {best_istep[best_rank]}\n")
                f.write(f"walker = {best_iwalker[best_rank]}\n")
                f.write(f"fx = {best_fx[best_rank]}\n")
                for label, x in zip(self.label_list, best_x[best_rank]):
                    f.write(f"{label} = {x}\n")
            print("Best Result:")
            print(f"  rank = {best_rank}")
            print(f"  step = {best_istep[best_rank]}")
            print(f"  walker = {best_iwalker[best_rank]}")
            print(f"  fx = {best_fx[best_rank]}")
            for label, x in zip(self.label_list, best_x[best_rank]):
                print(f"  {label} = {x}")

            mbF = 0.0
            with open("fx.txt", "w") as f:
                for i in range(len(self.Ts)):
                    if i > 0:
                        mbF += self.logQ[i-1]
                    f.write(f"{self.Ts[i]}")
                    f.write(f" {self.Fmeans[i]} {self.Ferrs[i]}")
                    f.write(f" {self.nmeans[i]} {self.nstds[i]}")
                    f.write(f" {mbF} {self.logQ[i]}")
                    f.write("\n")
