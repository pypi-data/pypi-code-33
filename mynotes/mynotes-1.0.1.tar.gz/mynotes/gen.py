"""Generate functions."""

# mynotes builds indexes and converts to HTML a tree of notes written in
# Markdown.
# Copyright (C) 2018 Yorick Brunet <mynotes@yok.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import operator
import os.path
import markdown
import shutil
import sys
from typing import List, Optional, Union
from mdx_gfm import GithubFlavoredMarkdownExtension
from pygments.formatters import HtmlFormatter
# http://pygments.org/docs/quickstart/
# https://overiq.com/blog/1527072795/pygments-tutorial/

from .utils import walk, DataDir, DataFile, Params
from . import plugins_html as plughtml
from . import constants as constants


def _bi_process_file(prms: Params,
                     root: str,
                     file_: str,
                     ) -> Optional[DataFile]:
    """Process file for :ref:`_bi_process_files`.

    Read the file title (looking for # TITLE) and return a :ref:`DataFile`
    object with, among others, the file name and either the title found as
    title or the filename as title.

    :param Params prms: Parameters for build_index subfunctions
    :param str root: Root directory of this file
    :param str file_: List of files to process
    :return: File data
    :rtype: DataFile or None
    """
    # Read title from file ...
    filepath = os.path.join(root, file_)
    try:
        with open(filepath, 'r') as fpr:
            try:
                m = constants.RE_HEADER.match(fpr.read())
                # ... if found, use it.
                if m:
                    title = m.group(1)
                    return DataFile(prms.home, prms.index, root, file_, title)
                # ... if not found, use filename.
                else:
                    return DataFile(prms.home, prms.index, root, file_, file_)
            except UnicodeDecodeError:
                if prms.verbose:
                    sys.stderr.write(f'Cannot parse file {filepath}\n')
    except FileNotFoundError:
        if prms.verbose:
            sys.stderr.write(f'File {filepath} not found\n')
    return None


def _bi_process_files(prms: Params,
                      root: str,
                      files: List[str],
                      ) -> List[DataFile]:
    """Process files for :ref:`build_index`.

    :param Params prms: Parameters for build_index subfunctions
    :param str root: Root directory of these files
    :param list[str] files: List of files to process
    :return: Files data
    :rtype: list[DataFile]
    """
    data = []
    if files:
        for file_ in files:
            r = _bi_process_file(prms, root, file_)
            if r is not None:
                data.append(r)
    return data


def _bi_process_dirs(prms: Params,
                     root: str,
                     dirs: List[str],
                     ) -> List[DataDir]:
    """Process directories for :ref:`build_index`.

    :param Params prms: Parameters for build_index subfunctions
    :param str root: Root directory of these directories
    :param list[str] dirs: List of directories to process
    :return: Directories data
    :rtype: list[DataDir]
    """
    data = []
    if dirs:
        for dir_ in dirs:
            data.append(DataDir(prms.home, prms.index, root, dir_,
                                dir_.replace('_', ' ')))
    return data


def _bi_gen_index(prms: Params,
                  root: str,
                  all_data: List[Union[DataFile, DataDir]],
                  ) -> None:
    """Generate index file for :ref:`build_index`.

    :param Params prms: Parameters for build_index subfunctions
    :param str root: Root directory of the index file
    :param all_data: List of files and directories to write in index file
    :type  all_data: list[DataFile, DataDir]
    """
    new_file = os.path.join(root, prms.index)
    with open(new_file, 'w') as fpw:
        if prms.verbose:
            print(f'Created {new_file}')
        # ... write index title
        if root == '.':
            fpw.write('# Index\n')
        else:
            fpw.write(f'# {root.split("/")[-1]} Index\n')
        # ... write links
        for data in all_data:
            fpw.write(f'1. {data.link()}\n')


def build_index(top_dir: str,
                prms: Params,
                ) -> None:
    """Build index starting from the top directory.

    Ignore directories specified in :ref:`excl_dirs` and files specified in
    :ref:`excl_files`.

    :param str top_dir: Top directory
    :param Params prms: Parameters for build_index method and submethods
    """
    # Walk from current directory
    for root, dirs, files in walk('.', prms.excl_dirs, prms.excl_files):
        all_data: List[Union[DataDir, DataFile]] = []
        # Process files in root/
        all_data.extend(_bi_process_files(prms, root, files))
        # Process directories in root/
        all_data.extend(_bi_process_dirs(prms, root, dirs))
        # Sort data w.r.t. compare() method
        all_data.sort(key=operator.methodcaller('compare'))
        # Search home file and place it at head position
        all_data = [x for x in all_data if x.is_home_file()] + \
                   [x for x in all_data if not x.is_home_file()]
        # Generate INDEX_FILE
        _bi_gen_index(prms, root, all_data)


def _gh_md2html_gfm(file_md: str,
                    extra_md: Optional[str] = None,
                    ) -> str:
    """Generate HTML file using py-gfm.

    :param str file_md: File's Markdown data
    :param str extra_md: Extra Markdown data
    :return: HTML data
    :rtype: str
    """
    md_exts = [GithubFlavoredMarkdownExtension()]
    html_data = markdown.markdown(file_md, extensions=md_exts)
    if extra_md is not None:
        html_data += '<hr/>'
        html_data += markdown.markdown(extra_md, extensions=md_exts)
    return html_data


def _gh_css_gfm() -> str:
    """Generate CSS styles for py-gfm.

    :return: CSS styles
    :rtype: str
    """
    return constants.GFM_CSS + HtmlFormatter().get_style_defs()


def _gh_copy_extra_dir(prms: Params,
                       root: str,
                       html_dir: str,
                       ) -> None:
    """Copy the :ref:`EXTRA_FILES_DIR` into according HTML directory.

    :param Params prms: Parameters
    :param str root: Root directory of the extra files directory
    :param str html_dir: HTML directory
    """
    extra_dir = os.path.join(root, constants.EXTRA_FILES_DIR)
    if os.path.exists(extra_dir):
        # ... copy EXTRA_FILES_DIR to according HTML directory
        shutil.copytree(extra_dir,
                        os.path.join(html_dir, constants.EXTRA_FILES_DIR))
        if prms.verbose:
            print(f'Copied {extra_dir} to {html_dir}')


def _gh_process_file(prms: Params,
                     root: str,
                     html_dir: str,
                     css: str,
                     plugins: List[str],
                     file_: str,
                     ) -> None:
    """Convert the file from markdown to HTML for :ref:`generate_html`.

    :param Params prms: Parameters
    :param str root: Root directory of the extra files directory
    :param str html_dir: HTML directory
    :param str css: CSS rules
    :param list[str] plugins: List of plugins to apply to HTML file
    :param str file_: Filename
    """
    # ... split the filename into name + ext
    fname, _ = os.path.splitext(file_)
    # ... read the markdown file
    with open(os.path.join(root, file_), 'r') as fpr:
        file_md = fpr.read()
    # ... extract title
    m = constants.RE_HEADER.match(file_md)
    title = m.group(1) if m else file_
    # ... read the home file if this is the index file
    home_file = os.path.join(root, prms.home)
    home_md = None
    if file_ == prms.index and os.path.exists(home_file):
        with open(home_file, 'r') as fpr:
            home_md = fpr.read()
    # ... build file's HTML file
    html_file = os.path.join(html_dir, fname + constants.HTML_EXT)
    # ... include plugins
    file_md = plughtml.generate_plugins_data(prms, plugins, file_, root,
                                             file_md)
    # ... convert markdown -> HTML
    html_data = _gh_md2html_gfm(file_md, home_md)
    # Convert links from markdown files to html files
    html_data = html_data.replace(prms.md_ext, constants.HTML_EXT)
    # ... add HTML header/footer
    html_data = constants.HTML_HEADER.format(title, css) + \
        html_data + \
        constants.HTML_FOOTER
    # ... write file's HTML file after markdown -> HTML conv
    with open(html_file, 'w') as fpw:
        fpw.write(html_data)
        if prms.verbose:
            print(f'Created {html_file}')


def generate_html(top_dir: str,
                  prms: Params,
                  plugins: List[str],
                  ) -> None:
    """Generate HTML files for markdown files.

    :param str top_dir: Top directory
    :param Params prms: Parameters for build_index method and submethods
    :param list[str] plugins: List of plugins to apply to HTML file
    """
    # Remove HTML directory to build a fresh one
    shutil.rmtree(constants.HTML_DIR, ignore_errors=True)
    # Remove index file from excluded files as we'd like to convert it to HTML
    try:
        prms.excl_files.remove(prms.index)
    except ValueError:
        pass
    # Generate CSS
    css = _gh_css_gfm()
    # Walk from current directory ...
    for root, dirs, files in walk('.', prms.excl_dirs, prms.excl_files):
        # ... build file's HTML directory
        html_dir = os.path.normpath(
                    os.path.join(constants.HTML_DIR, root))
        # ... create file's HTML directory
        os.makedirs(html_dir, exist_ok=True)
        # ... for EXTRA_FILES_DIR found ...
        _gh_copy_extra_dir(prms, root, html_dir)
        # ... for each file found ...
        for file_ in files:
            # ... split the filename into name + ext
            _, fext = os.path.splitext(file_)
            # ... if ext is the correct markdown extension ...
            if fext == prms.md_ext:
                _gh_process_file(prms, root, html_dir, css, plugins, file_)


# autoapi.sphinx directive
__api__ = [
    '_bi_process_file',
    '_bi_process_files',
    '_bi_process_dirs',
    '_bi_gen_index',
    'build_index',
    '_gh_md2html_gfm',
    '_gh_css_gfm',
    '_gh_copy_extra_dir',
    '_gh_process_file',
    'generate_html',
]
