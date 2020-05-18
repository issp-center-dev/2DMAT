rm -rf ./mapper0*
rm -f ./devided_MeshData00000000.txt
rm -f ./log.txt
rm -f ./ColorMap.txt

ln -sf ../../../src/original/mapper_mpi_py2.py .
ln -sf ../../../src/TRHEPD/bulk.exe .
ln -sf ../../../src/TRHEPD/surf.exe .
