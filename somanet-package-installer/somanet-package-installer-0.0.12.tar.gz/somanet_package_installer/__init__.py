import subprocess
import glob
import time
import re
import tempfile
import zipfile

import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='(%(levelname)s): %(message)s')
log = logging.getLogger(__name__)

name = 'somanet_package_installer'

def check_ethercat_slaves():
  """Check that the ethercat service has been started
  and that there are slaves.
  """
  proc = subprocess.run(['ethercat', 'slave'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  if proc.returncode != 0:
    raise RuntimeError('Command ethercat slave failed with: %s', proc.stderr.decode('utf-8').rstrip('\n'))

  if not proc.stdout:
    raise RuntimeError('No slaves detected')

def write_sii_to_slave(path, position=0):
  """Write SSI file to slave at the given position.

  Keyword arguments:
  path -- path to SSI file
  position -- slave position on the network (default 0)
  """
  log.info('Write SSI file %s to slave at position %s.', path, position)
  proc = subprocess.run(['ethercat', '-p', str(position), 'sii_write', path])

  if proc.returncode != 0:
    raise RuntimeError('Could not write SSI file %s to slave %s.' % (path, position))

def write_file_to_slave(path, position=0):
  """Write file to slave at the given position.

  Keyword arguments:
  path -- path to file
  position -- slave position on the network (default 0)
  """
  log.info('Write file %s to slave at position %s.', path, position)
  proc = subprocess.run(['ethercat', '-p', str(position), 'foe_write', path])

  if proc.returncode != 0:
    raise RuntimeError('Could not write file %s to slave %s.' % (path, position))

def write_esi_parts_to_slave(dtemp, position=0):
  """Write parts of ESI archive from temporary directory to slave at the given position.

  Keyword arguments:
  dtemp -- temporary directory where parts of ESI archive reside, run split_esi_into_parts first
  position -- slave position on the network (default 0)
  """
  log.info('Write parts of ESI archive to slave at position %s.', position)
  parts = glob.glob(dtemp + '/*.part*')
  parts.sort()
  for part in parts:
    write_file_to_slave(part, position)

def write_firmware_to_slave(bin_path, position=0):
  """Write firmware binary file to slave.

  Keyword arguments:
  bin_path -- path to firmware binary file
  position -- slave position on the network (default 0)
  """
  write_file_to_slave(bin_path, position)

def write_stack_info_to_slave(path, secret, position=0):
  """Write stack_info.json file to slave at the given position.

  Keyword arguments:
  path -- path to stack_info.json file
  position -- slave position on the network (default 0)
  """
  change_state_for_slave('BOOT', position)
  time.sleep(1)
  unlock_stack_for_slave(secret, position)
  time.sleep(1)
  write_file_to_slave(path, position)

def change_state_for_slave(state, position=0):
  """Change state for slave at the given position.

  Keyword arguments:
  state -- EtherCAT state that can be one of: INIT, PREOP, BOOT, SAFEOP or OP
  position -- slave position on the network (default 0)
  """
  log.info('Change state to %s for slave at position %s.', state, position)
  proc = subprocess.run(['ethercat', 'state', state])

  if proc.returncode != 0:
    raise RuntimeError('Could not change to %s for slave at position %s.' % (state, position))

def unlock_stack_for_slave(secret, position=0):
  """Unlock stack for slave at the given position.

  Keyword arguments:
  position -- slave position on the network (default 0)
  """
  log.info('Unlock stack for slave at position %s.', position)
  proc = subprocess.run(['ethercat', '-p', str(position), 'foe_read', 'fs-stackunlock=' + secret])

  if proc.returncode != 0:
    raise RuntimeError('Could not unlock stack for slave at position %s.' % (position))


def remove_file_from_slave(path, position=0):
  """Remove file from slave at the given position.

  Keyword arguments:
  path -- path to file
  position -- slave position on the network (default 0)
  """
  log.info('Remove file %s from slave at position %s.', path, position)
  proc = subprocess.run(['ethercat', '-p', str(position), 'foe_read', 'fs-remove=' + path])

  if proc.returncode != 0:
    raise RuntimeError('Could not remove file %s from slave at position %s.' % (path, position))

def remove_esi_parts_from_slave(position=0, esi='SOMANET_CiA_402.xml.zip'):
  """Remove parts of ESI archive from slave at the given position.

  Keyword arguments:
  position -- slave position on the network (default 0)
  esi -- name of ESI archive (default 'SOMANET_CiA_402.xml.zip')
  """
  proc = subprocess.Popen(['ethercat', '-p', str(position), 'foe_read', 'fs-getlist'], stdout=subprocess.PIPE)
  proc.wait()

  parts = []
  while True:
    line = proc.stdout.readline().decode('utf-8')
    if not line:
      break
    else:
      if (line.rstrip('\n').startswith(esi + '.part')):
        parts.append(line[:line.index(',')])

  for part in parts:
    remove_file_from_slave(part, position)

def split_esi_into_parts(dtemp, esi='SOMANET_CiA_402.xml.zip', bytes=9000):
  """Split ESI archive in temporary directory into parts of the given size.

  Keyword arguments:
  dtemp -- temporary directory where ESI archive resides
  esi -- name of ESI archive (default 'SOMANET_CiA_402.xml.zip')
  bytes -- parts max size in bytes (default 9000)
  """
  log.info('Split ESI archive %s into parts of %s bytes in size.', esi, bytes)
  proc = subprocess.run(['split', '--bytes=' + str(bytes), '-a', '3', '-d', dtemp + '/' + esi, dtemp + '/' + esi + '.part'])

  if proc.returncode != 0:
    raise RuntimeError('Could not split ESI archive %s into parts of %s bytes in size.' % (esi, bytes))

def clear_slave(position=0):
  """Remove cogging_torque.bin, config.csv and plant_model.csv from slave at the given position.

  Keyword arguments:
  position -- slave position on the network (default 0)
  """
  remove_file_from_slave('cogging_torque.bin', position)
  remove_file_from_slave('config.csv', position)
  remove_file_from_slave('plant_model.csv', position)

def erase_all(bsp_path, adapter_id=0):
  """Erase all memory on the flash device using the provided bsp and adapter id.

  Keyword arguments:
  bsp_path -- path to board support file, e.g. SOMANET-CoreC2X.xn
  adapter_id -- target adapter ID reported by `xflash -l` (default 0)
  """
  log.info('Erase all memory on the flash device using bsp %s from slave with adapter ID %s.', bsp_path, adapter_id)
  proc = subprocess.run(['xflash', '--id', str(adapter_id), '--erase-all', '--target-file', bsp_path])

  if proc.returncode != 0:
    raise RuntimeError('Could not erase all memory on the flash device using bsp %s from slave with adapter ID %s.' % (bsp_path, adapter_id))

def install_bootloader(bin_path, bsp_path, adapter_id=0):
  """Install bootloader on the device using the provided bootloader binary, bsp and adapter id.

  Keyword arguments:
  bin_path -- path to bootloader binary, e.g. app_SOMANET_bootloader-CoreC2X-ECAT-UART.bin
  bsp_path -- path to board support file, e.g. SOMANET-CoreC2X.xn
  adapter_id -- target adapter ID reported by `xflash -l` (default 0)
  """
  log.info('Install bootloader %s on the device using bsp %s from slave with adapter ID %s.', bin_path, bsp_path, adapter_id)
  proc = subprocess.run(['xflash', '--id', str(adapter_id), '--write-all', bin_path, '--target-file', bsp_path, '--boot-partition', '0x90000'])

  if proc.returncode != 0:
    raise RuntimeError('Could not install bootloader %s on the device using bsp %s from slave with adapter ID %s.' %(bin_path, bsp_path, adapter_id))

def match_filenames(pattern, position=0):
  """Match filenames by pattern for slave at the given position.

  Keyword arguments:
  pattern -- regular expression pattern, e.g. '^SOMANET_CiA_402.xml.zip.part'
  position -- slave position on the network (default 0)
  """
  filenames = []
  proc = subprocess.Popen(['ethercat', '-p', str(position), 'foe_read', 'fs-getlist'], stdout=subprocess.PIPE)
  proc.wait()

  if proc.returncode != 0:
    raise RuntimeError('Could not match filenames for slave at position %s.' % (position))

  p = re.compile(pattern)
  for line in proc.stdout.readlines():
    filename = line.decode('utf-8').rstrip("\n")
    filename = re.sub(r', size: \d+\s+$', "", filename)
    if p.match(filename):
      filenames.append(filename)
  return filenames

def extract_esi(position=0):
  """Reads all ESI chunks and extracts them from slave at the given position.

  Keyword arguments:
  position -- slave position on the network (default 0)
  """
  filenames = match_filenames('^SOMANET_CiA_402.xml.zip.part', 0)
  if len(filenames) > 0:
    dtemp = tempfile.mkdtemp(None, 'somanet-package-installer-esi-')
    f = open(dtemp + '/SOMANET_CiA_402.xml.zip', 'ab')
    for filename in filenames:
      proc = subprocess.Popen(['ethercat', '-p', str(position), 'foe_read', filename], stdout=subprocess.PIPE)
      proc.wait()

      if proc.returncode != 0:
        raise RuntimeError('Could not read all ESI chunks and extract them from slave at position %s' % (position))

      f.write(proc.stdout.read())
    f.close()

    zf = zipfile.ZipFile(dtemp + '/SOMANET_CiA_402.xml.zip')
    zf.extract('SOMANET_CiA_402.xml', dtemp)
    zf.close()

    f = open(dtemp + '/SOMANET_CiA_402.xml', 'r')
    content = f.read()
    f.close()
    return content
  else:
    log.error('No ESI chunks found on slave at position %s.', position)
