####
# bomail.guistuff.threadreader
#
# View for reading an individual thread.
####

import os
import sys
import subprocess
import curses
import shlex
import functools

from bomail.config.config import guicfg

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.cli.chstate as chstate
import bomail.cli.send as send
import bomail.cli.compose as compose

import bomail.util.addr as addr
import bomail.util.datestuff as datestuff
import bomail.util.util as util
import bomail.util.merge_lines as merge_lines

import bomail.guistuff.display as display
import bomail.guistuff.display_fmt as display_fmt
import bomail.guistuff.gui_util as gui_util
from bomail.guistuff.viewinterface import ViewInterface

# bound num between 0 and len(mylist)-1,
# unless the list is empty in which case 0
def bound(num, mylist):
  return max(0, min(num, len(mylist)-1))

class ThreadReader(ViewInterface):
  def __init__(self, gui, filenames):
    self.gui = gui
    self.load(filenames)

  def load(self, filenames):
    self.cursor_ind = 0
    self.display_ind = 0
    self.num_marked = 0
    self.num_displayed = 0

    # list of [filename, is_marked, display_data] for each filename
    # where display_data is either None or (lines_to_display, attr_data)
    self.file_info = [[f, False, None] for f in filenames]

    # for sorting filenames and file_info
    self.sort_new = False
    self.file_key = lambda a: a  #(datestuff.parse_to_utc_datestr(self.gui.mail_mgr.get(a, mailfile.DATE_L)), a)
    self.tup_key  = lambda t: self.file_key(t[0])
    self.file_info.sort(key=self.tup_key, reverse=self.sort_new)


  def mark_obsolete(self):
    pass

  def check_bounds(self):
    self.cursor_ind = bound(self.cursor_ind, self.file_info)
    self.display_ind = max(0,min(self.display_ind, self.cursor_ind))
    self.get_draw_info(self.gui)
    if self.display_ind + self.num_displayed < self.cursor_ind:
      self.display_ind = self.cursor_ind - self.num_displayed - 1
    self.display_ind = bound(self.display_ind, self.file_info)

  # return all filenames to be affected by the current action
  def get_curr_filenames(self):
    if len(self.file_info) == 0:
      return []
    elif self.num_marked == 0:
      return [self.file_info[self.cursor_ind][0]]
    else:
      return [t[0] for t in self.file_info if t[1]]  # marked

  def recheck_thread(self):
    thread_trips = self.gui.thread_mgr.get_threads_for([t[0] for t in self.file_info], self.gui.mail_mgr)
    my_files = thread_trips[0][2]
    if len(my_files) != len(self.file_info) or any([mj != self.file_info[j] for j,mj in enumerate(my_files)]):
      self.load(my_files)
    # otherwise, the change didn't affect us

  def update_for_new(self, filelist):
    self.recheck_thread()
    
  # first, remove those no longer matching and reset display info
  # of those changed but matching
  # second, merge with newly-matching
  def update_for_change(self, filelist):
    fileset = set(filelist)
    self.recheck_thread()
    for tup in self.file_info:
      if tup[0] in fileset:
        tup[2] = None  # reset display info
  
  def update_for_trash(self, filelist):
    fset = set(filelist)
    remain_files = [t[0] for t in self.file_info if t[0] not in fset]
    if len(remain_files) != len(self.file_info):
      self.load(remain_files)
      

  # lazily load display data and return lines, attr, is_unread, is_marked
  # memoize: the data is None until requested, then is loaded
  def get_disp_info(self, ind, width):
    info = self.file_info[ind]
    if info[2] is None:  # display info not present
      info[2] = display_fmt.get_msg_lines_nothread(self.gui.mail_mgr, info[0], width)
    is_unread = info[0] in self.gui.unread_set
    is_marked = info[1]
    return info[2][0], info[2][1], is_unread, is_marked


  # return curr_view, mode, note
  # mode is "all", "view", or "note"
  # curr_view is always self because there is not thread view
  def process_key(self, key):
    mode, note = "all", ""
    
    ## Navgation
    if key == guicfg.DOWN_KEY:
      self.scroll_down()
      mode, note = "view", ""
    elif key == guicfg.UP_KEY:
      self.scroll_up()
      mode, note = "view", ""
    elif key == guicfg.WAY_DOWN_KEY:
      self.scroll_down(amt=10)
      mode, note = "view", ""
    elif key == guicfg.WAY_UP_KEY:
      self.scroll_up(amt=10)
      mode, note = "view", ""

    # mark/unmark messages
    elif key == guicfg.MARK_KEY:
      curr_data = self.file_info[self.cursor_ind]
      name = display_fmt.get_shortened(curr_data[0], self.gui.mail_mgr)
      if curr_data[1]:  # is marked
        curr_data[1] = False
        self.num_marked -= 1
        mode, note = "view", "Un-marked " + name
      else:  # is not marked
        curr_data[1] = True
        self.num_marked += 1
        mode, note = "view", "Marked " + name

    elif key == guicfg.MARK_ALL_KEY:
      if self.num_marked == len(self.file_info):  # unmark all
        for info in self.file_info:
          info[1] = False
        self.num_marked = 0
        mode, note = "view", "Marked none"
      else:
        for info in self.file_info:
          info[1] = True
        self.num_marked = len(self.file_info)
        mode, note = "view", "Marked all"

    ## Expand/contract
    # TODO

    ## Viewing
    elif key == guicfg.VIEW_KEY:
      self.gui.mark_read([self.file_info[self.cursor_ind][0]])
      subprocess.call(guicfg.read_prog + " '" + self.file_info[self.cursor_ind][0] + "'", shell=True)
      self.gui.reset_after_prog()
      mode, note = "all", ""

    ## Go back
    elif key == guicfg.LEFT_KEY:
      return self.gui.tabs[self.gui.tab_ind], "all", ""

    return self, mode, note


  def scroll_up(self, amt=1):
    buff = max(0, int((self.num_displayed-2)/2))
    if self.cursor_ind - self.display_ind <= buff:
      self.display_ind -= amt
    self.cursor_ind -= amt
    self.check_bounds()

  def scroll_down(self, amt=1):
    buff = max(0, int((self.num_displayed-2)/2))
    if self.display_ind + self.num_displayed-1 - self.cursor_ind <= buff:
      self.display_ind += amt
    self.cursor_ind += amt
    self.check_bounds()

#  def scroll_down_page(self):
#    self.scroll_down(self.display_ind + self.num_displayed - self.cursor_ind)
#
#  # attempt to scroll up until the previous cursor message leaves the screen
#  def scroll_up_page(self):
#    old_cursor_ind = self.cursor_ind
#    while self.cursor_ind > 0:
#      self.cursor_ind -= 1
#      self.get_draw_info(self.gui)  # set num_displayed
#      # check if we've scrolled up a whole page yet
#      if self.cursor_ind + self.num_displayed <= old_cursor_ind:
#        break
#    self.display_ind = self.cursor_ind

  # return lines_of_txt, attribute_data
  def get_draw_info(self, gui):
    height, width = gui.tab_area.getmaxyx()
    ind = self.display_ind
    curr_y = 0
    self.num_displayed = 0
    all_lines = []
    all_attr_data = []
    xshift = 2
    yshift = 1
    curr_y = yshift
    line_width = width-2
    line_prefix = "* "
    all_lines.append("* "*int(width/2))
    while curr_y < height and ind < len(self.file_info):
      self.num_displayed += 1
      msg_lines, orig_attr_data, is_unread, is_marked = self.get_disp_info(ind, line_width)
      attr_data = list(orig_attr_data)
      if is_unread:
        attr_data = [(y, x, w, a | curses.A_BOLD if y==0 else a) for y,x,w,a in attr_data]
      if is_marked:
        all_lines.append(line_prefix + msg_lines[0][:-2] + "X" + msg_lines[0][-1:])
        all_lines.extend([line_prefix + l for l in msg_lines[1:]])
      else:
        all_lines.extend([line_prefix + l for l in msg_lines])
      if ind == self.cursor_ind:
        # highlight the first line
        attr_data = [(y, x, w, a | guicfg.cursor_attr if y==0 else a) for y,x,w,a in attr_data]
      
      # add this message info to the list
      all_attr_data.extend([(curr_y+y, x+yshift, w, a) for y,x,w,a in attr_data])
      curr_y += len(msg_lines)
      ind += 1
    return all_lines, all_attr_data


  def mod_note(self, note, width):
    num_msgs = len(self.file_info)
    count_note = "No messages" if num_msgs == 0 else "Message " + str(self.cursor_ind+1) + " of " + str(num_msgs)
    gap = width - (len(note) + len(count_note) + 4)
    if gap >= 0:
      note += " "*(gap + 3) + count_note
    return note
  

  def redraw(self, gui):
    height, width = gui.tab_area.getmaxyx()
    all_lines, all_attr_data = self.get_draw_info(gui)
    display.write_lines(gui.tab_area, 0, height, 0, 0, all_lines, all_attr_data)
    gui.tab_area.refresh()


