Installation of py2dmat
================================

Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python3 (>=3.6.8)

    - The following Python packages are required.
        - tomli >= 1.2
        - numpy >= 1.14

    - Optional packages

        - mpi4py (required for grid search)
        - scipy (required for Nelder-Mead method)
        - physbo (>=0.3, required for Baysian optimization)


How to download and install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install the ``py2dmat`` python package and the ``py2dmat`` command following the instructions shown below.

- Installation using PyPI (recommended)

    - ``python3 -m pip install py2dmat``

        - ``--user``  option to install locally (``$HOME/.local``)

        - If you use ``py2dmat[all]``, optional packages will be installed at the same time.
	  
- Installation from source code

    #. ``git clone https://github.com/issp-center-dev/2DMAT``
    #. ``python3 -m pip install ./2DMAT``

        - The ``pip`` version must be 19 or higher (can be updated with ``python3 -m pip install -U pip``).

- Download the sample files

    -  Sample files are included in the source code.
    - ``git clone https://github.com/issp-center-dev/2DMAT``


How to run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``py2dmat``, the analysis is carried out by using a predefined optimization algorithm ``Algorithm`` and a direct problem solver ``Solver``.

.. code-block:: bash
    
    $ py2dmat input.toml

See :doc:`algorithm/index` for the predefined ``Algorithm`` and :doc:`solver/index` for the ``Solver``.

The direct problem solvers for analyses of experimental data of two-dimensional material structure are provided as separate modules.
To perform these analyses, you need to install the modules and the required software packages.
At present, the following modules are provided:

- 2DMAT-SIM-TRHEPD-RHEED module for Total Refrection High-energy Positron Diffraction (TRHEPD)

- 2DMAT-SXRD module for Surface X-ray Diffraction (SXRD)

- 2DMAT-LEED module for Low-energy Electron Diffraction (LEED)
  
If you want to prepare the ``Algorithm`` or ``Solver`` by yourself, use the ``py2dmat`` package.
See :doc:`customize/index` for details.

The program can be executed without installing ``py2dmat`` command; instead, run ``src/py2dmat_main.py`` script directly as follows. It would be convenient when you are rewriting programs.

.. code-block:: bash

   $ python3 src/py2dmat_main.py input


How to uninstall
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please type the following command:

.. code-block:: bash

    $ python3 -m pip uninstall py2dmat
