#!/bin/python

import builtins, os, sys, argparse, pkgutil, imp, pprint, logging
builtins.pp = pprint.pprint

class LogFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level
      
      
def getargs(parser):
  parser.add_argument('--debug', action='store_true', default=False,
                      help='Enable debugging output')
  parser.add_argument('--verbose', action='store_true', default=False,
                      help='Be verbose')
  parser.add_argument('--quiet', action='store_true', default=False,
                      help='Be quiet')
  parser.add_argument('--debugstamp', action='store_true', default=False,
                      help='Disable debugging timestamp')


def init_logging(debug=False, debugstamp=False, verbose=False, quiet=False):
  builtins.log = logging.getLogger()
  log.setLevel(logging.NOTSET)

  if debugstamp:
    fmt = '%(asctime)s.%(msecs)03d %(threadName)s: [%(funcName)20s()] %(message)s'
  else:
    fmt = '[%(filename)s:%(lineno)s] %(message)s < < %(funcName)20s()'
  
  formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  
  if quiet:
    log.setLevel(logging.NOTSET)
    log.addFilter(LogFilter(logging.NOTSET))
  elif debug:
    log.setLevel(logging.DEBUG)
    log.addFilter(LogFilter(logging.DEBUG))
  elif verbose:
    log.setLevel(logging.INFO)
    log.addFilter(LogFilter(logging.INFO))
  else:
    log.setLevel(logging.ERROR)
    log.addFilter(LogFilter(logging.ERROR))
  
  handler.setLevel(log.getEffectiveLevel())
  log.addHandler(handler)
  
def run(desc='Choose one of the following subcommands.'):
  parser = argparse.ArgumentParser(prog=os.path.basename(os.path.splitext(sys.argv[0])[0]), description=desc)
  getargs(parser)
  subparsers = parser.add_subparsers(help='Available subcommands')
  subparser = {}
  scriptname = os.path.basename(sys.argv[0])
  
  try:
      pypaths = os.environ['PYTHONPATH'].split(os.pathsep)
  except KeyError:
      pypaths = []
    
  try:
    f, filename, detail = imp.find_module(scriptname, pypaths)
    imp.load_module(scriptname, f, filename, detail)
    if hasattr(sys.modules[scriptname], 'main') \
      and callable(sys.modules[scriptname].main):
      parser.set_defaults(func=sys.modules[scriptname].main)
    if hasattr(sys.modules[scriptname], 'getargs') \
      and callable(sys.modules[scriptname].getargs):
      sys.modules[scriptname].getargs(parser)
  except:
    raise
  
  for importer, modname, ispkg in pkgutil.iter_modules([p + '/' + scriptname for p in pypaths]):
    if ispkg: continue
    try:
      f, filename, detail = imp.find_module(modname, [importer.path])
      imp.load_module(modname, f, filename, detail)
      sys.path.append(importer.path)
      
      if hasattr(sys.modules[modname], 'main') \
        and callable(sys.modules[modname].main):
        if modname == scriptname:
          subparser[modname] = parser
        else:
          if hasattr(sys.modules[modname], 'HELP') \
            and isinstance(sys.modules[modname].HELP, str):
            subparser[modname] = subparsers.add_parser(modname, help=sys.modules[modname].HELP)
          else:
            subparser[modname] = subparsers.add_parser(modname, help='run '+modname)
        subparser[modname].set_defaults(func=sys.modules[modname].main)
      else:
        continue
      if hasattr(sys.modules[modname], 'getargs') \
        and callable(sys.modules[modname].getargs):
        sys.modules[modname].getargs(subparser[modname])

    except (ImportError, AttributeError):
      raise
    
  
  if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)
  else:
    Args = parser.parse_args(sys.argv[1:])
    init_logging(Args.debug, Args.debugstamp, Args.verbose, Args.quiet)
    print(vars(Args))
    Args.func(**vars(Args))
  
