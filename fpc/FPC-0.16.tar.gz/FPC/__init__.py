import datetime,builtins,platform,time,math,os,urllib
from urllib import request
IS_WIN=False if platform.system().find('Linux')>-1 else True
NOW=math.floor(datetime.datetime.now().timestamp())
def is_numeric(x):
	try:
		float(x)
		return True
	except:
		return False
def now():return math.floor(datetime.datetime.now().timestamp())
def print(*a,func=None,time='%m/%d %H:%M:%S',pretty=False,**s):
	a=list(a)
	if func:
		for i,x in enumerate(a):
			a[i]=func(x)
	if time:
		a.insert(0,datetime.datetime.now().strftime(time)+' :')
	if pretty:
		import pprint
		for x in a:
			pprint.pprint(x)
	else:
		builtins.print(*a,**s)
def notice(x,c='email'):request.urlopen(r'http://call.ff2.pw/?%s=%s&passwd=frank'%(c,urllib.parse.quote_plus(x)))
def rand_sleep(i=0.4,a=0.8):import random;time.sleep(random.randint(i*1000,a*1000)/1000);
def rand(i=9,a=None):import random;return random.randint(int(i),int(a)) if a else random.randint(0,int(i-1));
def md5(x):import hashlib;hl = hashlib.md5();hl.update(x.encode('utf-8') if isinstance(x,str) else x);return hl.hexdigest();
def bin2hex(x):import binascii;return binascii.hexlify(x.encode('utf-8') if isinstance(x,str) else x);
def base64_encode(x):import base64;return base64.b64encode(x)
def base64_decode(x):import base64;return base64.b64decode(x)
def log(*x,path=None):
	if path is None:
		path='/tmp/frank.log' if os.path.exists('/tmp') else './FPC.log'
	with open(path,'a',encoding='utf-8') as f:
		print(*x,file=f)
class mysql(object):
	def __init__(self, key=127,**args):
		import pymysql
		self.pymysql=pymysql
		_CONNECT_CONFIG={127:{'host':'127.0.0.1','user':'root','password':'123456','db':'localhost','charset':'utf8','cursorclass':pymysql.cursors.DictCursor}}
		connect_config = _CONNECT_CONFIG[key]
		for x in args:
			connect_config[x]=args[x]
		self.conn = pymysql.connect(**connect_config)
	def __call__(self,table):
		self.table=table
	def _split_dict(self,dicts):
		key=value=''
		for x in dicts:
			key+=r'`%s`,'%x
			if dicts[x] is None:value+='null,'
			else:value+=r'%s,'%(dicts[x]) if is_numeric(dicts[x]) else r'"%s",'%(self.pymysql.escape_string(dicts[x]))
		return key[:-1],value[:-1]
	def execute(self,strs):
		strs=strs.strip()
		is_query = True if strs[:4].lower() in ['sele','show'] else False
		with self.conn.cursor() as cur:
			data=cur.execute(strs)
			data=cur.fetchall() if is_query else cur.lastrowid
		is_query or self.conn.commit()
		return data
	def add(self,table,dicts=None):
		if isinstance(table,dict):
			dicts=table
			table=self.table
		key,value=self._split_dict(dicts)
		return self.execute(r''' insert `%s`(%s) values(%s) '''%(table,key,value))
class redis(object):
	server=False
	def __init__(self,host='127.0.0.1',db=0,port=6379,ssh_host=None,ssh_username='root',ssh_password=None):
		import redis
		if ssh_host:
			import sshtunnel
			sshtunnel.DAEMON=True
			sshtunnel.SSHTunnelForwarder.daemon_forward_servers=True
			sshtunnel.SSHTunnelForwarder.daemon_transport=True
			self.server = sshtunnel.SSHTunnelForwarder(ssh_address_or_host=ssh_host,ssh_username=ssh_username,ssh_password=ssh_password,remote_bind_address=(host,6379))
			self.server.start()
			port=self.server.local_bind_port
		self.redis=redis.StrictRedis(host=host, port=port, db=db,decode_responses=True)
	def __getattr__(self,attr):
		return getattr(self.redis,attr)
def process(target,is_thread=True,join=False,num=None,sleep=None,**args):
	pros=[]
	if 'args' in args:
		if isinstance(args['args'],list):
			args_list=args['args']
			if num is None:num=len(args_list)
		else:args_list=[args['args']]*num
	if num is None:num=1
	if is_thread:
		import threading
		for x in range(num):
			if 'args' in args:
				args['args']=args_list[x] if isinstance(args_list[x],(tuple,list)) else [args_list[x]]
			pros.append(threading.Thread(target=target,**args))
			pros[-1].start()
			if sleep:time.sleep(sleep)
	else:
		from multiprocessing import Process
		for x in range(num):
			if 'args' in args:
				args['args']=args_list[x] if isinstance(args_list[x],(tuple,list)) else [args_list[x]]
			pros.append(Process(target=target,**args))
			pros[-1].start()
			if sleep:time.sleep(sleep)
	if join:
		for x in range(num):
			pros[x].join()
