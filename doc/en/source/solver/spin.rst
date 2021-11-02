``spin`` solver
************************

``spin`` is a ``Solver`` that computes the energy of a snapshot of a spin system with two-body interaction.

Ising model

.. math ::

    \mathcal{H} = -\sum_{i\le j} J_{ij} \sigma_i \sigma_j - \sum_i h_i \sigma_i

and Potts model

.. math ::

    \mathcal{H} = -\sum_{i\le j} J_{ij} \delta(\sigma_i, \sigma_j) - \sum_i h_i \delta(\sigma_i, 0)

are available.
:math:`\delta` is defined as

.. math ::

   \delta(x, y) = \begin{cases} 1 & \text{if} \quad x = y \\ 0 & \text{otherwise} \end{cases}.

The possible values that :math:`\sigma` takes can be specified in ``algorithm``.

Input parameters
~~~~~~~~~~~~~~~~~~~~~~~~

- ``type``

  Format: string

  Description: Type of spin system.
  "ising" (Ising model) and "potts" (Potts model) are available.

- ``twobody``

  Format: string

  Description: Path to a two-body interaction file defining non-zero elements of the :math:`J` matrix.
  If not set, :math:`J` will be zero.

- ``onebody``

  Format: string

  Description: Path to a external field file defining non-zero elements of :math:`h`.
  If not set, :math:`h` will be zero.

Reference file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two-body interaction file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two-body interaction file defines non-zero elements of the two-body interaction matrix, :math:`J_{ij}`.
One line that consists of three numbers defines one elements.
The first and the second integers mean indices of sites :math:`i, j`, and the third figure means the value of :math:`J_{ij}`.
For example, the following line ::

  0 1 1.0

means :math:`J_{01} = 1.0`.

- Note

  - When :math:`J_{ij}` with :math:`i > j` is given, :math:`J_{ji}` will be set.
  - When the same element appears twice or more, the last one will be used.


External field file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

External field file defines non-zero elements of the external field vector, :math:`h_{i}`.
One line that consists of two numbers defines one elements.
The first integer means an index of site :math:`i`, and the second figure means the value of :math:`h_i`.
For example, the following line ::

  0 1.0

means :math:`h_{0} = 1.0`.

- Note

  - When the same element appears twice or more, the last one will be used.
