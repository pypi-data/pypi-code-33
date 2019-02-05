#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: infoprg.py
# Porpose: Show Version, Copyright, Description, etc
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

import wx.adv
from src.drumsT_DATA.data_info import prg_info

info_rls = prg_info()# calling
#-----------------#
NAME = info_rls[0]
PRG_NAME = info_rls[1]
VERSION = info_rls[2]
RELEASE = info_rls[3]
COPYRIGHT = info_rls[4]
WEBSITE = info_rls[5]
AUTHOR = info_rls[6]
MAIL = info_rls[7]
COMMENT = info_rls[8]
SHORT_DESCR = info_rls[9]
DESCRIPTION = info_rls[10]
SHORT_LIC = info_rls[11]
LONG_LIC = info_rls[12]

def info(drumsT_icon):
    """
    This part I copied entirely so. It's a predefined template to
    create a dialog with the program information
    """
    
    info =  wx.adv.AboutDialogInfo()
    
    info.SetIcon(wx.Icon(drumsT_icon, wx.BITMAP_TYPE_PNG))
    
    info.SetName(NAME)
    
    info.SetVersion(VERSION)
    
    info.SetDescription(_("Music drums school management\n\n"
            "DrumsT is a school manager application open-source and\n"
            "cross-platform, focused to individual lessons and designed\n"
            "for drums teachers. It can handle independently multiple\n"
            "school locations with progressive data storing of several\n"
            "school years and students lessons who learns\n"
            "the art of drumming.\n\n"
            "DrumsT is free software that respects your freedom!\n"))
    
    info.SetCopyright("%s %s" %(COPYRIGHT, AUTHOR))
    
    info.SetWebSite(WEBSITE)
    
    info.SetLicence(LONG_LIC)
    
    info.AddDeveloper("\n\n%s \n"
                      "Mail: %s\n"
                      "Website: %s\n\n"
                      "%s\n" %(AUTHOR,MAIL,WEBSITE,COMMENT))
    
    #info.AddDocWriter(u"La documentazione ufficiale é parziale e ancora\n"
                       #u"in fase di sviluppo, si prega di contattare l'autore\n"
                       #u"per ulteriori delucidazioni.")
    
    #info.AddArtist(u'Gianluca Pernigotto powered by wx.Python')
    
    #info.AddTranslator(u"Al momento, il supporto alle traduzioni manca del\n"
                        #u"tutto, l'unica lingua presente nel programma é\n"
                        #u"quella italiana a cura di: Gianluca Pernigotto\n\n"
                        
                        #u"Se siete interessati a tradurre il programma\n"
                        #u"in altre lingue, contattare l'autore.")
    
    wx.adv.AboutBox(info)
    #event.Skip()
