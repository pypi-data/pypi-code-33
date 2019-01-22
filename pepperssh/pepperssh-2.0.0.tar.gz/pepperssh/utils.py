
import os, zipfile, glob
import subprocess
from os.path import isabs, join, relpath
from contextlib import contextmanager

from .globs import translate_pattern


def shell(cmd, check=True):
    """
    Execute cmd.  Raises an exception if the command does not return 0
    """
    proc = subprocess.run(cmd, shell=True, check=False, stderr=subprocess.STDOUT,
                          stdout=subprocess.PIPE)
    output = proc.stdout.decode('utf-8').strip()
    if output:
        print(output)
    if check:
        proc.check_returncode()


def ensurelist(paramname, val, comment='#'):
    """
    Returns `val` as a list of strings.

    If `val` is already a list of strings, it is returned as-is.  If a string
    is passed, it is split into lines and blink and (optionally) comment lines
    are removed.

    paramname
      The parameter name to put into error messages.

    comment
      The single-line comment identifier.  Any lines starting with this are
      removed.  Note that end-of-line comments are *not* removed.
    """

    if isinstance(val, list):
        for line in val:
            if not isinstance(line, str):
                typename = type(line).__qualname__
                raise TypeError(f"{paramname} should be a list of strings.  Found: {typename}")
        return val

    if isinstance(val, str):
        lines = (line.strip() for line in val.strip().split('\n'))
        lines = (line for line in lines if line)
        if comment:
            lines = (line for line in lines if not line.startswith())
        return lines

    raise TypeError(f'{paramname} must be a list of strings or a string')


def archive(filename, *, patterns, root=None, nocompression=['*.png', '*.jpg'],
            exclude_dirs=['.git']):
    """
    Creates a zip file.

    * root: An optional directory used as the parent of all relative paths in
      other parameters.  If not provided, the current working directory is used.

    * patterns: A list of glob patterns to be included and excluded.

      For convenience, a triple quoted string is also accepted.  If used, each
      glob must be on its own line.  Blank lines and lines that begin with '#'
      (comments) are ignored.

      By default, a glob describes files to be added.  If a glob begins with '!'
      (followed by optional whitespace), it defines files to be excluded.  Note
      that exclusions take precedence over inclusions.  This is by design since
      it is usually convenient to use broad inclusions and specific exclusions.

    * exclude_dirs: Directory names, not paths or globs, that should be excluded.
      Excluding directories like .git and node_modules this way is significantly
      faster than excluding using a negated pattern.

    If a glob pattern starts with "/", it is considered an absolute pattern and
    is matched from the root directory.  Otherwise it is a relative pattern and
    will match anywhere under the root directory.

    For example, "/test.log" is absolute and will only match the file "test.log"
    in the root directory.  It can include subdirectoreis also like
    "/tests/*.py".  Otherwise, it can match anywhere in the path below the root.
    So "test.log" will match "<root>/test.log" and "<root>/subdir/test.log".
    Likewise, "tests/*.py" (with no leading slash) will match
    "<root>/tests/t.py" and "<root>/subdir/tests/t.py".

    Patterns are not recursive by default.  Use '**' to introduce recursion,
    similar to .gitignore and similar tools.  So "/tests/**" will match *all*
    files in "<root>/tests/" and all subdirectories.  The pattern "tests/**"
    will match all files under any "tests" directory.  "a/**/b/*.log" will match
    any log in any directory named "b" that is somewhere under an a, such as
    "a/b/test.log" and "a/x/y/z/b/test.log".
    """
    if not root:
        root = os.getcwd()

    if isinstance(patterns, str):
        lines = (line.strip() for line in patterns.split('\n'))
        nonblank = (line for line in lines
                    if line and not line.startswith('#'))
        patterns = list(nonblank)

    arc = zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED)

    includes = [p for p in patterns if p and not p.startswith('!')]
    excludes = [p for p in patterns if p and p.startswith('!')]

    include_regexps = [translate_pattern(p) for p in includes]
    exclude_regexps = [translate_pattern(p[1:].lstrip()) for p in excludes]
    nocomp_regexps  = [translate_pattern(p) for p in (nocompression or [])]

    exclude_dirs = set(exclude_dirs or [])

    def _matches_pattern(fn, regexps):
        for regexp in regexps:
            if regexp.search(fn):
                return True
        return False

    for parent, dirs, files in os.walk(root):
        if excludes and dirs:
            # See if we can exclude any of the directories to speed things up.
            remove = [dir for dir in dirs
                      if dir in exclude_dirs or _matches_pattern(join(parent, dir), exclude_regexps)
            ]
            for dir in remove:
                dirs.remove(dir)

        for fn in files:
            fqn = join(parent, fn)
            rn  = relpath(fqn, root)

            if not _matches_pattern(rn, include_regexps) or _matches_pattern(rn, exclude_regexps):
                continue

            compression = (zipfile.ZIP_STORED if not _matches_pattern(rn, nocomp_regexps) else None)
            arc.write(fqn, rn, compress_type=compression)


    #  for spec in includes:
    #      if isabs(spec):
    #          raise ValueError(
    #              f'Include specifications cannot be absolute.  ({spec!r})'
    #          )
    #      spec = join(root, spec)
    #      recursive = not spec.endswith('/*')

    #      for fn in glob.iglob(spec, recursive=recursive):

    #          if _matches_pattern(fn, exclude_regexps):
    #              continue

    #          compression = zipfile.ZIP_STORED
    #          if _matches_pattern(fn, nocomp_regexps):
    #              compression = None

    #          arcname = relpath(fn, root)
    #          arc.write(fn, arcname, compress_type=compression)

    return filename


@contextmanager
def chdir(dir):
    """
    A context manager that changes the directory to `dir`, then restores the previous
    directory when exited.
    """
    prev = os.getcwd()
    try:
        os.chdir(dir)
        yield
    finally:
        os.chdir(prev)
