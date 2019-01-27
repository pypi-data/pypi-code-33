from jivi.pr.Object import Object

from .TableAndField import Table,Field

class Session(Object):
	attr = []
	attr.append(dict(
		n='ppc',
		r=1,
		a='pixels-per-column'
		))
	attr.append(dict(n='ppr',r=1,a='pixels-per-row'))
	attr.append(dict(n='td',r=1,a='temp-directory',d=r'C:\temp'))
	
	def __init__(self,env,tabs):

		Object.__init__(self,env=env,tab={a['ck'] : a['cv'] for a in tabs['session']})
		
		self.tables = {}
		self.indexes = {}
		file_by_recid = {}
		self.font_lenght = {}
		
		self.ppr = int(self.ppr)
		self.ppc = int(self.ppc)
		
		#fi cc cl pl
		for a in tabs['font']:
			fi = a['fi']
			cc = a['cc']
			
			pl = a['pl']
			if not fi in self.font_lenght:
				self.font_lenght[fi] = {}
			self.font_lenght[fi][cc] = [pl, self.ptc(pl)]



		def check_tab(tab,required):
			tab = {k.lower().strip() : v for k,v in t.items()}
			for a in required:
				if not a in tab: return 0
			return tab
		for t in tabs['file']:
			tab = check_tab(t,['rrecid'])
			if not tab: continue
			table = Table(env=self.env,tab=tab)
			self.tables[table.name] = table
			file_by_recid[tab['rrecid']] = table
		for t in tabs['field']:
			tab = check_tab(t,['rrecid','_file-recid'])
			field = Field(env=self.env,tab=tab,table=file_by_recid[tab['_file-recid']])
				
				
				
	def ptc(self,x,dontconv=0):
		try:
			f = float(x)
		except:
			return None
		if dontconv: return f
		return f / self.ppc
			
	def htp(self,x,dontconv=0):
		try:
			f = float(x)
		except:
			return None
		if dontconv: return f
		return self.ppr * f
		
	def wtp(self,x,dontconv=0):
		try:
			f = float(x)
		except:
			return None
		if dontconv: return f
		return self.ppc * f

	def ctp(self,x,dontconv=0):
		try:
			f = float(x)
		except:
			return None
		if dontconv: return f
		return self.ppc * ( f - 1)

	def rtp(self,x,dontconv=0):
		try:
			f = float(x)
		except:
			return None
		if dontconv: return f
		return self.ppr * ( f - 1)