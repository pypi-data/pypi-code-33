import random
from bs4 import BeautifulSoup
from . import webtools
base_google_url = "http://www.google.com"
google_search_string = "/search?tbm=isch&q="


class google_image():
    def __init__(self, image_root_element, driver):
        self.driver = driver
        self.image_source_link = image_root_element.get_attribute('href')
        self.thumbnail_soup = BeautifulSoup(
                image_root_element.get_attribute("outerHTML"), 'html.parser')
        self.image_source_head_soup = BeautifulSoup(
                self._get_source_head_html(), 'html.parser')

    def _set_new_driver(self, link):
        self.driver.quit()
        self.driver = webtools.get_headless_web_driver_selenium_chrome(
                link)

    def _get_source_head_html(self):
        self._set_new_driver(self.image_source_link)
        _source_heads = self.driver.\
            find_elements_by_css_selector('.irc_mil.i3597')
        if len(_source_heads) > 0:
            return _source_heads[1].get_attribute("outerHTML")
        else:
            raise Exception

    def get_source_image_link(self):
        _url = self.image_source_head_soup.img['src']
        return _url

    def get_source_link(self):
        _url = self.image_source_head_soup.a['href']
        return _url

    def get_thumbnail_link(self):
        _url = self.thumbnail_soup.img['data-src']
        return _url


def _get_random_google_image(emo):
    driver = webtools.get_headless_web_driver_selenium_chrome(
             base_google_url + google_search_string + emo)
    rg_ls = driver.find_elements_by_class_name('rg_l')
    random_image_parent = rg_ls[random.randrange(0, len(rg_ls))]
    new_google_image = google_image(random_image_parent, driver)
    return new_google_image


def get_output_dict(emo):
    new_google_image = _get_random_google_image(emo)
    output_dict = {}
    try:
        output_dict['image'] = new_google_image.get_source_image_link()
        output_dict['link'] = new_google_image.get_source_link()
        output_dict['thumbnail'] = new_google_image.get_thumbnail_link()
    except Exception:
        return
    return output_dict


def get_output(emo):
    output_dict = get_output_dict(emo)
    return output_dict['image']
