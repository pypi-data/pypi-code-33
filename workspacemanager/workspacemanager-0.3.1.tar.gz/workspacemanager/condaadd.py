# coding: utf-8

"""
	This script add all project path to conda-venv

	https://stackoverflow.com/questions/37006114/anaconda-permanently-include-external-packages-like-in-pythonpath
"""

import os
import sh

from workspacemanager.utils import *
from pathlib import Path

import sys


def homeDir():
    return str(Path.home())

def generatePythonpath():
	venvName = "conda-venv"
	workspacePath = homeDir() + "/Workspace"
	sitePackagePath = sortedGlob(homeDir() + "/lib/anaconda*/envs/conda-venv/lib/python3.*/site-packages")[0]
	projects = getAllProjects(workspacePath)
	scriptDir = homeDir() + "/tmp"
	mkdir(scriptDir)
	condaLibPath = homeDir() + "/lib/anaconda3/bin"
	scriptPath = scriptDir + "/tmp-script-for-conda-add.sh"
	for projectPath in projects:
		scriptContent = ""
		# scriptContent += "source " + homeDir() + "/.bashrc" + "\n"
		# scriptContent += "source " + homeDir() + "/.bash_aliases" + "\n"
		# scriptContent += "source " + homeDir() + "/.hjbashrc" + "\n"
		scriptContent += "source " + condaLibPath + "/activate conda-venv" + "\n"
		scriptContent += condaLibPath + "/conda develop " + projectPath + "\n"
		# scriptContent += "source deactivate" + "\n"
		strToFile(scriptContent, scriptPath)


		print(sh.bash(scriptPath))
		removeIfExists(scriptPath)
	# activate = ["activate", "bconda-ve"]
	# print(sh.source(*activate))
	# for projectPath in projects:
	# 	print(sh.condain("conda-venv", "conda", "develop", projectPath))


if __name__ == '__main__':
	generatePythonpath()

