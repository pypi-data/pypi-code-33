#!/bin/env python
# -*- encoding: utf-8 -*-

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
