import argparse, os, os.path, re, shutil, subprocess, winreg

__all__ = ('aunt',)

def _xml(flags, key, lang, pc):
	token = 'processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"'
	xml = (f'''<?xml encoding="utf-8"?>
<unattend>
	<settings pass="WindowsPE">
		<component name="Microsoft-Windows-International-Core-WinPE" {token}>
			<UILanguage>{lang}</UILanguage>
		</component>
		<component name="Microsoft-Windows-Setup" {token}>
			<ImageInstall>
				<OSImage>
					<InstallFrom>
						<MetaData>
							<Key>/IMAGE/INDEX</Key>
							<Value>1</Value>
						</MetaData>
					</InstallFrom>
				</OSImage>
			</ImageInstall>
			<UserData>
				<ProductKey>
					<Key>{key or ''}</Key>
				</ProductKey>''' + ('''
				<AcceptEula>true</AcceptEula>''' if 'y' in flags else '') + f'''
			</UserData>
		</component>
	</settings>
	<settings pass="specialize">
		<component name="Microsoft-Windows-Shell-Setup" {token}>
			<ComputerName>{pc or 'PC'}</ComputerName>
		</component>
	</settings>
	<settings pass="OOBESystem">
		<component name="Microsoft-Windows-International-Core" {token}>
			<SystemLocale>{lang}</SystemLocale>
		</component>
		<component name="Microsoft-Windows-Shell-Setup" {token}>
			<OOBE>''' + ('''
				<HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>''' if 'n' in flags else '') + ('''
				<HideOnlineAccountScreens>true</HideOnlineAccountScreens>''' if 'm' in flags else '') + '''
			</OOBE>
		</component>
	</settings>
</unattend>''')
	with open('_tmp\\AutoUnattend.xml', 'w', encoding='utf-8', newline='\n') as f:
		f.write(xml)

_index = re.compile(r': (\d{1,2})\s').findall
_word = re.compile(r'(\w+)').search
_lang = re.compile(r'^([a-z]{2}-[a-zA-Z]{2}) ', re.M).search

def aunt(iso=None, flags='', edition=None, key=None, lang=None, pc=None):
	show, verbose = 'q' not in flags, '\n' if 'v' in flags else ''

	def section(msg):
		if show: print(verbose + msg)

	def error(msg):
		if show: print('> ' + msg)

	def detail(msg):
		if verbose: print('  ' + msg)

	def command(*args):
		return subprocess.run((exe[args[0]], *args[1:]), capture_output=True).stdout.decode(errors='ignore')

	def find(cmd, inst):
		for path in [inst] + os.environ['PATH'].split(';'):
			if os.path.exists(path + cmd):
				return path + cmd

	if verbose: print('find dependencies')
	exe = {cmd: find(f'\\{cmd}.exe', inst) for cmd, inst in (
		('7z', 'C:\\Program Files\\7-Zip'),
		('dism', 'C:\\Windows\\System32'),
		('oscdimg', 'C:\\Windows'))}
	missing = [cmd for cmd in exe if not exe[cmd]]
	if missing:
		error('missing ' + ', '.join(missing))
		return 1
	for path in exe.values():
		detail(path)

	if not iso: return 0
	q_iso = os.path.basename(iso)
	if ' ' in q_iso: q_iso = repr(q_iso) 
	if not os.path.exists(iso):
		print('missing ' + q_iso)
		return 1

	section(f'extract {q_iso}')
	detail(f'7z x -y -o_tmp {q_iso} bootmgr '
		'boot\\{bcd,bood.sdi,bootfix.bin,etfsboot.com} sources\\{boot.wim,compres.dll,install.esd,lang.ini,setup.exe}')
	command('7z', 'x', '-y', '-o_tmp', iso, 'bootmgr', 'boot\\bcd', 'boot\\boot.sdi', 'boot\\bootfix.bin', 'boot\\etfsboot.com',
		'sources\\boot.wim', 'sources\\compres.dll', 'sources\\install.esd', 'sources\\lang.ini', 'sources\\setup.exe')

	if not edition:
		section('query EditionID')
		subkey = 'Software\\Microsoft\\Windows NT\\CurrentVersion'
		detail(f"reg query 'HKEY_LOCAL_MACHINE\\{subkey}' /v EditionID")
		with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey) as k:
			edition = winreg.QueryValueEx(k, 'EditionID')[0]
		detail('= ' + edition)

	for file, wanted in ('boot.wim', ' Setup '), ('install.esd', f': {edition}\r'):
		section(f'read {file}')
		src, tmp = '_tmp\\sources\\' + file, '_tmp\\' + file
		cmd = f'dism /Get-WimInfo /WimFile:{src}'
		detail(cmd)
		cmd = cmd.split()
		index = _index(command(*cmd))
		for i in index:
			if wanted in command(*cmd, f'/Index:{i}'):
				break
		else:
			error(_word(wanted)[1] + ' not found')
			edition = None
			break
		if len(index) > 1:
			section(f'reduce {file}')
			cmd = f'dism /Export-Image /SourceImageFile:{src} /SourceIndex:{i} /DestinationImageFile:{tmp}'
			detail(cmd)
			command(*cmd.split())
			detail(f'mv _tmp\\{{,sources\\}}{file}')
			os.replace(tmp, src)
		else:
			detail('= already reduced')

	if edition:
		if not lang:
			section("read lang.ini")
			detail(f"grep -Eom1 '^([a-z]{2}-[a-zA-Z]{2}) ' _tmp\\sources\\lang.ini")
			with open('_tmp\\sources\\lang.ini') as f:
				lang = _lang(f.read())[1]
			detail('= ' + lang)
		section('write AutoUnattend.xml')
		_xml(flags, key, lang, pc)
		section(f'write {q_iso}')
		cmd = f'oscdimg -u2 -b_tmp\\boot\\etfsboot.com _tmp'
		detail(f'{cmd} {q_iso}')
		command(*cmd.split(), iso)

	section('delete _tmp')
	detail('rm -r _tmp')
	shutil.rmtree('_tmp')
	return 0 if edition else 2

def main():
	a = argparse.ArgumentParser(None,
		'aunt [-h] [-mnqvwy] [-e ED] [-k KEY] [-l LANG] [-p NAME] [ISO]', 'Auto Unattend 0.1')
	a.add_argument('ISO', nargs='?', help='Windows.iso to rewrite')
	a.add_argument('-a', '--all', action='store_true', help='xml flags -mnwy')
	a.add_argument('-e', '--edition', metavar='ED', help='Core, CoreN, Professional... not -e: auto')
	a.add_argument('-k', '--key', help='auto-activate... not -k: limited features')
	a.add_argument('-l', '--lang', help='en-US, fr-FR... not -l: auto')
	a.add_argument('-m', '--microsoft', action='store_true', help='no Microsoft account')
	a.add_argument('-n', '--network', action='store_true', help='no network setup')
	a.add_argument('-p', '--pc', metavar='NAME', help='computer name... not -p: PC')
	a.add_argument('-q', '--quiet', action='store_true', help='no output')
	a.add_argument('-v', '--verbose', action='store_true', help='detail actions in bash syntax')
	a.add_argument('-y', '--yes', action='store_true', help='accept license')
	args = a.parse_args()
	flags = (('mnwy' if args.all else '') +
		''.join([x[0] for x in ('microsoft', 'network', 'quiet', 'verbose', 'yes') if getattr(args,x)]))
	status = aunt(args.ISO, flags, args.edition, args.key, args.lang, args.pc)
	if args.ISO or status or args.quiet:
		return status
	a.print_help()

if __name__ == '__main__':
	exit(main())