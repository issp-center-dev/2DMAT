  1  0  0                          IPR ISTART LRFLAG              
  1 10  0.02  0.2                  NSYM  NSYMS ASTEP VSTEP  
  5  1  2  2                       NT0  NSET LSMAX LLCUT
  5                                NINSET
 1.0000 0.0000                  1      PQEX
 1.0000 2.0000                  2      PQEX
 1.0000 1.0000                  3      PQEX
 2.0000 2.0000                  4      PQEX
 2.0000 0.0000                  5      PQEX
  3                                NDIM
 opt000 0.0000 0.0000  0           DISP(1,j)  j=1,3
 0.0000 opt001 0.0000  0           DISP(2,j)  j=1,3
 0.0000 0.0000 0.0000  1           DISP(3,j)  j=1,3
 0.0000 0.0000 0.0000  0           DISP(4,j)  j=1,3
 0.0000  0                         DVOPT  LSFLAG
  3  0  0                          MFLAG NGRID NIV
100                                ITMAX
 1.0000 0.5000 2.0000              ALPHA,BETA,GAMMA
 0.0005 0.0020                     FTOL1,FTOL2
300 .00100                        NSTEP,STSZ
1.000  0.000  0.000  0.000
1.000  1.000  0.000  0.000
1.000  1.000  1.000  0.000
0.000  0.000  0.000  1.000

