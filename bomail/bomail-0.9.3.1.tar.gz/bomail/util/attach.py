####
# bomail.util.attach
#
# Utilities for dealing with attachments.
####

# given attachment paths, convert to a string to be stored in a file
# by quoting each and escaping inner quotes, then comma-and-space separating
def attach_paths_to_str(pathlist):
  pathlist = [p[1:].strip() if p.startswith(": ") else p for p in pathlist]
  anslist = ['"' + path.strip().replace('\\','\\\\').replace('"','\\"') + '"' for path in pathlist]
  return ', '.join(anslist)

# given a string formatted as above,
# parse into a list of paths
def attach_str_to_paths(s, initial_pathlist = None):
  pathlist = [] if initial_pathlist is None else initial_pathlist
  if len(s.strip()) == 0:
    return pathlist
  try:
    # find first "
    i = s.index('"')
    # find matching " by skipping anything escaped
    j = i+1
    while s[j] != '"':
      if s[j] == '\\':
        j += 1   # escapes the next character
      j += 1
    # found end of this path
    mys = s[i+1:j].replace('\\"','"').replace('\\\\','\\')
    pathlist.append(mys.strip())
    attach_str_to_paths(s[j+1:], pathlist)
    return pathlist
  except:
    pathlist.append(s)
    return pathlist

