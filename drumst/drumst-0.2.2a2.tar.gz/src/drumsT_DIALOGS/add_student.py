#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: add_student.py
# Porpose: students profile storing dialog
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

import wx

class AddRecords(wx.Dialog):
    """
    Show a dialog window for recording new students profiles.
    """
    def __init__(self, 
                 parent, 
                 title, 
                 name, 
                 surname, 
                 phone, 
                 address, 
                 birthDate, 
                 joinDate, 
                 level
                 ):
        """
        It is set need attributes to filter only some text fields
        """
        wx.Dialog.__init__(self, 
                           parent, 
                           -1, 
                           title, 
                           style=wx.DEFAULT_DIALOG_STYLE
                           )
        # set attributes
        self.name = name
        self.surname = surname
        self.listret = []
        
        # widgets:
        siz_name = wx.StaticBox(self, wx.ID_ANY, _("  Name:"))
        siz_surname = wx.StaticBox(self, wx.ID_ANY, _("  Surname:"))
        siz_phone = wx.StaticBox(self, wx.ID_ANY, _("  Phone:"))
        siz_address = wx.StaticBox(self, wx.ID_ANY, _("  Address:"))
        siz_birth = wx.StaticBox(self, wx.ID_ANY, _("  Birth-Dates:"))
        siz_date = wx.StaticBox(self, wx.ID_ANY, _("  Joined Date:"))
        siz_level = wx.StaticBox(self, wx.ID_ANY, _("  Level:"))
        siz_info = wx.StaticBox(self, wx.ID_ANY, _("  Others Info:"))
        
        self.txt_name = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER
                                    )
        self.txt_surname = wx.TextCtrl(self, wx.ID_ANY, "", 
                                       style=wx.TE_PROCESS_ENTER
                                       )
        self.txt_phones = wx.TextCtrl(self, wx.ID_ANY, "", 
                                      style=wx.TE_PROCESS_ENTER
                                      )
        self.txt_address = wx.TextCtrl(self, wx.ID_ANY, "", 
                                       style=wx.TE_PROCESS_ENTER | 
                                       wx.TE_MULTILINE
                                       )
        self.txt_birth = wx.TextCtrl(self, wx.ID_ANY, "", 
                                     style=wx.TE_PROCESS_ENTER
                                     )
        self.txt_date = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER
                                    )
        self.txt_level = wx.TextCtrl(self, wx.ID_ANY, "", 
                                     style=wx.TE_PROCESS_ENTER
                                     )
        self.txt_info = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER
                                    )
        close_btn = wx.Button(self, wx.ID_CANCEL, _("&Cancel"))
        ok_btn = wx.Button(self, wx.ID_OK, "") 
        
        # Properties:
        self.txt_name.SetMinSize((180, 30))
        self.txt_surname.SetMinSize((180, 30))
        self.txt_phones.SetMinSize((180, 30))
        self.txt_address.SetMinSize((300, 60))
        self.txt_birth.SetMinSize((180, 30))
        self.txt_date.SetMinSize((180, 30))
        self.txt_level.SetMinSize((150, 30))
        self.txt_info.SetMinSize((150, 30))
        
        # Layout:
        base = wx.FlexGridSizer(5, 2, 20, 20)
        
        box_name = wx.StaticBoxSizer(siz_name, wx.VERTICAL)
        box_name.Add(self.txt_name,0)
        
        box_surname = wx.StaticBoxSizer(siz_surname, wx.VERTICAL)
        box_surname.Add(self.txt_surname,0)
        
        box_phone = wx.StaticBoxSizer(siz_phone, wx.VERTICAL)
        box_phone.Add(self.txt_phones,0)
        
        box_address = wx.StaticBoxSizer(siz_address, wx.VERTICAL)
        box_address.Add(self.txt_address,0)
        
        box_birth = wx.StaticBoxSizer(siz_birth, wx.VERTICAL)
        box_birth.Add(self.txt_birth,0) 
        
        box_date = wx.StaticBoxSizer(siz_date, wx.VERTICAL)
        box_date.Add(self.txt_date,0)
        
        box_level = wx.StaticBoxSizer(siz_level, wx.VERTICAL)
        box_level.Add(self.txt_level,0)
        
        box_info = wx.StaticBoxSizer(siz_info, wx.VERTICAL)
        box_info.Add(self.txt_info,0)
        
        base.AddMany([(box_name, 0, wx.ALL, 15),(box_surname, 0, wx.ALL, 15),
                      (box_phone, 0, wx.ALL, 15),(box_address, 0, wx.ALL, 15),
                      (box_birth, 0,wx.ALL, 15),(box_date, 0, wx.ALL, 15),
                      (box_level, 0, wx.ALL, 15),(box_info, 0, wx.ALL, 15)]
                     )
        base.Add(close_btn, 0, wx.ALL | 
                               wx.ALIGN_CENTER_VERTICAL, 15)
        base.Add(ok_btn, 0, 
                 wx.ALL | 
                 wx.EXPAND |
                 wx.ALIGN_CENTER_VERTICAL, 15)

        self.SetSizer(base)
        base.Fit(self)
        self.Layout()
        
        if self.name != None: # evaluates if in insert or update mode
            self.txt_name.AppendText(self.name)
            self.txt_surname.AppendText(self.surname)
            self.txt_phones.AppendText(phone)
            self.txt_address.AppendText(address)
            self.txt_birth.AppendText(birthDate)
            self.txt_date.AppendText(joinDate)
            self.txt_level.AppendText(level)

        #----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, close_btn)
        self.Bind(wx.EVT_BUTTON, self.on_apply, ok_btn) 
        self.Bind(wx.EVT_TEXT, self.name_e , self.txt_name)
        self.Bind(wx.EVT_TEXT, self.surname_e , self.txt_surname)

    #---------------------Callback (event handler)----------------------#
    def on_close(self, event):
        #self.Destroy()
        event.Skip()
        
        
    def name_e(self, event):
        """
        Emit text change: If text is only spaces not enable to save.
        If name has spaces in head or in tail, strip method remove them.
        This method does not allow you to add spaces or tabs at the 
        beginning and end of a text because the fields name and surname 
        must be compared with others.
        """
        getVal = self.txt_name.GetValue()
        strippedString = getVal.strip() # remove all spaces head/tail in str
        
        if  strippedString == '':
            self.name = None
        else:
            self.name = strippedString.title() # capitalize the first letters

    def surname_e(self, event):
        """
        See above name_e() method.
        """
        getVal = self.txt_surname.GetValue()
        strippedString = getVal.strip()
        
        if  strippedString == '':
            self.surname = None
        else:
            self.surname = strippedString.title()

    def on_apply(self, event):
        """
        Apply is need to management errors before go GetValue().
        It is not allowed to leave here empty text fields
        
        """
        phone = self.txt_phones.GetValue()
        address = self.txt_address.GetValue().title()#capitalize first letters
        birthdate = self.txt_birth.GetValue()
        date = self.txt_date.GetValue()
        level = self.txt_level.GetValue()
        
        self.listret = [self.name,
                        self.surname,
                        phone,address,
                        birthdate,
                        date,level
                        ]
        for e in self.listret:
            if e == '':
                wx.MessageBox(_("Incomplete profile assignement. Is not "
                              "still possible to save into the database !"),
                              _("DrumsT: Warning"), 
                              wx.ICON_EXCLAMATION, 
                              self
                              )
                return
            
        event.Skip()
        
    def GetValue(self):
        """
        Return by call before Destroy()
        """
        return self.listret
