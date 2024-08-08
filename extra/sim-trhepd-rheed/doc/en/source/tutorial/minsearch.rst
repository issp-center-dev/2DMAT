Optimization by Nelder-Mead method
================================================================

In this section, we will explain how to calculate the inverse problem of analyzing atomic coordinates from diffraction data using the Nelder-Mead method.
The specific calculation procedure is as follows.

0. Preparation of the reference file

   Prepare the reference file to be matched (in this tutorial, it corresponds to ``experiment.txt`` described below).

1. Perform calculations on the bulk part of the surface structure.
   
   Copy ``bulk.exe`` to ``sample/minsearch`` and run the calculation.

2. Run the main program

   Run the calculation using ``py2dmat-sim-trhepd-rheed`` to estimate the atomic coordinates.

In the main program, the Nelder-Mead method implemented in `scipy.optimize.fmin <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin.html>`_ is applied to find the parameter that minimizes the deviation (R-value) between the intensity obtained using the solver (in this case ``surf.exe``) and the intensity listed in the reference file (``experiment.txt``).


Location of the sample files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample files are located in ``sample/single_beam/minsearch``.
The following files are stored in the folder.

- ``bulk.txt``

  Input file of ``bulk.exe``.

- ``experiment.txt`` , ``template.txt``

  Reference file to proceed with calculations in the main program.

- ``ref.txt``

  A file containing the answers you want to seek in this tutorial.

- ``input.toml``

  Input file of the main program.

- ``prepare.sh`` , ``do.sh``

  Script prepared for doing all calculation of this tutorial

The following sections describe these files and then show the actual calculation results.


The reference file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``template.txt`` file is almost the same format as the input file for ``surf.exe``.
The parameters to vary (such as the atomic coordinates you want to find) are labeled as ``value_*`` or some other appropriate strings.
The following is the content of ``template.txt``.

.. code-block::

    2                                    ,NELMS,  -------- Ge(001)-c4x2
    32,1.0,0.1                           ,Ge Z,da1,sap
    0.6,0.6,0.6                          ,BH(I),BK(I),BZ(I)
    32,1.0,0.1                           ,Ge Z,da1,sap
    0.4,0.4,0.4                          ,BH(I),BK(I),BZ(I)
    9,4,0,0,2, 2.0,-0.5,0.5               ,NSGS,msa,msb,nsa,nsb,dthick,DXS,DYS
    8                                    ,NATM
    1, 1.0, 1.34502591	1	value_01   ,IELM(I),ocr(I),X(I),Y(I),Z(I)
    1, 1.0, 0.752457792	1	value_02
    2, 1.0, 1.480003343	1.465005851	value_03
    2, 1.0, 2	1.497500418	2.281675
    2, 1.0, 1	1.5	1.991675
    2, 1.0, 0	1	0.847225
    2, 1.0, 2	1	0.807225
    2, 1.0, 1.009998328	1	0.597225
    1,1                                  ,(WDOM,I=1,NDOM)

In this input file, ``value_01``, ``value_02``, and ``value_03`` are used.
In the sample folder, there is a reference file ``ref.txt`` to know if the atomic positions are estimated correctly. The contents of this file are

.. code-block::

  fx = 7.382680568652868e-06
  z1 = 5.230524973874179
  z2 = 4.370622919269477
  z3 = 3.5961444501081647

``value_01``, ``value_02``, and ``value_03`` correspond to ``z1``, ``z2``, and ``z3``, respectively.
``fx`` is the optimal value of the objective function.

``experiment.txt`` is a file that is used as a reference in the main program.
In this tutorial, it is equivalent to ``convolution.txt`` obtained from the calculation when putting the parameters in ``ref.txt`` into ``template.txt`` and following the same procedure as in the tutorial on direct problems.
(Note that they are different from those in the tutorial of the direct problem because the input files for ``bulk.exe`` and ``surf.exe`` are different.)


Input files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section, we prepare the input file ``input.toml`` for the main program.
The details can be found in the input file section in the manual.
The content of ``input.toml`` is shown below.

.. code-block::

    [base]
    dimension = 3
    output_dir = "output"

    [solver]
    name = "sim-trhepd-rheed"
    run_scheme = "subprocess"
    generate_rocking_curve = true

    [solver.config]
    cal_number = [1]

    [solver.param]
    string_list = ["value_01", "value_02", "value_03" ]
    degree_max = 7.0

    [solver.reference]
    path = "experiment.txt"
    exp_number = [1]

    [solver.post]
    normalization = "TOTAL"

    [algorithm]
    name = "minsearch"
    label_list = ["z1", "z2", "z3"]

    [algorithm.param]
    min_list = [0.0, 0.0, 0.0]
    max_list = [10.0, 10.0, 10.0]
    initial_list = [5.25, 4.25, 3.50]


First, ``[base]`` section is explained.

- ``dimension`` is the number of variables to be optimized. In this case it is ``3`` since we are optimizing three variables as described in ``template.txt``.

- ``output_dir`` is the name of directory for the outputs. If it is omitted, the results are written in the directory in which the program is executed.

``[solver]`` section specifies the solver to be used inside the main program and its settings.

- ``name`` is the name of the solver you want to use. In this tutorial it is ``sim-trhepd-rheed``.

- ``run_scheme`` specifies how the solver is executed within the program. In the current version, ``subprocess`` can be specified.

- ``generate_rocking_curve`` specifies whether or not the rocking curves are generated in every steps.
  
The solver can be configured in the subsections ``[solver.config]``, ``[solver.param]``, and ``[solver.reference]``.

``[solver.config]`` section specifies options for reading the output file produced by ``surf.exe`` that is called from the main program.

- ``calculated_first_line`` specifies the first line to read from the output file.

- ``calculated_last_line`` specifies the last line of the output file to be read.

- ``cal_number`` specifies the indices of columns of the output file to read.
  
``[solver.param]`` section specifies options for the input file passed to ``surf.exe`` that is to be called from the main program.

- ``string_list`` is a list of variable names embedded in ``template.txt``.

- ``degree_max`` specifies the maximum angle in degrees.

``[solver.reference]`` section specifies the location of the experimental data and the range to read.

- ``path`` specifies the path where the experimental data is located.

- ``first`` specifies the first line of the experimental data file to read.

- ``end`` specifies the last line of the experimental data file to read.

- ``exp_number`` specifies the indices of columns of the experimental data file to read.

``[algorithm]`` section specifies the algorithm to use and its settings.

- ``name`` is the name of the algorithm you want to use. In this tutorial, it is set to ``minsearch``, since we are using the Nelder-Mead method.

- ``label_list`` is a list of label names to be attached to the output of ``value_0x`` (x=1,2,3).

``[algorithm.param]`` section specifies the range of parameters to search and their initial values.

- ``min_list`` and ``max_list`` specify the minimum and maximum values of the search range, respectively.

- ``initial_list`` specifies the initial values.

Other parameters, such as convergence criteria used in the Nelder-Mead method, can be set in the ``[algorithm]`` section, although they are omitted here so that the default values are used.
See the input file section of the manual for details.


Calculation execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, move to the folder where the sample files are located. (We assume that you are directly under the directory where you downloaded this software.)

.. code-block::

   $ cd sample/single_beam/minsearch

Copy ``bulk.exe`` and ``surf.exe``.

.. code-block::

   $ cp ../../sim-trhepd-rheed/src/bulk.exe .
   $ cp ../../sim-trhepd-rheed/src/surf.exe .

Run ``bulk.exe`` to produce ``bulkP.b``.

.. code-block::

   $ ./bulk.exe

After that, run the main program. The computation time will take only a few seconds on a normal PC.

.. code-block::

   $ py2dmat-sim-trhepd-rheed input.toml | tee log.txt

Then, the standard output will look as follows.

.. code-block::

    Read experiment.txt
    z1 =  5.25000
    z2 =  4.25000
    z3 =  3.50000
    [' 5.25000', ' 4.25000', ' 3.50000']
    PASS : degree in lastline = 7.0
    PASS : len(calculated_list) 70 == len(convolution_I_calculated_list)70
    R-factor = 0.015199251773721183
    z1 =  5.50000
    z2 =  4.25000
    z3 =  3.50000
    [' 5.50000', ' 4.25000', ' 3.50000']
    PASS : degree in lastline = 7.0
    PASS : len(calculated_list) 70 == len(convolution_I_calculated_list)70
    R-factor = 0.04380131351780189
    z1 =  5.25000
    z2 =  4.50000
    z3 =  3.50000
    [' 5.25000', ' 4.50000', ' 3.50000']
    ...

``z1``, ``z2``, and ``z3`` are the candidate parameters at each step, and ``R-factor`` is the function value at that point.
The results at each step are also written in the folder ``output/LogXXXX_YYYY`` (where XXXX and YYYY are the step counts).
The final estimated parameters will be written to ``output/res.dat``. 
In the current case, the following result will be obtained:

.. code-block::

    z1 = 5.230524973874179
    z2 = 4.370622919269477
    z3 = 3.5961444501081647

You can see that we will get the same values as the correct answer data in ``ref.txt``.

Note that ``do.sh`` is available as a script for batch calculation.
In ``do.sh``, ``res.txt`` and ``ref.txt`` are also compared for the check.
Here is what it does, without further explanation.

.. code-block:: bash

  #!/bin/sh

  sh ./prepare.sh

  ./bulk.exe

  time py2dmat-sim-trhepd-rheed input.toml | tee log.txt

  echo diff output/res.txt ref.txt
  res=0
  diff output/res.txt ref.txt || res=$?
  if [ $res -eq 0 ]; then
    echo Test PASS
    true
  else
    echo Test FAILED: res.txt and ref.txt differ
    false
  fi


Visualization of calculation results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``generate_rocking_curve`` is set to true, the data of the rocking curve at each step is stored in ``LogXXXX_00000001`` (where ``XXXX`` is the index of steps) as ``RockingCurve.txt``.
A tool ``draw_RC_double.py`` is provided to visualize this data.
In this section, we will use this tool to visualize the results.

.. code-block::

   $ cp output/0/Log00000001_00000001/RockingCurve.txt RockingCurve_ini.txt
   $ cp output/0/Log00000061_00000001/RockingCurve.txt RockingCurve_con.txt
   $ cp ../../../script/draw_RC_double.py .
   $ python draw_RC_double.py

By running the above, ``RC_double.png`` will be generated.

.. figure:: ../../../common/img/RC_double_minsearch.*

   Analysis using the Nelder-Mead method. The red circles represent the experimental values, the blue line represents the rocking curve at the first step, and the green line represents the rocking curve obtained at the last step.

From the figure, we can see that at the last step the result agrees with the experimental data.
