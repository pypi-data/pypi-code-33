
import os, sys


# the reason for this is to modify the variable in place ... yuck
def get_paths(pathcfg, config_filename, data_base, new_rawmail, old_rawmail):
    # --------------------------------------------------------------
    # Organization locations
    pathcfg.config_file = config_filename
    pathcfg.bomail_data_base = data_base
    pathcfg.new_rawmail_dir = new_rawmail
    pathcfg.old_rawmail_dir = old_rawmail
    
    # save a copy of sent messages here if sending from localhost
    pathcfg.save_sent_dir = pathcfg.new_rawmail_dir
    
    # --------------------------------------------------------------
    # File locations: suggested not to edit
    
    # Locations of directories
    pathcfg.rel_email_dirname = "email/"
    pathcfg.rel_drafts_dirname = "drafts/"
    pathcfg.rel_attach_dirname = "attachments/"
    pathcfg.rel_trash_dirname = "trash/"
    pathcfg.rel_metadata_dirname = "metadata/"
    pathcfg.email_dir     = os.path.join(pathcfg.bomail_data_base, pathcfg.rel_email_dirname)
    pathcfg.attach_dir    = os.path.join(pathcfg.bomail_data_base, pathcfg.rel_attach_dirname)
    pathcfg.drafts_dir    = os.path.join(pathcfg.bomail_data_base, pathcfg.rel_drafts_dirname)
    pathcfg.trash_dir     = os.path.join(pathcfg.bomail_data_base, pathcfg.rel_trash_dirname)
    pathcfg.metadata_dir  = os.path.join(pathcfg.bomail_data_base, pathcfg.rel_metadata_dirname)
    
    # Locations of files that must be edited by hand
    pathcfg.handlers_file      = os.path.join(pathcfg.metadata_dir, "mail-handlers.txt")
    pathcfg.addr_alias_file    = os.path.join(pathcfg.metadata_dir, "aliases.txt")
    
    # Locations of files that may be edited by hand
    pathcfg.tags_file          = os.path.join(pathcfg.metadata_dir, "tags.txt")
    pathcfg.addr_book_file     = os.path.join(pathcfg.metadata_dir, "addr_book.txt")
    
    # Locations of files that should not be hand-edited
    pathcfg.openlist_file      = os.path.join(pathcfg.metadata_dir, "openlist.txt")
    pathcfg.scheduledlist_file = os.path.join(pathcfg.metadata_dir, "scheduledlist.txt")
    pathcfg.msg_ids_file       = os.path.join(pathcfg.metadata_dir, "msg_ids.txt")
    pathcfg.tab_config_file    = os.path.join(pathcfg.metadata_dir, "tab_config.py")
    
    # Locations of logs, these can be deleted whenever
    pathcfg.acts_log_file      = os.path.join(pathcfg.metadata_dir, "acts_log.txt")
    pathcfg.error_log_file     = os.path.join(pathcfg.metadata_dir, "error_log.txt")

#for d in [email_dir, attach_dir, drafts_dir, trash_dir, metadata_dir]:
#  if not os.path.exists(d):
#    os.makedirs(d)


