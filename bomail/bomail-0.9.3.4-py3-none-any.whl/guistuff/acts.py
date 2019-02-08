###
# bomail.guistuff.acts
#
# "acts" are any undoable actions taken by the program,
# such as changing the state of an email, adding tags, or gui actions.
####

import sys
import dateutil.parser

from bomail.config.config import pathcfg,guicfg

import bomail.cli.search as search
import bomail.cli.chstate as chstate
import bomail.cli.mailfile as mailfile
import bomail.util.datestuff as datestuff
import bomail.guistuff.display as display
import bomail.guistuff.display_fmt as display_fmt
import bomail.guistuff.tabnothread as tabnothread
import bomail.guistuff.tabthread as tabthread


class Acts:
  def __init__(self, gui):
    self.acts = []
    self.act_ind = -1
    self.gui = gui

  def do(self, act):
    self.acts = self.acts[:self.act_ind + 1]  # cut off any old branches
    self.act_ind = len(self.acts) - 1         # just in case the index got too large
    self.acts.append(act)
    return self.redo()

  # return pair a, note
  # where a = kind of redraw to do
  def redo(self):
    self.act_ind += 1
    act = self.acts[self.act_ind]
    return self.exec_act(act)
    
  def exec_act(self, act):
    with open(pathcfg.acts_log_file, "a") as f:
      f.write("DO: " + str(act) + "\n")
    if act[0] in ["trash", "open", "closed", "scheduled", "add tags", "remove tags", "add attach", "remove attach"]:
      if len(act[1]) >= 100:  # number 100 chosen via extensive UI studies
        display.redraw_note(self.gui, "Processing command (please wait)...")

    if act[0] == "trash":  # ("trash", filelist, datalist)
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      chstate.trash(act[1], self.gui.mail_mgr)
      self.gui.update_for_trash(act[1], act[2])
      return "all", "Trashed " + shorts

    elif act[0] in ["open", "closed", "scheduled"]:  # (act, filelist, prevstatelist [, schedobj])
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      if act[0] == "open":
        chstate.make_open(act[1], self.gui.mail_mgr)
        note = "Opened " + shorts
      elif act[0] == "closed":
        chstate.make_closed(act[1], self.gui.mail_mgr)
        note = "Closed " + shorts
      else:
        chstate.schedule(act[1], act[3], self.gui.mail_mgr)
        note = "Scheduled for " + datestuff.get_local_str(act[3]).replace("T"," ") + ": " + shorts
      self.gui.update_for_change(act[1])
      return "all", note

    elif act[0] == "add tags":  # ("add tags", filelist, addedtagslist, oldtagslists, brandnewtags)
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      self.gui.mail_mgr.add_tags(act[1], act[2])
      if len(act[4]) > 0:
        self.gui.tag_mgr.add_tags(act[4])
      self.gui.update_for_change(act[1])
      return "all", "Added tags: " + ", ".join(act[2]) + " to " + shorts

    elif act[0] == "remove tags":  # ("remove tags", filelist, removedtagslist, oldtagslists)
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      self.gui.mail_mgr.remove_tags(act[1], act[2])
      self.gui.update_for_change(act[1])
      return "all", "Removed tags: " + ", ".join(act[2]) + " from " + shorts

    elif act[0] == "add attach":  # ("add attach", filelist, old_attachlist, new_attachlist)
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      for f in act[1]:
        self.gui.mail_mgr.set_attachlist(f, act[2] + act[3])
      self.gui.update_for_change(act[1])
      return "view", "Added attachment " + ", ".join(act[3]) + " to " + shorts

    elif act[0] == "remove attach":  # ("remove attach", filelist, prev_attachlist, remove_attachlist)
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      for f in act[1]:
        self.gui.mail_mgr.set_attachlist(f, [s for s in act[2] if s not in act[3]])
      self.gui.update_for_change(act[1])
      return "view", "Removed attachment " + ", ".join(act[3]) + " from " + shorts

    elif act[0] == "edit tab":  # ("edit tab", tab_ind, new_str, old_str)
      if not search.is_valid_searchstr(act[2]):
        return "all", "Cancelled, not a valid search string: " + act[2]
      self.gui.tabs[act[1]].search_str = act[2]
      self.gui.tabs[act[1]].load()
      self.gui.rewrite_tab_searches()
      self.gui.change_tab_ind(act[1])
      return "all", "Changed tab search string to: " + act[2]

    elif act[0] == "add tab":  # ("add tab", tab_ind, new_str)
      if not search.is_valid_searchstr(act[2]):
        return "all", "Cancelled, not a valid search string: " + act[2]
      if guicfg.threads_on:
        self.gui.tabs.insert(act[1], tabthread.TabThread(act[2], self.gui))
      else:
        self.gui.tabs.insert(act[1], tabnothread.TabNoThread(act[2], self.gui))
      self.gui.rewrite_tab_searches()
      self.gui.change_tab_ind(act[1])
      return "all", "Added new tab with search string: " + act[2]

    elif act[0] == "remove tab":  # ("remove tab", tab_ind, tab object, disp_info)
      del self.gui.tabs[act[1]]
      self.gui.rewrite_tab_searches()
      self.gui.change_tab_ind(min(act[1]-1, len(self.gui.tabs)-1))
      return "all", "Removed tab with search string: " + act[2].search_str

    elif act[0] == "move tab":  # ("move tab", tab_ind, amount)
      src = act[1]
      dest = src + act[2]
      self.gui.tabs[src], self.gui.tabs[dest] = self.gui.tabs[dest], self.gui.tabs[src]
      self.gui.change_tab_ind(dest)
      self.gui.rewrite_tab_searches()
      return "all", "Shifted tab " + ("left" if dest < src else "right")

    elif act[0] == "edit file":  # ("edit file", filename, mailfile_line, new_str, old_str)
      self.gui.mail_mgr.set(act[1], act[2], act[3])
      return "all", "Edited [" + mailfile.fields[act[2]] + "] of " + display_fmt.get_shortened(act[1], self.gui.mail_mgr) + " to: " + act[3]

    else:
      return "all", "Error: unknown action: " + act[0]


  def undo(self):
    act = self.acts[self.act_ind]
    self.act_ind -= 1
    with open(pathcfg.acts_log_file, "a") as f:
      f.write("UNDO: " + str(act) + "\n")

    if act[0] in ["trash", "open", "closed", "scheduled"]:
      if act[0] == "trash":  # ("trash", filelist, datalist)
        chstate.untrash(act[1], act[2], self.gui.mail_mgr)
        prevstates = [d[mailfile.STATE_L] for d in act[2]]
      else:  # (act, filelist, prevstatelist [, sched])
        prevstates = act[2]
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      
      openlist = []
      closedlist = []
      for f,s in zip(act[1], prevstates):
        if s == "open":
          openlist.append(f)
        elif s == "closed":
          closedlist.append(f)
        else:
          chstate.schedule([f], dateutil.parser.parse(s.split()[1]), self.gui.mail_mgr)
      if len(openlist) > 0:
        chstate.make_open(openlist, self.gui.mail_mgr)
      if len(closedlist) > 0:
        chstate.make_closed(closedlist, self.gui.mail_mgr)
      if act[0] == "trash":
        self.gui.update_for_new(act[1])
      else:
        self.gui.update_for_change(act[1])
      return "all", "Undid change of state to " + act[0] + " for " + shorts

    elif act[0] in ["add tags", "remove tags"]:  # (act, filelist, tagslist, oldtagslists [, brand_new_tags])
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      for f,prev in zip(act[1], act[3]):
        self.gui.mail_mgr.set_tags([f], prev)
      if act[0] == "add tags" and len(act[4]) > 0:
        self.gui.tag_mgr.remove_tags(act[4])
      self.gui.update_for_change(act[1])
      return "all", "Undid edit of tags for " + shorts

    elif act[0] == "add attach":  # ("add attach", filelist, old_attachlist, new_attachlist)
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      for f in act[1]:
        self.gui.mail_mgr.set_attachlist(f, act[2])
      self.gui.update_for_change(act[1])
      return "view", "Undid new attachment to " + shorts

    elif act[0] == "remove attach":  # ("remove attach", filelist, prev_attachlist, remove_attachlist)
      shorts = display_fmt.get_shortened_list(act[1], self.gui.mail_mgr)
      for f in act[1]:
        self.gui.mail_mgr.set_attachlist(f, act[2])
      self.gui.update_for_change(act[1])
      return "view", "Undid removal of attachment from " + shorts

    elif act[0] == "edit file":  # ("edit file", filename, mailfile_line, new_str, old_str)
      self.gui.mail_mgr.set(act[1], act[2], act[4])
      return "all", "Undid edit of [" + mailfile.fields[act[2]] + "] for " + display_fmt.get_shortened(act[1], self.gui.mail_mgr)

    elif act[0] == "edit tab":  # ("edit tab", tab_ind, new_str, old_str)
      self.gui.tabs[act[1]].search_str = act[3]
      self.gui.tabs[act[1]].mark_obsolete()
      self.gui.rewrite_tab_searches()
      return "all", "Undid change of tab search string"

    elif act[0] == "add tab":  # ("add tab", tab_ind, new_str)
      del self.gui.tabs[act[1]]
      self.gui.change_tab_ind(max(0, act[1]-1))
      self.gui.rewrite_tab_searches()
      return "all", "Undid addition of new tab"

    elif act[0] == "remove tab":  # ("remove tab", tab_ind, tab_object, disp_info)
      self.gui.tabs.insert(act[1], act[2])
      act[2].mark_obsolete()
      self.gui.change_tab_ind(act[1])
      self.gui.rewrite_tab_searches()
      return "all", "Undid removal of tab"

    elif act[0] == "move tab":  # ("move tab", tab_ind, amount)
      dest = act[1]
      src = dest + act[2]
      self.gui.tabs[src], self.gui.tabs[dest] = self.gui.tabs[dest], self.gui.tabs[src]
      self.gui.change_tab_ind(dest)
      self.gui.rewrite_tab_searches()
      return "all", "Undid shift of tab"

