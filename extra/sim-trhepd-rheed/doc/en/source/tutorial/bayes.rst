Optimization by Bayesian Optimization
================================================================

This tutorial describes how to estimate atomic positions from the experimental diffraction data by using Bayesian optimization (BO).
2DMAT uses `PHYSBO <https://www.pasums.issp.u-tokyo.ac.jp/physbo/en>`_ for BO.
The search grid has to be prepared in advance as a data file ``MeshData.txt``, similar to the case of the grid search.


Sample files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sample files are available from ``sample/single_beam/bayes`` .
This directory includes the following files:

- ``bulk.txt``

  The input file of ``bulk.exe``.

- ``experiment.txt``, ``template.txt``

  Reference files for the main program.

- ``MeshData.txt``

  The data file for the search grid.
  
- ``ref_BayesData.txt``

  Solution file for checking whether the calucation successes or not.

- ``input.toml``

  The input file of py2dmat.

- ``prepare.sh``, ``do.sh``

  Script files for running this tutorial.

In the following, we will subscribe these files and then show the result.


Reference files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial uses ``template.txt`` and ``experiment.txt`` that are similar to those in the previous tutorial (``minsearch``).
Except, in this tutorial the third parameter ``value_03`` is fixed to ``3.5`` in order to speed up the calculation.
The parameter space to be explored is given by ``MeshData.txt``.

.. code-block::

  1 3.5 3.5
  2 3.6 3.5
  3 3.6 3.6
  4 3.7 3.5
  5 3.7 3.6
  6 3.7 3.7
  7 3.8 3.5
  8 3.8 3.6
  9 3.8 3.7
  10 3.8 3.8
  ...

The first column is the index of the point, and the remaining columns are the coodinates, ``value_0`` and ``value_1`` that appear in the ``template.txt``.


Input files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This subsection describes the input file.
For details, see Bayes optimization section of 2DMAT manual.
``input.toml`` in the sample directory is shown as the following:

.. code-block:: toml

    [base]
    dimension = 2
    output_dir = "output"

    [solver]
    name = "sim-trhepd-rheed"
    run_scheme = "subprocess"

    [solver.config]
    cal_number = [1]

    [solver.param]
    string_list = ["value_01", "value_02" ]
    degree_max = 7.0

    [solver.reference]
    path = "experiment.txt"
    exp_number = [1]

    [algorithm]
    name = "bayes"
    label_list = ["z1", "z2"]
    seed = 1

    [algorithm.param]
    mesh_path = "MeshData.txt"

    [algorithm.bayes]
    random_max_num_probes = 10
    bayes_max_num_probes = 20


``[base]`` section describes the settings for a whole calculation.

- ``dimension`` is the number of variables you want to optimize. In this case, ``2`` is specified because two variables are optimized.

- ``output_dir`` is the name of directory for the outputs. If it is omitted, the results are written in the directory in which the program is executed.
  
``[solver]`` section specifies the solver to use inside the main program and its settings.

See the minsearch tutorial.

``[algorithm]`` section sets the algorithm to use and its settings.

- ``name`` is the name of the algorithm you want to use. In this tutorial we will do a Bayesian optimization analysis, and so it is set to ``bayes``.

- ``label_list`` is a list of labels shown in the output of the values of ``value_0x`` (x = 1,2).

``[algorithm.bayes]`` section sets the parameters for Bayesian optimization.

- ``random_max_num_probes`` specifies the number of random searches before Bayesian optimization.

- ``bayes_max_num_probes`` specifies the number of Bayesian searches.

For details on other parameters that can be specified in the input file, see the chapter on input files of ``bayes``.


Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, move to the folder where the sample file is located. (Hereinafter, it is assumed that you are the root directory of 2DMAT.)

.. code-block::

   $ cd sample/single_beam/bayes

Copy ``bulk.exe`` and ``surf.exe`` as in the tutorial for the direct problem.

.. code-block::

   $ cp ../../sim-trhepd-rheed/src/bulk.exe .
   $ cp ../../sim-trhepd-rheed/src/surf.exe .

Run ``bulk.exe`` to generate ``bulkP.b`` .

.. code-block::

   $ ./bulk.exe

Then, run the main program. It will take a few secondes on a normal PC.

.. code-block::

   $ python3 py2dmat-sim-trhepd-rheed input.toml | tee log.txt

A directory ``output/0`` will be created.
The following standard output will be shown:

.. code-block::

  # parameter
  random_max_num_probes = 10
  bayes_max_num_probes = 20
  score = TS
  interval = 5
  num_rand_basis = 5000
  value_01 =  5.10000
  value_02 =  4.90000
  R-factor = 0.037237314010261195
  0001-th step: f(x) = -0.037237 (action=150)
     current best f(x) = -0.037237 (best action=150)

  value_01 =  4.30000
  value_02 =  3.50000
  ...

where a list of hyperparameters are shown, followed by the candidate parameters at each step and the corresponding ``R-factor`` multiplied by :math:`-1`.
It also outputs the grid index (``action``) and ``f(x)`` with the best ``R-factor`` at that time.

Under the directory ``output/0``, subdirectories ``LogXXXX_00000000`` are created where XXXX is the grid index and the solver outputs are stored for each grid.
(The first column in ``MeshData.txt`` is taken as the id of the grid.)
The final estimated parameters are output to ``BayesData.txt``.

In this case, ``BayesData.txt`` can be seen as the following

.. code-block::

  #step z1 z2 fx z1_action z2_action fx_action
  0 5.1 4.9 0.037237314010261195 5.1 4.9 0.037237314010261195
  1 5.1 4.9 0.037237314010261195 4.3 3.5 0.06050786306685965
  2 5.1 4.9 0.037237314010261195 5.3 3.9 0.06215778000834068
  3 5.1 4.9 0.037237314010261195 4.7 4.2 0.049210767760634364
  4 5.1 4.9 0.037237314010261195 5.7 3.7 0.08394457854191653
  5 5.1 4.9 0.037237314010261195 5.2 5.2 0.05556857782716691
  6 5.1 4.9 0.037237314010261195 5.7 4.0 0.0754639895013157
  7 5.1 4.9 0.037237314010261195 6.0 4.4 0.054757310814479355
  8 5.1 4.9 0.037237314010261195 6.0 4.2 0.06339787375966344
  9 5.1 4.9 0.037237314010261195 5.7 5.2 0.05348404677676544
  10 5.1 4.7 0.03002813055356341 5.1 4.7 0.03002813055356341
  11 5.1 4.7 0.03002813055356341 5.0 4.4 0.03019977423448576
  12 5.3 4.5 0.02887504880071686 5.3 4.5 0.02887504880071686
  13 5.1 4.5 0.025865346123665988 5.1 4.5 0.025865346123665988
  14 5.2 4.4 0.02031077875240244 5.2 4.4 0.02031077875240244
  15 5.2 4.4 0.02031077875240244 5.2 4.6 0.023291891689059388
  16 5.2 4.4 0.02031077875240244 5.2 4.5 0.02345999725278686
  17 5.2 4.4 0.02031077875240244 5.1 4.4 0.022561543431398066
  18 5.2 4.4 0.02031077875240244 5.3 4.4 0.02544527153306051
  19 5.2 4.4 0.02031077875240244 5.1 4.6 0.02778877135528466
  20 5.2 4.3 0.012576357659158034 5.2 4.3 0.012576357659158034
  21 5.1 4.2 0.010217361468113488 5.1 4.2 0.010217361468113488
  22 5.1 4.2 0.010217361468113488 5.2 4.2 0.013178053637167673
  ...


The first column contains the number of steps, and the second, third, and fourth columns contain ``value_01``, ``value_02``, and ``R-factor``, which give the highest score at that time.
These are followed by the candidate ``value_01``, ``value_02`` and ``R-factor`` for that step.
In this case, you can see that the correct solution is obtained at the 21th step.

Note that ``do.sh`` is prepared as a script for batch calculation.
``do.sh`` also checks the difference between ``BayesData.dat`` and ``ref_BayesData.dat``.
The script is read as follows, though we omit further explanation.

.. code-block:: bash

    #!/bin/sh

    sh prepare.sh

    ./bulk.exe

    time py2dmat-sim-trhepd-rheed input.toml

    echo diff output/BayesData.txt ref_BayesData.txt
    res=0
    diff output/BayesData.txt ref_BayesData.txt || res=$?
    if [ $res -eq 0 ]; then
      echo TEST PASS
      true
    else
      echo TEST FAILED: BayesData.txt.txt and ref_BayesData.txt.txt differ
      false
    fi


Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can see at which step the parameter gave the minimum score from ``BayesData.txt``.
Since ``RockingCurve.txt`` is stored in the subfolder for each step, it is possible to compare it with the experimental value by following the procedure in :doc:``minsearch``.
