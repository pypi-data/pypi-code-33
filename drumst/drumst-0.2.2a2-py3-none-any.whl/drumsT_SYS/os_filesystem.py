#!/usr/bin/python
# -*- coding: UTF-8 -*- 
#
#########################################################
# Name: os_filesystem.py
# Porpose: Common operative system processing
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Created: 1 Feb. 2019
# Rev (00),(01)

# This file is part of DrumsT.

#    DrumsT is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    DrumsT is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with DrumsT. If not, see <http://www.gnu.org/licenses/>.

#########################################################

import os
import re

DIRNAME = os.path.expanduser('~') # /home/user

#--------------------------------------------------------------------------#
def write_newpath(path):
    """
    Write file configuration for new database path.
    This function is called when first time run or if 
    user change path-name for database
    """
    #err = False
    msg = (_("A new drumsT rootdir has been created on:\n\n"
           "{0}\n\n"
           "Restart the DrumsT application now.\n\n"
           "Good Work !").format(path)
           )
    try:
        with open('%s/.drumsT/drumsT.conf' %(DIRNAME),'r') as F:
            data = F.readlines()
        for a in data:
            if a.startswith('DATABASE_PATH_NAME='):
                match = a
                data = [w.replace(match, 
                        'DATABASE_PATH_NAME=%s\n' % (path)) 
                        for w in data
                        ]
    except IOError as error:
        #raise # WARNING: use raise statement for debug only
        print (error)
        #err = True
        msg = (_("DrumsT: Failed to write drumsT.conf:\n\n"
               "ERROR: {0}").format(error))
        return True, msg
    
    with open('%s/.drumsT/drumsT.conf' %(DIRNAME),'w') as Fw:
        for i in data:
            overwrite = Fw.write('%s' % i)
    return False, msg
#--------------------------------------------------------------------------#
def create_rootdir(path,name):
    """
    Prepare a root dir for database during first time running 
    or when create another school
    """
    err = False
    msg = None
    #if os.path.exists('%s' % path):
    if os.path.exists('%s/%s' % (path,name)):
        err = True
        msg = (_("DrumsT: Already exist : %s") % path)
        return err, msg
    try:
        os.makedirs('%s/%s' % (path,name))

    except OSError as error:
        err = True
        msg = (_("DrumsT: Failed to make database "
                 "root dir\n\nOSError: %s") % error)
        print (error)
        
    return err, msg
#--------------------------------------------------------------------------#
def urlify(string):
    """
    Convert any string with white spaces, tabs, digits, question marks,  
    apostrophes, exclamation points, etc, in URLs satisfying for the
    filesystems and SQlite
    """
    # remove all digits 1234567890
    #a = re.sub("\d+", "", string)

    # Remove all non-word characters (everything except numbers and letters)
    b = re.sub(r"[^\w\s]", '', string)
    # Replace all runs of whitespace with a single underscore
    c = re.sub(r"\s+", '_', b)
    
    return c
