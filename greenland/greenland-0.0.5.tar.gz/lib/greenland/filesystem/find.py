# * Copyright (C) 2018 M E Leypold, GPL3-or-later licensed  --------------------|
#
#     greenland.filesystem.tree -- Mapping filesystem state in an object tree.
# 
#     Copyright (C) 2018 M E Leypold
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# * Imports  -------------------------------------------------------------------|
# * Predicates  ----------------------------------------------------------------|

from fnmatch import fnmatch

def basename(name):
    def basename(obj):
        return obj.name ==name
    return basename

def matches(wildcards):
    def matches(obj):
        return fnmatch(obj.name,wildcards)
    return matches

def relpath_matches(wildcards):
    def relpath_matches(obj):
        return fnmatch(obj.relpath,wildcards)
    return relpath_matches

def extension(ext):
    def extension(obj):
        return obj.ext == ext
    return extension

def basenames(*names):
    def basenames(obj):
        return obj.name in names
    return basenames

def is_dir(obj):
    return obj.is_dir

from greenland.toolbox.predicates import AND, NOT, OR

version_control_data = (
    ( is_dir <<AND>> basenames('CVS','.svn') )
    <<OR>> basenames('.git')
)
    
backup_file = NOT(is_dir) <<AND>> matches('*~')

# More predicates will be added here as soon as the need comes up

# * Find procedures  -----------------------------------------------------------|

from .trees import find, find_files
