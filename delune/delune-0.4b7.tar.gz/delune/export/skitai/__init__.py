import skitai
import delune
import sys, os

def bootstrap (pref):	
	skitai.deflu (delune.SIG_UPD)
	
	assert pref.config.resource_dir	
	pref.config.resource_dir = os.path.abspath (pref.config.resource_dir)
	