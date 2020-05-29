########## (Edit) Parameters of Quantum Espresso (Edit) ##########
calculation='relax' # 'scf','realx','bands',...
ecutwfc=20.0        # Cut-off energy in Ry
kpts=(3,3,1)        # sampling k points (Monkhorst-Pack grid)
nbands=33           # # of bands (only used in band structure calc
pseudo_dir='./'     # Pseudopotential directory
pseudopotentials={ 'Si': 'Si.pbe-mt_fhi.UPF',
                   'H' : 'H.pbe-mt_fhi.UPF' }
##################################################################

'''
TRHEPD

Usage example:
  $ python trhepd.py abc.xyz

Output files:
  abc.cif
  abc_ext.xyz
  espresso.pwi
  espresso.pwo
'''

import sys
import math

args = sys.argv

### Read/Write file names ###

file_name = args[1]

n = len(file_name)
m = len('.xyz')

base_name = file_name[:n-m]

wfile_name = base_name+'_ext.xyz'

print('Input file name =',file_name)
print('Output file name =',wfile_name)

### Read ###

f = open(file_name)
r = f.readlines()    # r is a list constructed with each line of f
f.close()

### pick the atomic-coordinate lines ###

ratoms = []
for rl in r:               # rl is a string
    rs = rl.split()        # rs is a list
    if len(rs) == 4 and rs[0].isalpha():
        ratoms.append(rs)  # ratoms is a list of lists

natoms = len(ratoms)
print('natoms=', natoms)

### convert the atomic coordinates in float ###

z = []
for rs in ratoms:
    z.append( float(rs[3]) )

### slab thickness ###

slab_size = max(z) - min(z)
print('slab_size=', slab_size)

### z-coordinate of the bottom-most atoms ###

z_mergin = 0.001

z_bottom_most = min( z )
z_bottom_most0 = z_bottom_most-z_mergin
z_bottom_most1 = z_bottom_most+z_mergin

z_bottom_2nd = min([z2 for z2 in z if z2 > z_bottom_most1])
z_bottom_2nd0 = z_bottom_2nd - z_mergin
z_bottom_2nd1 = z_bottom_2nd + z_mergin

ratoms_bottom_most = []
for i in range(natoms):
    if z_bottom_most0 <= z[i] <= z_bottom_most1:
        rs = ratoms[i]
        ratoms_bottom_most.append([rs[0],float(rs[1]),float(rs[2]),float(rs[3])])

ratoms_bottom_2nd = []
for i in range(natoms):
    if z_bottom_2nd0 <= z[i] <= z_bottom_2nd1:
        rs = ratoms[i]
        ratoms_bottom_2nd.append([rs[0],float(rs[1]),float(rs[2]),float(rs[3])])

### Add Hydrogen terminators ###

r_SiH = 1.48 #angstrom
theta = 109.5 #H-Si-H angle in degree

dx = r_SiH * math.sin( math.radians(theta*0.5) )
dy = dx
dz = r_SiH * math.cos( math.radians(theta*0.5) )

Hs = []
for r2 in ratoms_bottom_2nd:
    dmin=100000.0
    imin=0
    for i in range(len(ratoms_bottom_most)):
        r1 = ratoms_bottom_most[i]
        x12 = r1[1]-r2[1]
        y12 = r1[2]-r2[2]
        d12 = x12**2 + y12**2
        if d12 < dmin:
            dmin = d12
            imin = i
    r1 = ratoms_bottom_most[imin]
    x12 = r1[1] - r2[1]
    y12 = r1[2] - r2[2]
    if (x12 == 0.0 and y12 != 0.0) or (x12 != 0.0 and y12 == 0.0):
        print('(001)surface')
        if x12 == 0.0:
            Hs.append( ['H','{:f}'.format(r2[1]),'{:f}'.format(r2[2]-dy),'{:f}'.format(r2[3]-dz)] )
            Hs.append( ['H','{:f}'.format(r2[1]),'{:f}'.format(r2[2]+dy),'{:f}'.format(r2[3]-dz)] )
        else:
            Hs.append( ['H','{:f}'.format(r2[1]-dx),'{:f}'.format(r2[2]),'{:f}'.format(r2[3]-dz)] )
            Hs.append( ['H','{:f}'.format(r2[1]+dx),'{:f}'.format(r2[2]),'{:f}'.format(r2[3]-dz)] )
    elif x12==0.0 and y12==0.0 :
        print('(111)surface')
        Hs.append( ['H','{:f}'.format(r2[1]),'{:f}'.format(r2[2]),'{:f}'.format(r2[3]-r_SiH)] )

### atomic coordinates including H terminators ###

n = len(ratoms_bottom_most)
ratoms_with_H = []
for rl in ratoms[:natoms-n]:
    str_rl = '  '.join(rl)+'\n'
    ratoms_with_H.append(str_rl)
for rl in Hs:
    str_rl = '  '.join(rl)+'\n'
    ratoms_with_H.append(str_rl)

natoms = natoms - n + len(Hs)
print('natoms=',natoms)

### Get cell info ###
#  The input XYZ file is assumed to have the cell info
#  at the last two lines

n = len(r)
a1 = r[n-2].split()
a2 = r[n-1].split()
a3 = [ str(slab_size+10.0) ]

### Make the cell info ###
#  (generate the extended-xyz file)

comment = 'Lattice="'+a1[0]+' 0.0 0.0  0.0 '+a2[1]+' 0.0 '+' 0.0 0.0 '+a3[0]+'"'+' Properties=species:S:1:pos:R:3 pbc="T T T"\n'

f = open(wfile_name, mode='w')
f.write(str(natoms)+'\n')
f.write(comment)
for rl in ratoms_with_H:
    f.write(rl)
f.close()

### ASE (Atomic Simulation Environment) ###

from ase.io import read, write
from ase.constraints import FixAtoms
from ase.calculators.espresso import Espresso

a = read(wfile_name)
cell = a.get_cell()

### CIF file ###

a.write(base_name+'.cif', format='cif')

### Constraints ###

z=[]
for rl in ratoms_with_H:  # rl is a string
    rs = rl.split()       # rs is a list
    z.append(float(rs[3]))

c = FixAtoms(indices=[s for s in range(natoms) if z[s]<=z_bottom_2nd1])
a.set_constraint(c)

### Quantum Espresso ###

command = ''
#command='mpirun -np 4 ./pw.x -in espresso.pwi > espresso.pwo'

if calculation=='scf':
    calc = Espresso( pseudo_dir=pseudo_dir,
                     pseudopotentials=pseudopotentials,
                     calculation=calculation,
                     kpts=kpts,
                     ecutwfc=ecutwfc,
                     command=command )
elif calculation=='relax':
    calc = Espresso( pseudo_dir=pseudo_dir,
                     pseudopotentials=pseudopotentials,
                     calculation=calculation,
                     kpts=kpts,
                     ecutwfc=ecutwfc,
                     command=command )
elif calculation=='bands':
    calc = Espresso( pseudo_dir=pseudo_dir,
                     pseudopotentials=pseudopotentials,
                     calculation=calculation,
                     nbnd=nbands,
                     ecutwfc=ecutwfc,
                     command=command )

a.calc = calc # add the calculator
a.get_potential_energy() # run pw.x
