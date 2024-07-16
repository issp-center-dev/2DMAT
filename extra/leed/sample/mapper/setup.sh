#!/bin/sh

set -e

#if [ ! -e leedsatl.zip ]; then
#  wget http://www.icts.hkbu.edu.hk/VanHove_files/leed/leedsatl.zip -O leedsatl.zip
#fi
rm -rf leedsatl
unzip leedsatl.zip -d leedsatl
cd leedsatl
tr -d '\r' < leedsatl.m1 > satl1.f
tr -d '\r' < leedsatl.m2 > satl2.f
tr -d '\r' < leedsatl.sb > satl_sub.f
patch -up1 < ../leedsatl.patch
cat << EOF > Makefile
all: satl1.exe satl2.exe
satl1.exe: satl1.f satl_sub.f
	gfortran -g -O2 -o satl1.exe satl1.f satl_sub.f
satl2.exe: satl2.f satl_sub.f
	gfortran -g -O2 -o satl2.exe satl2.f satl_sub.f
clean:
	rm -rf satl1.exe satl2.exe
EOF
make
