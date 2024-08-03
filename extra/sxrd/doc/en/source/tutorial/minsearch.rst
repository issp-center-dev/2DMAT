Optimization by Nelder-Mead method
================================================================

In this section, we will explain how to calculate the inverse problem of analyzing atomic coordinates from diffraction data using the Nelder-Mead method.
The specific calculation procedure is as follows.

1. Preparation of the reference file

   Prepare the reference file to be matched (in this tutorial, it corresponds to ``sic111-r3xr3_f.dat`` described below).

2. Preparation of the bulk data
   
   Prepare the data for bulk part (in this tutorial, it corresponds to ``sic111-r3xr3.blk``).

3. Run the main program

   Run the calculation using ``py2dmat-sxrd`` to estimate the atomic coordinates.

In the main program, the Nelder-Mead method implemented in `scipy.optimize.fmin <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin.html>`_ is applied to find the parameter that minimizes the deviation (R-value) between the intensity obtained using the solver (in this case ``sxrdcalc``) and the intensity listed in the reference file (``sic111-r3xr3_f.dat``).


Location of the sample files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample files are located in ``sample/minsearch``.
The following files are stored in the folder.

- ``input.toml``

  Input file of the main program.

- ``sic111-r3xr3.blk``, ``sic111-r3xr3_f.dat``

  Reference files to proceed with calculations in the main program.

- ``ref_res.txt``, ``ref_SimplexData.txt``

  The files containing the answers you want to seek in this tutorial.

- ``prepare.sh`` , ``do.sh``

  Script prepared for doing all calculation of this tutorial

The following sections describe these files and then show the actual calculation results.


Input files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section, we prepare the input file ``input.toml`` for the main program.
The details can be found in the input file section in the manual.
The content of ``input.toml`` is shown below.

.. code-block::

    [base]
    dimension = 2
    output_dir = "output"
    
    [solver]
    name = "sxrd"
    
    [solver.config]
    sxrd_exec_file = "sxrdcalc"
    bulk_struc_in_file = "sic111-r3xr3.blk"
    [solver.param]
    scale_factor = 1.0
    type_vector = [1, 2]
    [[solver.param.domain]]
    domain_occupancy = 1.0
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.00000000, 0.00000000, 1.00000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[1, 0.0, 0.0, 1.0]]
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.33333333, 0.66666667, 1.00000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[1, 0.0, 0.0, 1.0]]
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.66666667, 0.33333333, 1.00000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[1, 0.0, 0.0, 1.0]]
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.33333333, 0.33333333, 1.20000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[2, 0.0, 0.0, 1.0]]
    [solver.reference]
    f_in_file = "sic111-r3xr3_f.dat"
    
    [algorithm]
    name = "minsearch"
    label_list = ["z1", "z2"]
    [algorithm.param]
    min_list = [-0.2, -0.2]
    max_list = [0.2, 0.2]
    initial_list = [0.0, 0.0]


First, ``[base]`` section is explained.

- ``dimension`` is the number of variables to be optimized. In this case it is ``2`` since we are optimizing two variables as described in ``template.txt``. It should match the number of elements of ``solver.config.type_vector`` described below.

- ``output_dir`` is the name of directory for the outputs. If it is omitted, the results are written in the directory in which the program is executed.

``[solver]`` section specifies the solver to be used inside the main program and its settings.

- ``name`` is the name of the solver you want to use. In this tutorial it is ``sxrd``.

The solver can be configured in the subsections ``[solver.config]``, ``[solver.param]``, and ``[solver.reference]``.

``[solver.config]`` section specifies options for reading the output file produced by ``sxrdcalc`` that is called from the main program.

- ``sxrd_exec_file`` is the command name of ``sxrdcalc``. It is specified as a path to the executable file, or searched from the PATH environment variable.

- ``bulk_struc_in_file`` specifies the bulk structure file.

``[solver.param]`` section specifies options for the input file passed to ``sxrdcalc`` that is to be called from the main program.
For the details of parameters, see the input and output section of the manual.

``[solver.reference]`` section specifies the location of the experimental data.

- ``f_in_file`` specifies the path to the experimental data.

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

   $ cd sample/minsearch

Copy ``sxrdcalc``.

.. code-block::

   $ cp ../../sxrdcalc-main/sxrdcalc .

Run the main program. The computation time will take only a few seconds on a normal PC.

.. code-block::

   $ py2dmat-sxrd input.toml | tee log.txt

Then, the standard output will look as follows.

.. code-block::

    Optimization terminated successfully.
             Current function value: 0.000106
             Iterations: 26
             Function evaluations: 53
    iteration: 26
    len(allvecs): 27
    step: 0
    allvecs[step]: [0. 0.]
    step: 1
    allvecs[step]: [0. 0.]
    step: 2
    allvecs[step]: [0. 0.]
    ...

``z1`` and ``z2`` are the candidate parameters at each step, and ``R-factor`` is the function value at that point.
The final estimated parameters will be written to ``output/res.dat``. 
In the current case, the following result will be obtained:

.. code-block::

    fx = 0.000106
    z1 = -2.351035891479114e-05
    z2 = 0.025129315870799473

You can see that we will get the same values as the correct answer data in ``ref.txt``.

Note that ``do.sh`` is available as a script for batch calculation.
In ``do.sh``, ``res.txt`` and ``ref.txt`` are also compared for the check.
Here is what it does, without further explanation.

.. code-block:: bash

  #!/bin/sh

  sh ./prepare.sh

  ./bulk.exe

  time py2dmat-sxrd input.toml | tee log.txt

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


