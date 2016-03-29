#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# The code is placed into public domain by:
#   anatoly techtonik <techtonik@gmail.com>

#
# Bootstrap dependencies for compiling Mingwpy
# toolchain on Windows
#
# Securely fetch files using known hash/size
# combination, unpack them locally into .locally/
# subdir.

# --- bootstrap .locally --
#
# creates .locally/ subdirectory in the script's dir
# and sets a few global variables for convenience:
#
#   ROOT  - absolute path to source code checkout dir
#   LOOT  - absolute path to the .locally/ subdir
#
# provides some helpers:
#
#   unzip(zippath, target, subdir=None)
#                    - extracts subdir from the zip file
#   getsecure(targetdir, filespec, quiet=False)
#                    - download file and check hash/size

# ------------------------------ Data ---

"""
Every entry in specification for downloaded files below
contains following *required* fields:

  filename     - file is saved under this name in LOOT dir
                 (because file detection is not secure)
  hashsize     - to ensure that file is right
  url          -
  check        - LOOT path to check that file is unpacked

These fields are *optional*:

  name         - convenient name for dependency data
  unpackto     - LOOT path to unpack to
                 (in case archive doesn't have top dir)

Let's say this is filespec version 1.0
"""

filespec = [
  # tools needed for bootstrap
  dict(
    filename='7za920.zip',
    hashsize='9ce9ce89ebc070fea5d679936f21f9dde25faae0 384846',
    url='http://downloads.sourceforge.net/sevenzip/7za920.zip',
    check='7zip'
  ),
]

# tools needed to build gcc and friends
filespec32 = filespec + [
  dict(
    filename='msys2-base-i686-20160205.tar.xz',
    hashsize='2aa85b8995c8ab6fb080e15c8ed8b1195d7fc0f1 45676948',
    url='https://prdownloads.sourceforge.net/msys2/msys2-base-i686-20160205.tar.xz',
    check='msys32',
  ),
]

# tools needed to build gcc and friends
filespec64 = filespec + [
  dict(
    filename='msys2-base-x86_64-20160205.tar.xz',
    hashsize='bd689438e6389064c0b22f814764524bb974ae5b 44942956',
    url='https://prdownloads.sourceforge.net/msys2/msys2-base-x86_64-20160205.tar.xz',
    check='msys64',
  ),
]


# ------------------------------ Code ---

# --- create .locally/ subdir ---
import os
import platform
import sys

PY3K = sys.version_info >= (3, 0)
OS64BIT = platform.machine().endswith('64')

ROOT = os.path.abspath(os.path.dirname(__file__))
LOOT = os.path.join(ROOT, '.locally/')
if not os.path.exists(LOOT):
  os.mkdir(LOOT)

# ---[ utilities ]---

# from locally ...

import os
from hashlib import sha1
from os.path import exists, getsize, join
if PY3K:
  import urllib.request as urllib
else:
  import urllib

def hashsize(path):
  '''
  Generate SHA-1 hash + file size string for the given
  filename path. Used to check integrity of downloads.
  Resulting string is space separated 'hash size':

    >>> hashsize('locally.py')
    'fbb498a1d3a3a47c8c1ad5425deb46b635fac2eb 2006'
  '''
  size = getsize(path)
  h = sha1()
  with open(path, 'rb') as source:
    while True:
      # read in 64k blocks, because some files are too big
      # and free memory is not enough
      c = source.read(64*1024)
      if not c:
        break
      h.update(c)
  return '%s %s' % (h.hexdigest(), size)

class HashSizeCheckFailed(Exception):
  '''Throw when downloaded file fails hash and size check.'''
  pass

def getsecure(targetdir, filespec, quiet=False):
  '''
  Using description in `filespec` list, download
  files from specified URL (if they don't exist)
  and check that their size and sha-1 hash matches.

  Files are downloaded into `targetdir`. `filespec`
  is a list of entries, each entry is a dictionary
  with obligatory keys: filename, hashsize and url.

    filespec = [ {
      'filename': 'wget.py',
      'hashsize': '4eb39538d9e9f360643a0a0b17579f6940196fe4 12262',
      'url': 'https://bitbucket.org/techtonik/python-wget/raw/2.0/wget.py'
    } ]

  Raises HashSizeCheckFailed if hash/size check
  fails. Set quiet to false to skip printing
  progress messages.
  '''
  # [-] no rollback
  def check(filepath, shize):
    """Checking hash/size for the given file"""
    if hashsize(filepath) != shize:
      raise HashSizeCheckFailed(
                'Hash/Size mismatch for %s\n  exp: %s\n  act: %s'
                % (filepath, shize, hashsize(filepath)))

  for entry in filespec:
    filepath = join(targetdir, entry['filename'])
    if exists(filepath):
      if 'hashsize' not in entry:
        if not quiet:
          print("skipping - %-32s - downloaded, no hashsize" % entry['filename'])
          continue

      check(filepath, entry['hashsize'])
      if not quiet:
        print("skipping - %-32s - downloaded, hashsize ok" % entry['filename'])
      continue

    # file does not exists
    if not quiet:
      print("Downloading %s into %s" % (entry['filename'], targetdir))
    urllib.urlretrieve(entry['url'], filepath)
    if 'hashsize' not in entry:
      if not quiet:
        print("Hash/size is not set, skip check..")
      continue

    if not quiet:
      print('Checking hash/size for %s' % filepath)
    try:
      check(filepath, entry['hashsize'])
    except HashSizeCheckFailed:
      # [x] remove file only if it was just downloaded
      os.remove(filepath)
      raise

def unzip(zippath, target, subdir=None, verbose=0):
  '''extract entries from `subdir` of `zipfile` into `target/` directory'''
  import os
  from os.path import join, exists, dirname
  import shutil
  import zipfile
  zf = zipfile.ZipFile(zippath)
  
  dirs = set()  # cache to speed up dir creation

  for entry in zf.namelist():
    # [ ] normalize entry (remove .. and / for security)
    if subdir:
      if not entry.startswith(subdir + '/'):
        continue
      else:
        outfilename = join(target, entry.replace(subdir + '/', ''))
    else:
      outfilename = join(target, entry)

    if outfilename.endswith('/'):
      # directory entry
      if not exists(outfilename):
        os.makedirs(outfilename)
    else:
      # file entry
      # some .zip files don't have directory entries
      outdir = dirname(outfilename)
      if (outdir not in dirs) and not exists(outdir):
          os.makedirs(outdir)
          dirs.add(outdir)

      if verbose: 
        print(outfilename)

      outfile = open(outfilename, "wb")
      infile = zf.open(entry)
      shutil.copyfileobj(infile, outfile)
      outfile.close()
      infile.close()
  zf.close()


# from shellrun 2.0

import subprocess

class Result(object):
    def __init__(self, command=None, retcode=None, output=None):
        self.command = command or ''
        self.retcode = retcode
        self.output = output
        self.success = False
        if retcode == 0:
            self.success = True

def run(command):
    """
    Run `command` through shell and wait for it to complete.
    stdin/stdout/stderr are shared with Python, so the output
    is immediately visible and not captured. Returns Result
    with command, retcode and success attributes.

    - return code
    - no stdout capture
    - no stderr capture
    - no deadlocks or MemoryError
    - stdout, stderr and stdin are shared with Python process

   ┌─────────┐             ┌────────┐                   ┌─────────┐
   │  Parent │>─(stdin)─┬─>│ Python ├─────┬──(stdout)──>│  Parent │
   │(console)│          │  │ script ├─────│┬─(stderr)──>|(console)│
   └─────────┘          │  └────────┘     ││            └─────────┘
                        │  ┌────────────┐ ││
                        └─>│ Subprocess ├─┘│
                           │  (shell)   ├──┘
                           └────────────┘
    """
    process = subprocess.Popen(command, shell=True)
    process.communicate()
    return Result(command=command, retcode=process.returncode)

def run_capture_limited(command, maxlines=20000):
    """
    Run `command` through a system shell, return last `maxlines`
    as `output` string in Result object. 

        res.output       - output
        res.succeeded    - result of the operation True/False
        res.return_code  - specific return code

    ┌─────────┐ (stdin) ┌─────────────┐            ┌─────────┐
    │  Parent │>──┬────>│ Python      ├─(stdout)──>│  Parent │
    │(console)│   │     │ script      ├─(stderr)──>│(console)│
    └─────────┘   │     └───────────^─┘            └─────────┘
                  │  ┌────────────┐ │
                  └─>│ Subprocess ├─┤ (buffer: stdout+stderr
                     │  (shell)   ├─┘   limited to maxlines)
                     └────────────┘

    [x] start reader thread
      [x] reader: wait for lines
      [x] wait for process to complete
      [x] reader: wait for EOF

    [ ] may not be a binary accurate read, because of \n split
        and reassembly, needs testing
    [ ] buffer size is line limited, test big streams without
        newlines

    [ ] need tests for missing output
      [ ] process finished, pipe closed, did reader thread get
          all the output? when pipe closes? is it possible to
          miss the data?

    [ ] access local buffer from outside
      [ ] show current buffer contents if needed
      [ ] show current line count if needed
    """

    import collections
    import threading

    lines = collections.deque(maxlen=maxlines)
    def reader_thread(stream, lock):
        for line in stream:
            if not PY3K:
                lines.append(line)
            else:
                # the only safe way to decode *any* binary data to
                # string http://stackoverflow.com/a/27527728/239247
                lines.append(line.decode('cp437'))

    outpipe = subprocess.PIPE
    errpipe = subprocess.STDOUT
    process = subprocess.Popen(command, shell=True, stdout=outpipe,
                                                    stderr=errpipe)
    lock = threading.Lock()
    thread = threading.Thread(target=reader_thread, args=(process.stdout, lock))
    thread.start()

    # With communicate() we get in thread:
    #   ValueError: I/O operation on closed file
    # or in main thread
    #   IOError: close() called during concurrent operation on the same file object.
    #out, _ = process.communicate()
 
    process.wait()
    thread.join()

    return Result(command=command,
                  retcode=process.returncode,
                  output=''.join(lines))


# ---[ /utilities ]---


if __name__ == '__main__':

  # --- helpers ---

  if OS64BIT:
    BASH = LOOT + '/msys64/usr/bin/bash'
  else:
    BASH = LOOT + '/msys32/usr/bin/bash'

  def path2unix(path):
    """ convert Windows path "E:\path" to unix "/e/path" """
    return '/' + path[0].lower() + path[2:].replace('\\', '/')

  def bash(command, capture=False, verbose=True):
    """ run command inside MSYS2 environment.
        bash always starts in $HOME directory """
    global BASH
    cmd = BASH + ' --login -c "{}"'.format(command)
    if verbose:
      print("BASH: " + cmd)
    if capture:
      return run_capture_limited(cmd)
    else:
      return run(cmd)

  # /-- helpers ---


  print('---[ download dependencies ]---')

  if OS64BIT:
    speccy = filespec64
  else:
    speccy = filespec32
  getsecure(LOOT, speccy)

  print('---[ unpack dependencies ]---')

  def unzip_if_not_exists(archive, path):
    if exists(LOOT + path):
      print('(skip) %s is unpacked' % path)
    else:
      print('Unpacking %s from %s' % (path, archive))
      unzip(LOOT + filename, LOOT + path)

  # unpacking 7zip
  filename = filespec.pop(0)['filename']
  if '7z' not in filename:
    sys.exit('Error: 7zip entry must be the first in filespec')
  unzip_if_not_exists(filename, '7zip')
  cmd7zip = os.path.normpath(LOOT + '7zip/7za.exe')

  # unpacking everything else
  for entry in speccy:
    fname = entry['filename']

    targetdir = LOOT
    if 'unpackto' in entry:
      targetdir += entry['unpackto']
    unpacked = exists(LOOT + entry['check'])

    if unpacked:
      print('(skip) %s is unpacked' % fname)
    else:
      if 'unpackto' in entry:
        print('unpacking %s to %s' % (fname, entry['unpackto']))
      else:
        print('unpacking %s' % fname)
      if fname.endswith('.zip'):
        unzip(LOOT + fname, targetdir)
      else:
        if fname.endswith('.tar.gz') or fname.endswith('.tar.xz') or fname.endswith('.txz'):
          cmd = '"%s" x -so "%s" | "%s" x -y -si -ttar -o"%s"' % (cmd7zip, LOOT + fname, cmd7zip, targetdir)
        else:
          cmd = '"%s" x -y -bd -o"%s" "%s"' % (cmd7zip, targetdir, LOOT + fname)
        r = run_capture_limited(cmd, maxlines=10)
        if not r.success:
          print('error: command failed')
          print('  %s' % r.command)
          print('output:')
          for line in r.output.splitlines():
            print('  '+line)
            sys.exit(-1)


  print('---[ running checks ]---')

  if ' ' in os.getcwd():
    # MSYS2 is sensitive to spaces in paths
    sys.exit('check failed: current path contains spaces')

  print('---[ configuring MSYS2 ]---')

  # do first time setup
  bash('exit')
  # update pacman database
  bash('pacman -Sy')
  # install packages
  res = bash('pacman -S --needed --noconfirm git subversion tar zip p7zip make patch automake libtool bison gettext-devel wget sshpass texinfo')

  # check that gcc is not installed
  res = bash('gcc -v 2> /dev/null')
  if res.retcode != 127:
    sys.exit('check failed: gcc is installed')

  print('')
  print('---[ cloning custom mingw-build scripts ]---')
  run('git clone -b mingwpy-dev https://github.com/mingwpy/mingw-builds.git')

  print('')
  print('---[ configuring build paths and options ]---')
  print('Boot CWD: ' + os.getcwd())
  print('Bash CWD: ' + bash('pwd', capture=True, verbose=False).output)

  # calculating names to change working directory in MSYS2
  builddir = path2unix(os.getcwd() + '/build')
  workdir = path2unix(os.getcwd() + '/mingw-builds')

  
  cmdbase = "cd " + workdir
  cmdbase += "; ./build --mode=gcc-5.3.0 --static-gcc --threads=win32 --enable-languages=c,c++,fortran "
  cmdbase += " --rt-version=trunk --rev=201603 "

  cmd32base = cmdbase + " --arch=i686 --march-x32='pentium4' --mtune-x32='generic' --exceptions=sjlj "
  cmd32base += " --buildroot={}/i686".format(builddir)
  cmd32fetch = cmd32base + " --fetch-only "
  # multilib is disabled for all configurations
  #if not OS64BIT:
  #  # CC multilib allows installation of 32-bit and 64-bit libraries in parallel
  #  print('WARNING: Host platform is 32-bit, adding --no-multilib to build options')
  #  cmd32build += " --no-multilib"
  cmd32build = cmd32base + " --bootstrap --no-multilib --bin-compress --jobs=4"

  cmd64base = cmdbase + "--arch=x86_64 --march-x64='x86-64 --mtune-x64='generic' --exceptions=seh "
  cmd64base += " --buildroot={}/x86_64".format(builddir)
  cmd64fetch = cmd64base + " --fetch-only "
  cmd64build = cmd64base + " --bootstrap --no-multilib --bin-compress --jobs=4"


  print('')
  print('---[ fetching toolchains and writing .bat files ]---')

  def batman(batfile, command):
    global BASH
    content = """\
@echo off
{bash} --login -c "{cmd} %*"
""".format(bash=BASH, cmd=command)
    open(batfile, 'wb').write(content)

  print('')
  print('--- fetch and setup 32-bit toolchain ---')
  bash(cmd32fetch)
  batman(ROOT + '/build32.bat', cmd32build)

  print('')
  print('--- fetch and setup 64-bit toolchain ---')
  if not OS64BIT:
    print('WARNING: Host platform is 32-bit, skipping 64-bit build...')
  else:
    bash(cmd64fetch)
    batman(ROOT + '/build64.bat', cmd64build)

  print('')
  print('Run build32.bat or build64.bat to build the toolchain.')
  print('Done.')
