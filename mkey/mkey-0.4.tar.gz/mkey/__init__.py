import argparse, os.path, re, site, sys

__all__ = ('mkey',)

with open(site.getsitepackages()[1] + '\\mkey\\header.ahk') as f:
	_header = f.read()

_line = re.compile(r'(?:\[(.*)\]|(?:(.)(.)??([0-9]*) |([a-zA-Z0-9_. -]+): ?)(.*))$\n*', re.M).match
_site = re.compile(r'([a-z0-9.-]+\.[a-z]+(?:[/ ].*?)?)(?:: (.*))?').fullmatch

_mod = {'shift':'>+', 'ctrl':'>^', 'left':'~LButton & ', 'middle':'~MButton & ', 'right':'~RButton & '}
_key = {'shift':'RShift', 'ctrl':'RCtrl', 'left':'LButton', 'middle':'MButton', 'right':'RButton'}

def mkey(*files):
	status = 0
	for file in files or (None,):
		correct = True
		if file and not os.path.isfile(file):
			print(f'No file: ' + file, file=sys.stderr)
			status = max(status, 1)
			continue
		with open(file, encoding='utf-8') if file else sys.stdin as f:
			source = f.read()
		end = len(source)
		position = 0
		_if = False
		out = [_header]
		while position < end:
			match = _line(source, position)
			if not match:
				print(f'Error: ' + source[position:].split('\n', 1)[0], file=sys.stderr)
				correct = False
				status = 2
				break
			position = match.end()
			sec, key, sep, delay, exe, macro = match.groups('')
			if not exe and _if:
				out.append('#If')
				_if = False
			if sec:
				section = sec
				out.append('')
				continue
			if exe:
				out.append('#If ' + ' Or '.join(["WinActive('ahk_exe " + e +
					('' if '.' in e else '.exe') + "')" for e in exe.split()]))
				_if = True
			hotkey = _key[section] if exe else _mod[section] + key
			delay = '200' if delay=='0' else delay + '000' if delay else '0'
			if not sep:
				match = _site(macro)
				if match:
					url = match[1].split()
					fields = [repr(f[:-1] if f[-1]=='.' else f + '`n')
						for f in (match[2] or '').replace('>', '`t').split()]
					out.append(f'{hotkey}::' + (
						f'Login {repr(url[0])}, ' + ', '.join(fields) if fields else
						f'Sites {delay}, ' + ', '.join([repr(u) for u in url]) if len(url) > 1 else
						'Run ' + repr('http://' + url[0])))
					continue
				sep = ';'
			out.append(f'{hotkey}::' + ((
				'Send ' + repr(macro.replace(sep, '`n'))
				if delay == '0' else f'Command {delay}, ' +
				', '.join([repr(cmd) for cmd in macro.split(sep)]))
				if macro else 'Click 2'))
		if correct:
			with (open(os.path.splitext(file)[0] + '.ahk', 'w', encoding='utf-8-sig', newline='\n')
					if file else sys.stdout) as f:
				f.write('\n'.join(out))
	return status

def main():
	a = argparse.ArgumentParser(None, 'mkey [-h] [file] ...',
		'Mouse and Key 0.4', 'no file: stdin to stdout')
	a.add_argument('files', nargs='*', help='*.mkey (expand to *.ahk)')
	args = a.parse_args()
	files = args.files
	return a.print_help() if not files and sys.stdin.isatty() else mkey(*files)

if __name__ == '__main__':
	exit(main())