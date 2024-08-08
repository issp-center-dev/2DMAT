Installation of 2DMAT-LEED
================================

Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python3 (>=3.6.8)

  - The following Python packages are required.

    - tomli >= 1.2
    - numpy >= 1.14

  - py2dmat version 3.0 and later

  - SATLEED

    - A Fortran compiler is required for compilation.


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

2. Install SATLEED

   - The source archive is available from the following URL.

     .. code-block:: bash

        $ wget http://www.icts.hkbu.edu.hk/VanHove_files/leed/leedsatl.zip

   - Unpack the source package, and compile the source.

     It is necessary to modify parameters in the source files of ``SATLEED`` according to the details of the system under consideration.
     For the present tutorial, a script ``setup.sh`` is prepared that automatically modifies the parameters and compile the source files.

     .. code-block:: bash

	$ cd sample/mapper
	$ sh ./setup.sh

     By running ``setup.sh``, the executable files ``satl1.exe`` and ``satl2.exe`` will be generated in ``leedsatl`` directory.
     
3. Install 2DMAT-LEED

   - From source files:

     At present, the source files of 2DMAT-LEED are placed in ``extra`` directory of py2dmat source package. After obtaining the source files following the step 1, install 2dmat-leed using ``pip`` command as follows:

     .. code-block:: bash

	$ cd 2DMAT/extra/leed
	$ python3 -m pip install .

     You may add ``--user`` option to install the package locally (in ``$HOME/.local``).

     Then, the library of 2DMAT-LEED and the command ``py2dmat-leed`` wil be installed.


How to run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In 2DMAT, the analysis is done by using a predefined optimization algorithm and a direct problem solver.
There are two ways to do analyses of LEED:

1. Use py2dmat-leed program included in this package to perform analyses.
   The users prepare an input parameter file in TOML format, and run command with it.
   The type of the inverse problem algorithms can be chosen by the parameter.

2. Write a program for the analysis with 2DMAT-LEED library and 2DMAT framework.
   The type of the inverse problem algorithms can be chosen by importing the appropriate module.
   A flexible use would be possible, for example, to include data generation within the program.
   
The types of parameters and the instruction to use the library will be given in the subsequent sections.


How to uninstall
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to uninstall 2DMAT-LEED and 2DMAT modules, type the following commands:

.. code-block:: bash

   $ python3 -m pip uninstall py2dmat-leed py2dmat
