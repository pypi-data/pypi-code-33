import onepanel.git_hooks.pre_commit_content


def read_self():
	file_path = __file__
	if file_path.endswith('.pyc'):
		file_path = file_path.replace('pyc','py')
	with open(file_path,'r') as f:
		return f.read()


if __name__ == '__main__':
	onepanel.git_hooks.pre_commit_content.check_for_large_files()
