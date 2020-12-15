sh prepare.sh

./bulk.exe

time mpiexec --oversubscribe -np 4 python3 ../../../src/py2dmat/main.py input.toml

# echo diff ColorMap.txt ref_ColorMap.txt
# diff ColorMap.txt ref_ColorMap.txt
# if [ $? == 0 ]; then
#   echo TEST PASS
# else
#   echo TEST FAILED: ColorMap.txt and ref_ColorMap.txt differ
# fi
#
