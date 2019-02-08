


#--------------------------------------------------------------
bomail_tabcomplete_str = """

_bomail()
{
    local cur=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=( $(compgen -W "gui process check_sched search chstate compose mailfile send stats meta" -- $cur) )
}
complete -F _bomail bomail

"""


#--------------------------------------------------------------
sample_mailhandlers_str = """## bomail mail-handling configuration for processing of new email.
## Lines starting with '#' are comments.
## To 'uncomment' a line, delete the initial #.

## ============================================================
## Global options - comment to turn off.

## Tag replies to a thread with parent message's tags
-autotagreplies

## Use tags from last line of email if of the form "tags: tag1, ..."
-lastlinetags

## Automatically close any sent mail
-close-sent

## ============================================================
## Custom handlers - you write these.
##
## Each handler has blank lines before and after it, none in the middle.
##
## It has one or more search string lines (see bomail search -h),
## followed by (optional) a state change which can be
## "open", "close", or "schedule ..." (see bomail help datestr),
## followed by (optional) "tag first-tag, second-tag, ...".
## Use OR with multiple search lines. Examples:
##
## -from Facebook
## tag social
##
## -from Twitter
## OR -subject Twitter
## close
##
## -from Instagram
## OR -subject Instagram
## OR -to instagram@domain.com
## schedule p1d
## tag social, photos
"""

#--------------------------------------------------------------
sample_config_str = """## bomail configuration file
##
## All lines beginning with # are comments and are ignored.
## To uncomment a line, delete the initial #.



## ============================================================
## User info: must edit this section!

name = YOUR NAME
email_addr = USER@DOMAIN.COM

## Send email from this server.
## If smtp_servername = localhost, the other options are ignored.
## For SMTP, read username/pass from file, or enter them here.
smtp_servername = smtp.gmail.com
smtp_port = 587
smtp_userpass_file = HOMEDIR/.getmail/getmailrc
#smtp_username = USER or USER@DOMAIN.COM
#smtp_password = PASSWORD

#alias_addresses = ALSO_ME@DOMAIN.COM, ALSO_METOO@DOMAIN.COM

## Additional aliases here. Add numbers 2,3,...
## Just edit "From" line in email to send from these instead.
#name2 = YOUR NAME
#email_addr2 = ALTERNATE@DOMAIN.COM
#smtp_servername2 = smtp.office365.com
#smtp_port2 = 993
#smtp_userpass_file2 = HOMEDIR/.getmail/getmailrc_EDITME
#smtp_username2 = USER2 or USER2@DOMAIN.COM
#smtp_password2 = PASSWORD2



## ============================================================
## Organization options: should confirm these are okay

data_location = DATADIR
new_rawmail_location = NEWMAILDIR
processed_rawmail_location = OLDMAILDIR



## ============================================================
## Important UI options

## Comment next line to turn off threading (conversations)
threads_on

read_program = less
edit_program = vim

## Uncomment next line to use vim-style navigation (hjkl for left/down/up/right)
#hjkl_navigation

## Options are light1, light2, dark1, dark2
colorscheme = dark1



## ============================================================
## Other UI options

## Options are none, some, all
strip_newlines_in_msg_preview = some

## Num lines (including subject/author/date and preview lines) per message
total_lines_per_msg = 5
threadview_total_lines_per_msg = 10

## Number of characters to use ("len") and for spacing ("pad")
date_len = 20
date_pad = 2
author_len = 24
author_pad = 2

## Comment to turn off
#hline_between_msgs
skipline_between_msgs
show_tags
tags_on_topline


"""


