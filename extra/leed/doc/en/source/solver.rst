Input and output
================================

``2DMAT-LEED`` module is a ``Solver`` which calculates the Rocking curve from atomic positions etc., using ``SATLEED``, and returns the deviation from the experimental Rocking curve as :math:`f(x)`.

In this section, the input parameters, the input data, and the output data are explained.
The input parameters are taken from the ``solver`` entry of the ``Info`` class.
The parameters are specified in ``[solver]`` section when they are given from a TOML file.
If the parameters are given in the dictionay format, they should be prepared as a nested dict under the ``solver`` key.
In the following, the parameter items are described in the TOML format.

The input data consist of target reference data, and the bulk structure data.
The output data consist of files containing the result of optimization.
Their contents will be shown in this section.


Input parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input parameters are specified in subsections in the ``solver`` section (``config`` and ``reference``).

[``config``] section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``path_to_solver``

  Format: string

  Description: Path to the solver ``satl2.exe`` .


[``reference``] section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``path_to_base_dir``

  Format: string

  Description: Path to the directory which stores ``exp.d``, ``rfac.d``, ``tleed4.i``, ``tleed5.i``, ``tleed.o``, ``short.t``.

  
Reference file for Solver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target reference file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The file containing the data to be targeted to fit. Edit ``tleed4.i`` in ``path_to_base_dir`` in the [``reference``] section.
Add the number you want to optimize to ``optxxx`` (where xxx is a three-digit number in the format 000, 001, 002, ...). (where xxx is a three-digit integer in the form 000, 001, 002, ...).
Note that the number of xxx must match the order and number of variables in the list of ``py2dmat`` variables to be optimized.
Note that if IFLAG and LSFLAG are not set to 0, the satleed side is also optimized.

An example file is shown below.

.. code-block::

    1  0  0                          IPR ISTART LRFLAG
    1 10  0.02  0.2                  NSYM  NSYMS ASTEP VSTEP
    5  1  2  2                       NT0  NSET LSMAX LLCUT
    5                                NINSET
    1.0000 0.0000                  1      PQEX
    1.0000 2.0000                  2      PQEX
    1.0000 1.0000                  3      PQEX
    2.0000 2.0000                  4      PQEX
    2.0000 0.0000                  5      PQEX
    3                                 NDIM
    opt000 0.0000 0.0000  0           DISP(1,j)  j=1,3
    0.0000 opt001 0.0000  0           DISP(2,j)  j=1,3
    0.0000 0.0000 0.0000  1           DISP(3,j)  j=1,3
    0.0000 0.0000 0.0000  0           DISP(4,j)  j=1,3
    0.0000  0                         DVOPT  LSFLAG
    3  0  0                           MFLAG NGRID NIV
    ...
   
Output file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``leed``, the output files are stored in the folder with the MPI rank number.
