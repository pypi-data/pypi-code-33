#!/usr/bin/python
# -*- coding: UTF-8 -*- 
#
#########################################################
# Name: boot.py
# Porpose: Defines system path names to start up DrumsT program
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2017-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Created: 1 Feb. 2019
# Rev (00)

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
import sys
import os
import shutil
import platform

# work current directory of the program
PWD = os.getcwd()
#current user directory:
DIRNAME = os.path.expanduser('~') # /home/user

#-------------------------------------------------------------------------#
class Boot_drumsT(object):
    """
    *** ***
    It makes available the objects need to start up of the DrumsT program 
    *** ***

        1) Object system path established according to the type of 
        installation or execution of the program

        2) Object paths icons

        3) Parsing configuration file

        4) Check the DrumsT files and directories integrity

        5) Given a specific path, check the existence of the database
    """
    #----------------------------------------------------------------------#
    def __init__(self):
        """
        Locate the essentials path names to sharing data represented 
        by the ``self.main_path`` attribute and by path definitions 
        of the used icons and translation.
        
        These paths depend on how and where the program will run: 
        (local, as program installed, by which Operative System, etc)
            
        """
        self.main_path = None
        self.iconslist = None
        
        # What is the OS ??
        self.OS = platform.system()

        if os.path.isdir('%s/src' % PWD):
            #launch as local on any OS or as exe/app
            localepath = 'locale'
            self.main_path = '%s/share' % PWD
            # Icons:
            drumsT_icon = "%s/art/drumsT.png" % PWD
            openStudent_icon = '%s/art/openStudent.png' % PWD
            addStudent_icon = '%s/art/addStudent.png' % PWD
            changeStudent_icon = '%s/art/changeStudent.png' % PWD
            delStudent_icon = '%s/art/delStudent.png' % PWD
            tab_icon = '%s/art/opentab.png' % PWD
            lesson_icon = '%s/art/lesson.png' % PWD
            #help_icon = '%s/art/help.png' % PWD
            
        else: # Path system installation (usr, usr/local, ~/.local, \python3\)
            if self.OS == 'Windows':
                #Installed with 'pip install drumst' command
                # main path
                pythonpath = os.path.dirname(sys.executable)
                localepath = pythonpath + '\\share\\locale'
                self.main_path = pythonpath + '\\share\\drumst\\config'
                # Main path Icons:
                url = pythonpath + '\\share\\drumst\\icons'
                
            else:
                binarypath = shutil.which('drumst')
                
                if binarypath == '/usr/local/bin/drumst':
                    #usually Linux,MacOs,Unix main path
                    localepath = '/usr/local/share/locale'
                    self.main_path = '/usr/local/share/drumst/config'
                    # Main path Icons:
                    url = '/usr/local/share/drumst/icons'
                    pixmaps = '/usr/local/share/pixmaps'
                    
                elif binarypath == '/usr/bin/drumst':
                    #usually Linux main path
                    localepath = '/usr/share/locale'
                    self.main_path = '/usr/share/drumst/config'
                    # Main path Icons:
                    url = '/usr/share/drumst/icons'
                    pixmaps = '/usr/share/pixmaps'
                    
                else:
                    #installed with 'pip install --user drumst' command
                    import site
                    # main path
                    userbase = site.getuserbase()
                    localepath = userbase + '/share/locale'
                    self.main_path = userbase + '/share/drumst/config'
                    # Main path Icons:
                    url = userbase + '/share/drumst/icons'
                    pixmaps = '/share/pixmaps'
            
            drumsT_icon = "%s/drumsT.png" % pixmaps
            openStudent_icon = '%s/openStudent.png' % url
            addStudent_icon = '%s/addStudent.png' % url
            changeStudent_icon = '%s/changeStudent.png' % url
            delStudent_icon = '%s/delStudent.png' % url
            tab_icon = '%s/opentab.png' % url
            lesson_icon = '%s/lesson.png' % url
            #help_icon = '%s/help.png' % url
        
        self.iconslist = [os.path.join(norm) for norm in [drumsT_icon,
                                                          openStudent_icon,
                                                          addStudent_icon,
                                                          changeStudent_icon,
                                                          delStudent_icon,
                                                          tab_icon,
                                                          lesson_icon,
                                                          ]
                          ]
    #---------------------------------------------------------------------#
    
    def Userfileconf(self):
        """
        Checks the data obtained from the drumsT.conf configuration file
        on ~/user/.drumsT folder, and its integrity.
        Also, provides for its eventual regeneration or replacement.
        """
        copyerr = False
        existfileconf = True # file esiste (True) o non esiste (False)
        
        # check drumsT.conf 
        if os.path.exists('%s/.drumsT' % DIRNAME):#if exist folder ~/.DrumsT
            if os.path.isfile('%s/.drumsT/drumsT.conf' % DIRNAME):
                fileconf = self.parsing_fileconf() # fileconf data
                if fileconf[1] == 'error':
                    print ('drumsT.conf is corrupted! try to restore..')
                    existfileconf = False
                if float(fileconf[0]) != 1.0:
                    existfileconf = False
            else:
                existfileconf = False
            
            if not existfileconf: # if False
                try:
                    shutil.copyfile('%s/drumsT.conf' % self.main_path, 
                                    '%s/.drumsT/drumsT.conf' % DIRNAME)
                    fileconf = self.parsing_fileconf() # re-read the file
                except IOError:
                    copyerr = True
        else:
            try:
                shutil.copytree(self.main_path,'%s/.drumsT' % DIRNAME)
                fileconf = self.parsing_fileconf() # re-read the file
            except OSError:
                copyerr = True
            except IOError:
                copyerr = True

        return (self.iconslist[0], 
                self.iconslist[1], 
                self.iconslist[2], 
                self.iconslist[3], 
                self.iconslist[4], 
                self.iconslist[5], 
                self.iconslist[6],
                self.OS, 
                self.main_path,
                copyerr, 
                fileconf[1], #path or error or empty
                fileconf[2], #result of evalutation database pathname
                )
    #---------------------------------------------------------------------#
    
    def parsing_fileconf(self):
        """
        ** Parsing 'drumsT.conf' to get specified setting values.**
        This function always return a tupla object with three items
        in the following variations:
            
            (None, 'error', None)
            |
            |--- When the configuration file is corrupted or missing.
            
            (version, 'empty', None)
            |
            |--- The configuration file exists but the database path 
                object has not yet been established.
                
            (version, database path name, Boolean value)
            |
            |--- The configuration file exists and the database path object 
                is already established.
        """

        # NOTE reminder:
        # remove empty string from a list:
        #        cleaned = filter(None, uncomment)
        # Note however, that filter returns a list in Python 2, but a generator 
        # in Python 3. You will need to convert it into a list in Python 3 :
        #        cleaned = list(filter(None, uncomment)) 
        # or use the list comprehension solution:
        #        cleaned = [x for x in uncomment if x]
        
        drumsT_conf = '%s/.drumsT/drumsT.conf' % (DIRNAME)
        with open (drumsT_conf, 'r') as f:
            fconf = f.readlines()
        lst = [line.strip() for line in fconf if not line.startswith('#')]
        curr_conf = [x for x in lst if x]# list without empties values
        if not curr_conf:
            ret = None, 'error', None
        else:
            pathDB = curr_conf[1].split('=')[1]
            version = curr_conf[0].split('=')[1]
            if not pathDB:
                ret = version.strip(),'empty', None # first state of program
            else:
                ret = (version.strip(), 
                       pathDB.strip(), 
                       self.rootdirControl(pathDB.strip())
                       )
        
        return ret
    #---------------------------------------------------------------------#

    def rootdirControl(self, path_name):
        """
        Check root base path where is stored databases folder 
        with .drtDB extension
        """
        #path_name, file_name = ntpath.split(path) #must be imported ntpath

        if os.path.exists(path_name):
            path_exist = True
        else:
            path_exist = False
            
        #if os.path.isfile('%s/%s' %(path_name, file_name)):
            #file_exist = True
        #else:
            #file_exist = False
            
        return path_exist
