#!/bin/bash
# Script to build mingwpy on Appveyor systems
# Expects (default)
#  BITS: 64

# The directory from which script was called
our_wd=$(cygpath "$START_DIR")

BITS=${BITS:-64}
buildroot="${our_wd}/build"
rm -rf $buildroot
mkdir $buildroot

if [ "$BITS" == "64" ]; then
    mw_arch=x86_64
    mw_march="x86-64"
    mw_exceptions=seh
else
    mw_arch=i686
    mw_march=pentium4
    mw_exceptions=sjlj
fi

pacman -Sy --noconfirm git svn zip tar autoconf make libtool automake p7zip \
    patch bison gettext-devel wget sshpass texinfo dejagnu
pacman -Rs --noconfirm gcc gcc-fortran

cd $our_wd/mingw-builds
./build --mode=gcc-5.3.0 --static-gcc --arch=$mw_arch --march-x64="$mw_march" \
    --mtune-x$BITS='generic' --rev=201603 --rt-version=trunk --threads=win32 \
    --exceptions=$mw_exceptions --enable-languages=c,c++,fortran \
    --buildroot=$buildroot --bootstrap --no-multilib --bin-compress

ls $buildroot
