#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright (C) 2019 Christoph Fink, University of Helsinki
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.


import git
import glob
import os
import os.path
import shutil
import subprocess
import sys
import tempfile


def downloadWebis(packageDirectory):
    print(
        "It seems this is the first time you use python-webis. \n" +
        "Downloading and compiling webis (ECIR-2015-and-SEMEVAL-2015) \n",
        file=sys.stderr,
        flush=True
    )

    # --------------------------------
    # clone ECIR-2015-and-SEMEVAL-2015
    print(
        "Cloning ECIR-2015-and-SEMEVAL-2015 from github …",
        file=sys.stderr,
        flush=True
    )
    try:
        git.Repo(packageDirectory).remote().pull()
    except git.exc.GitError:
        try:
            shutil.rmtree(packageDirectory)
        except FileNotFoundError:
            pass
        git.Repo.clone_from(
            "https://github.com/christophfink/ECIR-2015-and-SEMEVAL-2015.git",
            packageDirectory
        )

    # ------------------------------
    # clone jazzy spellchecker files
    print(
        "Cloning jazzy from github … ",
        file=sys.stderr,
        flush=True
    )

    spellCheckerDir = os.path.join(
        packageDirectory,
        "resources",
        "lexi",
        "SpellChecker"
    )

    with tempfile.TemporaryDirectory() as jazzyRepoDir:
        git.Repo.clone_from(
            "https://github.com/christophfink/jazzy",
            jazzyRepoDir
        )

        try:
            shutil.rmtree(spellCheckerDir)
        except FileNotFoundError:
            pass

        shutil.copytree(
            os.path.join(jazzyRepoDir, "dict"),
            spellCheckerDir
        )

    # --------------------------
    # compile webis java classes
    print(
        "Compiling ECIR-2015-and-SEMEVAL-2015 java classes …",
        file=sys.stderr,
        flush=True
    )

    binDir = os.path.join(packageDirectory, "bin")
    srcDir = os.path.join(packageDirectory, "src")
    os.makedirs(binDir, exist_ok=True)

    try:
        classPath = \
            (
                "{srcDir:s}/.:{srcDir:s}/..:" +
                "{srcDir:s}/../lib:{srcDir:s}/../lib/*"
            ).format(
                srcDir=srcDir
            )
        for javaFile in glob.iglob(os.path.join(srcDir, "*.java")):
            if subprocess.run(
                [
                    "javac",
                    "-Xlint:none",
                    "-d", ".",
                    "-cp", classPath,
                    javaFile
                ],
                cwd=binDir
            ).returncode != 0:
                print(
                    "Could not compile {}.".format(javaFile) +
                    "python-webis might still be able to run",
                    file=sys.stderr,
                    flush=True
                )
    except FileNotFoundError:
        print("Please check that `javac` is available and in $PATH.")
        exit(-1)
