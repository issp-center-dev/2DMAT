Analyses by user programs
================================================================

In this tutorial, we will write a user program using 2DMAT-SXRD module and perform analyese. As an example, we adopt Nelder-Mead method for the inverse problem algorithm.


Location of the sample files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample files are located in ``sample/user_program``.
The following files are stored in the folder.

- ``simple.py``

  Source file of the main program. This program reads ``input.toml`` for the parameters.

- ``input.toml``

  Input file of the main program.

- ``sic111-r3xr3.blk``, ``sic111-r3xr3_f.dat``

  Reference files to proceed with calculations in the main program.

- ``ref_res.txt``, ``ref_SimplexData.txt``

  The files containing the answers you want to seek in this tutorial.

- ``simple2.py``

  Another version of source file of the main program. The parameters are embedded in the program as a dict.

The following sections describe these files and then show the actual calculation results.


Description of main program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``simple.py`` is a simple program for the analyses using 2DMAT-SXRD module.
The entire source file is shown as follows:

.. code-block:: python

   import numpy as np

   import py2dmat
   import py2dmat.algorithm.min_search
   import sxrd

   info = py2dmat.Info.from_file("input.toml")

   solver = sxrd.Solver(info)
   runner = py2dmat.Runner(solver, info)
   alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
   alg.main()


At the beginning of the program, the required modules are imported as listed below.

- ``py2dmat`` for the main module of 2DMAT.

- ``py2dmat.algorithm.min_search`` for the module of the inverse problem algorithm used in this tutorial.

- ``sxrd`` for the direct problem solver module.

Next, the instances of the classes are created.

- ``py2dmat.Info`` class

  This class is for storing the parameters. It is created by calling a class method ``from_file`` with a path to TOML file as an argument.

- ``sxrd.Solver`` class

  This class is for the direct problem solver of the 2DMAT-SXRD module. It is created by passing an instance of Info class.

- ``py2dmat.Runner`` class

  This class is for connecting the direct problem solver and the inverse problem algorithm. It is created by passing an instance of Solver class and an instance of Info class.

- ``py2dmat.algorithm.min_search.Algorithm`` class

  This class is for the inverse problem algorithm. In this tutorial, we use ``min_search`` module that implements the optimization by Nelder-Mead method. It is created by passing an instance of Runner class.

After creating the instances of Solver, Runner, and Algorithm in this order, we invoke ``main()`` method of the Algorithm class to start analyses.

In the above program, the input parameters are read from a file in TOML format. It is also possible to take the parameters in the form of dictionary.
``simple2.py`` is anther version of the main program in which the parameters are embedded in the program. The entire source file is shown below:

.. code-block:: python

    import numpy as np
    
    import py2dmat
    import py2dmat.algorithm.min_search
    import sxrd
    
    param = {
        "base": {
            "dimension": 2,
            "output_dir": "output",
        },
        "solver": {
            "config": {
                "sxrd_exec_file": "sxrdcalc",
                "bulk_struc_in_file": "sic111-r3xr3.blk",
            },
            "param": {
                "scale_factor": 1.0,
                "type_vector": [1, 2],
                "domain": [
                    {
                        "domain_occupancy": 1.0,
                        "atom": [
                            {
                                "name": "Si",
                                "pos_center": [0.00000000, 0.00000000, 1.00000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[1, 0.0, 0.0, 1.0]]
                            },
                            {
                                "name": "Si",
                                "pos_center": [0.33333333, 0.66666667, 1.00000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[1, 0.0, 0.0, 1.0]]
                            },
                            {
                                "name": "Si",
                                "pos_center": [0.66666667, 0.33333333, 1.00000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[1, 0.0, 0.0, 1.0]]
                            },
                            {
                                "name": "Si",
                                "pos_center": [0.33333333, 0.33333333, 1.20000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[2, 0.0, 0.0, 1.0]]
                            },
                        ],
                    },
                ],
            },
            "reference": {
                "f_in_file": "sic111-r3xr3_f.dat",
            },
        },
        "algorithm": {
            "label_list": ["z1", "z2"],
            "param": {
                "min_list": [-0.2, -0.2],
                "max_list": [ 0.2,  0.2],
                "initial_list": [ 0.0, 0.0 ],
            },
        },
    }
    
    info = py2dmat.Info(param)
    
    solver = sxrd.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()


An instance of Info class is created by passing a set of parameters in a dict form.
It is also possible to generate the parameters within the program before passing to the class.


Input files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The input file ``input.toml`` for the main program is the same as that used in the previous tutorial for Nelder-Mead method.
Except, ``algorithm.name`` parameter for specifying the algorithm type should be ignored.

The reference files are the same as those in the previous tutorials.


Calculation execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, move to the folder where the sample files are located. (We assume that you are directly under the directory where you downloaded this software.)

.. code-block::

   $ cd sample/user_program

Copy ``sxrdcalc``.

.. code-block::

   $ cp ../../sxrdcalc-main/sxrdcalc .

Run the main program. The computation time will take only a few seconds on a normal PC.

.. code-block::

   $ python3 simple.py | tee log.txt

The standard output will look as follows.

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
