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
  print("executing footage " + str(args))
  tools = bslideshow.BlenderTools()
  tools.addForeground(*args)

#args: moviePath, foregroundPath, movieOutput=None
def transition (args):
  print("executing transition " + str(args))
  tools = bslideshow.BlenderTools()
  tools.addForeground(*args)

#args: moviePath, foregroundPath, movieOutput=None
def banner (args):
  print("executing banner " + str(args))
  tools = bslideshow.BlenderTools()
  tools.addForeground(*args)


  


  

  


#args: def split (self, moviePath, frameStart, frameEnd, movieOutput=None)
def split (args):
  result = None
  print("executing split " + str(args))
  tools = bslideshow.BlenderTools()
  result = tools.split(*args)
  print(str(result))
  return result

#args: def scale (self, moviePath, width = 1920, height = 1080, movieOutput=None)
def scale (args):
  result = None
  print("executing scale " + str(args))
  tools = bslideshow.BlenderTools()
  result = tools.scale(*args)
  print(str(result))
  return result

#args: def frames (self, moviePath, frameStart=None, frameEnd=None, folderOutput=None)
def frames (args):
  result = None
  print("executing frames " + str(args))
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
