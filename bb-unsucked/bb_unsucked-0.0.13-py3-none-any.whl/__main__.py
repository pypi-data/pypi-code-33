
from bb_unsucked import * # WILDCARD_REMOVE_FOR_CYTHON_BUILD

import random

def print_help():
  print("""Usage:
  bb-unsucked build-cache path/to/recent_session.har
    Read cookies from a .har file and store them in a temporary directory
  
  bb-unsucked ls [-a]
    List current semester courses
    -a will print all courses
    
  bb-unsucked announcements [course_id]
  bb-unsucked ann [course_id]
    Print all current announcements.
    if course_id is given (like "CS330") only announcements from that course will be printed.
    
  bb-unsucked list-sidebar [course_id]
    Print sidebar content names for all courses.
    if course_id is given (like "CS330") only sidebar names from that course will be printed.
  
  bb-unsucked content course_id sidebar_element_name [optional_elm_idx] [--show]
    Print the content received by clicking on a sidebar element.
    Content is usually a list, but it may be a single post or a file.
    if Content is a list and you want a specific file, pass the element index as optional_elm_idx
    User will be prompted for file name to save to, or if --show flag is passed
    a temporary file name will be generated.
  
  bb-unsucked mount /mount/root/path
    Mount all blackboard data in a tree-like structure under /mount/root/path.
    This uses FUSE and requires that you have fusepy installed.
  
  bb-unsucked ftp-server
    Host an FTP server on 127.0.0.1:2121.
    When mounted this will have the same structure as the FUSE mount.
    Requires pyftpdlib installed.
  
  bb-unsucked clear-cache
    Clears all caches, keeps cookies.
  
  bb-unsucked print-config
    Prints read in config as a .ini file (good for debugging and viewing defaults)

Notes:

  course_id is a fuzzy substring match, so passing "cs" will match "cs417", "cs330", etc.

bb-unsucked version 0.0.13, Copyright (C) 2019 Jeffrey McAteer <jeffrey.p.mcateer@outlook.com>
bb-unsucked comes with ABSOLUTELY NO WARRANTY; for details see LICENSE file
""")

if len(sys.argv) < 2:
  print_help()
  sys.exit(1)

cmd = sys.argv[1]

bb = BBUnsucked()

if cmd == "build-cache":
  if len(sys.argv) > 2:
    harfile = sys.argv[2]
    bb.import_har(harfile)
    if not bb.verify_logged_in():
      eprint("The .har file we imported does not appear to have cookies blackboard accepts.")
      eprint("If you are offline you may ignore this warning message.")
      #bb._parse_courses_from_home_dashboard() # debugging false positives
      sys.exit(1)
    sys.exit(0)
  else:
    print("File argument required")
    sys.exit(1)

def print_class_announcements(my_class):
  print(my_class.nice_name())
  print("=" * len(my_class.nice_name()))
  for announcement in my_class.announcements(bb.session, bb.get_cookies()):
    announcement.print()
    print("")
    print("-" * 45)
    print("")

def print_sidebar_content(my_class):
  print(my_class.nice_name())
  print("=" * len(my_class.nice_name()))
  links = my_class.get_sidebar_links(bb.session, bb.get_cookies())
  for link in links:
    print(link["text"])

def print_sidebar_element(my_class, sidebar_element_name, optional_elm_idx=None, show_flag=False):
  links = my_class.get_sidebar_links(bb.session, bb.get_cookies())
  for link in links:
    if sidebar_element_name.lower() in link["text"].lower():
      print(link["text"])
      print("=" * len(link["text"]))
      
      r = bb.session.get(link["url"])
      soup = BeautifulSoup(r.text, "html5lib")
      downloadable_files = [] # holds {"url": "/url", "text": "Human Name"}
      announcement_items = [] # holds BBAnnouncement s
      unknown_links = [] # Holds strings of text content, we will not attempt to parse until we know more
      
      # Look for downloadable_files
      for elm in soup.findAll("a"):
        try: # for some reason if "href" in elm wasn't working
          nothing_to_see_here = elm["href"]
        except:
          continue
        if elm["href"].startswith("/bbcswebdav/"):
          # This is a downloadable file
          url = elm["href"].strip()
          if url.startswith("/"):
            url = bb.config["BASE_DOMAIN"] + url
          downloadable_files.append({
            "url": url,
            "text": elm.text
          })
      
      # Look for announcement_items
      for elm in soup.findAll("div", {"class": "details"}):
        children = elm.findChildren("p" , recursive=False)
        if len(children) > 0:
          post_timestamp = children[0].text # Posted on: Thursday, January 3, 2019 1:20:22 PM EST
          post_timestamp = correct_bb_timestamp_misc(post_timestamp) # Posted on: Thursday, January 03, 2019 01:20:22 PM EST
          timestamp_fmt = 'Posted on: %A, %B %d, %Y %H:%M:%S %p EST'
          post_epoch_s = int(datetime.datetime.strptime(post_timestamp, timestamp_fmt).strftime("%s"))
          post_containers = elm.findChildren("div", {"class" : "vtbegenerated"}, recursive=True)
          if len(post_containers) > 0:
            announcement_items.append(
              BBAnnouncement(post_epoch_s, post_containers[0])
            )
      
      # Look for unknown_links
      for elm in soup.findAll("div", {"class": "item clearfix"}):
        unknown_links.append(elm.text.strip())
      
      # Do things with downloadable_files
      if len(downloadable_files) < 1:
        pass
      elif len(downloadable_files) == 1 or optional_elm_idx != None:
        # Download it, display it?
        dl_file = downloadable_files[int(optional_elm_idx) if optional_elm_idx != None else 0]
        print("Downloading "+dl_file["text"]+"...")
        r2 = bb.session.get(dl_file["url"], stream=True)
        if r2.status_code != 200:
          print("Error, r2.status_code={}".format(r2.status_code))
          return
        content_type_received = r2.headers['Content-Type']
        content_type_received = content_type_received.lower()
        print("Content type is {}".format(content_type_received))
        file_name = None
        if show_flag:
          extension = content_type_received.split("/")[1] if "/" in content_type_received else content_type_received
          extension = extension.replace("/", "_")
          now_s = int(time.time())
          file_name = "/tmp/{}.{}".format(now_s, extension)
          print("Auto-saving to {}".format(file_name))
        
        if file_name == None:
          file_name = input("File path to save to (enter to cancel): ")
          if len(file_name) < 3:
            print("Aborting file save...")
            return
        
        total_bytes = 0
        with open(file_name, 'wb') as f:
          for chunk in r2.iter_content(1024):
            total_bytes += len(chunk)
            f.write(chunk)
        
        kilobytes = int(total_bytes / 1000)
        print("Saved {:,} kb to {:}".format(kilobytes, file_name))
        
        if show_flag:
          subprocess.call(["xdg-open", file_name])
        else:
          open_input = input("Open using xdg-open? (n for no, anything else for yes) ")
          if not "n" in open_input:
            subprocess.call(["xdg-open", file_name])
        
      else:
        print("Downloadable files")
        print("-" * len("Downloadable files"))
        idx = 0
        for dl_file in downloadable_files:
          print("({}) ".format(idx) + dl_file["text"])
          idx += 1
      
      # Handle announcement_items
      if len(announcement_items) < 1:
        pass
      elif len(announcement_items) == 1 or optional_elm_idx != None:
        optional_elm_idx = optional_elm_idx if optional_elm_idx != None else 0
        announcement_items[optional_elm_idx].print()
      else:
        for announcement in announcement_items:
          announcement.print()
          print("-" * 45)
          print("")
      
      # Handle unknown_links
      if len(unknown_links) > 0:
        for l_name in unknown_links:
          # Make sure we don't print content we actually know of, cross-reference against files
          unknown_link_is_known = False
          for dl_file in downloadable_files:
            if dl_file["text"].lower() == l_name.lower():
              unknown_link_is_known = True
              break
          if not unknown_link_is_known:
            print("UNKNOWN CONTENT: {}".format(l_name))
      
      nothing_printed = len(announcement_items) < 1 and len(downloadable_files) < 1 and len(unknown_links) < 1
      
      if nothing_printed and "grades" in sidebar_element_name.lower():
        # try to print a table of grades
        for row_elm in soup.findAll("div", {"class": "row"}):
          item_name_cols = row_elm.findChildren("div" , {"class": "cell gradable"}, recursive=True)
          activity_cols = row_elm.findChildren("div" , {"class": "cell activity timestamp"}, recursive=True)
          grade_cols = row_elm.findChildren("div" , {"class": "cell grade"}, recursive=True)
          status_cols = row_elm.findChildren("div" , {"class": "cell gradeStatus"}, recursive=True)
          
          everything_ok = (len(item_name_cols) > 0 and
                           len(activity_cols) > 0 and
                           len(grade_cols) > 0 and
                           len(status_cols) > 0 )
          
          if not everything_ok:
            # print(row_elm)
            continue
          
          # Remove javascript in name column cells
          for child in item_name_cols[0].find_all("script"):
            child.decompose() # magic that makes it go away
          for child in item_name_cols[0].find_all("div", {"class": "itemCat"}):
            child.decompose() # magic that makes it go away
          
          for child in activity_cols[0].find_all("span", {"class": "lastActivityDate"}):
            child.decompose()
          
          name =     item_name_cols[0].text.strip()
          activity = activity_cols[0].text.strip()
          grade =    grade_cols[0].text.strip()
          status =   status_cols[0].text.strip()
          
          print("%-45s %-11s %-18s %-9s" % (name, activity, status, grade))
          
        return
      
      # If we have nothing, print debugging stuff
      if nothing_printed:
        print("Everything is empty, printing debug statement in")
        for i in [3,2,1]:
          time.sleep(1)
          print("{}...".format(i))
        
        print(r.text)
        sys.exit(1)
      
# Do additional safety checks when cookies are > 4 hours old.
if get_file_age_s(bb.config["COOKIES_FILE"]) > (4 *60 * 60):
  if not bb.verify_logged_in():
    print("You are not logged in, please run")
    print("bb-unsucked build-cache path/to/recent_session.har")
    sys.exit(1)

if cmd == "ls":
  output = ""
  if len(sys.argv) > 2 and sys.argv[2] == "-a":
    for my_class in bb.classes():
      output += my_class.nice_name() + os.linesep
  else:
    for my_class in bb.current_classes():
      output += my_class.nice_name() + os.linesep
      
  print(output)
  write_to_interpose_cache(sys.argv, output)

elif cmd == "announcements" or cmd == "ann":
  if len(sys.argv) > 2:
    course_id = sys.argv[2].upper()
    at_least_one = False
    for my_class in bb.current_classes():
      if course_id in my_class.course_id:
        at_least_one = True
        print_class_announcements(my_class)
    if not at_least_one:
      print("Class {} not found".format(course_id))
  else:
    for my_class in bb.current_classes():
      print_class_announcements(my_class)

elif cmd == "list-sidebar" or ( cmd == "content" and len(sys.argv) <= 3):
  if len(sys.argv) > 2:
    course_id = sys.argv[2].upper()
    for my_class in bb.current_classes():
      if course_id in my_class.course_id:
        print_sidebar_content(my_class)
        break
    else:
      print("Class {} not found".format(course_id))
  else:
    for my_class in bb.current_classes():
      print()
      print_sidebar_content(my_class)

elif cmd == "content":
  if len(sys.argv) > 3:
    course_id = sys.argv[2].upper()
    sidebar_element_name = sys.argv[3]
    optional_elm_idx = int(sys.argv[4]) if len(sys.argv) > 4 else None
    show_flag = "--show" in sys.argv
    for my_class in bb.current_classes():
      if course_id in my_class.course_id:
        print_sidebar_element(my_class, sidebar_element_name, optional_elm_idx=optional_elm_idx, show_flag=show_flag)
        break
    else:
      print("Class {} not found".format(course_id))
  else:
    print("Class id and sidebar_element_name are required.")

elif cmd == "mount":
  if len(sys.argv) < 3:
    print("Must pass a mount directory")
  else:
    # Verify this, it is obnoxious to mount a dir and see no files
    if not bb.verify_logged_in():
      print("You are not logged in, please run")
      print("bb-unsucked build-cache path/to/recent_session.har")
      sys.exit(1)
    mount_point = sys.argv[2]
    print("Mounting blackboard data to {}...".format(mount_point))
    bb.fuse_mount(mount_point)

elif cmd == "ftp-server":
  # TODO parse optional IP and port strings
  #if len(sys.argv) < 3:
  #  print("Must pass a mount directory")
  #else:
  # Verify this, it is obnoxious to mount a dir and see no files
  if not bb.verify_logged_in():
    print("You are not logged in, please run")
    print("bb-unsucked build-cache path/to/recent_session.har")
    sys.exit(1)
  print("Starting FTP service on 127.0.0.1:2121...")
  bb.ftp_mount(addr_port_tuple=("127.0.0.1", 2121))

elif cmd == "clear-cache":
  bb.clear_caches()
  try:
    import bb_unsucked.fuse_fs
    bb_unsucked.fuse_fs.BBFS.getattr.cache_clear()
    bb_unsucked.fuse_fs.BBFS.readdir.cache_clear()
  except:
    pass

elif cmd == "print-config":
  config = configparser.ConfigParser()
  for key in bb.config.keys():
    config.set('DEFAULT', str(key), str(bb.config[key]))
  config.write(sys.stdout)

else:
  print("Unknown command '{}'".format(cmd))
  print_help()
  sys.exit(1)
