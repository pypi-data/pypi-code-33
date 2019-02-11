r"""Command-line tool to bslideshow

Usage::

    $ bs_footage /home/mivideo.mp4 foreground.mp4 /output/fout.mp4

"""
import sys
import bslideshow
#import pkg_resources  # part of setuptools

#fullscreenshot a b c d
#len = 6
#args = ['/media/jmramoss/ALMACEN/pypi/webbrowser/sbrowser/tool.py', 'fullscreenshot', 'a', 'b', 'c', 'd']

def main():
  #print("len = " + str(len(sys.argv)))
  #print("args = " + str(sys.argv))
  args = []
  for i in range(2, len(sys.argv)):
    args.append(sys.argv[i])

  getattr(sys.modules[__name__], sys.argv[1])(args)

#args: moviePath, foregroundPath, movieOutput=None
def footage (args):
  result = None
  print("executing footage " + str(args))
  tools = bslideshow.BlenderTools()
  result = tools.addForeground(*args)
  print(str(result))
  return result

#args: def doAddTransition (self, movie1Path, movie2Path, transitionPath=None, movieOutput=None):
def transition (args):
  result = None
  print("executing transition " + str(args))
  tools = bslideshow.BlenderTools()
  result = tools.doAddTransition(*args)
  print(str(result))
  return result

#args: def addBanner (self, moviePath, title, subtitle = None, title_right = None, subtitle_right = None, framesOffset = 48, color=None, movieOutput=None):
def banner (args):
  result = None
  print("executing banner " + str(args))
  if len(args) >= 6:
    args[5] = int(args[5])
  tools = bslideshow.BlenderTools()
  result = tools.addBanner(*args)
  print(str(result))
  return result


#args: def doAddMusic (self, moviePath, musicPath, movieOutput=None):
def bgmusic (args):
  result = None
  print("executing bgmusic " + str(args))
  tools = bslideshow.BlenderTools()
  result = tools.doAddMusic(*args)
  print(str(result))
  return result

def update (args):
  result = None
  print("executing update " + str(args))
  tools = bslideshow.BlenderTools()
  tools.updateBlenderBslideshow()
  return result
  
#args: animScene (self, folderImages, movieOutput=None):
def animIages (args):
  result = None
  print("executing animIages " + str(args))
  tools = bslideshow.Director()
  result = tools.animScene(*args)
  print(str(result))
  return result


#args: def encode (self, inpath, mode, prefix = None, outpath = None):
def encode (args):
  result = None
  print("executing encode " + str(args))
  tools = bslideshow.BlenderTools()
  result = tools.encode(*args)
  print(str(result))
  return result


#args: def split (self, moviePath, frameStart, frameEnd, movieOutput=None)
def split (args):
  result = None
  print("executing split " + str(args))
  if len(args) >= 2:
    args[1] = int(args[1])
  if len(args) >= 3:
    args[2] = int(args[2])
  tools = bslideshow.BlenderTools()
  result = tools.split(*args)
  print(str(result))
  return result

#args: def scale (self, moviePath, width = 1920, height = 1080, movieOutput=None)
def scale (args):
  result = None
  print("executing scale " + str(args))
  if len(args) >= 2:
    args[1] = int(args[1])
  if len(args) >= 3:
    args[2] = int(args[2])
  tools = bslideshow.BlenderTools()
  result = tools.scale(*args)
  print(str(result))
  return result

#args: def frames (self, moviePath, frameStart=None, frameEnd=None, folderOutput=None)
def frames (args):
  result = None
  print("executing frames " + str(args))
  if len(args) >= 2:
    args[1] = int(args[1])
  if len(args) >= 3:
    args[2] = int(args[2])
  tools = bslideshow.BlenderTools()
  result = tools.frames(*args)
  print(str(result))
  return result



def screenshot (args):
  print("executing screenshot " + str(args))
  url = args[0]
  target = None if len(args) <= 1 else args[1]
  browser = sbrowser.Browser()
  browser.openUrl(url).maximize()
  browser.screenshot(target)
  browser.close()
  pass

if __name__ == '__main__':
    main()
