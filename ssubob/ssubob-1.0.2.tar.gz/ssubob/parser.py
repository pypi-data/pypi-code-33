from bs4 import BeautifulSoup
import requests
import re
from collections import defaultdict, OrderedDict
import datetime


class FoodParser:
    def __init__(self):
        self.base_url = 'http://soongguri.com/menu/m_menujson.php'
        self.price_url = "http://soongguri.com/main.php?mkey=2&w=3&l=3"
        # 'http://soongguri.com/main.php?mkey=2&w=3&l=3&j=0'
        self.price_res = None
        self.faculty_food = None
        self.pupil_food = None
        self.the_kitchen = None
        self.snack_corner = None
        self.food_court = None
        self.no_food_today = {
            '조식': {
                '메뉴': ['식단이 없습니다', '운영시간을 확인해 주세요'],
                '가격': '가격정보가 없습니다.',
            },
            '중식': {
                '메뉴': ['식단이 없습니다', '운영시간을 확인해 주세요'],
                '가격': '가격정보가 없습니다.',
            },
            '석식': {
                '메뉴': ['식단이 없습니다', '운영시간을 확인해 주세요'],
                '가격': '가격정보가 없습니다.',
            },
        }
        self.no_food_court_today = {
            '메뉴': ['식단이 없습니다', '운영시간을 확인해 주세요']
        }

    def refresh(self, date=None):
        """
        서버에 request를 보내서 식당 정보들을 갱신한다.
        인자로 fkey를 받는데 1은 월요일, 5는 금요일 이런식이다.
        fkey 인자를 생략하면 자동으로 오늘의 식단 가져옴
        fkey 가 7 이상으로 넘어가면 다음주식단을 가져옴
        fkey 가 음수로 되면 과거 데이터를 가져옴
        아쉬운점은 가격을 못가져온다
        가격은 http://soongguri.com/main.php?mkey=2&w=3&l=3&j=0 여기있음
        여기서 다 파싱하면 뒤질지도 모름
        내가 뒤지는게 아니라 프로그램이 뒤질거같음
        사이트가 규칙이 갑자기 바뀌면 뻗으니까 안전하게 base_url 지금쓰는거 쓰고
        base_url에서 가져온 메뉴검색 -> 부모의 다음 쌍둥이 -> day_of_week번째 항목에 있는 가격 가져오기 이런식으로 하는게
        그나마 안전하지 않을까
        :return: None
        """
        date = date or datetime.date.today()
        day_of_week = date.weekday()
        # date.weekday() 메소드는 월요일 0 일요일7인 반면 fkey는 월요일 1 일요일 0이다
        day_of_week = (day_of_week + 1) % 8
        res = requests.get(self.base_url, params={'fkey': day_of_week}, timeout=2)
        # res = requests.get(self.base_url, timeout=2)
        jsn = res.json()
        if not jsn:
            return
        self.pupil_food = jsn.get('학생식당')
        self.the_kitchen = jsn.get('THE KITCHEN')
        self.snack_corner = jsn.get('스넥코너')
        self.food_court = jsn.get('푸드코트')
        self.faculty_food = jsn.get('숭실도담식당')
        self.price_res = requests.get(self.price_url, timeout=2)
        self.price_res.encoding = 'utf-8'

    def get_price(self, menu_items):
        prices = []
        for menu_item in menu_items:
            if menu_item == '*':
                continue
            res = self.price_res
            soup = BeautifulSoup(res.text, 'html.parser')
            div = soup.find_all('div', text=re.compile(menu_item))
            price_reg = re.compile('\d,\d{3} 원')

            if len(div) == 0:
                span = soup.find_all('span', text=re.compile(menu_item))
                if len(span) == 0:
                    continue
                else:
                    span = span[0]
                    price = price_reg.findall(span.parent.parent.parent.text)
                    if len(price) != 0:
                        prices.append(price)
            else:
                div = div[0]
                price = price_reg.findall(div.parent.text)
                if len(price) != 0:
                    prices.append(price)
        if len(prices) == 0:
            return '가격정보가 없습니다.'
        return max(list(prices), key=prices.count)[0]

    def get_food(self, place):
        if place == '학식':
            return self.get_pupil_food()
        elif place == '교식':
            return self.get_faculty_food()
        elif place == '푸드코트':
            return self.get_food_court()
        elif place == '기식':
            return self.get_dormitory_food()
        elif place == "더 키친":
            return self.get_the_kitchen()
        elif place == "스넥코너":
            return self.get_snack_corner()
        else:
            raise Exception('FoodParser.get_food() got unexpected parameter place={}'.format(place))

    def get_faculty_food(self):
        """
        교식 메뉴
        :return: dict
        """
        ret_dict = defaultdict()
        if not self.faculty_food:
            return self.no_food_today

        for section in self.faculty_food:
            ret_dict.update({section: []})
            soup = BeautifulSoup(self.faculty_food[section], 'html.parser')
            t = ''
            if soup.find_all(['p']):
                for i in soup.find_all(['p']):
                    t += '\n' + i.text
            elif soup.find_all(["div"]):
                for i in soup.find_all(['div']):
                    t += '\n' + i.text
            else:
                t = " ".join(self.faculty_food[section].lower().split("<br>"))

            exclude_english = re.compile('[^가-힣 ]+')

            res = exclude_english.sub('', ' '.join(t.split()))
            res = ' '.join(res.split())
            res = res.split(' ')
            price = self.get_price(res)

            ret_dict.update({section: {'메뉴': res, '가격': price}})
        return ret_dict

    def get_pupil_food(self):
        """
        exception 많이남(주말)
        :return: dict
        """
        ret_dict = defaultdict()
        if not self.pupil_food:
            return self.no_food_today

        for section in self.pupil_food:
            ret_dict.update({section: {'메뉴': []}})
            soup = BeautifulSoup(self.pupil_food[section], 'html.parser')
            t = ''
            if soup.find_all(['div']):
                for i in soup.find_all(['div']):
                    t += '\n' + i.text
            elif soup.find_all(["span"]):
                for i in soup.find_all(['span']):
                    t += '\n' + i.text
            else:
                t = " ".join(self.pupil_food[section].lower().split("<br>"))

            exclude_english = re.compile('[^가-힣\* ]+')

            res = exclude_english.sub('', ' '.join(t.split()))
            res = ' '.join(res.split())
            res = res.split(' ')
            res = [each for each in res if each != '']
            res = [each for each in res if each[0] != '*']
            price = self.get_price(res)

            ret_dict.update({section: {'메뉴': res, '가격': price}})
        return ret_dict

    def get_dormitory_food(self, date=None):
        dorm_url = 'http://ssudorm.ssu.ac.kr/SShostel/mall_main.php?viewform=B0001_foodboard_list&gyear={}&gmonth={}&gday={}'
        today = date or datetime.date.today()
        day_of_week = today.weekday()
        if day_of_week == 6:
            # 일요일에 다음주로 홈페이지가 넘어가버림
            yester_day = datetime.date.today() - datetime.timedelta(days=1)
            year = yester_day.year
            month = yester_day.month
            day = yester_day.day
        else:
            year = today.year
            month = today.month
            day = today.day
        res = requests.get(dorm_url.format(year, month, day), timeout=2)
        res.encoding = 'euc-kr'
        form = defaultdict()
        soup = BeautifulSoup(res.text, 'html.parser')
        parenthesis = re.compile(r"(\(.+)\)")
        table = soup.find_all('table', attrs={'class': 'boxstyle02'})[0]
        rows = table.findChildren(['tr'])
        day = 0  # 월화수목금 구분
        for row in rows[1:]:
            cells = row.findChildren('td')
            time = 0  # 조식 중식 석식 구분
            form.update({'월화수목금토일'[day]: {'조식': defaultdict(), '중식': defaultdict(), '석식': defaultdict(), '특식': defaultdict()}})
            for cell in cells[:4]:  # 방학중에는 :3으로 슬라이싱 하고 학기중에는 :4로 슬라이싱 하면됨
                text = cell.text.strip()
                text = parenthesis.sub('', text)
                menu = text.split('\r\n')
                form['월화수목금토일'[day]][['조식', '중식', '석식', '특식'][time]]['메뉴'] = menu
                time += 1
            day += 1
        return form

    def get_the_kitchen(self):
        """
        TODO: 정규표현식 이용해서 메뉴 가격 깔끔하게 나누기
        :return: dict{
            "메뉴": [
                '#Pasta#',
                '- cream sauce',
                '카르보나라파스타 - 6.0',
                '만조파스타 - 7.0',
                '크림소시지파스타 - 6.0',
                '새우크림파스타 - 6.0',
                '해물크림파스타 - 7.0',
                '빠네 파스타 - 8.0 (화.목10%할인) 7.2',
                '- tomato sauce',
                '포모도로파스타 - 6.0',
                '아라비아타파스타 - 6.0',
                '스파이시치킨파스타 - 7.0',
                '해물토마토파스타 - 7.0',
                '생모짜렐라페스토 파스타 -7.0',
                '- rose sauce',
                '쉬림프로제 파스타 - 7.0',
                '머쉬룸로제 파스타 - 7.0',
                '게살로제 파스타 - 7.0',
                '- olive oil sauce',
                ...
            ]
        }
        """
        ret_dict = defaultdict()

        if not self.the_kitchen:
            return self.no_food_court_today
        for section in self.the_kitchen:
            menu = self.the_kitchen[section]

            menus = menu.split('<br>')
            kitchen_regex = re.compile('[^가-힣 \d\-\.\+]+')
            menus = [kitchen_regex.sub('', menu) for menu in menus]
            menus = [menu.strip() for menu in menus if menu.strip() != '']

            ret_dict.update({section: menus})
        return ret_dict

    def get_snack_corner(self):
        """
            TODO: 정규표현식 이용해서 메뉴 가격 깔끔하게 나누기
            :return: dict
        """
        ret_dict = {}
        if not self.snack_corner:
            return self.no_food_court_today
        for section in self.snack_corner:
            menu = self.snack_corner[section]
            soup = BeautifulSoup(menu, 'html.parser')
            div = soup.find_all(['div'])
            t = ''
            for i in div:
                t += '\n' + i.text
            f = [i.replace(' ', '').replace('\xa0', '') for i in t.split('\n') if i != '']
            f = [i.replace('<new>', '') for i in f if i]
            f = [i.strip() for i in f if i != '' and len(i) < 20]
            food_list = list(OrderedDict((x, True) for x in f).keys())
            ret_dict.update({section: food_list})
        return ret_dict

    def get_food_court(self):
        """
            :return: dict
        """

        ret_dict = defaultdict()
        if not self.food_court:
            return self.no_food_court_today

        for section in self.food_court:
            ret_dict.update({section: []})
            soup = BeautifulSoup(self.food_court[section], 'html.parser')
            t = ''
            if soup.find_all(['div']):
                for i in soup.find_all('div')[1:]:
                    if len(i.text) < 35:
                        t += '{}\n'.format(i.text.strip())

                t = re.sub(r"\n+", '\n', t.strip())
            else:
                # TODO: span parsing
                t = ''

            menus = t.split('\n')
            menus = [menu for menu in menus if not menu == '']
            menus = [menu for menu in menus if menu[0] not in ['#', '<', '(']]

            hangul = re.compile('[^가-힣 0-9.]+')
            menus = [hangul.sub('', menu) for menu in menus]
            menus = [' '.join(menu.strip().split()) for menu in menus]

            ret_dict.update({section: menus})
        return ret_dict


food_api = FoodParser()

