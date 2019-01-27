''' Utilities for web mining and HTML processing. '''
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def find_hrefs(content):
    ''' Finds href links in a HTML string.

    :param: content: A HTML string.

    :returns: A list of href links found by BeautifulSoup.
    '''
    soup = BeautifulSoup(content)

    return [a.get('href', '') for a in soup.findAll('a')]

def wait_browser(browser, selector, secs=10, by=By.XPATH):
    return WebDriverWait(browser, secs).until(
        EC.presence_of_element_located((by, selector))
    )
