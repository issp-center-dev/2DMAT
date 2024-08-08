Optimization by population annealing
================================================

This tutorial describes how to estimate the optimization problem of Himmelblau function by using the population annealing Monte Carlo method (PAMC).

Sample files
~~~~~~~~~~~~~~~~~~

Sample files are available from ``sample/analytical/pamc`` .
This directory includes the following files:

- ``input.toml``

  The input file of py2dmat

- ``plot_result_2d.py``

  Program to visualize the results
  
- ``do.sh``

  Script files for running this tutorial


Input files
~~~~~~~~~~~~~

This subsection describes the input file.
For details, see the input file section of the manual.

.. code-block::

    [base]
    dimension = 2
    output_dir = "output"

    [solver]
    name = "analytical"
    function_name = "himmelblau"

    [runner]
    [runner.log]
    interval = 20

    [algorithm]
    name = "pamc"
    seed = 12345

    [algorithm.param]
    max_list = [6.0, 6.0]
    min_list = [-6.0, -6.0]
    unit_list = [0.3, 0.3]

    [algorithm.pamc]
    bmin = 0.0
    bmax = 200.0
    Tnum = 21
    Tlogspace = false
    numsteps_annealing = 100
    nreplica_per_proc = 100

In the following, we will briefly describe this input file.
For details, see the manual of :doc:`../algorithm/pamc`.

The contents of ``[base]``, ``[solver]``, and ``[runner]`` sections are the same as those for the search by the Nelder-Mead method (``minsearch``).

``[algorithm]`` section specifies the algorithm to use and its settings.

- ``name`` is the name of the algorithm you want to use In this tutorial we will use the population annealing Monte Carlo (PAMC) algorithm, so specify ``pamc``.

- ``seed`` is the seed that a pseudo-random number generator uses.

``[algorithm.param]`` section sets the parameter space to be explored.

- ``min_list`` is a lower bound and ``max_list`` is an upper bound.

- ``unit_list`` is step length in one MC update (deviation of Gaussian distribution).

``[algorithm.pamc]`` section sets the parameters for PAMC.

- ``numsteps_annealing`` is the number of interval steps between temperature decreasing.

- ``bmin``, ``bmax`` are the minimum and the maximum of inversed temperature, respectively.

- ``Tnum`` is the number of (inversed) temperature points.

- When ``Tlogspace`` is ``true``, the temperature points are distributed uniformly in the logarithmic space.

- ``nreplica_per_proc`` is the number of replicas (MC walkers) in one MPI process.


Calculation
~~~~~~~~~~~~

First, move to the folder where the sample file is located. (Hereinafter, it is assumed that you are the root directory of 2DMAT.)

.. code-block::

   $ cd sample/analytical/pamc

Then, run the main program. It will take a few secondes on a normal PC.

.. code-block::

   $ mpiexec -np 4 python3 ../../../src/py2dmat_main.py input.toml | tee log.txt

Here, the calculation is performed using MPI parallel with 4 processes.
If you are using Open MPI and you request more processes than the number of cores, add the ``--oversubscribed`` option to the ``mpiexec`` command.

When executed, a folder for each MPI rank will be created under the directory ``output``, and ``trial_TXXX.txt`` files containing the parameters evaluated in each Monte Carlo step and the value of the objective function at each temperature (``XXX`` is the index of points), and ``result_TXXX.txt`` files containing the parameters actually adopted will be created.
These files are concatnated into ``result.txt`` and ``trial.txt``.

These files have the same format: the first two columns are time (step) and the index of walker in the process, the third is the (inversed) temperature, the fourth column is the value of the objective function, and the fifth and subsequent columns are the parameters.
The final two columns are the weight of walker (Neal-Jarzynski weight) and the index of the grand ancestor (the replica index at the beginning of the calculation).

.. code-block::

    # step walker beta fx x1 x2 weight ancestor
    0 0 0.0 187.94429125133564 5.155393113805774 -2.203493345018569 1.0 0
    0 1 0.0 3.179380982615041 -3.7929742598748666 -3.5452766573635235 1.0 1
    0 2 0.0 108.25464277273859 0.8127003489802398 1.1465364357510186 1.0 2
    0 3 0.0 483.84183395038843 5.57417423682746 1.8381251624588506 1.0 3
    0 4 0.0 0.43633134370869153 2.9868796504069426 1.8428384502208246 1.0 4
    0 5 0.0 719.7992581349758 2.972577711255287 5.535680832873856 1.0 5
    0 6 0.0 452.4691017123836 -5.899340424701358 -4.722667479627368 1.0 6
    0 7 0.0 45.5355817998709 -2.4155554347674215 1.8769341969872393 1.0 7
    0 8 0.0 330.7972369561986 3.717750630491217 4.466110964691396 1.0 8
    0 9 0.0 552.0479484091458 5.575771168463163 2.684224163039442 1.0 9
    0 10 0.0 32.20027165958588 1.7097039347500953 2.609443449748964 1.0 10
    ...


``output/best_result.txt`` is filled with information about the parameter with the optimal objective function, the rank from which it was obtained, and the Monte Carlo step.

.. code-block::

    nprocs = 4
    rank = 0
    step = 1416
    walker = 76
    fx = 1.2934852891645974e-05
    x1 = 3.5849122439454018
    x2 = -1.8479993173120015

Finally, ``output/fx.txt`` stores the statistics at each temperature point:

.. code-block::

    # $1: 1/T
    # $2: mean of f(x)
    # $3: standard error of f(x)
    # $4: number of replicas
    # $5: log(Z/Z0)
    # $6: acceptance ratio
    0.0 300.30221072734275 15.51347277317414 400 0.0 0.95625
    10.0 0.10242968777639305 0.004707441824226148 400 -6.288173357129039 0.078525
    20.0 0.057183322050182284 0.002645707013463865 400 -7.016157801630186 0.023825
    30.0 0.04113146664363754 0.0019866335071532255 400 -7.477440282564104 0.015575
    40.0 0.030213182090724544 0.0014292149366135543 400 -7.82499342385409 0.01135
    ...

The first column is (inversed) temperature, and
the second/third ones are the mean and standard error of :math:`f(x)`, respectively.
The fourth column is the number of replicas and the fifth one is the logarithm of the ratio of the partition functions, :math:`\log(Z_n/Z_0)`, where :math:`Z_0` is the partition function at the first temperature.
The sixth column is the acceptance ratio of MC updates.


Visualization
~~~~~~~~~~~~~~~~~~~

By illustrating ``result_T.txt``, you can estimate regions where the function values become small.
In this case, the figure ``result_fx.pdf`` and ``result_T.pdf`` of the 2D parameter space is created by using the following command.
The color of symbols of ``result_fx.pdf`` and ``result_T.pdf`` mean ``R-factor`` and :math:`\beta`, respectively.

By executing the following command, the figures of two-dimensional parameter space ``res_T%.png`` will be generated where ``%`` stands for the indices of temperature. The symbol color corresponds to the function value.

.. code-block::

    $ python3 plot_result_2d.py -o res_T0.png result_T0.txt

It is seen from the figures that the samples are concentrated near the minima of ``f(x)`` where the objective function has a small value.

.. figure:: ../../../common/img/res_pamc_T0.*

.. figure:: ../../../common/img/res_pamc_T1.*

   Plot of sampled parameters. The horizontal axis denotes ``x1``, the vertical axis denotes ``x2``, and the color represents the value of ``f(x)``.
