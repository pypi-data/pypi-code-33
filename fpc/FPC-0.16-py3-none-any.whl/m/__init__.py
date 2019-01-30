import datetime,builtins,platform,time
from urllib import request
IS_WIN=False if platform.system().find('Linux')>-1 else True
NOW=datetime.datetime.now().timestamp()
def print(*arg,**args):builtins.print(datetime.datetime.now().strftime('%m/%d %H:%M:%S'),':',*arg,**args)
def notice(data):request.urlopen(r'http://call.ff2.pw/?wc=%s&passwd=frank'%(urllib.parse.quote_plus(data)))
def rand(min=0.4,max=0.8):import random;time.sleep(random.randint(min*1000,max*1000)/1000);
def md5(x):import hashlib;hl = hashlib.md5();hl.update(x.encode('utf-8') if isinstance(x,str) else x);return hl.hexdigest();
class mysql(object):
	def __init__(self, key=127,**args):
		import pymysql
		_CONNECT_CONFIG={127:{'host':'127.0.0.1','user':'root','password':'123456','db':'localhost','charset':'utf8','cursorclass':pymysql.cursors.DictCursor}}
		connect_config = _CONNECT_CONFIG[key]
		for x in args:
			connect_config[x]=args[x]
		self.connection = pymysql.connect(**connect_config)
	def execute(self,strs):
		is_query = True if strs[:4].lower() in ['sele','show'] else False
		with self.connection.cursor() as cur:
			data=cur.execute(strs)
			if is_query : data=cur.fetchall()
		is_query or self.connection.commit()
		return data
class redis(object):
	def __init__(self,host='127.0.0.1',db=0,port=6379):
		import redis
		self.redis=redis.StrictRedis(host=host, port=port, db=db,decode_responses=True)
	def __getattr__(self,attr):
		return getattr(self.redis,attr)
