Installation of 2DMAT-Functions
================================================================

Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python3 (>=3.6.8)

  - The following Python packages are required.

    - tomli >= 1.2
    - numpy >= 1.14

- py2dmat version 3.0 and later


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

2. Install py2dmat-function

   - From source files:

     At present, the source files of 2dmat-functions are placed in ``extra`` directory of py2dmat source package. After obtaining the source files following the step 1, install 2dmat-functions using ``pip`` command as follows:

     .. code-block:: bash

	$ cd 2DMAT/extra/function
	$ python3 -m pip install .

     You may add ``--user`` option to install the package locally (in ``$HOME/.local``).

     Then, the library of 2DMAT-Functions wil be installed.


How to run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In 2DMAT, the analysis is done by using a predefined optimization algorithm and a direct problem solver.
The ways to do analyses of Functions is to write a program for the analysis with 2DMAT-Functions library and 2DMAT framework.
The type of the inverse problem algorithms can be chosen by importing the appropriate module.
A flexible use would be possible, for example, to include data generation within the program.
The types of parameters and the instruction to use the library will be given in the subsequent sections.


How to uninstall
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to uninstall 2DMAT-Functions and 2DMAT modules, type the following commands:

.. code-block:: bash

   $ python3 -m pip uninstall py2dmat-function py2dmat
