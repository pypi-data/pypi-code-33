from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SeleniumUtilsMixin:

    def wait_for(self, text, by=None, timeout=None):
        """Explicit wait.

        Default is by partial link text
        """
        timeout = timeout or 20
        by = by or By.PARTIAL_LINK_TEXT
        element = WebDriverWait(self.selenium, timeout).until(
            EC.presence_of_element_located((by, text)))
        return element

    def wait_for_edc(self):
        WebDriverWait(self.selenium, 20).until(
            EC.presence_of_element_located((By.ID, 'edc-body')))
