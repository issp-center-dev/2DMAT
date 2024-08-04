Adding functions
================================

In this tutorial, we describe the procedure how to define a new function and perform analyses.
As an example, we will introduce Booth function given below:

.. math::

   f(x,y) = (x + 2 y - 7) ^2 + (2 x + y - 5) ^2

The minimum value of this function is :math:`f(1,3) = 0`.


Location of the sample files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample files are located in ``sample/booth``.
The following files are stored in the folder.

- ``booth.py``

  Source file of the direct problem solver that evaluates Booth function.

- ``main.py``

  Source file of the main program. This program reads ``input.toml`` for the parameters.

- ``input.toml``

  Input parameter file for ``main.py``.

- ``do.sh``

  Script file for running this tutorial.

The following sections describe these files and then show the actual calculation results.


Description of main program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``booth.py``, a class for the direct problem solver is defined using 2DMAT-Functions module that evaluates Booth function.
The entire program is shown as follows:

.. code-block:: python

    import numpy as np
    import py2dmat.extra.function

    class Booth(py2dmat.extra.function.Solver):
        def evaluate(self, xs: np.ndarray, args=()):
            assert xs.shape[0] == 2
            x, y = xs
            fx = (x + 2 * y - 7)**2 + (2 * x + y - 5)**2
            return fx

First, the required modules are imported.
``py2dmat.extra.function`` corresponds to 2DMAT-Functions module.

Next, ``Booth`` class is defined as derived from ``Solver`` class of 2DMAT-Functions.
The direct problem solver class must have a method called ``evaluate`` which have the form ``evaluate(self, xs, args) -> float``.
The arguments of this method are:
``xs`` of ``numpy.ndarray`` type for the parameter values, and ``args`` of ``Tuple`` type for the optional data that consists of the step count ``step`` and the iteration count ``set`` used in the class accordingly.

``main.py`` is a simple program that performs analyses using the Booth class.

.. code-block:: python

    import numpy as np

    import py2dmat
    import py2dmat.algorithm.min_search as min_search
    from booth import Booth

    info = py2dmat.Info.from_file("input.toml")
    solver = Booth(info)
    runner = py2dmat.Runner(solver, info)

    alg = min_search.Algorithm(info, runner)
    alg.main()


In the program, the instances of the classes are created.

- ``py2dmat.Info`` class

  This class is for storing the parameters.
  An instance is created by calling a class method ``from_file`` with a path to TOML file as an argument.

- ``Booth`` class

  Booth class is imported from ``booth.py`` as introduced above, and is instantiated.

- ``py2dmat.Runner`` class

  This class is for connecting the direct problem solver and the inverse problem algorithm.
  An instance is created by passing an instance of Solver class and an instance of Info class.

- ``py2dmat.algorithm.min_search.Algorithm`` class

  This class is for the inverse problem algorithm.
  In this tutorial, we use ``min_search`` module that implements the optimization by Nelder-Mead method.
  An instance is created by passing an instance of Runner class.

After creating the instances of Solver, Runner, and Algorithm in this order, we invoke ``main()`` method of the Algorithm class to start analyses.


Input files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An example of the input parameter file ``input.toml`` is shown below.

.. code-block:: toml

    [base]
    dimension = 2
    output_dir = "output"

    [algorithm]
    seed = 12345

    [algorithm.param]
    max_list = [6.0, 6.0]
    min_list = [-6.0, -6.0]
    num_list = [31, 31]

    [solver]

    [runner]
    [runner.log]
    interval = 20


Calculation execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, move to the folder where the sample files are located.

.. code-block::

   $ cd sample/booth

Run the main program. The computation time will take only a few seconds on a normal PC.

.. code-block::

   $ python3 main.py | tee log.txt

The standard output will look as follows.

.. code-block::

    Optimization terminated successfully.
             Current function value: 0.000000
             Iterations: 44
             Function evaluations: 82
    iteration: 44
    len(allvecs): 45
    step: 0
    allvecs[step]: [ 5.15539311 -2.20349335]
    step: 1
    allvecs[step]: [ 4.65539311 -1.82849335]
    step: 2
    allvecs[step]: [ 4.40539311 -1.26599335]
    step: 3
    allvecs[step]: [ 3.28039311 -0.73474335]
    step: 4
    allvecs[step]: [2.21789311 0.65588165]
    step: 5
    allvecs[step]: [2.21789311 0.65588165]
    ...
    step: 42
    allvecs[step]: [0.99997645 3.00001226]
    step: 43
    allvecs[step]: [0.99997645 3.00001226]
    end of run
    Current function value: 1.2142360244883376e-09
    Iterations: 44
    Function evaluations: 82
    Solution:
    x1 = 0.9999764520155436
    x2 = 3.000012263854959

``x1`` and ``x2`` are the candidate parameters at each step.
The final estimated parameters will be written in ``output/res.dat``.
In the current case, the following result will be obtained:

.. code-block::

    fx = 1.2142360244883376e-09
    x1 = 0.9999764520155436
    x2 = 3.000012263854959

It is found that the minimum has been reproduced.

Note that ``do.sh`` is available as a script for batch calculation.
