import argparse, os.path, re, site, subprocess, sys, threading

__all__ = ('innoreg',)

_site = site.getsitepackages()[1] + '\\innoreg\\'
_errors = ('', 'No file: ', 'Error: ')

for _version in 6, 5, 0:
	_compiler = f'C:\\Program Files (x86)\\Inno Setup {_version}\\ISCC.exe'
	if os.path.exists(_compiler):
		break

_header = re.compile(r'\n*(.+)\n{2,}').match
_parse = re.compile(
	r'(\t*)(([+-])? *((?:(.+?)\\)*)(?:(.*?) +(?:-?|([.\'"]?)(.*?)\7)(?: +(?:-?|([.\'"]?)(.*?)\9))?)? *(!)?) *$'
	r'((?:\n\1[^\t\n]+)*)\n*', re.M).match
_split = re.compile(r'[^\t\n]+').findall
_expand = re.compile(r'%[A-Za-z]').search

def innoreg(files=(), flags=''):
	flags = set(flags)
	if flags & {'d', 'u'}: flags.add('a')
	status = 0
	inno = []

	def log(message, error=0):
		nonlocal correct, status, flags
		if 'q' not in flags and ('v' in flags or error):
			print(f'{_errors[error]}{message}', file=sys.stderr)
		correct &= error == 0
		status = max(status, error)

	for file in files or (None,):
		correct = True
		if file:
			ext = os.path.splitext(file)[1]
			if ext in ('.iss', '.exe'):
				inno.append((file, False)) if ext == '.iss' else log(file, 2)
				continue
		if file and not os.path.isfile(file):
			log(file, 1)
			continue
		bits = ('32',) if 'x' in flags else ('32', '64')
		with open(file, encoding='utf-8') if file else sys.stdin as f:
			source = f.read().replace('{', '{{')
		end = len(source)
		indent = []

		log(f"Convert '{file}'" if file else 'stdin to stdout')
		match = _header(source)
		if not match:
			log('bad header', 2)
			continue
		position = match.end()
		languages = match[1].split()
		custom_messages, components, registry = [], [], []
		sections = {
			'Setup':['AppName=innoreg', 'AppVersion=0.4'] + ([] if 'l' in flags else ['ShowLanguageDialog=auto']) +
				['OutputBaseFilename=' + (os.path.basename(os.path.splitext(file)[0]) if file else 'setup'), 'OutputDir=.',
				'CreateAppDir=no', 'DisableReadyPage=yes', 'DisableFinishedPage=yes', 'Uninstallable=no',
					f'WizardSmallImageFile={_site}logo.bmp'] + (['AlwaysRestart=yes'] if 'r' in flags else []),
			'Languages':[f'Name:"{lang}"; MessagesFile:"{_site}{lang}.islu"' for lang in languages],
			'CustomMessages':custom_messages, 'Components':components, 'Registry':registry,
			'Code':['procedure CurPageChanged(CurPageID: Integer);', 'begin',
				'if CurPageID = wpSelectComponents then WizardForm.NextButton.Caption := SetupMessage(msgButtonInstall);',
				'end;', 'procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);',
				'begin', 'Confirm := false;', 'end;']}
		if 'd' in flags or 'u' in flags:
			args = ", '', SW_HIDE, ewWaitUntilTerminated, ResultCode);"
			sections['Code'] += ['procedure CurStepChanged(CurStep: TSetupStep);', 'var', 'ResultCode: Integer;', 'begin',
			"if CurStep = ssInstall then Exec('reg.exe', 'load HKU\\Default C:\\Users\\Default\\NTUSER.DAT'" + args,
			"if CurStep = ssPostInstall then Exec('reg.exe', 'unload HKU\\Default'" + args, 'end;']

		while position < end:
			match = _parse(source, position)
			position = match.end()
			tabs, line, delete, keys, key, value, quote1, data1, quote0, data0, exclusive, messages = match.groups()
			if not (key or value):
				log(line, 2)
				continue
			keys = keys[:-1]
			r = len(components)
			r = 'r' + chr(97 + r//26) + chr(97 + r%26)
			messages = _split(messages) or [value or key]
			if len(messages) > 1:
				custom_messages += [f'{languages[i]}.{r}={messages[i]}' for i in range(len(messages))]
				messages = ['{cm:' + r + '}']
			t = len(tabs)
			if t:
				r, keys = f'{indent[t-1][0]}\\{r}', indent[t-1][1] + (f'\\{keys}' if keys else '')
			else:
				root = keys.split('\\', 1)[0] 
				if root not in ('HKCR', 'HKCU', 'HKLM', 'HKU', 'HKCC'):
					log('root key must be HKCR, HKCU, HKLM, HKU, HKCC', 2)
					continue
				if root!='HKCU': flags.add('a')
			indent[t:] = [(r, keys)]
			components.append(f'Name:"{r}"; Description:"{messages[0]}"; Types:full')
			root, keys = (keys.split('\\', 1) + [''])[:2]
			if exclusive and root not in ('HKCU', 'HKLM'):
				log('only HKCU, HKLM can be exclusive', 2)
				continue
			for root, keys in (
				(('HKU', 'Default\\' + keys),) if root=='HKCU' and flags & {'d', 'u'} else ()) + (
				() if root=='HKCU' and 'd' in flags else ((root, keys),)):
				for b in bits:
					subkey = f'Root:{root}{b}; Subkey:"{keys}"; '
					if exclusive:
						registry.append(
							f'Root:{"HKCU" if root=="HKLM" else "HKLM"}{b}; Subkey:"{keys}"; ' +
								(f'ValueName:"{value}"; ' if value else '') +
								f'Flags:delete' + ('key' if value is None else 'value'))
					if value is not None:
						for quote, data, no in (quote1, data1, ''), (quote0, data0, 'not '):
							registry.append(subkey + (f'ValueName:{value}; ' if value else '') +
								('Flags:deletevalue' if data is None else 'ValueType:' +
								('dword' if quote=='' else 'binary' if quote=='.' else
									'multisz' if quote=='"' else 'expandsz' if _expand(data) else 'string') +
								f'; ValueData:"{data if quote else int(data, 16)}"') + f'; Components:{no}{r}')
					if delete:
						registry.append(f"{subkey}Flags:deletekey; Components:{'not ' if delete=='+' else ''}{r}")
		if correct:
			if registry:
				if 'a' not in flags:
					sections['Setup'].append('PrivilegesRequired=lowest')
				if _version == 6:
					sections['Setup'] += ['WizardStyle=modern', 'WizardResizable=no',
						f'WizardSizePercent=100,{max(100, min(150, 4*len(components) + 76))}']
				out = []
				for sec, lines in sections.items():
					if lines:
						log(f'{len(lines):4}  {sec}')
						out.append('\n'.join([f'[{sec}]'] + lines))
				out = '\n\n'.join(out)
				if file:
					file = os.path.splitext(file)[0] + '.iss'
					with open(file, 'w', encoding='utf-8-sig', newline='\n') as f:
						f.write(out)
					inno.append((file, True))
				else:
					sys.stdout.write(out)
			else:
				log('no registry modification', 2)

	def exe(file, delete):
		nonlocal log, flags
		log(f"Compile '{file}'")
		if not subprocess.run((_compiler, '-q', file)).returncode:
			if delete:
				log(f"Delete '{file}'")
				os.remove(file)
			if 's' in flags:
				file = os.path.splitext(file)[0] + '.exe'
				log(f"Start '{file}'")
				os.startfile(file)

	if inno and 'e' not in flags:
		if _version:
			threads = []
			for i in inno:
				t = threading.Thread(target=exe, args=i)
				t.start()
				threads.append(t)
			for t in threads:
				t.join()
		else:
			log('ISCC.exe', 1)

	return status

def main():
	a = argparse.ArgumentParser(None, 'innoreg [-h] [-adelqrsuvx] [file] ...',
		'Inno Setup Registry 0.4', 'no file: -e stdin to stdout')
	a.add_argument('files', nargs='*', help='*.ireg (expand and compile) or *.iss (compile)')
	a.add_argument('-a', '--admin', action='store_true', help='auto-selected if key other than HKCU')
	a.add_argument('-d', '--default', action='store_true', help='HKCU is C:\\Users\\Default')
	a.add_argument('-e', '--expand', action='store_true', help='expand only, do not compile to *.exe')
	a.add_argument('-l', '--lang', action='store_true', help='always shop language dialog')
	a.add_argument('-q', '--quiet', action='store_true', help='hide errors')
	a.add_argument('-r', '--reboot', action='store_true', help='prompt the user to restart the system')
	a.add_argument('-s', '--start', action='store_true', help='start the new *.exe')
	a.add_argument('-u', '--users', action='store_true', help='HKCU is C:\\Users\\Default + current user')
	a.add_argument('-v', '--verbose', action='store_true', help='detail all actions and sections')
	a.add_argument('-x', '--x86', action='store_true', help='32 bit registry only')
	args = vars(a.parse_args())
	files = args.pop('files')
	flags = {opt[0] for opt in args if args[opt]}
	return a.print_help() if not files and sys.stdin.isatty() else innoreg(files, flags)

if __name__ == '__main__':
	exit(main())