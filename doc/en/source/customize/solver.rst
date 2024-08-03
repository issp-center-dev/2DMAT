``Solver``
================================

``Solver`` is a class that describes the direct problem, providing a method ``evaluate`` that returns the value of the objective function from the input parameters.
It is defined as a derived class of ``py2dmat.solver.SolverBase``:

.. code-block:: python

    import py2dmat

    class Solver(py2dmat.solver.SolverBase):
        pass

The following methods should be defined.

- constructor

  Solver class should have a constructor that takes an ``Info`` class object as an argument:

  .. code-block:: python

     def __init__(self, info: py2dmat.Info):
         pass

  - It is required to call the constructor of the base class.

    - ``super().__init__(info)``    

  - The constructor of ``SolverBase`` defines the following instance variables.

    - ``self.root_dir: pathlib.Path`` : Root directory

      - use ``info.base["root_dir"]``

    - ``self.output_dir: pathlib.Path`` : Output directory

      - use ``info.base["output_dir"]``

    - ``self.proc_dir: pathlib.Path`` : Working directory for each MPI process

      - as ``self.output_dir / str(mpirank)``

  - ``work_dir`` may be defined to be used for workspace of the solver.
	  
  - See the input parameter ``info`` and save as instance variables.

- ``evaluate`` method

  The form of ``evaluate`` method should be as follows:

  .. code-block:: python

     def evaluate(self, x, args=(), nprocs=1, nthreads=1) -> float:
         pass

  This method evaluates the objective function at a given parameter value `x` and returns the result. It takes the following arguments:

  - ``x: np.ndarray``

    The parameter value in :math:`N` dimensional vector of numpy.ndarray type.

  - ``args: Tuple = ()``

    The additional arguments passed from the Algorithm in the form of a Tuple of two integers.
    One is the step count that corresponds to the Monte Carlo steps for MC type algorithms, or the index of the grid point for grid search algorithm.
    The other is the set number that represents :math:`n`-th iteration.

  - ``nprocs: int = 1``

  - ``nthreads: int = 1``

    The number of processes and threads that specify how to run the solver in MPI/thread parallelisation. In the current version, ``nprocs=1`` and ``nthreads=1`` are accepted.
  
  The ``evaluate`` method returns the value of the objective function as a float number.
