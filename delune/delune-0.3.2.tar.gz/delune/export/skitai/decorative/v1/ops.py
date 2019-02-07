import delune
import os
import json
from rs4 import pathtool
import json
import codecs
import time
import shutil
from rs4 import pathtool

RESOURCE_DIR = None

def getdir (*d):
	global RESOURCE_DIR
	return os.path.join (RESOURCE_DIR, "delune", *d)
	
def load_data (alias, numthreads, plock):
	def normpath (path):
		if os.name == "nt":
			return path.replace ("/", "\\")
		return path.replace ("\\", "/")

	with codecs.open (getdir ("config", alias), "r", "utf8") as f:
		colopt = json.loads (f.read ())			
		colopt ['data_dir'] = [getdir ("collections", normpath(d)) for d in colopt ['data_dir']]
	
	name = "standard"
	if "name" in colopt ["analyzer"]:
		name = colopt ["analyzer"].get ("name")			
		del colopt ["analyzer"]["name"]
	analyzer_class = delune.get_analyzer (name)
	
	if 'classifier' in colopt:		
		analyzer = analyzer_class (10000, numthreads, **colopt ["analyzer"])
		col = delune.model (colopt ["data_dir"], delune.READ, analyzer, plock = plock, version = colopt.get ("version", 1))
		actor = col.get_classifier (**colopt.get ('classifier', {}))
	else:
		analyzer = analyzer_class (8, numthreads, **colopt ["analyzer"])
		col = delune.collection	(colopt ["data_dir"], delune.READ, analyzer, plock = plock, version = colopt.get ("version", 1))	
		actor = col.get_searcher (**colopt.get ('searcher', {}))
		actor.create_queue ()
	delune.assign (alias, actor)

#------------------------------------------------------------------

def decorate (app):
	global RESOURCE_DIR
	RESOURCE_DIR = app.config.resource_dir
	
	@app.route ("/<alias>/config", methods = ["GET"])
	@app.permission_required (["index", "replica"])
	def config (was, alias):
		fn = getdir ("config", alias)
		return was.response.file (fn, "application/json")
	
	@app.route ("/list", methods = ["GET"])
	@app.permission_required (["replica", "index"])
	def collections (was):
		return was.response.API ({'collections': list (delune.status ().keys ())})	
	
	@app.route ("/<alias>", methods = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"])
	@app.permission_required (["replica", "index"])
	def collection (was, alias, side_effect = ""):
		fn = getdir ("config", alias)
		if was.request.command == "get":
			if side_effect == "undo":
				for mark in "#-":
					if os.path.isfile (getdir ("config", mark + alias)):
						os.rename (
							getdir ("config", mark + alias),
							getdir ("config", alias)
						)
						was.setlu ("delune:collection")					
						return was.response ("201 Accept", was.response.API ())
				return was.response.Fault ("404 Not Found", 20100, "resource already commited")
			
			if not delune.get (alias):
				return was.response.Fault ("404 Not Found", 40401, "resource %s not exist" % alias)
				
			status = delune.status (alias)
			conf = getdir ("config", alias)
			with codecs.open (conf, "r", "utf8") as f:
				colopt = json.loads (f.read ())		
				status ['colopt'] = {
					'data': colopt,
					'mtime': 	os.path.getmtime (conf),
					'size': 	os.path.getsize (conf),
					'path': conf
				}
			return was.response.API (status)
				
		if was.request.command == "delete":
			if not os.path.isfile (fn):
				return was.response.Fault ("404 Not Found", 40401, "resource not exist")
			
			a, b = os.path.split (fn)
			if side_effect == "data":
				newfn = os.path.join (a, "-" + b)
			else:
				newfn = os.path.join (a, "#" + b)		
			os.rename (fn, newfn)
			was.setlu ("delune:collection")
			return was.response.API ()
		
		for mark in "#-":
			if os.path.isfile (getdir ("config", mark + alias)):			
				return was.response.Fault ("406 Conflict", 40601, "removed resource is already exists, use UNDO")
				
		if was.request.command == "post" and delune.get (alias):
			return was.response.Fault ("406 Conflict", 40601, "resource already exists")		
		elif was.request.command == "patch" and not delune.get (alias):
			return was.response.Fault ("404 Not Found", 40401, "resource not exist")
				
		with codecs.open (fn, "w", "utf8") as f:
			f.write (was.request.body.decode ("utf8"))
		
		was.setlu ("delune:collection")		
		return was.response.API ()

	# replica -------------------------------------------------------
			
	@app.route ("/<alias>/locks", methods = ["GET"])
	@app.permission_required ("replica")
	def locks (was, alias):	
		return was.response.API ({"locks": delune.get (alias).si.lock.locks ()})

	@app.route ("/<alias>/locks/<name>", methods = ["POST", "DELETE", "OPTIONS"])
	@app.permission_required ("replica")
	def handle_lock (was, alias, name):	
		if was.request.command == "post":
			delune.get (alias).si.lock.lock (name)		
			return was.response.API ()
		delune.get (alias).si.lock.unlock (name)
		return was.response.API ()
	
	@app.route ("/<alias>/groups/<group>/<fn>", methods = ["GET"])
	@app.permission_required ("replica")
	def getfile (was, alias, group, fn):
		s = delune.status (alias)
		if group == "primary":
			path = os.path.join (s ["indexdirs"][0], fn)
		else:
			path = os.path.join (s ["indexdirs"][0], group, fn)
		return was.response.file (path)

	@app.route ("/<alias>/groups/<group>/segments/<fn>", methods = ["GET"])
	@app.permission_required ("replica")
	def getsegfile (was, alias, group, fn):
		s = delune.status (alias)
		seg = fn.split (".") [0]
		if group == "primary":
			if seg not in s ["segmentsizes"]:
				return was.response.Fault ("404 Not Found", 40401, "resource not exist")
			path = os.path.join (s ["segmentsizes"][seg][0], fn)	
		else:
			path = os.path.join (s ["indexdirs"][0], group, fn)
		return was.response.file (path)
	
	# index ------------------------------------------------------------

	@app.route ("/<alias>/commit", methods = ["GET"])
	@app.permission_required ("index")
	def commit (was, alias):
		delune.get (alias).queue.commit ()
		return was.response.API ()

	@app.route ("/<alias>/rollback", methods = ["GET"])
	@app.permission_required ("index")
	def rollback (was, alias):
		delune.get (alias).queue.rollback ()
		return was.response.API ()
	
	@app.route ("/<alias>/documents", methods = ["POST", "DELETE", "OPTIONS"])
	@app.permission_required ("index")
	def documents (was, alias, truncate_confirm = "", q = None, lang = "en", analyze = 1):
		if was.request.command == "delete":
			if q:
				delune.get (alias).queue (1, json.dumps ({"query": {'qs': q, 'lang': lang, 'analyze': analyze}}))
				return was.response.API ()
			elif truncate_confirm != alias:
				return was.response.Fault ("400 Bad Request", 40003, 'parameter truncate_confirm=(alias name) required')			
			delune.get (alias).queue.truncate ()
			return was.response.API ()
	
		delune.get (alias).queue (0, was.request.body)
		return was.response.API ()
	
	@app.route ("/<alias>/documents/<_id>", methods = ["GET", "DELETE", "PUT", "PATCH", "OPTIONS"])
	@app.permission_required ("index")
	def document (was, alias, _id, nthdoc = 0):
		if was.request.command == "get":		
			return was.response.API (delune.query (alias, "_id:" + _id, nthdoc = nthdoc))
		
		delune.get (alias).queue (1, json.dumps ({"query": {'qs': "_id:" + _id}}))
		if was.request.command in ("patch", "put"):
			delune.get (alias).queue (0, was.request.body)
		return was.response.API ()

