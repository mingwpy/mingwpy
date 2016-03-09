# mingwpy customization of mingw-builds

## prepare msys2 to allow mingw-builds to run

Install and update a fresh msys2 from https://msys2.github.io according to the instructions given there.

*NEVER* use an installation path for msys2 containing SPACES or other special characters!

Now install the following tools and programs with the help of pacman:

    pacman -Sy --noconfirm git svn zip tar autoconf make libtool automake p7zip \
        patch bison gettext-devel wget sshpass texinfo

Now make sure the mingw-w64 toolchain supplied by pacman is NOT installed:

`gcc -v` should show the following error: `bash: gcc: command not found`

Clone the custimized mingw-builds scripts:

    git clone -b mingwpy-dev https://github.com/mingwpy/mingw-builds.git
    cd mingw-builds`

The mingw-builds build script is responsible to download an approbriate toolchain needed for  the gcc build process.

## build the 64-bit toolchain

To download only (to build later):

    ./build --mode=gcc-5.3.0 --static-gcc --arch=x86_64 --march-x64='x86-64' \
        --mtune-x64='generic' --rev=201603 --rt-version=trunk --threads=win32 \
        --exceptions=seh --enable-languages=c,c++,fortran --fetch-only

To download and build all at once:

    ./build --mode=gcc-5.3.0 --static-gcc --arch=x86_64 --march-x64='x86-64' \
        --mtune-x64='generic' --buildroot=/tmp/x86_64 --rev=201603 --rt-version=trunk \
        --threads=win32 --exceptions=seh --enable-languages=c,c++,fortran --bootstrap \
        --no-multilib --bin-compress --jobs=4

## build the 32-bit toolchain

To download only (to build later):

    ./build --mode=gcc-5.3.0 --static-gcc --arch=i686 --march-x32='pentium4' \
        --mtune-x32='generic' --buildroot=/tmp/i686 --rev=201603 --rt-version=trunk \
        --threads=win32 --exceptions=sjlj --enable-languages=c,c++,fortran --fetch-only

To download and build all at once:

    ./build --mode=gcc-5.3.0 --static-gcc --arch=i686 --march-x32='pentium4' \
        --mtune-x32='generic' --buildroot=/tmp/i686 --rev=201603 --rt-version=trunk \
        --threads=win32 --exceptions=sjlj --enable-languages=c,c++,fortran --bootstrap \
        --no-multilib --bin-compress --jobs=4

The build process can be accelerated with the flag`--jobs=N`. The number `N` given should be the number of cores 
availabe for the build process.

The toolchains are fully portable and can be unpacked without admin rights or other installation hussles. As some 
build systems doesn't like paths with spaces or other special characters it is recommended to avoid such paths. 
To use the toolchain it is necessary to find the executables in the `bin` folder. This can be achieved with 
extending the `PATH` environment variable 

To use the toolchains for CPython please perform the step described in [readme_specs.md](https://github.com/mingwpy/mingwpy/blob/master/specs/readme_specs.md).
