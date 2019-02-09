####
# bomail.util.thread
#
# Manages EMAIL threads (not multithreading), a.k.a. conversations.
####

import sys
import os
import bisect

import bomail.cli.mailfile as mailfile
import bomail.util.util as util
import bomail.util.msgids as msgids
import bomail.util.datestuff as datestuff
import bomail.guistuff.display_fmt as display_fmt

####
# base source of algorithm:
# http://www.jwz.org/doc/threading.html 
# (with my tweaks)

# Every possible email has a unique msg_id;
# some of them also have filenames present.
# For every msg_id we hear about that is relevant, we have a "container"
# and entry in id_to_cntr.
# Each thread is a tree of containers with some root.
# Threads also have "pruned" versions that remove containers for which
# we don't have filenames.
####

usage_str = """
Usage:
    python3 thread.py -h     # print this help
    python3 thread.py

Reads a list of filenames from stdin, one per line.
Prints a representation of each thread those files belong to.
"""

class ThreadMgr:
  def __init__(self):
    self.id_to_cntr = {}         # msg_id to its Container
    self.id_to_pruned_root = {}  # msg_id to its root's Container

  # return all (pruned) roots containing these files
  # prlist contains (msgid, filename) pairs
  def update_for_add(self, prlist, mail_mgr):
    #print("==== Calling update_for_add\n    " + "\n    ".join(list(map(str,prlist))) + "\n====\n")
    touched_cntrs = build_id_to_cntr(prlist, mail_mgr, self.id_to_cntr)
    return self.do_pruning(touched_cntrs, mail_mgr)

  # return pruned roots for all these containers
  def do_pruning(self, touched_cntrs, mail_mgr):
    touched_rootset = set()
    for c in touched_cntrs:
      while c.parent is not None:
        c = c.parent
      touched_rootset.add(c)
    pruned_roots = prune_empty(list(touched_rootset), is_root_list=True)
    for r in pruned_roots:
      r.point_to_pruned_root(r, self.id_to_pruned_root)
      r.recount()
    return pruned_roots

  # don't remove container, because its msg_id may be part of a useful chain
  # and don't look up any of these files in mail_mgr, as they don't exist anymore!
  def update_for_trash(self, filelist, data_list, mail_mgr):
    msg_id_list = [d[mailfile.MSG_ID_L] for d in data_list]
    touched_cntrs = []
    for msg_id in msg_id_list:
      if msg_id in self.id_to_cntr:
        c = self.id_to_cntr[msg_id]
        c.remove_self()
        touched_cntrs.append(c)
    return self.do_pruning(touched_cntrs, mail_mgr)


  # given a "base" filename list
  # Return a list of triples (matching_files, root_cntr, all_files) where:
  #  - each triple corresponds to one thread
  #  - matching_files are those from the *base* list that are in this thread
  #  - root_cntr is the Container of the root of the thread
  #  - all_files is a list in some order of *all* files in thread
  #  - sort order of matching_files and threads are according to filelist
  #    (first entry in each thread being used)
  def get_threads_for(self, flist, mail_mgr):
    if len(flist) == 0:
      return []  # I love this case
    #print("==== Calling get_threads_for\n    " + "\n    ".join(filelist) + "\n====\n")
    msg_id_list = [mail_mgr.get(f, mailfile.MSG_ID_L) for f in flist]
    new_prlist = [(m,f) for m,f in zip(msg_id_list,flist) if m not in self.id_to_pruned_root]
    self.update_for_add(new_prlist, mail_mgr)
    return self.get_the_threads(flist, msg_id_list)


  # this is pretty slow with many threads...
  # return list of triples (matching_files_in_thread, root, all_files_in_thread)
  def get_the_threads(self, flist, msg_id_list):
    results = []
    results_roots = {}  # map container to int, its index in results
    for msg_id,f in zip(msg_id_list, flist):
      try:
        r = self.id_to_pruned_root[msg_id]
      except:
        util.err_log("Thread error: message id not in self.id_to_pruned_root.\n" + str(msg_id) + "\n" + str(f) + "\nIs in id_to_cntr: " + str(msg_id in self.id_to_cntr))
        continue
      if r in results_roots:
        results[results_roots[r]][0].append(f)
      else:
        temp = []
        #r.build_fname_list(temp)
        build_fname_list_2(r, temp)
        results_roots[r] = len(results)
        results.append(([f], r, temp))
    return results




# MAIN THREAD-BUILDING ALGORITHM
# build all message Containers and put in the table id_to_cntr
# prlist contains (msgid, filename) pairs
# mutates prlist
# return list of all files touched
def build_id_to_cntr(prlist, mgr, id_to_cntr):
  #print("==== Calling build_id_to_cntr\n    " + "\n    ".join(list(map(str,prlist))) + "\n====\n")
  # use to track already-added filenames
  fileset = set(f for m,f in prlist)
  file_i = 0
  touched_cntrs = []

  # go through files creating containers for all msg_ids encountered
  # and setting their parent-child relationships
  while file_i < len(prlist):  # note prlist gets lengthened dynamically
    msg_id,filename = prlist[file_i]
    #print("-------- Iterating on " + str(filename) +"\n")

    # A. get this message's container
    if msg_id in id_to_cntr:
      cntr = id_to_cntr[msg_id]
    else:
      cntr = Container(msg_id)
      id_to_cntr[msg_id] = cntr
    cntr.filename = filename
    touched_cntrs.append(cntr)

    # A.5 (Bo's modification) append my "children" messages to prlist if not there
    children_ids = mgr.get_refby(filename)
    for c_id in children_ids:
      #print("-- referenced by " + c_id)
      if mgr.ids.has(c_id) and c_id not in id_to_cntr:
        #print("not in id_to_cntr!")
        c_fname = mgr.ids.get(c_id)
        if c_fname not in fileset:
          #print("nor in fileset!")
          fileset.add(c_fname)
          prlist.append((c_id,c_fname))

    # B. link its references list together as "parent of parent of ... of this"
    # First create containers for any of them if necessary
    # Also, add their files to filelist if not present
    ref_ids = mgr.get_references(filename)
    ref_containers = []
    for ref_id in ref_ids:
      #print("-- references " + ref_id)
      if ref_id == msg_id:  # message references itself. this happens sometimes
        continue

      # add its containers to table if not present
      if ref_id in id_to_cntr:
        ref_cntr = id_to_cntr[ref_id]
      else:
        ref_cntr = Container(ref_id)
        id_to_cntr[ref_id] = ref_cntr
      ref_containers.append(ref_cntr)
      # also append ref_id's onto prlist if file exists
      if mgr.ids.has(ref_id):
        ref_filename = mgr.ids.get(ref_id)
        if ref_filename not in fileset:
          prlist.append((ref_id,ref_filename))
          fileset.add(ref_filename)
    # Second, link the containers, but don't overwrite existing parent-child links
    for i in range(len(ref_containers)-1):
      # do the linking
      a,b = ref_containers[i], ref_containers[i+1]
      if b.parent is None and not a.has_descendant(b.msg_id) and not b.has_descendant(a.msg_id):
        a.add_child(b, mgr)

    # C. definitively set the parent of this message, overwriting existing relationships
    if cntr.parent is not None:
      cntr.parent.children.remove(cntr)
      cntr.parent = None
    if len(ref_containers) > 0:
      # This if-condition failing would be bizarre, but it's happened to me
      if not cntr.has_descendant(ref_containers[-1].msg_id):
        ref_containers[-1].add_child(cntr, mgr)

    # D. increment file_i
    file_i += 1
  return touched_cntrs


# Prune empty containers (those with no file) where possible.
# Originally given list of root containers, recursively works down.
# If given container is empty, prune it if:
#  - it's a root with only one child - the child takes its place.
#  - it's a non-root - all its children get "spliced" in at its level.
# Return the pruned list (do not modify original)
def prune_empty(cntr_list, is_root_list=False):
  if len(cntr_list) == 0:
    return []

  # A. prune all children of containers in this list
  for c in cntr_list:
    c.pruned_children = prune_empty(c.children)

  # B. prune empty containers from this list and promote their children
  new_cntr_list = []
  for c in cntr_list:
    if c.filename is None and (not is_root_list or len(c.pruned_children) == 1):
      new_cntr_list += c.pruned_children
    else:
      new_cntr_list.append(c)
  return new_cntr_list
  

class Container:
  def __init__(self, msg_id):
    self.msg_id = msg_id
    self.parent = None  # Container
    self.children = []
    self.pruned_children = []   # prunes msg_ids with no associated file
    self.filename = None
    self.count = 0  # number in descendents (including self) who have a filename


  def __str__(self):
    return "Container " + self.msg_id + " : " + str(self.filename) + " : " + str(self.children)

  def __repr__(self):
    return str(self)

  def __hash__(self):
    return hash(self.msg_id)

  def __eq__(self, other):
    return self.msg_id == other.msg_id

  def __ne__(self, other):
    return self.msg_id != other.msg_id


  def add_child(self, child, mgr):
    self.children.append(child)
    child.parent = self
#    sort_msgs(self.children, mgr)


  def get_root(self):
    return self if self.parent is None else self.parent.get_root()


  # Do NOT use pruned_children for this, or we might miss a relationship
  # that has been pruned
  def has_descendant(self, mid):
    if self.msg_id == mid:
      return True
    for c in self.children:
      if c.has_descendant(mid):
        return True
    return False

  def remove_self(self):
    self.filename = None


  # point pruned msg_ids to roots
  def point_to_pruned_root(self, r, id_to_pruned_root):
    id_to_pruned_root[self.msg_id] = r
    for c in self.pruned_children:
      c.point_to_pruned_root(r, id_to_pruned_root)


  def recount(self):
    num = 0 if self.filename is None else 1
    for c in self.pruned_children:
      num += c.recount()
    self.count = num
    return num

  # add (level, filename) to list in preorder depth-first order:
  # me, first child and all descendants, second child and all descendants, ....
  def build_level_and_name_list(self, a, level=0):
    if self.filename is not None:
      a.append((level, self.filename))
    for c in self.pruned_children:
      c.build_level_and_list(a, level+1)

  # just get a list of all filenames in the tree
  # This simple recursive version is not used due to performance
  def build_fname_list(self, a):
    if self.filename is not None:
      a.append(self.filename)
    for c in self.pruned_children:
      c.build_fname_list(a)


# build a list of all filenames in the tree rooted at node
# this is called a lot so tried to make it fast one size-one trees
# and overall
def build_fname_list_2(node, a):
  f = node.filename
  if f is not None:
    a.append(f)
  if len(node.pruned_children) == 0:
    return
  nodes = list(node.pruned_children)
  while len(nodes) > 0:
    n = nodes.pop()
    f = n.filename
    if f is not None:
      a.append(f)
    for c in n.pruned_children:
      nodes.append(c)
    

if __name__ == "__main__":
  if "-h" in sys.argv:
    print(usage_str)
    exit(0)
  width = 100  # TODO command-line option

  mail_mgr = mailfile.MailMgr()
  thread_mgr = ThreadMgr()
  filelist = [f.strip() for f in sys.stdin.readlines()]
  thread_trips = thread_mgr.get_threads_for(filelist, mail_mgr)
  for trip in thread_trips:
    print("================")
    for f in trip[2]:  # all files in thread
      print(("--> " if f in trip[0] else "    ") + f)
      # TODO: sort and indent according to thread replies, depending on command-line option
      lines, blank_attr_data = display_fmt.get_msg_lines_nothread(mail_mgr, f, width, use_curses=False)
      for l in lines:
        print("    " + l)
      print()
    print()


