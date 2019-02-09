####
# bomail.guistuff.mygui
#
# The main UI object.
####

import curses
import os
import sys
import locale
import traceback

from bomail.config.config import pathcfg,guicfg

import bomail.util.search_opts as search_opts
import bomail.util.util as util

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.cli.process as process
import bomail.cli.check_sched as check_sched

from bomail.util.addr import AddrBook
from bomail.util.thread import ThreadMgr
from bomail.util.tags import TagMgr

import bomail.guistuff.display as display
import bomail.guistuff.get_txt as get_txt
import bomail.guistuff.gui_util as gui_util
from bomail.guistuff.acts import Acts
from bomail.guistuff.tabthread import TabThread
from bomail.guistuff.tabnothread import TabNoThread


default_tab_ind = 0
default_tab_searches = [
  "-open",
  "-draft",
  "-sent",
  ""]


class Gui:
  def __init__(self, screen):
    self.init_screen(screen)

    self.mail_mgr = mailfile.MailMgr()
    self.addr_book = AddrBook()
    if guicfg.threads_on:
      self.thread_mgr = ThreadMgr()
    else:
      self.thread_mgr = None
    self.tag_mgr = TagMgr()
    self.acts = Acts(self)

    self.unread_set = set()  # unread filenames

    try:
      with open(pathcfg.tab_config_file) as f:
        s = f.read()
        namespace = {}
        exec(s, namespace)
        self.tab_ind = namespace["tab_ind"]
        tab_searches = namespace["tab_searches"]
    except:
      self.tab_ind = default_tab_ind
      tab_searches = default_tab_searches
    if guicfg.threads_on:
      self.tabs = [TabThread(s, self) for s in tab_searches]
    else:
      self.tabs = [TabNoThread(s, self) for s in tab_searches]

    self.tabs[self.tab_ind].load()  # better load initial tab now, during loading screen
    self.curr_view = self.tabs[self.tab_ind]
    curses.flushinp()


  def init_screen(self, screen):
    self.screen = screen
    curses.curs_set(False)  # no cursor
    screen.scrollok(1)      # writing to last line/char is allowed
    curses.init_pair(guicfg.DEFAULT_CLR_PAIR, guicfg.foreground_color, guicfg.background_color)
    curses.init_pair(guicfg.BOMAIL_CLR_PAIR, guicfg.bomail_color, guicfg.background_color)
    curses.init_pair(guicfg.AUTHOR_CLR_PAIR, guicfg.author_color, guicfg.background_color)
    curses.init_pair(guicfg.TAGS_CLR_PAIR, guicfg.tags_color, guicfg.background_color)
    curses.init_pair(guicfg.THREAD_CLR_PAIR, guicfg.thread_color, guicfg.background_color)
      
    screen.keypad(True)
    
    self.attr = curses.color_pair(guicfg.BOMAIL_CLR_PAIR) | guicfg.bomail_attr
    self.screen.bkgd(" ", curses.color_pair(guicfg.BOMAIL_CLR_PAIR))
    self.tab_area = curses.newwin(curses.LINES - display.TOPLINES - display.BOTTOMLINES, curses.COLS, display.TOPLINES, 0)
    self.tab_area.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))
    self.note_area = curses.newwin(1, curses.COLS, curses.LINES - display.BOTTOMLINES + 1, 0)
    self.note_area.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))
    self.commands_area = curses.newwin(display.BOTTOMLINES-3, curses.COLS, curses.LINES - display.BOTTOMLINES + 3, 0)
    self.commands_area.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))

    display.draw_loading_screen(self)

  # after calling a program like 'less', reset curses stuff
  def reset_after_prog(self):
    curses.curs_set(False)
    curses.noecho()
    curses.cbreak()
    self.screen.keypad(True)

  def update_for_new(self, filelist):
    if len(filelist) == 0:
      return
    if guicfg.threads_on:
      prlist = [(self.mail_mgr.get(f, mailfile.MSG_ID_L),f) for f in filelist]
      self.thread_mgr.update_for_add(prlist, self.mail_mgr)
    for t in self.tabs:
      if t != self.curr_view:
        t.update_for_new(filelist)
    self.curr_view.update_for_new(filelist)

  def update_for_change(self, filelist):
    if len(filelist) == 0:
      return
    if guicfg.threads_on:
      prlist = [(self.mail_mgr.get(f, mailfile.MSG_ID_L), f) for f in filelist]
      self.thread_mgr.update_for_add(prlist, self.mail_mgr)
    for t in self.tabs:
      if t != self.curr_view:
        t.update_for_change(filelist)
    self.curr_view.update_for_change(filelist)

  # filelist are the now-deleted filenames
  # data_list are their data (note they are no longer in mail manager!)
  def update_for_trash(self, filelist, data_list):
    if len(filelist) == 0:
      return
    if guicfg.threads_on:
      self.thread_mgr.update_for_trash(filelist, data_list, self.mail_mgr)
    for t in self.tabs:
      if t != self.curr_view:
        t.update_for_trash(filelist)
    if self.curr_view.update_for_trash(filelist):  # if true, go back to tab
      self.change_tab_ind(self.tab_ind)

  def rewrite_tab_searches(self):
    with open(pathcfg.tab_config_file, "w") as f:
      f.write("tab_ind = " + str(self.tab_ind) + "\n\n")
      f.write("tab_searches = [\n")
      for t in self.tabs:
        f.write("  \"" + t.search_str.replace('"','\\"') + "\",\n")
      f.write("]\n")

  def change_tab_ind(self, new_ind):
    self.tab_ind = new_ind
    self.curr_view = self.tabs[self.tab_ind]
    if not self.curr_view.is_loaded:
      self.curr_view.load()

  def mark_read(self, filelist):
    for f in filelist:
      self.unread_set.discard(f)  # removes if present

  def mark_unread(self, filelist):
    self.unread_set.update(filelist)

  def go(self):
    keep_alive = True
    mode, note = "all", "Welcome"  # mode is all, view, or note
    while keep_alive:
      display.redraw(self, self.curr_view, mode, note)
      mode, note = "note", ""
      key = self.screen.getkey()
      keep_alive, mode, note = self.process_key(key)
    # done with program; save tab settings and quit
    self.rewrite_tab_searches()
    return self.tabs[self.tab_ind].get_curr_filenames()

  # given keypress
  # return 3 results:
  # 1) True if keep program alive, False to exit
  # 2) the mode to redraw
  # 3) the note to draw
  def process_key(self, key):
    if key == guicfg.QUIT_KEY:
      return False, "", ""

    # otherwise, return True, mode, note
    key_used, mode, note = self.process_toplevel_key(key)
    if key_used:
      return True, mode, note

    curr_filenames = self.curr_view.get_curr_filenames()
    key_used, mode, note = self.process_fileacts_key(key, curr_filenames)
    if key_used:
        return True, mode, note
    # else
    self.curr_view, mode, note = self.curr_view.process_key(key)
    return True, mode, note


  # return (True if we use the keypress, False o.w.), mode, note
  def process_toplevel_key(self, key):
    ## Navigating tabs
    if key >= "0" and key <= "9":
      key_num = int(key)
      new_ind = key_num - 1 if key_num > 0 else 9   # key "0" goes to the 10th tab
      if new_ind < len(self.tabs):
        self.change_tab_ind(new_ind)
        return True, "all", ""
      # else
      return True, "note", "Can't switch: tab " + str(key_num) + " nonexistent"
    elif key == guicfg.TAB_LEFT_KEY:
      if self.tab_ind > 0:
        self.change_tab_ind(self.tab_ind - 1)
        return True, "all", ""
      # else
      return True, "note", "Already at leftmost tab."
    elif key == guicfg.TAB_RIGHT_KEY:
      if self.tab_ind < len(self.tabs) - 1:
        self.change_tab_ind(self.tab_ind + 1)
        return True, "all", ""
      # else
      return True, "note", "Already at rightmost tab."

    ## Adding, removing, shifting tabs
    elif key == guicfg.ADD_TAB_KEY:
      new_str = get_txt.get_tab_search_txt(self, "")
      if new_str is None:
        return True, "all", "Cancelled"
      # else
      mode, note = self.acts.do(("add tab", self.tab_ind + 1, new_str))
      return True, mode, note
    elif key == guicfg.REMOVE_TAB_KEY:
      if len(self.tabs) > 0:
        mode, note = self.acts.do(("remove tab", self.tab_ind, self.tabs[self.tab_ind]))
        return True, mode, note
      # else
      return True, "note", "Could not remove the only tab."
    elif key == guicfg.MOVE_TAB_LEFT_KEY:
      if self.tab_ind > 0:
        mode, note = self.acts.do(("move tab", self.tab_ind, -1))
        return True, mode, note
      # else
      return True, "note", "Tab is already leftmost."
    elif key == guicfg.MOVE_TAB_RIGHT_KEY:
      if self.tab_ind < len(self.tabs) - 1:
        mode, note = self.acts.do(("move tab", self.tab_ind, 1))
        return True, mode, note
      # else
      return True, "note", "Tab is already rightmost."
    elif key == guicfg.EDIT_TAB_KEY:
      old_str = self.tabs[self.tab_ind].search_str
      new_str = get_txt.get_tab_search_txt(self, old_str)
      if new_str is None:
        return True, "all", "Cancelled"
      # else
      mode, note = self.acts.do(("edit tab", self.tab_ind, new_str, old_str))
      return True, mode, note
    elif key == guicfg.SEARCH_IN_TAB_KEY:
      old_str = self.tabs[self.tab_ind].search_str
      q = get_txt.get_search_in_tab_txt(self)
      if q is None or len(q) == 0:
        return True, "all", "Cancelled"
      # else
      new_str = search_opts.get_new_search_str(old_str, q)
      mode, note = self.acts.do(("add tab", self.tab_ind + 1, new_str))
      return True, mode, note

    ## Undo, redo
    elif key == guicfg.UNDO_KEY:
      if len(self.acts.acts) > 0 and self.acts.act_ind >= 0:
        mode, note = self.acts.undo()
        return True, mode, note
      # else
      return True, "note", "Nothing to undo."
    elif key == guicfg.REDO_KEY:
      if len(self.acts.acts) > 0 and self.acts.act_ind + 1 < len(self.acts.acts):
        mode, note = self.acts.redo()
        return True, mode, note
      # else
      return True, "note", "Nothing to redo."

    ## Get updates
    elif key == guicfg.GET_KEY:
      display.redraw_note(self, "Getting new mail and updates (please wait)...")
      new_files = process.main(self.mail_mgr, self.tag_mgr)
      unsched_files = check_sched.main(self.mail_mgr)
      self.update_for_new(new_files)
      self.update_for_change(unsched_files)
      self.mark_unread(new_files)
      self.mark_unread(unsched_files)
      curses.flushinp()  # it might've been a long wait, flush keypresses
      unsched_str = "" if len(unsched_files) == 0 else ", de-scheduled " + str(len(unsched_files)) + " emails"
      num_sent = sum([1 if self.mail_mgr.get(f,mailfile.SENT_L)=="True" else 0 for f in new_files])
      sent_str = "" if num_sent == 0 else " (" + str(num_sent) + " sent)"
      return True, "all", "Got " + str(len(new_files)) + " new emails" + sent_str + unsched_str

    ## we didn't use the keypress
    return False, "", ""


  # return (True if the key was used, False o.w.), mode, note
  def process_fileacts_key(self, key, curr_filelist):
    mode, note = "", ""

    ## If no files, only valid operation is to write a new blank draft
    if len(curr_filelist) == 0:
      if key == guicfg.WRITE_KEY:
        mode, note = gui_util.go_compose_draft(self, "n", None)
        return True, mode, note
      return True, "note", "Key not recognized / nothing to do"

    ## Changing state
    if key == guicfg.OPEN_KEY:
      mode, note = self.acts.do(("open", curr_filelist, [self.mail_mgr.get(f, mailfile.STATE_L) for f in curr_filelist]))
    elif key == guicfg.CLOSE_KEY:
      mode, note = self.acts.do(("closed", curr_filelist, [self.mail_mgr.get(f, mailfile.STATE_L) for f in curr_filelist]))
    elif key == guicfg.SCHEDULE_KEY:
      mode, note = gui_util.go_schedule(self, curr_filelist)
    elif key == guicfg.TRASH_KEY:
      mode, note = self.acts.do(("trash", curr_filelist, [self.mail_mgr.get_all(f) for f in curr_filelist]))

    ## Tags
    elif key == guicfg.ADD_TAGS_KEY:
      mode, note = gui_util.go_add_tags(self, curr_filelist)
    elif key == guicfg.REMOVE_TAGS_KEY:
      mode, note = gui_util.go_remove_tags(self, curr_filelist)
    
    ## Writing and sending
    elif key == guicfg.WRITE_KEY:
      filename = curr_filelist[0]
      mode, note = gui_util.go_write_key(self, filename)
    elif key == guicfg.SEND_KEY:
      if all([filename[-5:] == "draft" for filename in curr_filelist]):
        mode, note = gui_util.go_send(self, curr_filelist)
      else:
        if len(curr_filelist) == 1:
          mode, note = "note", "Cannot send: not a draft"
        else:
          mode, note = "note", "Cannot send: not all drafts"

    # we used the key if we set the mode
    return (len(mode) > 0), mode, note


def main(screen):
  try:
    filenames = Gui(screen).go()
    output = "\n".join(filenames)
  except:
    output = traceback.format_exc()
  return output

