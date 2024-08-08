Installation of 2DMAT-SIM-TRHEPD-RHEED
================================================================

Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python3 (>=3.6.8)

  - The following Python packages are required.

    - tomli >= 1.2
    - numpy >= 1.14

  - py2dmat version 3.0 and later

  - sim-trhepd-rheed version 1.0.2 and later


How to download and install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install py2dmat

   - From source files:

     Download source files of py2dmat from the repository as follows:

     .. code-block:: bash

	$ git clone -b update https://github.com/issp-center-dev/2DMAT.git

     Install py2dmat using ``pip`` command:

     .. code-block:: bash

	$ cd 2DMAT
	$ python3 -m pip install .

     You may add ``--user`` option to install py2dmat locally (in ``$HOME/.local``).

     If you run the following command instead, optional packages will also be installed at the same time.

     .. code-block:: bash

	$ python3 -m pip install .[all]

2. Install sim-trhepd-rheed

   - Download the source package from the official site:

     .. code-block:: bash

	$ wget -O sim-trhepd-rheed-1.0.2.tar.gz https://github.com/sim-trhepd-rheed/sim-trhepd-rheed/archive/refs/tags/v1.0.2.tar.gz

   - Unpack the source package, and compile the source. Edit Makefile in sim-trhepd-rheed/src as needed.

     .. code-block:: bash

	$ tar xvfz sim-trhepd-rheed-1.0.2.tar.gz
	$ cd sim-trhepd-rheed-1.0.2/src
	$ make

     The executable files ``bulk.exe``, ``surf.exe``, ``potcalc.exe``, and ``xyz.exe`` will be generated.
     Put ``bulk.exe`` and ``surf.exe`` in a directory listed in the PATH environment variable, or specify the paths to these commands at run time.
     
3. Install 2dmat-sim-trhepd-rheed

   - From source files:

     At present, the source files of 2dmat-sim-trhepd-rheed are placed in ``extra`` directory of py2dmat source package. After obtaining the source files following the step 1, install 2dmat-sim-trhepd-rheed using ``pip`` command as follows:

     .. code-block:: bash

	$ cd 2DMAT/extra/sim-trhepd-rheed
	$ python3 -m pip install .

     You may add ``--user`` option to install the package locally (in ``$HOME/.local``).

     Then, the library of 2DMAT-SIM-TRHEPD-RHEED and the command ``py2dmat-sim-trhepd-rheed`` wil be installed.


How to run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In 2DMAT, the analysis is done by using a predefined optimization algorithm and a direct problem solver.
There are two ways to do analyses of TRHEPD:

1. Use py2dmat-sim-trhepd-rheed program included in this package to perform analyses.
   The users prepare an input parameter file in TOML format, and run command with it.
   The type of the inverse problem algorithms can be chosen by the parameter.

2. Write a program for the analysis with 2DMAT-SIM-TRHEPD-RHEED library and 2DMAT framework.
   The type of the inverse problem algorithms can be chosen by importing the appropriate module.
   A flexible use would be possible, for example, to include data generation within the program.
   
The types of parameters and the instruction to use the library will be given in the subsequent sections.


How to uninstall
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to uninstall 2DMAT-SIM-TRHEPD-RHEED and 2DMAT modules, type the following commands:

.. code-block:: bash

   $ python3 -m pip uninstall py2dmat-sim-trhepd-rheed py2dmat
