
import datetime
import time
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Stage(object):
	START = 0
	LOGINED = 1
	PERF_OPENED = 2


class Selenium_yes24(object):
	#def __init__(self, idperf, x=100, y=100, w=1024, h=700):
	def __init__(self, idperf, x=100, y=100, w=512, h=350):
		self.idperf = idperf
		self.stage = Stage.START

		options = Options()
		options.add_argument('--disable-infobars')
		options.add_argument('--window-position={},{}'.format(x,y));
		options.add_argument('--window-size={},{}'.format(w,h))
		self.driver = webdriver.Chrome('./chromedriver', chrome_options=options)  # Optional argument, if not specified will search path.
		#self.driver.set_window_position(x, y)
		#self.driver.set_window_size(w, h)
		self.driver.implicitly_wait(5)

	def login(self, userid, userpw):
		URL = 'https://ticket.yes24.com/Pages/Login/LoginEnt.aspx?ReturnURL=http://ticket.yes24.com/Home/Perf/PerfDetailInfo.aspx&&ReturnParams=IdPerf={}'.format(self.idperf)
		self.driver.get(URL);

		## LOGIN FIRST
		self.driver.find_element_by_name('txtLoginID').send_keys(userid)
		self.driver.find_element_by_name('txtPassword').send_keys(userpw)
		self.driver.find_element_by_name('imgLogin').click()

		## CHECK LOGIN FINISHED
		self.driver.find_element_by_xpath("//a[contains(@href,'LogOutUrl')]")

		## CHANGE TITLE
		self.driver.execute_script("document.title = '{}'".format(userid))

		## save stage
		self.stage = Stage.LOGINED

		"""
		executor_url = driver.command_executor._url
		session_id = driver.session_id

		print(session_id)
		print(executor_url)
		"""

	def logout(self):
		# it is for removing command_executor
		time.sleep(1)
		self.driver.quit()

	def openBlank(self, count=1):
		self.driver.execute_script("window.open()")

		## handling popup
		main_window_handle = self.driver.current_window_handle

		popup_window_handle = None
		for handle in self.driver.window_handles:
		    if handle != main_window_handle:
		        popup_window_handle = handle
		        #break

		self.driver.switch_to.window(popup_window_handle)

	def openPerf(self, idperf, idtime):
		URL = 'http://ticket.yes24.com/Pages/Perf/Sale/PerfSaleProcess.aspx?IdPerf={}&IdTime={}'.format(idperf, idtime)
		self.driver.get(URL)
		self.stage = Stage.PERF_OPENED

	def goLastPage(self):
		print("Going to last page")
		# 1 Pass Calandar
		e = self.driver.find_element_by_xpath("//img[@id='btnSeatSelect']")
		self.driver.execute_script("arguments[0].click();", e)

		# 2 Seat
		ret = True
		while ret:
			self.selectRandomSeat()
			ret = self.detectAlert()

		# 3 Coupon
		# 4 Deliver
		self.nextStep()

	def selectRandomSeat(self):
		self.driver.switch_to.default_content()
		retry_xpath_empty(self.driver, "//div[@id='divFlash']")

		## switch frame
		#iframe = self.driver.find_element_by_xpath("//iframe[@id='ifrmSeatFrame']")	
		iframes = self.driver.find_elements_by_tag_name("iframe")	
		self.driver.switch_to.frame(iframes[0])

		# WAIT UNTIL PAGE LOADED
		retry_xpath_empty(self.driver, "//div[@id='divSeatArray']")
		divSeatArray = self.driver.find_element_by_xpath("//div[@id='divSeatArray']")

		# parse HTML into Seats
		soup = BeautifulSoup(divSeatArray.get_attribute("innerHTML"), "html.parser")
		seats = soup.findAll('div')
		colorSeats = [seat for seat in seats if seat['class'][0] != 's13']

		# click random seat
		wantSeatId = colorSeats[0]['id']
		wantSeat = divSeatArray.find_element_by_xpath("//div[@id='{}']".format(wantSeatId))
		self.driver.execute_script("arguments[0].click();", wantSeat)
		time.sleep(1)

		## complete select seat
		try:
			e = self.driver.find_element_by_xpath("//*[@class='booking']")
			self.driver.execute_script("arguments[0].click();", e)
		except NoSuchElementException as e:
			print(str(e))

	def detectAlert(self):
		try:
			WebDriverWait(self.driver, 3).until(EC.alert_is_present(),
							"Timed out for popup to appear")
			alert = self.driver.switch_to_alert()
			alert.accept()
			print("alert appeared. Just Clicked")
			return True
		except TimeoutException:
			print("no alert. Keep going to next step")
			return False

	def nextStep(self):
		self.driver.switch_to.default_content()
		#### COUPON
		e = retry_find_element_by_xpath(self.driver, "//a[contains(@onclick,'fdc_PromotionEnd')]")
		self.driver.execute_script("arguments[0].click();", e)

		#### DELIVERY
		retry_find_element_by_xpath(self.driver, "//span[@id='deliveryPos']")
		retry_input_empty(self.driver, 'ordererUserName')

		## 티켓 수령방법을 선택하세요.
		while True:
			checked = self.driver.execute_script("var rdos = document.getElementsByName('rdoDelivery');if(rdos.length>0) return rdos[0].checked;")
			print("checked:", checked)
			if checked:
				break
			time.sleep(0.2)

		e = retry_find_element_by_xpath(self.driver, "//a[contains(@onclick,'fdc_DeliveryEnd')]")
		self.driver.execute_script("arguments[0].click();", e)

	def prepare_lastpage(self, payment_method=1):

		# 2 credit card / 222 kakao bank / 22 bank
		if payment_method == 1:
			e = self.driver.find_element_by_xpath("//input[@idgroup='2']")
			self.driver.execute_script("arguments[0].click();", e)
		elif payment_method == 2:
			e = self.driver.find_element_by_xpath("//input[@idgroup='222']")
			self.driver.execute_script("arguments[0].click();", e)
		elif payment_method == 3:
			e = self.driver.find_element_by_xpath("//input[@idgroup='22']")
			self.driver.execute_script("arguments[0].click();", e)
			select = Select(self.driver.find_element_by_id("selBank"))
			# 50 KB / 11631 KEB / 57 NH / 11629 SH / 49 WOORI
			# 11634 POST / 11630 HANA / 11633 SC
			select.select_by_value("50")

		e = self.driver.find_element_by_id("cbxCancelFeeAgree")
		self.driver.execute_script("arguments[0].click();", e)
		e = self.driver.find_element_by_id("chkinfoAgree")
		self.driver.execute_script("arguments[0].click();", e)

		self.handleCaptcha()

	def handleCaptcha(self):
		## captchaImg ready??
		while True:
			es = self.driver.find_element_by_xpath("//img[@id='captchaImg']")
			if es is not None and es.is_displayed():
				src = es.get_attribute("src")
				print("captcha:", src)
				captchaKey = src.split('key=')[1]
				break
			print("captchaImg not ready")
			time.sleep(1)

		## captchaText empty??
		captchaText = self.driver.find_element_by_name('captchaText')
		if captchaText.get_attribute('value') != "":
			return

		## register captchaKey
		insertURL = "https://wangticket.com/captcha/new_captcha.php?captchaKey={}".format(captchaKey)
		r = requests.get(insertURL)
		print("[new captcha]", r.status_code, r.reason)
		print(r.text)
		captchaId = int(r.text)

		## waiting captchaText ready!
		while True:
			time.sleep(5)
			getURL = "https://wangticket.com/captcha/get_captcha.php?captchaId={}".format(captchaId)
			r = requests.get(getURL)
			#print("[get captcha]", r.status_code, r.reason)
			print(r.text)
			data = r.json()
			captchaText = data['captchaText']
			if captchaText is not None and captchaText.strip():
				self.driver.find_element_by_name('captchaText').send_keys(captchaText)
				break

	def handleDialog(self):
		ALERT1 = "자동주문방지 문자를 잘못 입력하셨습니다."
		ALERT2 = "티켓 주문처리중 오류가 발생하였습니다."
		#"예매 완료까지 허용된 제한 시간이 만료 되어 예매를 완료 할 수 없습니다. 다시 예매 하여 주십시오!"
		#"오류 내용 : 좌석선점오류[62][235]"
		#"제휴처 좌석선점에 오류가 발생하였습니다.[45][335]"
		#""
		ALERT3 = "자동주문방지 문자를 입력해주세요."

		content_xpath = "//div[@id='dialogAlert']"
		content = self.driver.find_element_by_xpath(content_xpath)
		contentHTML = content.get_attribute('innerHTML')
		print("alert is displayed.", contentHTML)

		btn_xpath = "//button[@aria-disabled='false']"
		e = self.driver.find_element_by_xpath(btn_xpath)
		self.driver.execute_script("arguments[0].click();", e)
		print("alert clicked")

		if ALERT1 in contentHTML:
			return 1
		elif ALERT2 in contentHTML:
			return 2
		else:
			return -1

	def checkout(self):
		while True:
			## captcha empty??
			self.handleCaptcha()

			## checkout button
			e = self.driver.find_element_by_xpath("//img[@id='imgPayEnd']")
			self.driver.execute_script("arguments[0].click();", e)

			## dialog check
			while True:
				prgrs_xpath = "//div[@aria-labelledby='ui-dialog-title-dialogPayProgress']"
				alert_xpath = "//div[@aria-labelledby='ui-dialog-title-dialogAlert']"

				prgrs = self.driver.find_elements_by_xpath(prgrs_xpath)
				alert = self.driver.find_elements_by_xpath(alert_xpath)

				if len(prgrs)>0 and prgrs[0].is_displayed():
					print("prgrs is displayed")
				elif len(alert)>0 and alert[0].is_displayed():
					ret = self.handleDialog()
					if ret == 2:
						print("Should find new seats")
						return
					elif ret == 1:
						print("Should enter captcha again")
						break
				else:
					print("nothing displayed")
				time.sleep(1)


	def change_value_by_id(self, vid):
		self.driver.execute_script("jgIdPerf={}".format(vid))

	def change_element_value_by_id(self, eid, v):
		self.driver.execute_script("document.getElementById('{}').value = '{}';".format(eid,v))

	def change_element_html_by_id(self, eid, html):
		self.driver.execute_script("document.getElementById('{}').innerHTML = \"{}\";".format(eid,html))

def retry_click_element_by_xpath(driver, xpath):
	while True:
		try:
			element = driver.find_element_by_xpath(xpath)
			element.click()
			break
		except:
			print("failed to click.", xpath)
			time.sleep(0.2)
	return element


def retry_find_element_by_xpath(driver, xpath):
	while True:
		element = driver.find_element_by_xpath(xpath)
		if element.is_displayed():
			break
		else:
			print("element is not displayed yet.", xpath)
			time.sleep(0.2)
	return element

def retry_input_empty(driver, inputid):
	while True:
		element = driver.find_element_by_id(inputid)
		if element.get_attribute('value') == '':
			print("input is empty yet.", inputid)
			time.sleep(0.2)
		else:
			break
	return

def retry_xpath_empty(driver, xpath):
	while True:
		element = driver.find_element_by_xpath(xpath)
		if element.get_attribute('innerHTML') == '':
			print("xpath is empty yet.", xpath)
			time.sleep(0.2)
		else:
			break
	return

