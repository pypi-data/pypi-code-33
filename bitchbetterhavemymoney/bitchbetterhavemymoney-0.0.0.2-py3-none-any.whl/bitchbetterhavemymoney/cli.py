from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import getpass, sys, os

def main():
  p = getpass.getpass(prompt="Password:")
  CURSOR_UP_ONE = '\x1b[1A'
  ERASE_LINE = '\x1b[2K'
  sys.stdout.write(CURSOR_UP_ONE)
  sys.stdout.write(ERASE_LINE)
  print("Getting your cheques ready...")

  options = webdriver.ChromeOptions()
  options.add_argument('headless')

  driver = webdriver.Chrome(options=options)
  driver.get("https://www.monizze.be/en/login/")

  email = driver.find_element_by_name("email")
  email.clear()
  email.send_keys("0471074098")

  password = driver.find_element_by_name("password")
  password.clear()
  password.send_keys(p)
  password.send_keys(Keys.RETURN)

  assert "No results found." not in driver.page_source

  cheques = driver.find_element_by_xpath("/html/body/div/main/section/div/div/div[1]/div[1]/p/strong[1]").text

  amount = "You have {} maaltijdcheques!".format(cheques)

  sys.stdout.write(CURSOR_UP_ONE)
  sys.stdout.write(ERASE_LINE)
  print(amount)
  driver.close()



if __name__ == "__main__":
    main()
