####
# bomail.guistuff.tabthread
#
# Tabs when configuration has threading, i.e.
# emails are grouped into conversations.
####

import shlex
import curses

from bomail.config.config import guicfg

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search

import bomail.util.datestuff as datestuff
import bomail.util.merge_lines as merge_lines
import bomail.util.util as util

import bomail.guistuff.display as display
import bomail.guistuff.display_fmt as display_fmt
import bomail.guistuff.threadreader as threadreader
from bomail.guistuff.viewinterface import ViewInterface

# bound num between 0 and len(mylist)-1,
# unless the list is empty in which case 0
def bound(num, mylist):
  return max(0, min(num, len(mylist)-1))

class TabThread(ViewInterface):
  def __init__(self, search_str, gui):
    self.search_str = search_str
    self.gui = gui
    self.is_loaded = False
    self.cursor_ind = 0
    self.cursor_key = None  # where it sorted
    self.display_ind = 0
    self.num_marked = 0
    self.num_displayed = 0

    # list of filenames matching our search query
    # and total (pulled in by threads)
    self.matching_files = []

    # list of [match_list, all_list, is_marked, display_data]
    # where match_list is all the files in the thread matching query
    # and all_list is all files in the thread, both sorted
    self.thread_info = []

    # for sorting lists and thread_info
    self.sort_new = not "-sortold" in shlex.split(self.search_str)
    self.file_key = lambda a: a  #datestuff.parse_to_utc_datestr(self.gui.mail_mgr.get(a, mailfile.DATE_L))
    self.filelist_key = lambda l: self.file_key(l[0])
    self.tup_key = lambda t: self.filelist_key(t[0])


  def load(self):
    display.draw_loading_screen(self.gui)
    self.matching_files = search.search_argstr(self.search_str, self.gui.mail_mgr)
    self.matching_files.sort(key=self.file_key, reverse=self.sort_new)
    self.cursor_ind = 0
    self.cursor_key = None  # where it sorted
    self.display_ind = 0
    self.num_marked = 0
    self.num_displayed = 0
    # list of (matching, root_container, all) for each thread
    self.thread_info = []
    self.reload_thread_info()
    self.is_loaded = True

  def mark_obsolete(self):
    self.is_loaded = False

  def check_bounds(self):
    self.cursor_ind = bound(self.cursor_ind, self.thread_info)
    self.display_ind = min(self.display_ind, self.cursor_ind)
    self.get_draw_info(self.gui)
    if self.display_ind + self.num_displayed < self.cursor_ind:
      self.display_ind = self.cursor_ind - self.num_displayed - 1
    self.display_ind = bound(self.display_ind, self.thread_info)
    self.cursor_key = None if len(self.thread_info) == 0 else self.tup_key(self.thread_info[self.cursor_ind])

  # get files in currently marked threads, or under cursor
  def get_curr_filenames(self):
    if not self.is_loaded:
      self.load()
    if len(self.thread_info) == 0:
      return []
    elif self.num_marked == 0:
      return self.thread_info[self.cursor_ind][0]
    else:  # all files in all marked threads
      res = []
      for tup in self.thread_info:
        if tup[2]:  # is marked
          res.extend(tup[1])  # all files
      return res

  # using self.matching_files, get threads
  # and set cursor_index attempting to match previous location
  def reload_thread_info(self):
    oldsize = len(self.thread_info)
    # get new thread triples
    thread_trips = self.gui.thread_mgr.get_threads_for(self.matching_files, self.gui.mail_mgr)
    self.thread_info = [[trip[0], trip[2], False, None] for trip in thread_trips]
    self.cursor_ind = 0
    if self.cursor_key is not None:
      putbefore = (lambda t: t > self.cursor_key) if self.sort_new else (lambda t: self.cursor_key > t)
      for tup in self.thread_info:
        if putbefore(self.tup_key(tup)):
          self.cursor_ind += 1
        else:
          break
    self.num_marked = 0
    self.check_bounds()


  # new files have been imported into the system
  def update_for_new(self, filelist):
    if not self.is_loaded:
      return
    # the challenge is some of these files may not match, but be
    # replies to existing matches. It also changes sort order.
    # So re-request all threads
    new_matching = search.filter_argstr(self.search_str, self.gui.mail_mgr, filelist)
    new_matching.sort(key=self.file_key, reverse=self.sort_new)
    self.matching_files, temp = merge_lines.merge_lists(self.matching_files, new_matching, self.file_key, 0, reverse=self.sort_new)
    self.reload_thread_info()

  def update_for_change(self, filelist):
    if not self.is_loaded:
      return
    # build threads for all files that (a) did match and didn't change, (b) changed and now match
    fileset = set(filelist)
    changed_matching = search.filter_argstr(self.search_str, self.gui.mail_mgr, filelist)
    changed_matching.sort(key=self.file_key, reverse=self.sort_new)
    unchanged_matching = [f for f in self.matching_files if f not in fileset]
    oldlen = len(self.matching_files)
    self.matching_files, temp = merge_lines.merge_lists(unchanged_matching, changed_matching, self.file_key, 0, reverse=self.sort_new)
    self.reload_thread_info()

  # return True if we have no files left
  def update_for_trash(self, filelist):
    if not self.is_loaded:
      return True
    fileset = set(filelist)
    self.matching_files = [f for f in self.matching_files if f not in fileset]
    self.reload_thread_info()
    return len(self.thread_info) == 0

  # return lines, attr, is_unread, is_marked
  def get_disp_info(self, ind, width):
    info = self.thread_info[ind]
    if info[3] is None:  # display info not present
      info[3] = display_fmt.get_msg_lines_thread(self.gui.mail_mgr, info[0], info[1], width)
    is_unread = any([f in self.gui.unread_set for f in info[1]])
    is_marked = info[2]
    return info[3][0], info[3][1], is_unread, is_marked

  # return curr_view, mode, note
  # mode is "all", "view", or "note"
  # curr_view is self or a thread view to switch to
  def process_key(self, key):
    if not self.is_loaded:
      self.load()
    mode, note = "all", ""
    
    ## Navigation
    if key == guicfg.DOWN_KEY:
      self.scroll_down()
      mode, note = "view", ""
    if key == guicfg.UP_KEY:
      self.scroll_up()
      mode, note = "view", ""
    if key == guicfg.WAY_DOWN_KEY:
      self.scroll_down(amt=10)
      mode, note = "view", ""
    if key == guicfg.WAY_UP_KEY:
      self.scroll_up(amt=10)
      mode, note = "view", ""

    ## Mark/unmark threads
    elif key == guicfg.MARK_KEY:
      curr_info = self.thread_info[self.cursor_ind]
      name = display_fmt.get_shortened(curr_info[0][0], self.gui.mail_mgr)
      if curr_info[2]:  # is marked
        curr_info[2] = False
        self.num_marked -= 1
        mode, note = "view", "Un-marked " + name
      else:
        curr_info[2] = True
        self.num_marked += 1
        mode, note = "view", "Marked " + name
    elif key == guicfg.MARK_ALL_KEY:
      if self.num_marked == len(self.thread_info):  # unmark all
        for info in self.thread_info:
          info[2] = False
        self.num_marked = 0
        mode, note = "view", "Marked none"
      else:
        for info in self.thread_info:
          info[2] = True
        self.num_marked = len(self.thread_info)
        mode, note = "view", "Marked all"
     
    ## Viewing
    elif key == guicfg.VIEW_KEY or key == guicfg.RIGHT_KEY:
      myinfo = self.thread_info[self.cursor_ind]
      self.gui.mark_read(myinfo[1])
      return threadreader.ThreadReader(self.gui, myinfo[1]), "all", ""

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

  # return lines_of_txt, attribute_data
  # this is verbatim tabnothread except for file_info/thread_info...
  # probably can combine them...
  def get_draw_info(self, gui):
    height, width = gui.tab_area.getmaxyx()
    ind = self.display_ind
    curr_y = 0
    self.num_displayed = 0
    all_lines = []
    all_attr_data = []
    while curr_y < height and ind < len(self.thread_info):
      self.num_displayed += 1
      msg_lines, orig_attr_data, is_unread, is_marked = self.get_disp_info(ind, width)
      attr_data = list(orig_attr_data)
      if is_unread:
        attr_data = [(y, x, w, a | curses.A_BOLD if y==0 else a) for y,x,w,a in attr_data]
      if is_marked:
        all_lines.append(msg_lines[0][:-2] + "X" + msg_lines[0][-1:])
        all_lines.extend(msg_lines[1:])
      else:
        all_lines.extend(msg_lines)
      if ind == self.cursor_ind:
        # highlight the first line
        attr_data = [(y, x, w, a | guicfg.cursor_attr if y==0 else a) for y,x,w,a in attr_data]
      
      # add this message info to the list
      all_attr_data.extend([(curr_y+y, x, w, a) for y,x,w,a in attr_data])
      curr_y += len(msg_lines)
      ind += 1
    return all_lines, all_attr_data

  def mod_note(self, note, width):
    num_threads = len(self.thread_info)
    count_note = "No threads" if num_threads == 0 else "Thread " + str(self.cursor_ind+1) + " of " + str(num_threads)
    gap = width - (len(note) + len(count_note) + 4)
    if gap >= 0:
      note += " "*(gap + 3) + count_note
    return note
  

  # also verbatim from tabnothread
  def redraw(self, gui):
    if not self.is_loaded:
      self.load()
    # save cursor key
    height, width = gui.tab_area.getmaxyx()
    all_lines, all_attr_data = self.get_draw_info(gui)
    display.write_lines(gui.tab_area, 0, height, 0, 0, all_lines, all_attr_data)
    gui.tab_area.refresh()


