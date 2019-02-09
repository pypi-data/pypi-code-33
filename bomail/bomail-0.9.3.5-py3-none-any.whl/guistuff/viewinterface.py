####
# bomail.guistuff.viewinterface
#
# Interface for a view of a tab or thread, inside the gui.
####


class ViewInterface:
  # get list of currently marked filenames (or filename under cursor)
  # for operations to apply to
  def get_curr_filenames(self):
    raise Exception("Not implemented")

  # return mode, note, new_view
  # mode: string (what to redraw, 'all', 'tab', 'note')
  # note: string (what note to redraw)
  # new_view: a ViewInterface object such as self
  def process_key(self, key):
    raise Exception("Not implemented")

  # note the messages must be reloaded
  def mark_obsolete(self):
    raise Exception("Not implemented")

  # called when new messages are received
  # need previous data??
  # no return variables
  def update_for_new(self, filelist):
    raise Exception("Not implemented")

  # called when messages/metadata are changed
  # need previous data??
  # no return variables
  def update_for_change(self, filelist):
    raise Exception("Not implemented")

  # called when messages are deleted from system
  # need previous data??
  # return True if our view is now empty, False otherwise
  def update_for_trash(self, filelist):
    raise Exception("Not implemented")

  def redraw(self, gui):
    raise Exception("Not implemented")

  # return the modified note
  def mod_note(self, note):
    raise Exception("Not implemented")


