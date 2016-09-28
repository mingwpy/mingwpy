this is a temporary folder with additional specs and resource files needed for the standalone toolchains.

- `32 bit python-2.6 .. 3.2`: copy files and folders from [msvcr90/i386](https://github.com/mingwpy/mingwpy/blob/master/specs/msvcr90/i386) to the toolchain folder structure
- `32 bit python-3.3 .. 3.4`: copy files and folders from [msvcr100/i386](https://github.com/mingwpy/mingwpy/blob/master/specs/msvcr100/i386) to the toolchain folder structure
- `64 bit python-2.6 .. 3.2`: copy files and folders from [msvcr90/x86-64](https://github.com/mingwpy/mingwpy/blob/master/specs/msvcr90/x86-64) to the toolchain folder structure
- `64 bit python-3.3 .. 3.4`: copy files and folders from [msvcr100/x86-64](https://github.com/mingwpy/mingwpy/blob/master/specs/msvcr100/x86-64) to the toolchain folder structure


=========HOWTO Use the GCC specs file========
You may use a text editor of your choice to inspect it. It may be confusing at first, but there are many places of interest. To use the specs file, invoke gcc with -specs=<path_to_specs_file> or place it at "/mingw/lib/gcc/mingw32/<version>/specs" to make GCC use it by default, where <version> refers to the GCC version installed.

More info：
http://www.mingw.org/wiki/HOWTO_Use_the_GCC_specs_file
