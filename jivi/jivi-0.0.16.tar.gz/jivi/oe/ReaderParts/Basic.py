class Reader:
	@property
	def txt(self):
		return self._txt
	
	@txt.setter
	def txt(self,ptxt):
		self._txt = ptxt
		self.txt_no_lines = self._txt.replace("\n"," ").lower()
		self._currentindex = 0
		self.start_index = 0
		self.len = len(self._txt)
		self.lenmo = self.len - 1
		self.index = 0

	@property
	def part(self):
		return self._txt[self.start_index:self.index]
	
	@property
	def current_line(self):
		index_start = self._txt.rfind("\n",0,self.index)
		index_stop = self._txt.find("\n",self.index)
		if index_start == -1: index_start = 0
		if index_stop == -1: index_stop = self.len
		return self._txt[index_start:index_stop]

	@property
	def current_line_index(self):
		return self._txt.count("\n",0,self.index)

	@property
	def index(self):
		return self._currentindex
	
	@index.setter
	def index(self,i):
		self._currentindex = i
		self.stopped = self._currentindex >= self.len
		if self.stopped:
			self.char = None
			return
		self.char = self._txt[i]
		
	def find(self,needle,index=None,alt=None):
		if index == None: index = self._currentindex
		i = self._txt.find(needle,index)
		return i if i != -1 else alt
		
	def char_before(self,index=None,alt=""):
		if index == None: index = self._currentindex
		return self._txt[index-1] if index > 0 else alt

	def char_after(self,index=None,alt=""):
		if index == None: index = self._currentindex
		return self._txt[index+1] if self.lenmo >= (index + 1) else alt
		
	