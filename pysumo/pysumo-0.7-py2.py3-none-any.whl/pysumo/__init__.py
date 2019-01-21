import socketio
import time
import subprocess
import atexit
import sys

name = "pysumo"

TIMEOUT = 10
TIMESTEP = 0.1

def on_exit():
	sp.kill()

atexit.register(on_exit)

DETACHED_PROCESS = 0x00000008
sp_path = next(p for p in sys.path if 'site-packages' in p)
sp_path += "\\pysumo\\pysumo.exe"
sp = subprocess.Popen(sp_path, creationflags=DETACHED_PROCESS)

class Drone:
	def __init__(self):
		self.isConnected = False
		self.isPostureKicker = False
		self.isPostureJumper = False
		self.isPostureStanding = False
		self.battery = -1
	# Private utils
	def checkConnection(self):
		if(not self.isConnected):
			print("pySumo> Error: use connect() first")
			return None
	def checkSpeed(self, speed):
		if speed < 0 or speed > 127:
			print("pySumo> Error: speed must be between 0 and 127")
	# Public
	def connect(self):
		self.sio = socketio.Client()
		@self.sio.on("connect")
		def on_connect():
			print("pySumo> connected")
			self.sio.emit("pythonConnected")
		@self.sio.on("disconnect")
		def on_disconnect():
			print("pySumo> disconnected from server")
		@self.sio.on("droneConnected")
		def on_droneConnected():
			self.isConnected = True
			self.postureJumper()
		@self.sio.on("postureJumper")
		def on_postureJumper():
			self.isPostureJumper = True
			self.isPostureKicker = False
			self.isPostureStanding = False
		@self.sio.on("postureKicker")
		def on_postureJumper():
			self.isPostureKicker = True
			self.isPostureJumper = False
			self.isPostureStanding = False
		@self.sio.on("postureStanding")
		def on_postureStanding():
			self.isPostureKicker = False
			self.isPostureJumper = False
			self.isPostureStanding = True
		@self.sio.on("postureStuck")
		def on_postureStuck():
			self.isPostureKicker = False
			self.isPostureJumper = False
			self.isPostureStanding = False
			print("pySumo> drone stuck")
		@self.sio.on("battery")
		def on_battery(data):
			print(data)
			self.battery = data
		self.sio.connect("http://localhost:4532")
		i = 0
		while not(self.isConnected):
			if i > TIMEOUT:
				print("pySumo> Error: Cannot connect")
				break
			time.sleep(TIMESTEP)
			i += TIMESTEP
	def isReady(self):
		return (self.isPostureJumper or self.isPostureKicker or self.isPostureStanding)
	def postureJumper(self, sec=None):
		self.checkConnection();
		self.sio.emit("postureJumper")
		if sec:
			time.sleep(sec)
	def postureKicker(self, sec=None):
		self.checkConnection();
		self.sio.emit("postureKicker")
		if sec:
			time.sleep(sec)
	def postureStanding(self, sec=None):
		self.checkConnection();
		self.sio.emit("postureStanding")
		if sec:
			time.sleep(sec)
	def highJump(self, sec=None):
		self.checkConnection();
		self.sio.emit("animationsHighJump")
		self.postureKicker = False
		self.postureJumper = False
		self.postureStanding = False
		i = 0
		while not(self.isReady()) and i<TIMEOUT:
			time.sleep(TIMESTEP)
			i += TIMESTEP
		if sec:
			time.sleep(sec)
	def longJump(self, sec=None):
		self.checkConnection();
		self.sio.emit("animationsLongJump")
		self.postureKicker = False
		self.postureJumper = False
		self.postureStanding = False
		i = 0
		while not(self.isReady()) and i<TIMEOUT:
			time.sleep(TIMESTEP)
			i += TIMESTEP
		if sec:
			time.sleep(sec)
	def animationsStop(self, sec=None):
		self.checkConnection();
		self.sio.emit("animationsStop")
		i = 0
		while not(self.isReady()) and i<TIMEOUT:
			time.sleep(TIMESTEP)
			i += TIMESTEP
		if sec:
			time.sleep(sec)
	def forward(self, speed, sec=None):
		self.checkSpeed(speed)
		self.checkConnection();
		self.sio.emit("forward", {"speed": speed})
		if sec:
			time.sleep(sec)
	def backward(self, speed, sec=None):
		self.checkSpeed(speed)
		self.checkConnection();
		self.sio.emit("backward", {"speed": speed})
		if sec:
			time.sleep(sec)
	def right(self, speed, sec=None):
		self.checkSpeed(speed)
		self.checkConnection();
		self.sio.emit("right", {"speed": speed})
		if sec:
			time.sleep(sec)
	def left(self, speed, sec=None):
		self.checkSpeed(speed)
		self.checkConnection();
		self.sio.emit("left", {"speed": speed})
		if sec:
			time.sleep(sec)
	def stop(self, sec=None):
		self.checkConnection();
		self.sio.emit("droneStop")
		if sec:
			time.sleep(sec)


