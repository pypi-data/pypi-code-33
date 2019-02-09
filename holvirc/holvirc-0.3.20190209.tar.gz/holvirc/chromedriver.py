"""Ubuntu chomium webdriver"""
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', chrome_options=chrome_options)
