####
# bomail.guistuff.display
#
# Displaying various stuff on screen.
####

import sys
import time
import curses
import curses.textpad
import subprocess
import runpy
import tempfile
import os
import re
import time
import textwrap, time

import bomail.config.config as config
import bomail.config.guiconfig as guicfg
import bomail.cli.chstate as chstate
import bomail.cli.mailfile as mailfile
import bomail.cli.compose as compose
import bomail.cli.search as search
import bomail.util.addr as addr
import bomail.util.tags as tags
import bomail.util.search_opts as search_opts

def rpad(s,n):
  return s if len(s) >= n else s + " "*(n-len(s))

def lpad(s,n):
  return s if len(s) >= n else " "*(n-len(s)) + s

def pad(key_instr_pr, nkey, ninstr):
  keys,instr = key_instr_pr
  return lpad(keys,nkey) + " " + rpad(instr,ninstr)

ldur_chars = guicfg.LEFT_KEY + guicfg.DOWN_KEY + guicfg.UP_KEY + guicfg.RIGHT_KEY
way_ldur_chars = guicfg.WAY_LEFT_KEY + guicfg.WAY_DOWN_KEY + guicfg.WAY_UP_KEY + guicfg.WAY_RIGHT_KEY
page_options = "expand, fast move"
if not guicfg.hjkl_nav:
  ldur_chars = "↓↑→" 
  way_ldur_chars = "⇧ ↔"  # shift+arrows
  page_options = "expand thread"

ldur_k  = ldur_chars, "left/down/up/right"
page_k  = way_ldur_chars, page_options
quit_k  = guicfg.QUIT_KEY, "quit"
tab_k1  = guicfg.TAB_LEFT_KEY + guicfg.TAB_RIGHT_KEY, "go tab left/right"
tab_k2  = guicfg.MOVE_TAB_LEFT_KEY + guicfg.MOVE_TAB_RIGHT_KEY, "push tab left/right"
tab_k3  = guicfg.ADD_TAB_KEY + guicfg.REMOVE_TAB_KEY, "add/remove tab"
tab_k4  = guicfg.EDIT_TAB_KEY + guicfg.SEARCH_IN_TAB_KEY, "edit/search tab"
state_k = guicfg.OPEN_KEY + guicfg.CLOSE_KEY + guicfg.SCHEDULE_KEY + guicfg.TRASH_KEY, "open/close/sched/trash"
tags_k  = guicfg.ADD_TAGS_KEY + guicfg.REMOVE_TAGS_KEY, "add/delete tags"
undo_k  = guicfg.UNDO_KEY + guicfg.REDO_KEY, "undo/redo"
get_k   = guicfg.GET_KEY, "get update"
write_k = guicfg.WRITE_KEY, "write"
send_k  = guicfg.SEND_KEY, "send"
view_k  = guicfg.VIEW_KEY, "view"
mark_k  = guicfg.MARK_KEY + guicfg.MARK_ALL_KEY, "mark/all"
TAB_MSG_INSTR_STR = [
  pad(quit_k, 2,12) + pad(ldur_k, 4,23) + pad(get_k,  2,12) + pad(tab_k1,2,0),
  pad(mark_k, 2,12) + pad(page_k, 4,23) + pad(view_k, 2,12) + pad(tab_k2,2,0),
  pad(undo_k, 2,12) + pad(tags_k, 4,23) + pad(write_k,2,12) + pad(tab_k3,2,0),
  pad(("",""),2,12) + pad(state_k,4,23) + pad(send_k, 2,12) + pad(tab_k4,2,0),
]


TOPLINES = 3
BOTTOMLINES = 7


#--------------------------------------------------------------
# drawing to screen

# insert the given string to the given window with the given attribute
def my_insstr(window, y, x, s, attr):
  height, width = window.getmaxyx()
  if y >= height:
    return
  window.insstr(y, x, s.encode("utf-8")[:width-x], attr)

#def my_addstr(window, y, x, s, attr):
#  height, width = window.getmaxyx()
#  if y >= height:
#    return
#  window.addstr(y, x, s.encode("utf-8")[:width-x], attr)


# write the array of msg_lines to screen,
# then set all the attributes for each (y, x, width, attr) in attr_data
def write_lines(window, y_min, y_max, y_start, x_start, msg_lines, attr_data):
  h,w = window.getmaxyx()
  for j,line in enumerate(msg_lines):
    y = y_start + j
    if y >= y_min and y < y_max:
      try:
        my_insstr(window, y, x_start, line.encode("utf-8"), 0)
      except:
        my_insstr(window, y, x_start, line, 0)
  for j,x,width,attr in attr_data:
    x = x_start + x
    y = y_start + j
    if y >= y_min and y < y_max and x+width < w:
      window.chgat(y, x, width, attr)


def draw_loading_screen(gui):
  height, width = gui.screen.getmaxyx()
  gui.screen.clear()
  gui.screen.refresh()  # this needs to be here, no idea why
  toptabs = "[1]"
  my_insstr(gui.screen, 0, 0, toptabs, gui.attr)
  my_insstr(gui.screen, 2, 0, "-"*curses.COLS, gui.attr)
  gui.screen.chgat(0, 0, 3, curses.A_STANDOUT | gui.attr)
  gui.screen.hline(height-BOTTOMLINES, 0, "-", width, gui.attr)
  gui.screen.hline(height-BOTTOMLINES+2, 0, "-", width, gui.attr)
  redraw_note(gui, "Loading (please wait)...")
  

# mode is all, view, or note
# curr_view implements viewinterface.ViewInterface
def redraw(gui, curr_view, mode, note=""):
  # only redraw overlay if all
  if mode == "all":
    redraw_overlay(gui)
  # only redraw view if all or view
  if mode in ["all", "view"]:
    redraw_view(gui, curr_view)
  # always draw the note
  height,width = gui.note_area.getmaxyx()
  note = curr_view.mod_note(note, width)
  redraw_note(gui, note)  # refreshes screen


# top lines
def redraw_overlay(gui):
  height, width = gui.screen.getmaxyx()
  gui.screen.clear()
  gui.screen.refresh()  # this needs to be here, no idea why
  toptabs = "[1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]  [9]  [0]"
  if len(gui.tabs) <= 10:
    len_tt = len(gui.tabs)*5 - 2
    toptabs = toptabs[:len_tt]
  else:
    toptabs = toptabs + "  [ ]" * (len(gui.tabs) - 10)
  my_insstr(gui.screen, 0, 0, toptabs, gui.attr)
  my_insstr(gui.screen, 1, 0, gui.tabs[gui.tab_ind].search_str, gui.attr)
  my_insstr(gui.screen, 2, 0, "-"*curses.COLS, gui.attr)
  if 5*gui.tab_ind + 3 <= width:
    gui.screen.chgat(0, 5*gui.tab_ind, 3, curses.A_STANDOUT | gui.attr)  # highlight tab number
  gui.screen.hline(height-BOTTOMLINES, 0, "-", width, gui.attr)
  gui.screen.hline(height-BOTTOMLINES+2, 0, "-", width, gui.attr)


# tab section and commands
def redraw_view(gui, curr_view):
  gui.tab_area.clear()
  gui.tab_area.refresh()
  curr_view.redraw(gui)
  draw_bottom_text(gui, TAB_MSG_INSTR_STR)


def redraw_tab_lin(thread_view, gui):
  thread_view.ensure_display_loaded()
  height, screen_width = gui.tab_area.getmaxyx()

  # can assume we have > 0 files
  subj_str = gui.mail_mgr.get(thread_view.repr_file, mailfile.SUBJ_L)[:screen_width]
  my_insstr(gui.tab_area, 0, 0, subj_str, curses.A_BOLD | guicfg.DEFAULT_CLR_PAIR)
  gui.tab_area.hline(1, 0, "-", screen_width)
  offset = 2

  curr_y = thread_view.top_y_coord + offset
  for ind,tup in enumerate(thread_view.file_data):
    if tup[2]:  # is collapsed
      msg_lines, orig_attr_data = tup[3]  # collapsed disp_data
    else:
      msg_lines, orig_attr_data = tup[4]  # expanded disp data
    attr_data = list(orig_attr_data)
    if tup[0] in gui.unread_set:  # is_unread
      attr_data = [(y, x, w, a | curses.A_BOLD if y==0 else a) for y,x,w,a in attr_data]
    if ind == thread_view.cursor_ind:
      attr_data = [(y,x,screen_width,(attr if y>0 else attr|guicfg.cursor_attr)) for y,x,screen_width,attr in attr_data]
    write_lines(gui.tab_area, offset, height, curr_y, 0, msg_lines, attr_data)
    if curr_y >= 0 and curr_y < height and tup[1]:  # is marked
      attr = curses.A_BOLD | gui.attr
      if ind == thread_view.cursor_ind:
        attr |= guicfg.cursor_attr
      gui.tab_area.addch(curr_y, screen_width - 2, "X", attr)
    if curr_y-1 >= 0 and curr_y+1 < height and tup[2]:  # collapsed
      gui.tab_area.addstr(curr_y+1, 1, "<--")

    curr_y += len(msg_lines)

  gui.tab_area.refresh()
  draw_bottom_text(gui, TAB_MSG_INSTR_STR)


# TODO - implement!
def redraw_tab_tree(thread_view, gui):
  return redraw_tab_lin(thread_view, gui)


def draw_bottom_text(gui, lines):
  height, width = gui.commands_area.getmaxyx()
  gui.commands_area.clear()
  for i,line in enumerate(lines):
    if i >= height:
      break
    my_insstr(gui.commands_area, i, 0, lines[i], gui.attr)
  gui.commands_area.refresh()


# add "message x of y" to end of note
# return new note
def mod_note(gui, note):
  mytab = gui.tabs[gui.tab_ind]
  if guicfg.threads_on:
    if mytab.mode == "thread list":
      num_msgs = len(mytab.file_data)
      ind = mytab.cursor_ind
      count_note = "No threads" if num_msgs == 0 else "Thread " + str(ind+1) + " of " + str(num_msgs)
    elif mytab.mode == "one thread":
      num_msgs = len(mytab.file_data[mytab.cursor_ind][0].all_files)
      ind = mytab.file_data[mytab.cursor_ind][0].cursor_ind
      count_note = "No messages" if num_msgs == 0 else "Message " + str(ind+1) + " of " + str(num_msgs)
  else:
    num_msgs = len(mytab.file_data)
    ind = mytab.cursor_ind
    count_note = "No messages" if num_msgs == 0 else "Message " + str(ind+1) + " of " + str(num_msgs)
  height, width = gui.screen.getmaxyx()
  gap = width - (len(note) + len(count_note) + 4)
  if gap >= 0:
    note += " "*(gap + 3) + count_note
  return note



def redraw_note(gui, note):
  gui.note_area.clear()
  my_insstr(gui.note_area, 0, 0, note, gui.attr)
  gui.note_area.refresh()
  gui.screen.refresh()

