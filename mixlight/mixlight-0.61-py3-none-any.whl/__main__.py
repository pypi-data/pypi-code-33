
import sys, os, argparse, subprocess, time
import mixlight


from mixlight.mixlight_node import mixlight_Node

def fileCopy(pi, po, fn, strFolder=None):
  with open(pi + '/' + fn) as fi:
    with open(po + '/' + fn, "w") as fo:
      for line in fi:
        if strFolder:
          fo.write(line.replace("<folder>", strFolder))
        else:
          fo.write(line)

def main(args=None):
  """The main routine."""
  if args is None:
    args = sys.argv[1:]

  parser = argparse.ArgumentParser(description = 'mixlight argument parser')
  parser.add_argument('action', choices=[ 'config', 'install', 'start', 'hass' ], help='action to be taken')
  parser.add_argument('folder', help='configuration folder used')

  parsed = parser.parse_args(args)

  # sources folder
  sourcePath = os.path.dirname(mixlight.__file__)
  # argument folder
  if not parsed.folder.endswith('/'):
    parsed.folder = parsed.folder + '/'
  directory = os.path.dirname(parsed.folder)
  if not os.path.exists(directory):
    os.makedirs(directory)

  # check command
  if parsed.action == 'config':
    fileCopy(sourcePath, parsed.folder, 'mixlight.yaml')
    fileCopy(sourcePath, parsed.folder, 'entities.yaml')
  elif parsed.action == 'install':
    daemonsFolder = '/lib/systemd/system'
    fileCopy(sourcePath, daemonsFolder, 'mixlight.service', parsed.folder)
    subprocess.check_output(['systemctl', 'daemon-reload'])
  elif parsed.action == 'hass':
    daemonsFolder = '/lib/systemd/system'
    fileCopy(sourcePath, daemonsFolder, 'hass.service', parsed.folder)
    subprocess.check_output(['systemctl', 'daemon-reload'])
  elif parsed.action == 'start':
    linker = mixlight_Node(directory)
    linker.load_config()
    linker.start()
    try:
      while True:
        linker.check_entities()
        linker.write_changes()
        time.sleep(0.01)
    except KeyboardInterrupt:
      linker.unregister()
      linker.stop()


if __name__ == "__main__":
    main()

