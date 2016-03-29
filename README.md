The goal of *mingwpy* project is to provide a free toolchain for building Python extensions for Windows OS, and make sure that those extensions are compatible with CPython compiled with native Visual Studio.

*mingwpy* toolchain contains customized gcc, g++ and gfortran compilers of the [GNU toolchain](https://en.wikipedia.org/wiki/GNU_toolchain) based on the [Mingw-w64](http://mingw-w64.org) and the [mingw-builds](https://github.com/niXman/mingw-builds) projects.

 * Documentation: https://mingwpy.github.io/
 * Discussions: https://groups.google.com/forum/#!forum/mingwpy

### Installing built mingwpy toolchain with pip

Experimental builds of mingwpy for Python 2.7 and 3.4 are available for testing purposes:

    pip install -i https://pypi.anaconda.org/carlkl/simple mingwpy

Note: [Python 3.5 is not supported yet](https://mingwpy.github.io/issues.html#choice-of-msvc-runtime).

### Building mingwpy yourself

#### Prerequisites: Install MSYS2 for mingw-builds

Install https://msys2.github.io/ "Unix environment" for Windows to be able
to run `mingw-builds` scripts.

*NEVER* use an installation path for msys2 containing SPACES or other special characters!

Use `pacman` from MSYS2 to install `mingw-builds` dependencies:

    pacman -Sy --noconfirm git svn zip tar autoconf make libtool automake p7zip \
        patch bison gettext-devel wget sshpass texinfo

Now make sure the `mingw-w64` toolchain is NOT installed by `pacman`, because we
are going to build our own:

    $ gcc -v
    bash: gcc: command not found

Clone customized `mingw-builds` scripts:

    git clone -b mingwpy-dev https://github.com/mingwpy/mingw-builds.git
    cd mingw-builds

The `mingw-builds` build scripts in turn download the rest of prerequisites
for building GCC compiler.

#### Build 64-bit toolchain

To download only (to build later):

    ./build --mode=gcc-5.3.0 --static-gcc --arch=x86_64 --march-x64='x86-64' \
        --mtune-x64='generic' --rev=201603 --rt-version=trunk --threads=win32 \
        --exceptions=seh --enable-languages=c,c++,fortran --fetch-only

To download and build all at once:

    ./build --mode=gcc-5.3.0 --static-gcc --arch=x86_64 --march-x64='x86-64' \
        --mtune-x64='generic' --rev=201603 --rt-version=trunk --threads=win32 \
        --exceptions=seh --enable-languages=c,c++,fortran \
        --buildroot=/tmp/x86_64 --bootstrap --no-multilib --bin-compress --jobs=4

#### Build 32-bit toolchain

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

#### Configuring the toolchain for a specific version of CPython

The toolchain needs to know which version of Visual Studio to target. Each Python is compiled with different VS version, so you need to tune the toolchain by copying appropriate spec files, see
[readme_specs.md](https://github.com/mingwpy/mingwpy/blob/master/specs/readme_specs.md).

