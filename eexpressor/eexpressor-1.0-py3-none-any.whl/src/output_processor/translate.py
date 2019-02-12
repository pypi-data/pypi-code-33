from . import webtools
translation_link = "http://translate.google.com/?#view=home&op=translate\
&sl=auto&tl=en&text="


def _get_translation(emo):
    # Using google auto translation
    # Requires network connection
    emo.replace(' ', '%20')
    driver = webtools.get_headless_web_driver_selenium_chrome(
            translation_link + emo)
    tlid = driver.find_element_by_css_selector(".tlid-translation.translation")
    translation = tlid.find_element_by_tag_name("span")
    return translation.text


def get_output(emo):
    return _get_translation(emo)
