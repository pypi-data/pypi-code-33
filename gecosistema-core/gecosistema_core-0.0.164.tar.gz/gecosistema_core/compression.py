# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        compression.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     28/09/2018
# -------------------------------------------------------------------------------
import zipfile
import bz2
import tarfile
import rarfile
import os
from .strings import *
from .filesystem import *

def compress(filenames, filezip="", removesrc=False):
    """
    compress
    """

    if isstring(filenames) and directory(filenames):
        filenames = ls(filenames)
    else:
        filenames = listify(filenames, sep=",")

    if not filezip:
        if len(filenames) == 1:
            filezip = forceext(filenames[0], "zip")
        elif len(filenames) > 1:
            filezip = forceext(justpath(filenames[0]), "zip")
        else:
            return None

    mkdirs(justpath(filezip))

    if (justext(filezip) == "zip"):
        with zipfile.ZipFile(filezip, 'w', zipfile.ZIP_DEFLATED) as archive:
            for filename in filenames:
                if file(filename):
                    archive.write(filename, filename)

    if (justext(filezip) == "tgz"):
        with tarfile.open(filezip, "w") as archive:
            for filename in filenames:
                if file(filename):
                    archive.add(filename)

    if file(filezip):
        if removesrc:
            remove(filenames)
        return filezip
    return False



