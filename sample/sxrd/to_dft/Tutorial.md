### Tutorial

#### 1. Preparation of input file

In the following we will present how to prepare a standard input file for using to\_dft tool. The file format of the input file is `toml`. The following section describes the contents of the input file using `to_dft_input.toml` in the `sample/sxrd/to_dft ` folder. The contents of the file are as follows.

```toml
[Main]
output_file_head = "surf_bulk_new111_ext"
[Main.solver]
solver = "sxrd"
[Main.algorithm]
algorithm = "minsearch"
[Main.param]
z_margin = 0.001
slab_margin = 10.0
r_SiH = 1.48 #angstrom
theta = 109.5 #H-Si-H angle in degree
[Main.lattice]
unit_vec = [[7.67932, 0.00000, 0.00000], [0.00000, 3.83966, 0.00000]]
[ASE]
solver_name = "qe"
kpts = [3,3,1]        # sampling k points (Monkhorst-Pack grid)
command = "mpirun -np 4 ./pw.x -in espresso.pwi > espresso.pwo"
[Solver]
[Solver.control]
calculation='bands' # 'scf','realx','bands',...
pseudo_dir='./'     # Pseudopotential directory
[Solver.system]
ecutwfc = 20.0        # Cut-off energy in Ry
nbands = 33           # # of bands (only used in band structure calc
[Solver.pseudo]
Si = 'Si.pbe-mt_fhi.UPF'
H = 'H.pbe-mt_fhi.UPF'
```

The input file consists of three sections: `Main`, `ASE`, and `Solver`. Below is a brief description of the variables for each section.

##### `Main` section

- output\_file\_head

  Format: string

  Description: Header for output files (xyz and cif files)

`Main.solver` section

`Main.algorithm` section

- algorithm

  Format: string

  Description: Algorithm name of 2DMAT optimization

##### `Main.Param` section

- `z_margin`

  Format: float

  Description: Margin used to extract the lowest and second-to-last atoms. For example, if the z-coordinate of the atom in the bottom layer is `z_min`, the atoms in `z_min - z_margin <= z <= z_min + z_margin` will be extracted.

- `slab_margin`

  Format: float

  Description: Margin for tuning the size of the slab. If the z-coordinates of the atoms in the bottom and top layers are `z_min` , `z_max`, then the slab size is given by `z_max-z_min+slab_margin`.

- `r_SiH`

  Format: float

  Description: The distance (in A˚) between a vertex (e.g. Si) and H of a tetrahedral structure.

- `theta`

  Format: float

  Description: The angle between the vertex and H of the tetrahedral structure (e.g. Si-H-Si).

##### `Main.lattice` section

- `unit_vec`

  Format: list

  Description: Specify a unit vector that forms a 2D plane (ex. `unit_vec = [[7.67932, 0.00000, 0.00000], [0.00000, 3.83966, 0.00000]]`).

##### `ASE` section

This section specifies parameters related to `ASE`.

- `solver_name`

  Format: string

  Description: The name of the solver. Currently, only `qe` is given.

- `kpts`

  Format: list

  Description: Specify the k-points to be sampled (Monkhorst-Pack grid).

- `command`

  Format: string

  Description: Set the command used to run the solver.

##### `Solver` section

In this section, parameters related to `Solver` are specified. You will need to specify this if you want to perform first-principles calculations directly using ASE. Basically, the configuration is the same as the one specified in the input file of each solver. For example, in the case of QE, `Solver.control` contains the parameters to be set in the `control` section of QE.

#### 2.  Execute the to\_dft.py and output files

After preparing the input file, then execute the to\_dft.py by following command:

```shell
python3 to_dft.py input.toml
```

Then the unit number in a,b direction and layer number can be specified:

```shell
# of a-units, b-units & bulk layers:
```

For example type `1 1 2` to set two layer bulk structure. 

##### Output files

After finishing calculation the following files are generated:

- `surf-bulk.xyz`

- `surf_bulk_new111_ext.xyz`
- `surf_bulk_new111_ext.cif`
- `espresso.pwi` 

The `surf-bulk.xyz` is structure file for bulk and optimized surface structure. The  `surf_bulk_new111_ext.xyz` and `surf_bulk_new111_ext.cif` are structure files after hydrogen termination, in order to eliminate the influence of dangling bond-derived electrons from the opposite surface of interest.

The following is a comparison of  `surf-bulk.xyz` and `surf_bulk_new111_ext.xyz`.

-  `surf-bulk.xyz`

```xyz
22
Lattice= "5.33940000 0.00000000 0.00000000 -2.66970000 4.62405604 0.00000000 -0.00000000 -0.00000000 6.53940000" Properties=species:S:1:pos:R:3 pbc="T T T"
Si 0.00000000 0.00000000 0.00000000 
Si -0.00000003 3.08270404 0.00000000 
Si 2.66970003 1.54135200 0.00000000 
C -0.00000000 -0.00000000 1.63485000 
C -0.00000003 3.08270404 1.63485000 
C 2.66970003 1.54135200 1.63485000 
Si 1.77979998 -0.00000000 2.17979998 
Si -0.88989999 1.54135200 2.17979998 
Si 1.77979998 3.08270400 2.17979998 
C 1.77979998 -0.00000000 3.81464998 
C -0.88989999 1.54135200 3.81464998 
C 1.77979998 3.08270400 3.81464998 
Si 0.88989999 1.54135200 4.35960002 
Si 3.55959996 -0.00000000 4.35960002 
Si -1.77979998 3.08270400 4.35960002 
C 0.88989999 1.54135200 5.99444996 
C 3.55959996 -0.00000000 5.99444996 
C -1.77979998 3.08270400 5.99444996 
Si -0.00000000 -0.00000000 6.53940000 
Si -0.00000003 3.08270404 6.53940000 
Si 2.66970003 1.54135200 6.53940000 
Si 0.88989999 1.54135200 7.97806800 
```

- `surf_bulk_new111_ext.xyz`

```xyz
22
Lattice= "5.3394 0 0 -2.669700000000638 4.6240560409662645 0 0.0 0.0 17.978068" Properties=species:S:1:pos:R:3 pbc="T T T"
C       -0.00000000      -0.00000000       1.63485000
C       -0.00000003       3.08270404       1.63485000
C        2.66970003       1.54135200       1.63485000
Si       1.77979998      -0.00000000       2.17979998
Si      -0.88989999       1.54135200       2.17979998
Si       1.77979998       3.08270400       2.17979998
C        1.77979998      -0.00000000       3.81464998
C       -0.88989999       1.54135200       3.81464998
C        1.77979998       3.08270400       3.81464998
Si       0.88989999       1.54135200       4.35960002
Si       3.55959996      -0.00000000       4.35960002
Si      -1.77979998       3.08270400       4.35960002
C        0.88989999       1.54135200       5.99444996
C        3.55959996      -0.00000000       5.99444996
C       -1.77979998       3.08270400       5.99444996
Si      -0.00000000      -0.00000000       6.53940000
Si      -0.00000003       3.08270404       6.53940000
Si       2.66970003       1.54135200       6.53940000
Si       0.88989999       1.54135200       7.97806800
H       -0.00000000      -0.00000000       0.54785000
H       -0.00000003       3.08270404       0.54785000
H        2.66970003       1.54135200       0.54785000
```

The `surf_bulk_new111_ext.xyz` is the result of the replacement of the lowest level atom with H and the addition of H to form a tetrahedral structure.

This file can be read by appropriate visualization software as ordinary XYZ Format coordinate data, but the lattice vector information of the periodic structure is written in the place where comments are usually written. You can also copy the data of “element name + 3D coordinate” from the third line of the output file to the input file of QE.

`espresso.pwi` is the input file for QE’s scf calculation, and structural optimization and band calculation can be done by modifying this file accordingly. For details, please refer to the [QE online manual][1] .

[1]:	https://www.quantum-espresso.org/Doc/INPUT_PW.html