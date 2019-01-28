from time import sleep
import pyautogui
import threading
import os
import logging
import traceback


class autogui():
	'''auto gui everything!'''

	def __init__(self):
		self.getter = None # get the ctrl+c content
		pyautogui.PAUSE = 0.5
		pyautogui.FAILSAFE = False


	def auto_login(self, url, username, passwd, pause=False):
		'''login in template decerator'''
		def wrapper(func):
			os.system('nohup google-chrome 2>&1 &') # 不占终端运行
			sleep(3)
			pyautogui.hotkey('ctrlleft', 'shiftleft', 'n')
			sleep(3)
			pyautogui.hotkey('altleft', 'tab')  # 关闭第一个正常窗口，否则窗口切换会混乱！
			sleep(3)
			pyautogui.hotkey('altleft', 'f4')
			sleep(3)
			# pyautogui.hotkey('ctrlleft', 'winleft', 'up')
			# pyautogui.hotkey('ctrlleft', 'altleft', '5') # Ubuntu server?  # 通过事先手动打开一个最大化的chrome解决！
			sleep(3)
			pyautogui.typewrite(url ,0.1)
			sleep(3)
			# pyautogui.press('enter')
			pyautogui.click(500, 100, button='left')
			sleep(3)

			func()

			pyautogui.typewrite(username,0.1)
			sleep(3)
			pyautogui.press('tab')
			pyautogui.typewrite(passwd,0.1)
			sleep(3)
			if pause:
				pyautogui.alert('Next') # 手动输入验证码时，暂停
			pyautogui.press('enter')
			sleep(3)
			
		return wrapper


	def copy(self):
		'''use gedit to get the contnet'''
		os.system('nohup gedit temp 2>&1 &') # self.getter = pyautogui.prompt(text='', title='' , default='')


	def confirm(self):
		'''confirm the promopt frame'''
		pyautogui.hotkey('ctrlleft', 'v')
		sleep(3)
		pyautogui.hotkey('ctrlleft', 's')
		sleep(3)
		pyautogui.hotkey('altleft', 'f4')


	def get_copy(self):
		'''use threading to skip the block of the thread'''
		try:
			os.remove('temp')
			sleep(3)
		except:
			logging.info("Exception: "+traceback.format_exc()) # print exception message
			sleep(3)
		
		process_copy = threading.Thread(target=self.copy, name='process_copy')
		# sleep(2)
		sleep(3)
		pyautogui.hotkey('ctrlleft', 'c')
		# sleep(2)
		sleep(3)
		process_copy.start()
		# sleep(1)
		sleep(3)
		self.confirm()
		# sleep(2)
		sleep(3)

		with open ('temp', 'r') as temp:
			self.getter = temp.read()


	def get_position(self):
		'''get the position of mouse, should run this method in a terminal to quit easily'''
		print('Press Ctrl-C to quit!')
		try:
			while True:
				x, y = pyautogui.position()
				positionStr = 'X: {} Y: {}'.format(*[str(x).rjust(4) for x in [x, y]])
				print(positionStr, end='')
				print('\b' * len(positionStr), end='', flush=True)
		except KeyboardInterrupt:
			logging.info("Exception: "+traceback.format_exc()) # print exception message
			print('\n')




# ag = autogui()
# ag.get_copy()
# # ag.get_position()
# print(ag.getter)