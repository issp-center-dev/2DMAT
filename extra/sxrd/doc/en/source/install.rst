Installation of 2DMAT-SXRD
================================================================

Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python3 (>=3.6.8)

  - The following Python packages are required.

    - tomli >= 1.2
    - numpy >= 1.14

  - py2dmat version 3.0 and later

  - sxrdcalc

    - C compiler and GNU Scientific Library are required.


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

2. Install sxrdcalc

   - sxrdcalc is available from the official site at: `https://github.com/sxrdcalc/sxrdcalc <https://github.com/sxrdcalc/sxrdcalc>`_

     The source package can be downloaded from the web site by pressing "Code" button and choosing "Download ZIP", or by the following command.

     .. code-block:: bash

	$ wget -O sxrdcalc.zip https://github.com/sxrdcalc/sxrdcalc/archive/refs/heads/main.zip

   - Unpack the source package, and compile the source. Edit Makefile in sxrdcalc-main as needed. GNU Scientific Library is required for the compilation.

     .. code-block:: bash

	$ unzip sxrdcalc.zip
	$ cd sxrdcalc-main
	$ make

     The executable file ``sxrdcalc`` will be generated.
     Put ``sxrdcalc`` in a directory listed in the PATH environment variable, or specify the paths to these commands at run time.
     
3. Install 2dmat-sxrd

   - From source files:

     At present, the source files of 2dmat-sxrd are placed in ``extra`` directory of py2dmat source package. After obtaining the source files following the step 1, install 2dmat-sxrd using ``pip`` command as follows:

     .. code-block:: bash

	$ cd 2DMAT/extra/sxrd
	$ python3 -m pip install .

     You may add ``--user`` option to install the package locally (in ``$HOME/.local``).

     Then, the library of 2DMAT-SXRD and the command ``py2dmat-sxrd`` wil be installed.


How to run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In 2DMAT, the analysis is done by using a predefined optimization algorithm and a direct problem solver.
There are two ways to do analyses of SXRD:

1. Use py2dmat-sxrd program included in this package to perform analyses.
   The users prepare an input parameter file in TOML format, and run command with it.
   The type of the inverse problem algorithms can be chosen by the parameter.

2. Write a program for the analysis with 2DMAT-SXRD library and 2DMAT framework.
   The type of the inverse problem algorithms can be chosen by importing the appropriate module.
   A flexible use would be possible, for example, to include data generation within the program.
   
The types of parameters and the instruction to use the library will be given in the subsequent sections.


How to uninstall
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to uninstall 2DMAT-SXRD and 2DMAT modules, type the following commands:

.. code-block:: bash

   $ python3 -m pip uninstall py2dmat-sxrd py2dmat
