try:
    from mpi4py import MPI
    Comm = MPI.Comm

    __comm = MPI.COMM_WORLD
    __size = __comm.size
    __rank = __comm.rank

    def comm() -> MPI.Comm:
        return __comm

    def size() -> int:
        return __size

    def rank() -> int:
        return __rank

    def enabled() -> bool:
        return True


except ImportError:
    Comm = None

    def comm() -> None:
        return None

    def size() -> int:
        return 1

    def rank() -> int:
        return 0

    def enabled() -> bool:
        return False
