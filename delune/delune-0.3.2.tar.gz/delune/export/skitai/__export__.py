# 2017. 3. 13 by Hans Roh (hansroh@gmail.com)

from skitai.saddle import Saddle
import delune
from rs4 import pathtool
import os
import json
import codecs
import time
import shutil
import time

from decorative.admin import ui
from decorative.v1 import ops, pub

app = Saddle (__name__)
app.config.numthreads = 1
app.last_maintern = time.time ()

app.decorate_with (pub, mount = "/v1")
app.decorate_with (ops, mount = "/v1/ops", ns = "ops")
app.decorate_with (ui, mount = "/admin")

@app.route ("/status")
@app.permission_required (["index", "replica"])
def status (was):
	return was.status ()

@app.before_mount
def before_mount (wasc):
	app.config.numthreads = len (wasc.threads)
	permission_check_handler = wasc.app.config.get ("permission_check_handler")
	if permission_check_handler:
		app.permission_check_handler (permission_check_handler)
		
	delune.configure (app.config.numthreads, wasc.logger.get ("app"), 16384, 128)
	pathtool.mkdir (ops.getdir ("config"))
	for alias in os.listdir (ops.getdir ("config")):
		if alias.startswith ("-"):
			with codecs.open (ops.getdir ("config", alias), "r", "utf8") as f:
				colopt = json.loads (f.read ())
			for d in [ops.getdir ("collections", ops.normpath(d)) for d in colopt ['data_dir']]:
				if os.path.isdir (d):
					shutil.rmtree (d)
			os.remove (ops.getdir ("config", alias))
		elif alias.startswith ("#"):
			continue
		else:
			ops.load_data (alias, app.config.numthreads, wasc.plock)
	  
@app.umounted
def umounted (wasc):
	delune.shutdown ()

@app.before_request
def before_request (was):	
	with app.lock:
		last_maintern = was.getlu ("delune:collection") > app.last_maintern and app.last_maintern or 0
		if last_maintern:
			app.last_maintern = time.time ()
	
	if last_maintern:
		was.log ('collection changed, maintern...')
		for alias in os.listdir (ops.getdir ("config")):			
			if alias [0] in "#-":
				if delune.get (alias [1:]):
					delune.close (alias [1:])
			elif not delune.get (alias):
				ops.load_data (alias, app.config.numthreads, was.plock)			
			elif os.path.getmtime (ops.getdir ("config", alias)) > last_maintern:
				delune.close (alias)
				ops.load_data (alias, app.config.numthreads, was.plock)
	
	if was.request.args.get ('alias') and was.request.routed.__name__ != "collection":
		alias = was.request.args.get ('alias')
		if not delune.get (alias):
			return was.response.Fault ("404 Not Found", 40401, "resource %s not exist" % alias)
