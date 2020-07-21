import sys
import os
from mpi4py import MPI
import numpy as np

class MPI_params:
    def __init__(self):
        self.nprocs_parent = None
        self.nprocs_per_parent = 1

    @classmethod
    def from_dict(cls, d):
        """
           Read information from dictionary

           Parameters
           ----------
           d: dict
               Dictionary including parameters for replica exchange Monte Carlo method

           Returns
           -------
           params: MPI_params object
               self
        """
        params = cls()
        params.nprocs_parent = d["nprocs_parent"]
        params.nprocs_per_parent = d["nprocs_per_parent"]
        return params

    @classmethod
    def from_toml(cls, fname):
        """
        Read information from toml file

        Parameters
        ----------
        f: str
            The name of an input toml file

        Returns
        -------
        DFTParams: MPI_params object
            self
        """
        import toml
        return cls.from_dict(toml.load(fname))

def MPI_Init(mpi_params):
    """

    mpi_params: MPI_params

    Returns:
    -------
    comm: comm world
        MPI communicator
    """

    nprocs_parent = mpi_params.nprocs_parent
    commworld = MPI.COMM_WORLD
    worldrank = commworld.Get_rank()
    worldprocs = commworld.Get_size()

    if worldprocs < nprocs_parent:
        if worldrank == 0:
            print("ERROR! Please run with at least as many MPI processes as the number of parent processes")
        sys.exit(1)

    if worldprocs > nprocs_parent:
        if worldrank == 0:
            print(
                "Setting number of parent processes smaller than MPI processes; I hope you"
                + " know what you're doing..."
            )
            sys.stdout.flush()
        if worldrank >= nprocs_parent:
            # belong to comm that does nothing
            comm = commworld.Split(color=1, key=worldrank)
            comm.Free()
            sys.exit()  # Wait for MPI_finalize
        else:
            comm = commworld.Split(color=0, key=worldrank)
    else:
        comm = commworld
    return comm



class Calculator_base(object):
    def __init__(self, comm, mpi_params, Algorithm, subdirs=True):
        self.comm = comm
        self.rank = self.comm.Get_rank()
        self.procs = self.comm.Get_size()
        self.nprocs_parent = mpi_params["nprocs_parent"]
        #myconfig = configs[self.rank]
        #self.mycalc = Algorithm(Solver, myconfig)
        self.mycalc = Algorithm
        self.subdirs = subdirs

    def run(self, run_info):
        if self.subdirs:
            # make working directory for this rank
            try:
                os.mkdir(str(self.rank))
            except FileExistsError:
                pass
            os.chdir(str(self.rank))
        observables = self.mycalc.run(run_info)
        if self.subdirs:
            os.chdir("../")
        obs_buffer = np.empty([self.procs, len(observables)])
        self.comm.Allgather(observables, obs_buffer)
        return obs_buffer