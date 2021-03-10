Bayesian Optimization
=====================================

This tutorial subscribes how to estimate atomic positions from the experimental diffraction data by using Bayesian optimization (BO).
2DMAT uses `PHYSBO <https://www.pasums.issp.u-tokyo.ac.jp/physbo/en>`_ for BO.

Sample files
~~~~~~~~~~~~~~~~~~~~~~~~

Sample files are available from ``sample/py2dmat/bayes`` .
This directory includes the following files:

- ``bulk.txt``

  The input file of ``bulk.exe``

- ``experiment.txt`` , ``template.txt``

  Reference files for the main program

- ``ref_BayesData.txt``

  Solution file for checking whether the calucation successes or not

- ``input.toml``

  The input file of py2dmat

- ``prepare.sh`` , ``do.sh``

  Script files for running this tutorial

In the following, we will subscribe these files and then show the result.

Reference files
~~~~~~~~~~~~~~~~~~~

This tutorial uses ``template.txt`` , ``experiment.txt`` similar to the previous one (``minsearch``).
Only difference is that in this tutorial the third parameter ``value_03`` is fixed to ``3.5`` in order to speed up the calculation.
The parameter space to be explored is given by ``MeshData.txt``.

.. code-block::

    1 6.000000 6.000000
    2 6.000000 5.750000
    3 6.000000 5.500000
    4 6.000000 5.250000
    5 6.000000 5.000000
    6 6.000000 4.750000
    7 6.000000 4.500000
    8 6.000000 4.250000
    9 6.000000 4.000000
    ...

The first column is the index of the point and the remaining ones are the coodinates, ``value_0`` and ``value_1`` in the ``template.txt``.

Input files
~~~~~~~~~~~~~~~~~~~

This subsection describes the input file.
For details, see :ref:`the manual of bayes <bayes_input>`.
``input.toml`` in the sample directory is shown as the following ::

    [base]
    dimension = 2

    [solver]
    name = "sim-trhepd-rheed"

    [solver.config]
    calculated_first_line = 5
    calculated_last_line = 74
    row_number = 2

    [solver.param]
    string_list = ["value_01", "value_02" ]
    degree_max = 7.0

    [solver.reference]
    path = "experiment.txt"
    first = 1
    last = 70

    [algorithm]
    name = "bayes"
    label_list = ["z1", "z2"]

    [algorithm.param]
    mesh_path = "MeshData.txt"

    [algorithm.bayes]
    random_max_num_probes = 5
    bayes_max_num_probes = 20


- The ``[base]`` section describes the settings for a whole calculation.

    - ``dimension`` is the number of variables you want to optimize. In this case, specify ``2`` because it optimizes two variables.

- The ``[solver]`` section specifies the solver to use inside the main program and its settings.

    - See the minsearch tutorial.

- The ``[algorithm]`` section sets the algorithm to use and its settings.

    - ``name`` is the name of the algorithm you want to use, and in this tutorial we will do a Bayesian optimization analysis, so specify ``bayes``.

    - ``label_list`` is a list of label names to be given when outputting the value of ``value_0x`` (x = 1,2).

    - The ``[algorithm.bayes]`` section sets the parameters for Bayesian optimization.

         - ``random_max_num_probes`` specifies the number of random searches before Bayesian optimization.

         - ``bayes_max_num_probes`` specifies the number of Bayesian searches.

For details on other parameters that can be specified in the input file, see the chapter on input files of ``bayes``.

Calculation
~~~~~~~~~~~~

First, move to the folder where the sample file is located (hereinafter, it is assumed that you are the root directory of 2DMAT).

.. code-block::

    cd sample/py2dmat/bayes

Copy ``bulk.exe`` and ``surf.exe`` as the tutorial for the direct problem.

.. code-block::

    cp ../../../../sim-trhepd-rheed/src/TRHEPD/bulk.exe .
    cp ../../../../sim-trhepd-rheed/src/TRHEPD/surf.exe .

Execute ``bulk.exe`` to generate ``bulkP.b`` .

.. code-block::

    ./bulk.exe

Then, run the main program (it takes a few secondes)

.. code-block::

   python3 ../../../src/py2dmat_main.py input.toml | tee log.txt

This makes a directory with the name of ``0`` .
The following standard output will be shown:

.. code-block::

   #parameter
    random_max_num_probes = 5
    bayes_max_num_probes = 20
    score = TS
    interval = 5
    num_rand_basis = 5000
    Read MeshData.txt
    value_01 =  4.75000
    value_02 =  4.50000
    WARNING : degree in lastline = 7.0, but 6.0 expected
    PASS : len(calculated_list) 70 == len(convolution_I_calculated_list)70
    R-factor = 0.05141906746102885
    0001-th step: f(x) = -0.051419 (action=46)
       current best f(x) = -0.051419 (best action=46)

    value_01 =  6.00000
    value_02 =  4.75000
    ...


A list of hyperparameters, followed by candidate parameters at each step and the corresponding ``R-factor`` multiplied by :math:`-1`, are shown first.
It also outputs the grid index (``action``) and ``f(x)`` with the best ``R-factor`` at that time.
Under the directory ``0``, subdirectories with the name is the grid id are created, like ``Log%%%%%`` (``%%%%%`` is the grid id), and the solver output for each grid is saved.
(The first column in ``MeshData.txt`` will be assigned as the id of the grid).
The final estimated parameters are output to ``BayesData.txt``.

In this case, ``BayesData.txt`` can be seen as the following

.. code-block::

    #step z1 z2 R-factor z1_action z2_action R-factor_action
    0 4.75 4.5 0.05141906746102885 4.75 4.5 0.05141906746102885
    1 4.75 4.5 0.05141906746102885 6.0 4.75 0.06591878368102033
    2 5.5 4.25 0.04380131351780189 5.5 4.25 0.04380131351780189
    3 5.0 4.25 0.02312528177606794 5.0 4.25 0.02312528177606794
    4 5.0 4.25 0.02312528177606794 6.0 5.75 0.05501069117756031
    5 5.0 4.25 0.02312528177606794 5.0 4.75 0.037158316568603085
    6 5.0 4.25 0.02312528177606794 5.75 4.75 0.06061194437867895
    7 5.0 4.25 0.02312528177606794 4.25 3.5 0.062098618649988294
    8 5.0 4.25 0.02312528177606794 6.0 6.0 0.04785241875354398
    9 5.0 4.25 0.02312528177606794 4.5 4.0 0.05912332368374844
    10 5.0 4.25 0.02312528177606794 4.75 4.25 0.04646333628698967
    11 5.0 4.25 0.02312528177606794 5.5 4.5 0.0466682914488051
    12 5.0 4.25 0.02312528177606794 5.0 4.5 0.033464998538380517
    13 5.25 4.25 0.015199251773721183 5.25 4.25 0.015199251773721183
    14 5.25 4.25 0.015199251773721183 5.25 4.0 0.0475246576904707
    ...


The first column contains the number of steps, and the second, third, and fourth columns contain `` value_01``, `` value_02``, and `` R-factor``, which give the highest score at that time.
This is followed by the candidate ``value_01``, ``value_02`` and ``R-factor`` for that step.
In this case, you can see that the correct solution is obtained at the 13th step.

In addition, ``do.sh`` is prepared as a script for batch calculation.
``do.sh`` also checks the difference between ``BayesData.dat`` and ``ref_BayesData.dat``.
I will omit the explanation below, but I will post the contents.

.. code-block::

    sh prepare.sh

    ./bulk.exe

    time python3 ../../../src/py2dmat_main.py input.toml

    echo diff BayesData.txt ref_BayesData.txt
    res=0
    diff BayesData.txt ref_BayesData.txt || res=$?
    if [ $res -eq 0 ]; then
      echo TEST PASS
      true
    else
      echo TEST FAILED: BayesData.txt.txt and ref_BayesData.txt.txt differ
      false
    fi

Visualization
~~~~~~~~~~~~~~~~~~~

You can see at what step the parameter gave the minimum score by looking at ``BayesData.txt``.
Since ``RockingCurve.txt`` is stored in a subfolder for each step, it is possible to compare it with the experimental value by following the procedure of :doc:``minsearch``.
