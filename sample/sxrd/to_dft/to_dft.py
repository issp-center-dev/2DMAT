from math import cos, sin
import numpy as np
import tomli
from hashlib import algorithms_available
from ase import Atoms
from py2dmat.solver.sim_trhepd_rheed import Solver
from py2dmat._info import Info
import math
import subprocess
import os

Pi = math.pi

file_name = "to_dft_input.toml"

with open(file_name, "rb") as f:
    dirs = tomli.load(f)
    input_main = dirs["Main"]
    input_ase = dirs["ASE"]
    input_sol = dirs["Solver"]
    pseudopotentials = input_sol.pop("pseudo")
    algorithm = input_main["algorithm"]["algorithm"]


lattice = []
vector  = [[] for _ in range(3)]
angular = []
coord_fric =  []
symbol = []
coord_car = []

f_list = os.listdir("./")

for i in f_list:
    if os.path.splitext(i)[1] == '.blk':
        file_name = i

with open("./"+file_name,"r") as f:
    lines = f.readlines()
    lattice = list(map(float,list(filter(None,lines[1].replace('\n','').split(' ')))[0:3]))
    angular = list(map(float,list(filter(None,lines[1].replace('\n','').split(' ')))[3:]))

    for line in lines[2:]:
        coord_fric.append(list(map(float,list(filter(None,line.replace('\n','').split(' ')))[1:4])))
        symbol.append(line.replace('\n','').split(' ')[0])

angular = [2*Pi*x/360 for x in angular]

vector[0] = [lattice[0],0,0]
vector[1] = [cos(angular[2])*lattice[1],sin(angular[2])*lattice[1],0]
vector[2] = [lattice[2]*cos(angular[1]),(lattice[2]*cos(angular[0])-cos(angular[1])*cos(angular[2]))/sin(angular[2]),lattice[2]*(1+2*cos(angular[0])*cos(angular[1])*cos(angular[2])-pow(cos(angular[0]),2)-pow(cos(angular[1]),2)-pow(cos(angular[2]),2))**0.5/sin(angular[0])]

coord_car = np.dot(coord_fric,vector).tolist()

surf_symbol = []
surf_coord_fric = []
surf_disvector = []

with open("./2dmat_input.toml", "rb") as f:
    toml_dict = tomli.load(f)
    for domain in toml_dict["solver"]["param"]["domain"]:
        for atom in domain["atom"]:
            surf_symbol.append(atom["name"])
            surf_coord_fric.append(atom["pos_center"])
            surf_disvector.append(atom["displace_vector"][0])

if toml_dict["algorithm"]["name"] == "mapper":
    with open("./ColorMap.txt","r") as f:
        min_r = list(map(float,f.readline().replace('\n','').split(' ')))
        for line in f.readlines():
            line = list(map(float,line.replace('\n','').split(' ')))
            if line[-1]<=min_r[-1]:
                min_r = line
        opti_result = min_r[0:-1]

if toml_dict["algorithm"]["name"] == "minsearch":
    with open("./res.txt","r") as f:
        for line in f.readlines():
            if 'z' in line:
                line = line.replace('\n','').split(' ')
                opti_result.append(float(line[2]))

if algorithm == "exchange" or algorithm == "pamc":
    with open("./best_result.txt","r") as f:
        for line in f.readlines():
            if 'z' in line:
                line = line.replace('\n','').split(' ')
                opti_result.append(float(line[2]))

surf_coord_car = np.dot(surf_coord_fric,vector).tolist()
surf_coord_final = []

for i,atom in enumerate(surf_coord_car):
    surf_disvector[i][-1] = opti_result[surf_disvector[i][0]-1]
    surf_coord_final.append((atom+np.dot(surf_disvector[i][1:],vector)).tolist())

# Extend a, b, layer #

layer = input("# of a-units, b-units & bulk layers: ").split(' ')

for i in range(2):
    bulk_pre = []
    surf_pre = []
    symbol_pre = []
    surf_symbol_pre = []
    for j in range(int(layer[i])-1):
        for atom in coord_car:
            bulk_pre.append((np.array(atom)+(j+1)*np.array(vector[i])).tolist())
        for atom in surf_coord_final:
            surf_pre.append((np.array(atom)+(j+1)*np.array(vector[i])).tolist())
        symbol_pre += symbol
        surf_symbol_pre += surf_symbol
    coord_car += bulk_pre
    surf_coord_final += surf_pre
    symbol += symbol_pre
    surf_symbol += surf_symbol_pre

for i in range(int(layer[2])-1):
    bulk_pre = []
    for atom in coord_car:
        bulk_pre.append((np.array(atom)-(i+1)*np.array(vector[2])).tolist())
    symbol += symbol
    coord_car += bulk_pre

comment = "Lattice= \"{:.8f} {:.8f} {:.8f} {:.8f} {:.8f} {:.8f} {:.8f} {:.8f} {:.8f}\" Properties=species:S:1:pos:R:3 pbc=\"T T T\""\
    .format(vector[0][0], vector[0][1],vector[0][2], vector[1][0],vector[1][1], vector[1][2],vector[2][0], vector[2][1],vector[2][2])

with open("./surf-bulk.xyz","w") as w:
    w.write(str(len(coord_car)+len(surf_coord_final))+"\n")
    w.write(comment+"\n")
    for i in range(len(coord_car)):
        w.write(symbol[i]+' ')
        for j in range(3):
            w.write(str("{:.8f}".format(coord_car[i][j]))+' ')
        w.write("\n")
    for i in range(len(surf_coord_final)):
        w.write(surf_symbol[i]+' ')
        for j in range(3):
            w.write(str("{:.8f}".format(surf_coord_final[i][j]))+' ')
        w.write("\n")

import pprint

print("Parameters for main part")
pprint.pprint(input_main)
print("Parameters for ase part")
pprint.pprint(input_ase)
print("Parameters for solver part")
pprint.pprint(input_sol)
print("Pseudopotentials")
pprint.pprint(pseudopotentials)

### Read/Write file names ###
file_name = "surf-bulk.xyz"
wfile_name = input_main["output_file_head"]

from ase.io.extxyz import read_xyz, write_xyz

atoms = read_xyz(open(file_name), index=0)
atoms_info = Atoms()
for atom in atoms:
    atoms_info += atom
ratoms = atoms_info.get_positions()
satoms = atoms_info.symbols
natoms = ratoms.shape[0]

z_max = np.max(ratoms, axis=0)[2]
z_min = np.min(ratoms, axis=0)[2]
slab_size = z_max - z_min
print('slab_size=', slab_size)
z_margin = input_main["param"]["z_margin"]
z_atoms = ratoms[:, 2]

z_bottom_most = [z_min - z_margin, z_min + z_margin]
second_min_index = np.where(np.sort(z_atoms) > z_min)[0][0]
z_bottom_2nd_val = np.sort(z_atoms)[second_min_index]
z_bottom_2nd = [z_bottom_2nd_val - z_margin, z_bottom_2nd_val + z_margin]

atoms_bottom_most = Atoms()
for idx in reversed(np.where((z_atoms <= z_bottom_most[1]) & (z_atoms >= z_bottom_most[0]))[0]):
    atoms_bottom_most += atoms_info.pop(idx)
ratoms_bottom_most = atoms_bottom_most.get_positions()
ratoms_bottom_2nd = ratoms[np.where((z_atoms <= z_bottom_2nd[1]) & (z_atoms >= z_bottom_2nd[0]))]

### Add Hydrogen terminators ###
r_SiH = input_main["param"]["r_SiH"]
theta = input_main["param"]["theta"]

dx = r_SiH * math.sin(math.radians(theta * 0.5))
dy = dx
dz = r_SiH * math.cos(math.radians(theta * 0.5))

tmp_x_idx = np.arange(ratoms_bottom_most.shape[0])
tmp_y_idx = np.arange(ratoms_bottom_2nd.shape[0])
xx, yy = np.meshgrid(tmp_x_idx, tmp_y_idx)
rxy_atoms_most = ratoms_bottom_most[:, :2]
rxy_atoms_2nd = ratoms_bottom_2nd[:, :2]
distances = np.linalg.norm(rxy_atoms_most[xx] - rxy_atoms_2nd[yy], axis=2)

for idx, r2 in enumerate(ratoms_bottom_2nd):
    r1 = ratoms_bottom_most[np.argmin(distances[:, idx])]
    x12 = r1[0] - r2[0]
    y12 = r1[1] - r2[1]
    if (np.abs(x12) < 1e-12 and np.abs(y12) > 1e-12) or (np.abs(x12) > 1e-12 and np.abs(y12) < 1e-12):
        print('(001)surface')
        if np.abs(x12) < 1e-12:
            atoms_info += Atoms(numbers=[1, 1],
                                positions=[(r2[0], r2[1] - dy, r2[2] - dz), (r2[0], r2[1] + dy, r2[2] - dz)])
        else:
            atoms_info += Atoms(numbers=[1, 1],
                                positions=[(r2[0] - dx, r2[1], r2[2] - dz), (r2[0] + dx, r2[1], r2[2] - dz)])
    elif np.abs(x12) < 1e-12 and np.abs(y12) < 1e-12:
        print('(111)surface')
        atoms_info += Atoms(numbers=[1], positions=[(r2[0], r2[1], r2[2] - r_SiH)])

print("Symbols = {}".format(atoms_info.symbols))
print("natoms = {}".format(len(atoms_info)))
### Get cell info ###
#  The input XYZ file is assumed to have the cell info
#  at the last two lines
a1 = input_main["lattice"]["unit_vec"][0]
a2 = input_main["lattice"]["unit_vec"][1]
a3 = np.array([0.0, 0.0, slab_size + input_main["param"]["slab_margin"]])
atoms_info.set_cell(np.array([a1, a2, a3]))
comment = "Lattice= \"{} {} {} {} {} {} {} {} {}\" Properties=species:S:1:pos:R:3 pbc=\"T T T\"".format(a1[0], a1[1],
                                                                                                        a1[2], a2[0],
                                                                                                        a2[1], a2[2],
                                                                                                        a3[0], a3[1],
                                                                                                        a3[2])
write_xyz(open(wfile_name + ".xyz", "w"), atoms_info, comment)
from ase.io import read, write

ase_union = read(wfile_name + ".xyz")
### CIF file ###
ase_union.write(wfile_name + '.cif', format='cif')
### Constraints ###
from ase.constraints import FixAtoms

z_atoms = atoms_info.get_positions()[:, 2]
ase_union.set_constraint(FixAtoms(indices=np.where(z_atoms <= z_bottom_2nd[1])[0]))

### Quantum Espresso ###
from ase.calculators.espresso import Espresso

calculation = input_sol["control"]["calculation"]
kpts = input_ase["kpts"]
command = input_ase["command"]
if calculation == 'scf':
    qe = Espresso(input_data=input_sol,
                  pseudopotentials=pseudopotentials,
                  kpts=kpts,
                  command=command)
elif calculation == 'relax':
    qe = Espresso(input_data=input_sol,
                  pseudopotentials=pseudopotentials,
                  kpts=kpts,
                  command=command)
elif calculation == 'bands':
    qe = Espresso(input_data=input_sol,
                  pseudopotentials=pseudopotentials,
                  kpts=kpts,
                  command=command)
ase_union.calc = qe
ase_union.calc.write_input(atoms_info)
try:
    ase_union.get_potential_energy()  # run pw.x
except:
    print("Calculation of get_potential_energy is not normally finished.")
    pass
