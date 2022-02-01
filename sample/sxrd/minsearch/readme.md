### Sample of Nelder-Mead method (minsearch) with sxrd solver

#### Optimization by minsearch algorithm with sxrd solver

In this sample we will show how to perform the optimization by Nelder-Mead method (minsearch) with sxrd solver like using [sim-trhepd-rheed](https://github.com/sim-trhepd-rheed/sim-trhepd-rheed) solver. The specific calculation procedure is as follows.

1. Preparation of the reference file for sxrd solver

   The reference file should match the format of `sxrdcalc`, detail is described below in **Reference file** section.<br/>

2. Preparation of the input file for sxrd solver

   The `[algorithm]` section should be change to satisfy the minsearch algorithm, detail is described below in **Input file** section.<br/>
   
3. Execute 2DMAT

   After preparing the reference file and input file, we can easily call 2DMAT and submit the input file:

   `python3 2dmat input.toml`
   
   And we will get the output file, you can find the reference output files in this sample, and detail is described below in **Output file** section.<br/>

#### Reference file

The reference file containing the data to be targeted to fit. The path is specified by `f_in_file` in the`[solver.reference]` section of input file. For each line `h k l F sigma` is given. Here, `h k l ` are the wavenumbers, `F` is the intensity, and `sigma` is the uncertainty of `F`. An example file is shown below.

> `0.000000 0.000000 0.050000 572.805262 0.1 
> 0.000000 0.000000 0.150000 190.712559 0.1 
> 0.000000 0.000000 0.250000 114.163340 0.1 
> 0.000000 0.000000 0.350000 81.267319 0.1 
> 0.000000 0.000000 0.450000 62.927325 0.1 
> 0.000000 0.000000 0.550000 51.209358 0.1` 
>
> `...` 

#### Input file

The parameters in `[base]`,`[solver]` sections will keep the same as the sample of using mapper algorithm. We need to change the parameter in `[algorithm]` section.

- `[algorithm]` 

  `name = "minsearch"`  Name should be change to minsearch

  `label_list = ["z1", "z2"]` The list number should equal to `dimension` in `[base]` section and number of `type_vector` in `[solver.config]` section.

- `[algorithm.param]` 

  `min_list = [-0.2, -0.2]` 
  `max_list = [0.2, 0.2]`

  The `min_list` and `max_list` specify the minimum and maximum values of the search range, respectively.

  `initial_list = [0.0, 0.0]` The `initial_list` specifies the initial values.<br/>

#### Output

The standard output is the same as tutorial **Optimization by Nelder-Mead method**, The final estimated parameters will be output to `res.dat`.

>fx = 0.000106
>z1 = -2.351035891479114e-05
>z2 = 0.025129315870799473

Here is the reference result of 2DMAT calculation.