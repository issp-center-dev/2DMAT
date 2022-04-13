# Simple example of SATLEED

## What's this

LEED data of clean Cu(001) surface and the I-V curves appear in Fig. 1 of Ref. [1]

[1] Md Kabiruzzaman, Rezwan Ahmed, Takeshi Nakagawa, and Seigi Mizuno,
Investigation of c(2×2) Phase of Pb and Bi Coadsorption on Cu(001) by Low Energy Electron Diffraction,
Evergreen. 4 (1), pp. 10-15 (2017)
https://doi.org/10.5109/1808306

## Files

- `REEDME.md`
    - this file
- `setup.sh`
    - perform the followings
        - download and expand the zip file of SATLEED
        - change the parameters
        - generate `Makefile`
        - make executables
- `do.sh`
    - run py2dmat
- `leedsatl.patch`
    - patch file for rewriting parameters
- `input.toml`
    - input file for py2dmat
- `MeshData.txt`
    - grid data (parameter space)

## Flow

Make `satl1.exe` and `satl2.exe`

``` bash
sh ./setup.sh
```

Perform grid search

``` bash
sh ./do.sh
```
