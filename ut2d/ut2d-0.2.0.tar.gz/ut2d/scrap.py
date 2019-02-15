import re
import requests

from bs4 import BeautifulSoup as BS

SEARCH_ENGINES = {
    'google': 'https://www.google.com',
    'bing': 'https://www.bing.com',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
}

TZ_INFO = {
    'AST': 'GMT-4',
    'EDT': 'GMT-4',
    'EST': 'GMT-5',
    'CDT': 'GMT-5',
    'CST': 'GMT-6',
    'MDT': 'GMT-6',
    'MST': 'GMT-7',
    'PDT': 'GMT-7',
    'PST': 'GMT-8',
    'AKDT': 'GMT-8',
    'AKST': 'GMT-9',
    'HADT': 'GMT-9',
    'SDT': 'GMT-10',
    'HST': 'GMT-10',
    'HAST': 'GMT-10',
    'SST': 'GMT-11',
    'CHST': 'GMT+10',
}

# TODO: well-known cities


def locate_tz(text: str) -> str:
    return re.search('\(.*\)', text).group()[1:-1]


def tz_to_gmt(text: str) -> str:
    """
    GMT-4 -> GMT-4 -> -4
    UTC-4 -> GMT-4 -> -4
    AST   -> GMT-4 -> -4
    """
    if text[:3].upper() in ['UTC', 'GMT']:
        if len(text) == 3:
            return '+0'
        else:
            return text[3:]
    else:
        time_in_gmt = TZ_INFO.get(text.upper())
        if not time_in_gmt:
            raise ValueError('time zone not found')
        else:
            return time_in_gmt[3:]


class TimezoneScrapper:

    def __init__(self, city: str):
        self.city = city
        self.search_engines = []
        self.timezone = None
        
        self._find_search_engines()
        self._find_timezone()
    
    def _find_search_engines(self):
        for se, se_url in SEARCH_ENGINES.items():
            try:
                r = requests.get(se_url, headers=HEADERS)
                if r.status_code == 200:
                    self.search_engines.append(se)
            except:
                pass

        if not self.search_engines:
            print(u'\U0001F625',
                  ' I am sorry, but search city function needs Internet connection to popular search engines && no connection available!'
                  ' Please check your Internet connection!')
    
    def _find_timezone(self):
        for se in self.search_engines:
            if (se == 'google') and (not self.timezone):
                self._scrap_google()
            if (se == 'bing') and (not self.timezone):
                self._scrap_bing()

    def _scrap_google(self):
        city_fmt = self.city.lstrip().rstrip().replace(' ', '+')

        base_url = 'https://www.google.com/search?q='
        full_url = base_url + city_fmt + '+' + 'time'

        try:
            r = requests.get(full_url, headers=HEADERS)
            soup = BS(r.content, 'html.parser')
            tz = soup.select('span[class="KfQeJ"]')[1].text
            
            tz_fmt = locate_tz(tz)
            self.timezone = tz_to_gmt(tz_fmt)
        except:
            pass

    def _scrap_bing(self):
        city_fmt = self.city.lstrip().rstrip().replace(' ', '%20')

        base_url = 'https://www.bing.com/search?q='
        full_url = base_url + city_fmt + '%20' + 'time'

        try:
            r = requests.get(full_url, headers=HEADERS)
            soup = BS(r.content, 'html.parser')
            tz = soup.select_one('div[class="baselClock"] div[class="b_focusLabel"]').text

            tz_fmt = locate_tz(tz)
            self.timezone = tz_to_gmt(tz_fmt)
        except:
            pass
