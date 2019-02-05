#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: data_info.py
# Porpose: Version, Copyright, Description, etc
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2017-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

def prg_info():
    """
    Reading strings useful to get program data informations.
    """
    Release_Name = 'DrumsT'
    Program_Name = 'drumst'
    Version = '0.2.2a2'
    Release = 'February 5 2019'
    Copyright = '© 2013-2019'
    Website = 'https://gitlab.com/jeanslack/drumst'
    Author = 'Gianluca Pernigotto (aka jeanslack)'
    Mail = '<jeanlucperni@gmail.com>'
    Comment = ("If you want to customize this program,\n"
            "or if you need assistance, more information,\n"
            "please, do not hesitate to contact me.")
    
    short_d = ("School Management For Drum Teachers")
    
    long_d = ("%s is a school manager application open-source and\n"
            "cross-platform, focused to individual lessons and designed\n"
            "for drums teachers. It can handle independently multiple\n"
            "school locations with progressive data storing of several\n"
            "school years and students lessons who learns\n"
            "the art of drumming.\n\n"
            "%s is free software that respects your freedom!\n" % (
                                                        Release_Name,
                                                        Release_Name
                                                                    )
                )
            
    short_l = ("GPL3 (Gnu Public License)")
    
    license = ("Copyright - %s %s\n"
                "Author and Developer: %s\n"
                "Mail: %s\n\n"
                "%s is free software: you can redistribute\n"
                "it and/or modify it under the terms of the GNU General\n"
                "Public License as published by the Free Software\n"
                "Foundation, either version 3 of the License, or (at your\n"
                "option) any later version.\n\n"
                
                "%s is distributed in the hope that it\n"
                "will be useful, but WITHOUT ANY WARRANTY; without\n"
                "even the implied warranty of MERCHANTABILITY or\n" 
                "FITNESS FOR A PARTICULAR PURPOSE.\n" 
                "See the GNU General Public License for more details.\n\n"
                
                "You should have received a copy of the GNU General\n" 
                "Public License along with this program. If not, see\n" 
                "http://www.gnu.org/licenses/" %(Copyright,
                                                 Author,
                                                 Author,Mail,
                                                 Release_Name, 
                                                 Release_Name
                                                 )
                )
                
    return (Release_Name, 
            Program_Name, 
            Version, 
            Release, 
            Copyright, 
            Website, 
            Author, 
            Mail, 
            Comment, 
            short_d, 
            long_d, 
            short_l, 
            license
            )
