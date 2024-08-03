Analyses by user programs
================================================================

In this tutorial, we will write a user program using 2DMAT-LEED module and perform analyese. As an example, we adopt Nelder-Mead method for the inverse problem algorithm.


Location of the sample files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample files are located in ``sample/user_program``.
The following files are stored in the folder.

- ``simple.py``

  Source file of the main program. This program reads ``input.toml`` for the parameters.

- ``input.toml``

  Input file of the main program.

- ``base``

  Directory that contains reference files to proceed with calculations in the main program.
  The reference files include: ``exp.d``, ``rfac.d``, ``short.t``, ``tleed.o``, ``tleed4.i``, and ``tleed5.i``.

- ``ref.txt``

  A file containing the answers you want to seek in this tutorial.

- ``simple2.py``

  Another version of source file of the main program. The parameters are embedded in the program as a dict.

- ``prepare.sh`` , ``do.sh``

  Script prepared for doing all calculation of this tutorial

The following sections describe these files and then show the actual calculation results.


Description of main program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``simple.py`` is a simple program for the analyses using 2DMAT-LEED module.
The entire source file is shown as follows:

.. code-block:: python

    import py2dmat
    import py2dmat.algorithm.min_search
    import leed
    
    info = py2dmat.Info.from_file("input.toml")
    
    solver = leed.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()


At the beginning of the program, the required modules are imported as listed below.

- ``py2dmat`` for the main module of 2DMAT.

- ``py2dmat.algorithm.min_search`` for the module of the inverse problem algorithm used in this tutorial.

- ``leed`` for the direct problem solver module.

Next, the instances of the classes are created.

- ``py2dmat.Info`` class

  This class is for storing the parameters. It is created by calling a class method ``from_file`` with a path to TOML file as an argument.

- ``leed.Solver`` class

  This class is for the direct problem solver of the 2DMAT-LEED module. It is created by passing an instance of Info class.

- ``py2dmat.Runner`` class

  This class is for connecting the direct problem solver and the inverse problem algorithm. It is created by passing an instance of Solver class and an instance of Info class.

- ``py2dmat.algorithm.min_search.Algorithm`` class

  This class is for the inverse problem algorithm. In this tutorial, we use ``min_search`` module that implements the optimization by Nelder-Mead method. It is created by passing an instance of Runner class.

After creating the instances of Solver, Runner, and Algorithm in this order, we invoke ``main()`` method of the Algorithm class to start analyses.

In the above program, the input parameters are read from a file in TOML format. It is also possible to take the parameters in the form of dictionary.
``simple2.py`` is anther version of the main program in which the parameters are embedded in the program. The entire source file is shown below:

.. code-block:: python

    import py2dmat
    import py2dmat.algorithm.min_search
    import leed
    
    params = {
        "base": {
            "dimension": 2,
            "output_dir": "output",
        },
        "solver": {
            "config": {
                "path_to_solver": "./leedsatl/satl2.exe",
            },
            "reference": {
                "path_to_base_dir": "./base",
            },
        },
        "algorithm": {
            "label_list": ["z1", "z2"],
            "param": {
                "min_list": [-0.5, -0.5],
                "max_list": [0.5,  0.5],
                "initial_list": [-0.1, 0.1],
            },
             
        },
    }
    
    info = py2dmat.Info(params)
    
    solver = leed.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()


An instance of Info class is created by passing a set of parameters in a dict form.
It is also possible to generate the parameters within the program before passing to the class.


Input files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The input file for the main program, ``input.toml``, contains parameters for the direct problem solver and the inverse problem algorithm. The contents of the ``base`` and ``solver`` sections are the same as those in the previous example.
The parameters for the Nelder-Mead method should be specified in the ``algorithm.param`` section, while ``algorithm.name`` for the type of algorithm is ignored.

- ``min_list`` and ``max_list`` specifies the search region in the form of the lower and upper bounds of the parameters as lists.

- ``initial_list`` specifies the initial values.


Calculation execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, move to the folder where the sample files are located. (We assume that you are directly under the directory where you downloaded this software.)

.. code-block::

   $ cd sample/user_program

Copy the SATLEED programs that have been compiled in the grid search tutorial.
Otherwise, run ``sh setup.sh`` in the ``sample/mapper`` directory to generate ``leedsatl/satl1.exe`` and ``leedsatl/satl2.exe``.

.. code-block::

   $ mkdir leedsatl
   $ cp ../mapper/leedsatl/satl2.exe leedsatl/

Then, run the main program. The computation time will take only a few seconds on a normal PC.

.. code-block::

   $ python3 simple.py | tee log.txt

The standard output will be shown like as follows.

.. code-block::

    Optimization terminated successfully.
             Current function value: 0.157500
             Iterations: 29
             Function evaluations: 63
    iteration: 29
    len(allvecs): 30
    step: 0
    allvecs[step]: [-0.1  0.1]
    step: 1
    allvecs[step]: [-0.1  0.1]
    step: 2
    allvecs[step]: [-0.1  0.1]
    step: 3
    allvecs[step]: [-0.1  0.1]
    step: 4
    allvecs[step]: [-0.1  0.1]
    step: 5
    allvecs[step]: [-0.0375  -0.05625]
    step: 6
    allvecs[step]: [-0.0375  -0.05625]
    step: 7
    allvecs[step]: [-0.0375  -0.05625]
    ...


``z1`` and ``z2`` are the candidate parameters at each step, and ``R-factor`` is the function value at that point.
The final estimated parameters will be written to ``output/res.dat``. 
In the current case, the following result will be obtained:

.. code-block::

    fx = 0.1575
    z1 = -0.01910402104258537
    z2 = 0.10217590294778345

You can see that we will get the same values as the correct answer data in ``ref.txt``.

Note that ``do.sh`` is available as a script for batch calculation.

