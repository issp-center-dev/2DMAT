if [ ! -e leedsatl.zip ]; then
  wget http://www.icts.hkbu.edu.hk/VanHove_files/leed/leedsatl.zip -O leedsatl.zip
fi
rm -rf leedsatl
unzip leedsatl.zip -d leedsatl
cp leedsatl/leedsatl.m1 leedsatl/satl1.f
cp leedsatl/leedsatl.m2 leedsatl/satl2.f
cp leedsatl/leedsatl.sb leedsatl/satl_sub.f
patch -up0 < leedsatl.patch
cat << EOF > leedsatl/Makefile
all: satl1.exe satl2.exe
satl1.exe: satl1.f satl_sub.f
	gfortran -o satl1.exe satl1.f satl_sub.f
satl2.exe: satl2.f satl_sub.f
	gfortran -o satl2.exe satl2.f satl_sub.f
clean:
	rm -rf satl1.exe satl2.exe
EOF
cd leedsatl
make
