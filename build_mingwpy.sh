#!/bin/bash
# Script to build mingwpy on Appveyor systems
# Expects (default)
#  START_DIR: ($PWD if not set)
#  GCC_VER: 8.2.0
#  REV_NO: 201812
#  BITS: 64

# The directory from which script was called
if [ -n "${START_DIR}" ]; then
    our_wd=$(cygpath "$START_DIR")
else  # Or maybe we're sourcing directly
    our_wd=$PWD
fi

GCC_VER=${GCC_VER:-8.2.0}
REV_NO=${REV_NO:-201812}
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

# Remove competing gcc / gfortrans
pacman -Rs --noconfirm gcc gcc-fortran mingw-w64-${mw_arch}-toolchain

# Install some needed packages
pacman -Sy --noconfirm p7zip sshpass dejagnu

cd $our_wd/mingw-builds
./build --mode=gcc-${GCC_VER} \
    --static-gcc \
    --arch=$mw_arch --march-x64="$mw_march" \
    --mtune-x$BITS='generic' \
    --rev=${REV_NO} \
    --rt-version=v6 \
    --threads=win32  --exceptions=$mw_exceptions \
    --enable-languages=c,c++,fortran \
    --buildroot=$buildroot --bootstrap --no-multilib --bin-compress

ls $buildroot
