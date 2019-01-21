from typing import Callable
import fnmatch
from datetime import datetime
import shutil
import os
import collections

get_name=lambda some_path:os.path.splitext(os.path.basename(some_path))[0]

def get_parent_dir(some_path,depth=1):
	for i in range(depth):
		some_path=os.path.dirname(os.path.abspath(some_path))
	return some_path

def create_path(depth: int,*paths):
	path=os.path.join(*paths)
	os.makedirs(get_parent_dir(path,depth),exist_ok=True)
	return path

def get_existing_path(paths,silent=False):
	for p in paths:
		if os.path.exists(p): return p
	if not silent:
		raise NotImplementedError('Could not find any existing path.')

def clear_folder(folder,remove_subdirs=True):
	for the_file in os.listdir(folder):
		file_path=os.path.join(folder,the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif remove_subdirs and os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as e:
			print(e)

def get_full_paths_from(parent_dir: str):
	for file in os.listdir(parent_dir):
		yield os.path.join(parent_dir,file)

def get_splitted(path):
	folders=[]
	while 1:
		path,folder=os.path.split(path)
		
		if folder!="":
			folders.append(folder)
		else:
			if path!="":
				folders.append(path)
			break
	folders.reverse()
	return folders

class InfoDict(collections.OrderedDict):
	
	def get_dir_path(self,*paths):
		return os.path.join(*self.get_portions(),*paths)
	
	# def create_file_path(self,ext,dir_depth=1):
	# 	return create_info_path(self,ext=ext,*self.get_portions(),dir_depth=dir_depth)
	
	def get_portions(self):
		portions=list()
		for k,v in self.items():
			if v: portions.append(f"{k}={v}")
			else: portions.append(k)
		return portions
	
	def get_text(self,delim="_"):
		return delim.join(self.get_portions())
	
	def __str__(self):
		return self.get_text()

class Folder:
	
	def __init__(self,path,parent=None):
		if not os.path.exists(path):
			assert os.path.splitext(os.path.split(path)[-1])[-1]=='',f"Please, use folder path as input. Provided path is: \n{path}"
			os.makedirs(path)
		if not os.path.isdir(path):
			path=get_parent_dir(path,1)
		self.path=path
		self.parent: Folder=parent
		self.is_root=parent is None
		self.child_parts=list()
	
	def get_filepath(self,*name_portions,ext='',delim='_',include_depth=None,include_datetime=False,**name_kwargs):
		parts=list()
		if include_depth not in [0,None]:
			if type(include_depth) is Callable:
				parent_parts=include_depth(get_splitted(self.path))
			elif type(include_depth) is int:
				parent_parts=get_splitted(self.path)[-include_depth:]
			elif type(include_depth) in [tuple,list]:
				parent_parts=[get_splitted(self.path)[-x] for x in include_depth]
			else:
				raise NotImplementedError(f'include_depth={include_depth}')
			parts.extend(parent_parts)
		# if include_parents:
		# 	parent=self
		# 	root_parts=list()
		# 	while True:
		# 		print('parent',parent)
		# 		print(parent.child_parts)
		# 		if parent.child_parts:
		# 			root_parts.append(parent.child_parts)
		# 		if parent.is_root: break
		# 		parent=parent.parent
		# 	if root_parts: parts.extend([y for x in root_parts[::-1] for y in x])
		part_kwargs=InfoDict(name_kwargs).get_text(delim)
		if part_kwargs: parts.append(part_kwargs)
		part_portions=delim.join([str(x) for x in name_portions])
		if part_portions: parts.append(part_portions)
		if include_datetime: parts.append(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
		assert parts,'Nothing if provided to create filepath.'
		return os.path.join(self.path,delim.join(parts).replace(' ',delim)+ext)
	
	def create(self,*child_folders,**info_kwargs):
		parts=list()
		if child_folders: parts.extend(child_folders)
		if info_kwargs: parts.extend(InfoDict(info_kwargs).get_portions())
		assert parts,'Nothing is provided to create directory'
		self.child_parts=parts
		return Folder(create_path(0,self.path,os.path.join(*self.child_parts)),self)
	
	def delete(self):
		shutil.rmtree(self.path)
	
	def __getitem__(self,item):
		return self.create(item)
	
	def __repr__(self):
		return f"Folder({self.path})"

get_neighbor_path=lambda curr_path,filename:os.path.join(get_parent_dir(curr_path),filename)

def get_paths_matching(target_dir,match: str):
	items=os.listdir(target_dir)
	outs=list()
	for item in items:
		if match in item: outs.append(os.path.join(target_dir,item))
	return outs

def replace_ext(fpath,out_extension):
	base_path,ext=os.path.splitext(fpath)
	return base_path+out_extension

def find_file(directory,pattern):
	for root,dirs,files in os.walk(directory):
		for basename in files:
			if fnmatch.fnmatch(basename,pattern):
				filename=os.path.join(root,basename)
				return filename

def main():
	project_folder=Folder(__file__)
	logs_folder=project_folder.create('log_files')
	results_folder=project_folder.create('Results')
	qwe=InfoDict(name='didi',day='today',trial=1)
	# qwe=logs_folder.get_filepath(name='didi',day='today',trial=1,include_depth=2)
	print(qwe.get_dir_path())
	print(qwe)
	pass

if __name__=='__main__':
	main()
