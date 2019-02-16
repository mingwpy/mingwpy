#!/bin/bash
# Script to build mingwpy on Appveyor systems
# Expects (default)
#  START_DIR: ($PWD if not set)
#  GCC_VER: 5.3.0
#  REV_NO: 201812
#  BITS: 64

# The directory from which script was called
if [ -n "${START_DIR}" ]; then
    our_wd=$(cygpath "$START_DIR")
else  # Or maybe we're sourcing directly
    our_wd=$PWD
fi

# Version of gcc to build
GCC_VER=${GCC_VER:-5.3.0}
# Revision number to append to build name
REV_NO=${REV_NO:-201812}
# Number of threads to use for make step
N_THREADS=${N_THREADS:-4}
# 32 or 64 bits?
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
pacman -Sy --noconfirm git subversion tar zip make patch automake autoconf libtool bison gettext-devel texinfo autogen
pacman -Sy --noconfirm p7zip sshpass dejagnu

cd $our_wd/mingw-builds
./build --mode=gcc-${GCC_VER} \
    --static-gcc \
    --arch=$mw_arch --march-x64="$mw_march" \
    --mtune-x$BITS='generic' \
    --rev=${REV_NO} \
    --rt-version=trunk \
    --threads=win32  --exceptions=$mw_exceptions \
    --enable-languages=c,c++,fortran \
    --buildroot=$buildroot --bootstrap --no-multilib --bin-compress \
    --jobs=${N_THREADS}

ls $buildroot
