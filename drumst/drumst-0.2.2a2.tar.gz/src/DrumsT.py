#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: DrumsT.py
# Porpose: bootstrap check
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

import wx
from src.drumsT_SYS.boot import Boot_drumsT

# add translation macro to builtin similar to what gettext does
#import locale
import builtins
builtins.__dict__['_'] = wx.GetTranslation
from src.drumsT_SYS import app_const as appC

class DrumsTeacher(wx.App):
    """
    This is a bootstrap interface that is needed to do 
    application initialization to ensure that the system, 
    toolkit and wxWidgets are fully initialized.
    """
    def __init__(self, redirect=True, filename=None):
        """
        Creating attributes that will be used after in other class
        with GetApp()
        """
        print ("App __init__")
        settings = Boot_drumsT()# create instance
        getval = settings.Userfileconf()# get values
        # icons
        self.drumsT_icon = getval[0]
        self.openStudent_icon = getval[1]
        self.addStudent_icon = getval[2]
        self.changeStudent_icon = getval[3]
        self.delStudent_icon = getval[4]
        self.tab_icon = getval[5]
        self.lesson_icon = getval[6]
        # check
        self.OS = getval[7]
        self.main_path = getval[8]
        self.copyerr = getval[9]
        self.rootdir = getval[10]
        self.existing_db = getval[11]
        # Call the base class constructor:
        wx.App.__init__(self, redirect, filename) 
    
    #------------------------------------------------------------------

    def OnInit(self):
        """
        Return True if everything works.
        Return False if something is wrong.
        """
        lang = ''
        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        self.updateLanguage(lang)
        
        if self.copyerr: # if source dir is corrupt
            message = (_("Can not find the configuration file!\n"
                         "Please, remove and reinstall the drumsT "
                         "application·"))
            print ("DrumsT: Fatal Error, %s" % message)
            wx.MessageBox(message, 'drumsT: Fatal Error', wx.ICON_STOP)
            return False

        if self.rootdir == 'empty': # not set
            self.reprise()
            return True

        elif self.rootdir == 'error': # is corrupt
            message = (_("The configuration file is wrong! "
                       "Please, reinstall the drumsT application"))
            print ("DrumsT: Fatal Error, %s" % message)
            wx.MessageBox(message, _('DrumsT: Fatal Error'), wx.ICON_STOP)
            return False

        #--------------------Check paths--------------------------------#
        #ret = rootdirControl(self.rootdir) #control existing 

        if not self.existing_db:
            message = (_("The root directory for saving databases no longer\n"
                       "exists! Do you want to import an existing one or\n"
                       "create a new one?"))
            print ("DrumsT: Warning, The root directory for saving "
                   "databases no longer exists.")
            style = wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION
            dlg = wx.MessageDialog(parent=None, message=message, 
                                   caption="DrumsT: Warning", style=style
                                   )
            if dlg.ShowModal() == wx.ID_YES:
                self.reprise()
                return True
            else:
                return False
       #-----------------------------------------------------------------#
        else: # run main frame
            from src.drumsT_FRAMES.mainwindow import MainFrame
            main_frame = MainFrame()
            main_frame.Show()
            self.SetTopWindow(main_frame)
            return True
    #------------------------------------------------------------------
    def reprise(self):
        """
        Start a temporary dialog: this is showing during first time 
        start the DrumsT application.
        """
        from src.drumsT_DIALOGS.first_time_start import FirstStart
        main_frame = FirstStart(self.drumsT_icon)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    
     #------------------------------------------------------------------
    
    def updateLanguage(self, lang):
        """
        Update the language to the requested one.
        
        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.
        
        :param string `lang`: one of the supported language codes
        
        """
        # if an unsupported language is requested default to English
        if lang in appC.supLang:
            selLang = appC.supLang[lang]
            #print ('set a custom language: %s' % selLang)
        else:
            selLang = wx.LANGUAGE_DEFAULT
            #print ("Set language default\n%s" % appC.supLang)
            
            
        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale
        
        # create a locale object for this language
        self.locale = wx.Locale(selLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
        else:
            self.locale = None
    #-------------------------------------------------------------------
    
    def OnExit(self):
        print ("OnExit")
        return True
    #------------------------------------------------------------------
    
def main():
    """
    redirect standard out to a separate window:
        app = DrumsTeacher(redirect=True)
    redirect standard out to a terminal:
        app = DrumsTeacher(False)
    If () is empty default is redirect=True:
        app = DrumsTeacher()
    If None is same at True:
        app = DrumsTeacher(None)
    """
    app = DrumsTeacher(False)
    fred = app.MainLoop()
    print ("after MainLoop", fred)
