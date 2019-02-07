import re

CPU_INFO_FILE = '/proc/cpuinfo'

HEX_PATTERN = r'^0x[0-9a-fA-F]+$'
FLOAT_PATTERN = r'^\d+\.\d+$'
INT_PATTERN = r'^\d+$'

def filterKeyName(name):
  return name.lower().replace(' ', '_')

def parseValue(value):
  if re.search(HEX_PATTERN, value):
    return int(value, 16)
  elif re.search(FLOAT_PATTERN, value):
    return float(value)
  elif re.search(INT_PATTERN, value):
    return int(value, 10)
  else:
    return value

def lineToKeyValue(line):
  return list(map(lambda item: item.strip(), line.split(':')))

def getContentSections(content):
  sections = []
  current = {}

  for items in map(lineToKeyValue, content.splitlines()):
    if len(items) < 2:
      sections.append(current)
      current = {}
    else:
      key = filterKeyName(items[0])
      current[key] = parseValue(items[1])
  sections.append(current);

  return sections

def buildInfo(content):
  info = {}
  cpus = []

  for section in getContentSections(content):
    if 'processor' in section:
      cpus.append(section)
    else:
      info = { **info, **section }

  return { 'cpus': cpus, **info }

def getCpuInfo(filename=None):
  with open(filename or CPU_INFO_FILE, 'r') as file:
    content = file.read()
    return buildInfo(content)
