``sim-trhepd-rheed`` solver
***********************************************

.. _sim-trhepd-rheed: https://github.com/sim-trhepd-rheed/sim-trhepd-rheed

``sim-trhepd-rheed`` is a ``Solver`` that uses sim-trhepd-rheed_ to calculate the diffraction rocking curve from the atomic position :math:`x` and returns the deviation from the experimental rocking curve as :math:`f(x)`. 

Preparation
~~~~~~~~~~~~

You will need to install sim-trhepd-rheed_ beforehand.

1. Download the source code from the official ``sim-trhepd-rheed`` website. 
2. Move to ``sim-trhepd-rheed/src`` folder and make ``bulk.exe`` and ``surf.exe`` by using ``make``.

Before running ``py2dmat``, run ``bulk.exe`` to create the bulk data.
The ``surf.exe`` is called from ``py2dmat``.

Input parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input parameters can be specified in subcsections ``config``, ``post``, ``param``, ``reference`` in ``solver`` section.

[``config``] section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``surface_exec_file``

  Format: string (default: "surf.exe")

  Description: Path to ``sim-trhepd-rheed`` surface reflection solver ``surf.exe``.

- ``surface_input_file``

  Format: string (default: "surf.txt")

  Description: Input file for surface structure.

- ``bulk_output_file``

  Format: string (default: "bulkP.b")

  Description: Output file for bulk structure.

- ``surface_output_file``

  Format: string (default: "surf-bulkP.s")

  Description: Output file for surface structure.

- ``calculated_first_line``

  Format: integer (default: 5)

  Description: One of the parameters that specifies the range of output files to be read, calculated by the solver. This parameter specifies the first line to be read.

- ``calculated_last_line``

  Format: integer (default: 60)

  Description: One of the parameters that specifies the range of output files to be read, calculated by the solver. This parameter specifies the last line to be read.

- ``row_number``

  Format: integer (default: 8)

  Description: One of the parameters that specifies the range of output files to be read, calculated by the solver. This parameter specifies the column to be read.

[``post``] section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``normalization``

  Format: string ("TOTAL" or "MAX", default: "TOTAL")

  Description: This parameter specifies whether the experimental and computational data vectors are normalized by the sum of the whole values or by the maximum value.

- ``Rfactor_type``

  Format: string ("A" or "B", default: "A")

  Description: This parameter specifies how to calculate the R-factor. 
  The experimental and computational data vectors are denoted as :math:`u = (u_{1}, u_{2},...,u_{m})` , 
  :math:`v = (v_{1}, v_{2},...,v_{m})`　, respectively. 
  When "A" type is chosen, R-factor is defined as :math:`R  = (\sum_i^m (u_{i}-v_{i})^{2})^{1/2}` .
  When "B" type is chosen, R-factor is defined as :math:`R  = (\sum_i^m (u_{i}-v_{i})^{2})^{1/2}/( \sum_i^m u_{i}^2 + \sum_i^m v_{i}^2)` .

- ``omega``

  Format: float (default: 0.5)

  Description: This parameter specifies the half-width of convolution.

- ``remove_work_dir``

  Format: boolean (default: false)

  Description: Whether to remove working directories after reading R-factor or not

[``param``] section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``string_list``

  Format: list of string. The length should match the value of dimension (default: ["value_01", "value_02"]).

  Description: List of placeholders to be used in the reference template file to create the input file for the solver. These strings will be replaced with the values of the parameters being searched for.

- ``degree_max``

  Format: float (default: 6.0)

  Description:  Maximum angle (in degrees)

[``reference``] section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``path``

  Format: string (default: ``experiment.txt``)

  Description: Path to the experimental data file.
  
- ``first``

  Format: integer (default: 1)

  Description: One of the parameters that specify the range of experimental data files to be read. This parameter specifies the first line of the experimental file to be read.

- ``last``

  Format: integer (default: 56)

  Description: One of the parameters that specify the range of experimental data files to be read. This parameter specifies the last line of the experimental file to be read.


Reference file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input template file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The input template file ``template.txt`` is a template for creating an input file for ``surf.exe``.
The parameters to be moved in ``py2dmat`` (such as the atomic coordinates you want to find) should be replaced with the appropriate string, such as ``value_*``.
The strings to be used are specified by ``string_list`` in the ``[solver]`` - ``[param]`` section of the input file for the solver.
An example template is shown below.

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

In this case, ``value_01``, ``value_02``, and ``value_03`` are the parameters to be moved in ``py2dmat``.


Target file
^^^^^^^^^^^^^^
This file (``experiment.txt``) contains the data to be targeted.
The first column contains the angle, and the second column contains the calculated value of the reflection intensity multiplied by the weight.
An example of the file is shown below.

.. code-block::

    0.100000 0.002374995
    0.200000 0.003614789
    0.300000 0.005023215
    0.400000 0.006504978
    0.500000 0.007990674
    0.600000 0.009441623
    0.700000 0.010839445
    0.800000 0.012174578
    0.900000 0.013439485
    1.000000 0.014625579
    ...


Output file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For ``sim-trhepd-rheed``, the files output by ``surf.exe`` will be output in the ``Log%%%%%_#####`` folder under the folder with the rank number.
``%%%%%`` means an index of iteration in ``Algorithm`` (e.g., steps in Monte Carlo),
and ``#####`` means an index of group (e.g., replica index in Monte Carlo).
In large calculation, the number of these folders becomes too large to be written in the storage of the system.
For such a case, let ``solver.post.remove_work_dir`` parameter be ``true`` in order to remove these folders.
This section describes the own files that are output by this solver.

``stdout``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It contains the standard output of ``surf.exe``.
An example is shown below.

.. code-block::

     bulk-filename (end=e) ? :
     bulkP.b
     structure-filename (end=e) ? :
     surf.txt
     output-filename :
     surf-bulkP.s

``RockingCurve.txt``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This file is located in the ``Log%%%%%_#####`` folder.
The first line is the header, and the second and subsequent lines are the angle, convoluted calculated/experimental values, normalized calculated/experimental values, and raw calculated values in that order.
An example is shown below.

.. code-block::

    #degree convolution_I_calculated I_experiment convolution_I_calculated(normalized) I_experiment(normalized) I_calculated
    0.1 0.0023816127859192407 0.002374995 0.004354402952499057 0.005364578226620574 0.001722
    0.2 0.003626530149456865 0.003614789 0.006630537795012198 0.008164993342397588 0.003397
    0.3 0.00504226607469267 0.005023215 0.009218987407498791 0.011346310125551366 0.005026
    0.4 0.006533558304296079 0.006504978 0.011945579793136154 0.01469327865677437 0.006607
    0.5 0.00803056955158873 0.007990674 0.014682628499657693 0.018049130948243314 0.008139
    0.6 0.009493271317558538 0.009441623 0.017356947736613827 0.021326497600946535 0.00962
    0.7 0.010899633015118851 0.010839445 0.019928258053867838 0.024483862338931763 0.01105
    ...
