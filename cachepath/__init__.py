# -*- coding: utf-8 -*-

"""
Package that provides CachePath, as well as exporting a Python2/3 compatible Path.
"""

__author__ = """Hayden Flinner"""
__email__ = 'hayden@flinner.me'
__version__ = '0.1.0'

try:
    from pathlib import Path, WindowsPath, PosixPath, _windows_flavour, _posix_flavour
except:  # py2
    from pathlib2 import Path, WindowsPath, PosixPath, _windows_flavour, _posix_flavour

import os
import shutil
__all__ = [
    'CachePath',
    'Path',  # Helpful re-export for those who want Py2 compatibility
    'clear',
    'rm',
]

sep = _windows_flavour.sep if os.name == 'nt' else _posix_flavour.sep

import tempfile
location = tempfile.gettempdir()

def clear(path):
    """Clear the file/dir, leaving it empty (dir) or 0 length (file)."""
    if path.is_dir():
        for sub in path.iterdir():
            if sub.is_dir():
                shutil.rmtree(sub)
            else:
                sub.unlink()
    else:
        with path.open('w'):
            pass

def rm(path):
    """Delete the file/dir, even if it's a dir with files in it."""
    if path.is_dir:
        shutil.rmtree(str(path))
    else:
        path.unlink()

class CachePath(Path):
    """Construct a CachePath from one or several strings/Paths.

    Constructing a CachePath automatically creates the file/folder it points to
    if it doesn't already exist, as well as any preceding folders.

    CachePaths also have a few helper methods:

        :func:`CachePath().clear() <cachepath.clear>`

        :func:`CachePath().rm() <cachepath.rm>`

        By accident, these methods are also attached to regular Paths after
        constructing a CachePath, but it's not recommended to depend on this
        behavior.

    Examples
    --------
    Basic Usage::

        CachePath() == '/tmp/xyz123randomfile'
        CachePath('myfilename') == '/tmp/myfilename'
        CachePath('myfolder', dir=True) == '/tmp/myfolder/'

    Multi-component Paths::

        p = CachePath('date/processed_data', dir=True)
        # Or, Alternate constructor to avoid {}/{}.format()
        p = CachePath('date', 'processed_data', dir=True)

    For an example of real usage, we'll hack a cache for a website scraper,
    useful if, you're working on your parsing logic and/or want
    the files that were used to be available on disk instead of just in memory.
    ::
        def get_scraped_ebay_stats(product_id):
            p = CachePath('ebay_results/{}'.format(product_id))
            if not p.exists():
               sh('wget {}'.format(p))
            return parser.parse(p.read_text())

    Parameters
    ----------
    *args : [str], optional
        List of strings to join for Path. If None, ``getempfile`` is used.

    *dir: bool, optional
        Is the path intended to be a directory? Useful when you just need a
        tempdir for lots of files, and you don't want to make a CachePath
        out of each. ::

            d = CachePath(date, dir=True)
            (d/'tool1results').touch()
            (d/'tool2results').touch()
            list(d.iterdir()) == ['tool1results', 'tool2results']

    *mode : int, optional
        Mode to create file with, if it doesn't already exist.
    """

    def __new__(cls, *args, dir=False, mode=0o666):
        if not args:
            args = [tempfile.mktemp(dir=location)]
        if cls is CachePath:
            cls = WindowsPath if os.name == 'nt' else PosixPath
        returning = cls._from_parts([location, *args])
        cls.clear = clear
        cls.rm = rm

        # Create all of the dirs leading to the path, if they don't exist.
        # If the path is supposed to be a directory, make that too.
        dirp = returning if dir else returning.parent
        dirp.mkdir(exist_ok=True, parents=True)

        return returning
