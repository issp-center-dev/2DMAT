Input file
===========================

As the input file format, `TOML <https://toml.io/ja/>`_ format is used.
The input file consists of the following four sections.

- ``base``

  - Specify the basic parameters about ``py2dmat`` . 

- ``solver``

  - Specify the prarameters about ``Solver`` .

- ``algorithm``

  - Specify the prarameters about ``Algorithm`` .

- ``runner``

  - Specify the parameters about ``Runner`` .


[``base``] section
************************

- ``dimension``

  Format: Integer

  Description: Dimension of the search space (number of parameters to search)

- ``root_dir``

  Format: string (default: The directory where the program was executed)

  Description: Name of the root directory. The origin of the relative paths to input files.

- ``output_dir``

  Format: string (default: The directory where the program was executed)

  Description: Name of the directory to output the results.

[``solver``] section
************************

The ``name`` determines the type of solver. Each parameter is defined for each solver.


- ``name``

  Format: String

  Description: Name of the solver. The following solvers are available.

    - ``sim-trhepd-rheed`` : Solver to calculate Total-reflection high energy positron diffraction (TRHEPD) or Reflection High Energy Electron Diffraction (RHEED) intensities.

    - ``analytical`` : Solver to provide analytical solutions (mainly used for testing).

See :doc:`solver/index` for details of the various solvers and their input/output files.

.. _input_parameter_algorithm:

[``algorithm``] section
*******************************

The ``name`` determines the type of algorithm. Each parameter is defined for each algorithm.

- ``name``

  Format: String

  Description: Algorithm name. The following algorithms are available.

    - ``minsearch`` : Minimum value search using Nelder-Mead method

    - ``mapper`` : Grid search

    - ``exchange`` :  Replica Exchange Monte Carlo

    - ``bayes`` :  Bayesian optimization

- ``seed``

  Format: Integer

  Description: A parameter to specify seeds of the pseudo-random number generator used for random generation of initial values, Monte Carlo updates, etc.
        For each MPI process, the value of ``seed + mpi_rank * seed_delta`` is given as seeds.
        If omitted, the initialization is done by  `the Numpy's prescribed method <https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng>`_.


- ``seed_delta``

  Format: Integer (default: 314159)

  Description: A parameter to calculate the seed of the pseudo-random number generator for each MPI process.
        For details, see the description of ``seed``.

See :doc:`algorithm/index` for details of the various algorithms and their input/output files.

[``runner``] section
************************

This section sets the configuration of ``Runner``, which bridges ``Algorithm`` and ``Solver``.
It has a subsection ``log``

[``log``] section
^^^^^^^^^^^^^^^^^^^^^^^^
Settings related to logging of solver calls.

- ``filename``

  Format: String (default: "runner.log")

  Description: Name of log file.

- ``interval``

  Format: Integer (default: 0)

  Description: The log will be written out every time solver is called ``interval`` times.
        If the value is less than or equal to 0, no log will be written.

- ``write_result``

  Format: Boolean (default: false)

  Description: Whether to record the output from solver.

- ``write_input``

  Format: Boolean (default: false)

  Description: Whether to record the input to solver.
