from bs4 import BeautifulSoup as bs
from . import webtools
from .. import errors

dict_site = {'eng': "http://en.oxforddictionaries.com/definition/",
             'kor': "http://ko.dict.naver.com/#/search?query="}


def _get_eng_meaning(emo):
    url = dict_site['eng'] + emo
    html = webtools.get_html(url)
    soup = bs(html, 'html.parser')
    inds = soup.find_all("span", attrs={'class': 'ind'})
    if inds == [] or inds is None:
        raise errors.CANT_FIND_SUCH_EMOTION_ERROR()
        return
    return inds[0].string


def _get_kor_meaning(emo):
    url = dict_site['kor'] + emo
    driver = webtools.get_headless_web_driver_selenium_chrome(url)
    ellipsis = driver.find_element_by_class_name("ellipsis")
    u_word_dics = ellipsis.find_elements_by_class_name("u_word_dic")
    meaning = ""
    for u_word_dic in u_word_dics[1:]:
        if u_word_dic.get_attribute('data-lang') == 'ko':
            meaning += u_word_dic.text + ' '
    meaning = meaning[0:-1]
    return meaning


def _get_meaning(emo, lang):
    if lang == 'eng':
        return _get_eng_meaning(emo)
    elif lang == 'kor':
        return _get_kor_meaning(emo)
    else:
        raise errors.UNKNOWN_LANG_ERROR()


def get_output(emo, lang):
    try:
        meaning = _get_meaning(emo, lang)
        return meaning
    except Exception as e:
        print(e)
