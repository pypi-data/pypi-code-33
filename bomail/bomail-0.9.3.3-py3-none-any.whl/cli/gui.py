####
# bomail.cli.gui
#
# Launch the user interface (which is text based, so not a GUI. I know)
####

import sys
import os
import locale
import curses

import bomail.guistuff.mygui as mygui

gui_helpstr = """
Quitting
--------
q       quit the program. prints the filename(s) under the cursor

Undo and redo
-------------
You can undo/redo most actions like adding/removing tabs,
tagging messages, deleting messages. History is infinite.
u       undo last action (if possible)
r       redo action that was just undone

Tabs and searching
-----------------
Tabs are numbered across the top. Each tab has a search query and
the tab lists all matching messages (or threads).
1..9, 0 switch to that tab number
[ ]     switch one tab to the left and right
{ }     "push" this tab left or right (rearranging tabs)
+       add a new tab. will prompt for the search query
-       delete current tab
e       edit the current tab's search query
/       search within tab. Prompts for a string, then
        creates a new tab with the search results.

Navigation - messages/threads
-----------------------------
v       view thread, or open viewing program to view message.
Arrow keys scroll up/down.
If threading (conversations) is on, then right/left go into/out of
the view of a single thread. In that view, right/left will expand/
collapse individual messages. Shift+right and Shift+left will expand/
collapse all messages.

In ~/.bomailrc you can turn on hjkl_navigation (vim-style) instead
of arrow keys. In this case J and K scroll up/down fast, or
line-by-line in thread view.

Sending/receiving mail
----------------------
Note bomail does not retrieve any mail from the server, it just
looks in the new mail folder. To fetch mail, use e.g. getmail.
g       get updates: look for new mail, open scheduled messages
S       (capital S) send message (if draft); prompts you to confirm

Writing/modifying drafts
------------------------
w       "write" key. Either compose new draft or edit existing.
--If current message is not a draft, prompts these options:
n       compose a brand-new draft unrelated to this message
a       reply-all
o       reply-one (only reply to the sender)
r       reply-recipients (reply to all but sender; for mailing lists)
f       forward
[any other key cancels]
--If current message is a draft, prompts these options:
n       compose a brand-new draft unrelated to this message
e       edit this draft (calls the program chosen in ~/.bomailrc)
        note you can hand-edit the draft instead of the following...
s       edit subject line
a       add attachment(s)
x       remove attachment(s)
t       add new TO: recipient(s)
c       add new CC: recipient(s)
b       add new BCC: recipient(s)
y       remove TO: recipient(s)
v       remove CC: recipient(s)
m       remove BCC: recipient(s)
[any other key cancels]

Message metadata
-------------------------------
You can mark multiple messages and apply the following operations
to all marked messages. If none are marked, the operations apply
to the current message under the cursor.
x       toggle current message/thread as marked/unmarked
X       toggle all messages/threads in tab as marked/unmarked
o       place message(s) in open state (it matches "-open" queries)
c       place in closed state
s       place in scheduled state; prompts for date and time.
        See 'bomail help datestr'
t       move message(s) to trash (located in your bomail/trash folder)
a       add tag(s) to message(s). Opens dialogue to enter the tag
d       delete tag(s) from message(s).

"""

def main(screen):
  return mygui.main(screen)


def main_cli():
  if len(sys.argv) >= 2:
    print(gui_helpstr)
    return
  os.environ.setdefault('ESCDELAY', '25')
  locale.setlocale(locale.LC_ALL, '')
  result = curses.wrapper(main)
  os.system("clear")  # clear console and print filenames or error message
  print()
  print(result)


if __name__ == "__main__":
  main_cli()

