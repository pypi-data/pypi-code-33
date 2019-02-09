#!/usr/bin/python

# import module
from __future__ import print_function
from math import *
import argparse
import mechanize
import cookielib
import sys
import bs4
import requests
import os
import glob
import random
import time

reload(sys)
sys.setdefaultencoding('utf-8')

__VERSION__ = '0.1.3 (in development)'
__BOTNAME__ = 'zvBot' # default botname
__LICENSE__ = '''
MIT License

Copyright (c) 2018 Noval Wahyu Ramadhan <xnver404@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# lambda
sprt = lambda: logger('-'*arg.long_separator, sprt=True)

# super user
ADMIN = []

# blacklist user
BLACKLIST = []

# Command options
SINGLE_COMMAND = ['@quit',  '@help']
NOT_SINGLE_COMMAND = [ '@calc', '@igstalk', '@img',
        '@tr', '@igd', '@wiki',
        '@sgb_quote', '@tanpakertas_quote', '@rasa_quote',
        '@img_quote', '@kbbi',
        '@lyrics' ]

COMMANDS = NOT_SINGLE_COMMAND + SINGLE_COMMAND
BLACKLIST_COMMAND = []

# helper
HELP_TEXT = [ 'commands:\n',

        ' - @help : show this help message.',
        ' - @kbbi <word> : search entries for a word/phrase in KBBI Online.',
        ' - @lyrics <song title> : look for the lyrics of a song',
        ' - @img <query> : look for images that are relevant to the query.',
        ' - @calc <value> : do mathematical calculations.',
        ' - @igd <url> : download Instagram photos from url.',
        ' - @sgb_quote <quote> : SGB quote maker.',
        ' - @rasa_quote <quote> : rasa untukmu quote maker.',
        ' - @tanpakertas_quote <quote> : tanpa kertas quote maker.',
        ' - @img_quote <quote> : IMG quote maker.',
        ' - @wiki <word> : search for word definitions in wikipedia.',
        ' - @tr <text> : translate any language into English.',
        ' - @igstalk <username> : View user profiles on Instagram.',

        '<br>Example:\n',

        ' - @kbbi makan',
        ' - @img random',
        ' - @lyrics eminem venom',
        ' - @calc 1+2+3+4+5',
        ' - @sgb_quote write your quote here!',
        ' - @igd https://instagram.com/p/<code>',
        ' - @tr halo dunia',
        ' - @wiki wibu',
        ' - @wiki kpop' ]

def command(mess, name = ''):
    me = mess[0]

    if me == '@lyrics':
        query = '{}'.format(' '.join(mess[1:]))

        hdr = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}

        r = requests.get('https://search.azlyrics.com/search.php',
                 params = {'q': query,
                           'w': 'songs'},
                           headers = hdr)
        url = bs4.BeautifulSoup(r.text, 'html.parser').find('td', {'class': 'text-left visitedlyr'})

        if not url:
            r = requests.get('https://www.lyricsmode.com/search.php',
                    params = {'search': query},
                    headers = hdr)
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            url = soup.find('a', {'class': 'lm-link lm-link--primary lm-link--highlight'})

            if not url:
                return 'lyrics can\'t be found'

            r = requests.get('https://www.lyricsmode.com{}'.format(url.attrs['href']))
            soup = bs4.BeautifulSoup(r.text, 'html.parser')

            return '{0}\n\n{1}'.format(
                ' - '.join([i.text[1:] for i in soup.find('ul', {'class': 'breadcrumb'}).findAll('li')[-2:]])[:-7],
                soup.find('p', {'class': 'ui-annotatable js-lyric-text-container'}).text[29:])

        r = requests.get(url.a.attrs['href'])
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        return '{0}\n{1}'.format(
            soup.title.text[:-22],
            soup.findAll('div')[21].text)

    elif me == '@kbbi':
        url = 'https://kbbi.kemdikbud.go.id/entri/{}'.format(' '.join(mess[1:]))
        raw = requests.get(url).text
        if "Entri tidak ditemukan." in raw:
            return 'entry not found: {}'.format(' '.join(mess[1:]))

        arti = []
        arti_contoh = []
        isolasi = raw[raw.find('<h2>'):raw.find('<h4>')]
        soup = bs4.BeautifulSoup(isolasi, 'html.parser')
        entri = soup.find_all('ol') + soup.find_all('ul')

        for tiap_entri in entri:
            for tiap_arti in tiap_entri.find_all('li'):
                kelas = tiap_arti.find(color="red").get_text().strip()
                arti_lengkap = tiap_arti.get_text().strip()[len(kelas):]

                if ':' in arti_lengkap:
                    arti_saja = arti_lengkap[:arti_lengkap.find(':')]
                else:
                    arti_saja = arti_lengkap

                if kelas:
                    hasil = '({0}) {1}'
                else:
                    hasil = '{1}'

                arti_contoh.append(hasil.format(kelas, arti_lengkap))
                arti.append(hasil.format(kelas, arti_saja))

        return '\n'.join(arti).replace('(n)', '( n )')

    elif me == '@tr':

        params = {
            'hl':'id',
            'sl':'auto',
            'tl':'en',
            'ie':'UTF-8',
            'prev':'_m',
            'q':' '.join(mess[1:])
        }

        url = 'https://translate.google.com/m'
        r = requests.get(url, params=params)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        return soup.find(class_='t0').text

    elif me == '@wiki':
        m = False

        url = 'https://id.m.wikipedia.org/wiki/' + '_'.join(mess[1:])
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        res = '$'
        temp = ''
        if soup.find('p'):
            if 'dapat mengacu kepada beberapa hal berikut:' in soup.find('p').text or 'bisa merujuk kepada' in soup.find('p').text:
                temp += soup.find('p').text + '\n'
                for i in soup.find_all('li'):
                    if 'privasi' in i.text.lower():
                        m = False
                    if m:
                        temp += '- ' + i.text + '\n'
                    if 'baca dalam' in i.text.lower():
                        m = True
            else:
                 paragraph = 6 if arg.paragraph >= 6 else arg.paragraph
                 for i in soup.find_all('p')[:paragraph]:
                     if 'akurasi' in i.text.lower():
                         pass
                     else:
                         temp += i.text + '\n\n'

        res += temp
        res += '<br>read more: ' + r.url

        if '$<br>' in res:
            res = ' sorry, I can\'t find the definition of "%s"' % ' '.join(mess[1:])

        return res[1:]

    elif me == '@help':
        res = 'Hello %s, ' % (' '.join([i.capitalize() for i in name.split()]))
        res += 'you are admin now\n\n' if name in ADMIN else 'have a nice day\n\n'

        for x in HELP_TEXT:
            c = x.split()
            if len(c) > 2:
                if x.split()[1] in COMMANDS:
                    if name in ADMIN:
                        res += x + '\n'
                    elif x.split()[1] not in BLACKLIST_COMMAND:
                        res += x + '\n'
            else:
                res += x + '\n'

        return res

# --------------- unknow ----------------- #

def updt(progress, total):
    indi = '\x1b[32m#\x1b[0m' if arg.color else '#'
    barLength, status = 25, '%s/%s' % (convertSize(progress), convertSize(total))
    progress = float(progress) / float(total)
    block = int(round(barLength * progress))
    text = "\r{:<9}[{}] {} [{:.0f}%]".format(
        'PROGRESS',
        indi * block + "-" * (barLength - block),
        status,
        round(progress * 100, 0)
        )
    sys.stdout.write(text)
    sys.stdout.flush()

def convertSize(n, format='%(value).1f %(symbol)s', symbols='customary'):
    SYMBOLS = {
        'customary': ('B', 'K', 'Mb', 'G', 'T', 'P', 'E', 'Z', 'Y'),
        'customary_ext': ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                          'zetta', 'iotta'),
        'iec': ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
        'iec_ext': ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                    'zebi', 'yobi'),
    }
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)

def parse_url(url):
    return url[8 if url.startswith('https://') else 7:].split('/')[0]

def get_file(url, name = 'zvBot.jpeg'):
    logger('downloading file from %s' % parse_url(url))
    r = requests.get(url, stream=True)

    file_size = len(r.content)

    downloaded = 0
    with open(name, 'wb') as f:
        for i in r.iter_content(1024):
            if buffer:
                updt(downloaded, file_size)
                f.write(i)
                f.flush()
                downloaded += len(i)
    print ('') # new line

    return True

# -------------- starting bot ---------------- #

class start_bot:
    def __init__(self, username, password):
        self.url = 'https://mbasic.facebook.com'
        self.username = username
        self.password = password
        self.image_numbers = self.get_last_images()
        self.burl = None

        # user config
        self.config = {
            'blacklist':{},
            'last':{},
            'limit':{},
            'botname':{}
        }

        self.br = self.setup()
        self.login()

    def run_a_bot(self):
        self.br.open(self.url + '/messages/read')
        name = False

        for i in self.br.links():
            if name:
                self.name = i.text.lower().split(' (')[0]

                # added new user
                if self.name not in self.config['last'].keys():
                    self.config['blacklist'][self.name] = False
                    self.config['limit'][self.name] = 0
                    self.config['botname'][self.name] = __BOTNAME__
                    self.config['last'][self.name] = 'unknow'


                if not self.config['blacklist'][self.name]:
                    logger('choose chat from %s' % i.text)

                    if self.name not in BLACKLIST or self.config['blacklist'][self.name]:
                        self.burl = self.url + i.url
                        break

                    else:
                        logger('blacklist user detected, skipped\n%s' % '-'*arg.long_separator, 'WARNING')
                        self.config['blacklist'][self.name] = True
                        break

            if 'Cari pesan' == i.text:
                name = True

        if self.burl:
            for _ in range(arg.refresh):
                shell = True
                allow = True
                not_igd_and_set = True

                text = self.br.open(self.burl).read()

                for x in self.br.links():
                    if arg.group_chat:
                        if x.text.lower()[-5:] == 'orang':
                            logger('group chat detected, skipped', 'WARNING')
                            sprt()
                            self.config['blacklist'][self.name] = True
                            break
                    else:
                        break

                soup = bs4.BeautifulSoup(text, 'html.parser')
                m = soup.find_all('span')
                com = ['']

                for num, i in enumerate(m):
                    if 'dilihat' in i.text.lower():
                        if m[num-3].text[:3].lower() == '@igd' and 'instagram' in m[num-3].text and len(m[num-3].text.split('/')) > 4:
                            logger('receive command: @igd')
                            not_igd_and_set = False
                            self.config['last'][self.name] = '@igd'
                            logger('make a requests')
                            ig_code = m[num-3].text.split('/')[4][1:]
                            logger('code: %s', ig_code)
                            self.get_file_from_instagram(ig_code)
                            break
                        not_com = m[num-3].text.lower()
                        com = not_com.split()
                        break

                if self.config['last'][self.name] and _ == 0 and not self.config['blacklist'][self.name]:
                    logger('last command: %s' % self.config['last'][self.name])

                if len(com) == 1 and com[0] in NOT_SINGLE_COMMAND:
                    shell = False

                try:
                    if self.config['limit'][self.name] == arg.limit and self.name not in ADMIN and not self.config['blacklist'][self.name] and com[0] in COMMANDS:
                        logger('user has exceeded the limit')
                        self.send('You have reached the usage limit')
                        self.config['blacklist'][self.name] = True

                    if com[0] in COMMANDS and com[0] != '@help':
                        self.config['limit'][self.name] += 1

                    if com[0] in BLACKLIST_COMMAND:
                        allow = False
                        if not self.config['blacklist'][self.name] and self.name not in ADMIN:
                            logger('receive command: %s' % com[0])
                            self.send('sorry, this command has been disabled by admin')

                    if self.name in ADMIN:
                        allow = True

                    # execute
                    if com[0] in COMMANDS and shell and allow:
                        if com[0] != '@igd' and not self.config['blacklist'][self.name]:
                            self.bcom = com[0]
                            self.config['last'][self.name] = com[0]

                            c_m = com[0]
                            logger('receive command: %s' % c_m)

                            if not_igd_and_set and com[0] != '@quit':
                                if com[0] in NOT_SINGLE_COMMAND or '_quote' in com[0]:
                                    logger('value:%s' % not_com.replace(com[0],''))

                                logger('make a requests')
                                if com[0] == '@img':
                                    self.send_image(get_file('https://source.unsplash.com/640x640/?' + not_com.replace(com[0],'')[1:]))
                                    sprt()

                                elif com[0] == '@calc':
                                    try:
                                        i = ''
                                        for x in not_com:
                                            if x.isdigit() or x in ['/', '*', '+', '-', '%']:
                                                i += x

                                        res = eval(i)
                                        self.send('%s\n\n= %s' % (not_com[6:],res))
                                    except (NameError,SyntaxError):
                                        self.send('invalid value: %s' % not_com[6:])

                                elif '_quote' in com[0]:
                                    self.send_image(self.quote(' '.join(com[1:])))
                                    sprt()

                                elif com[0] == '@igstalk':
                                    self.ig_stalk(com[1])

                                else:
                                    self.send(command(com, self.name))

                            elif com[0] == '@quit':
                                if self.name in ADMIN:
                                    self.send('bot stopped, thank you for chatting with me ^^')
                                    exit('stopped bot\n' + '-'*arg.long_separator)
                                else:
                                    self.send('You are not an admin, access is denied')

                except IndexError:
                    pass


    # ------------- other tool ------------ #

    def ig_stalk(self,username):
        text = requests.get('https://insta-stalker.com/profile/%s' % username).text
        soup = bs4.BeautifulSoup(text, 'html.parser')

        try:
            data = {'profile_url':soup.find(class_='profile-img').attrs['src'],
                'bio':'',
                'data':{'following':0, 'followers':0, 'posts':0}}

            for num,i in enumerate(soup.find_all('p')[:-2]):
                if 'http' not in i.text and num == 1:
                    break
                data['bio'] += i.text + '\n\n'

            if 'private' not in data['bio']:
                for num,i in enumerate(soup.find_all('script')[8:][:9]):
                    if 'var' in i.text:
                        break
                    data['data'][data['data'].keys()[num]] = i.text[:-3].split('(')[-1]

            self.send_image(get_file(data['profile_url']))
            self.send('%s\nFollowing: %s\nFollowers: %s\nPosts: %s' % (data['bio'][:-1], data['data']['following'], data['data']['followers'], data['data']['posts']))
        except AttributeError:
            self.send('invalid username: %s' % username)

    def quote(self, quote = 'hello world!'):

        link = 'http://shiroyasha.tech/?tools='
        if self.bcom == '@sgb_quote':
            link = 'https://wirayudaaditya.site/quotes/?module='
            xs = 'sgbquote'
        elif self.bcom == '@tanpakertas_quote':
            xs = 'tanpakertas_'
        elif self.bcom == '@rasa_quote':
            xs = 'rasauntukmu'
        elif self.bcom == '@img_quote':
            link = 'https://wirayudaaditya.site/quotes/?module='
            xs = 'autoquotemaker'

        self.br.open(link + xs)

        self.br.select_form(nr=0)
        self.br.form['quote'] = quote
        if self.bcom in ('@sgb_quote','@tanpakertas_quote','@img_quote'):
           self.br.form['copyright'] = self.name
        res = self.br.submit().read()

        soup = bs4.BeautifulSoup(res, 'html.parser')
        if self.bcom in ('@img_quote', '@sgb_quote'):
            open('zvBot.jpeg', 'wb').write(soup.find_all('a')[-1].img['src'].split(',')[1].decode('base64'))
        else:
            open('zvBot.jpeg', 'wb').write(soup.find_all('center')[1].img['src'].split(',')[1].decode('base64'))

        return True

    # --------------- other functions ------- #

    def upload_file(self,name):
        logger('uploading file')
        r =  requests.post('https://www.datafilehost.com/upload.php',
                           files={'upfile':open(name,'rb')} )

        return str(bs4.BeautifulSoup(r.text,'html.parser').find('tr').input['value'])

    def get_last_commands(self):
        _ = False
        self.br.open(self.url + '/messages/read')

        for i in self.br.links():
            if 'Lihat Pesan Sebelumnya' == i.text:
                break

            if _:
                 name = i.text.lower().split(' (')[0]
                 self.config['limit'][name] = 0
                 self.config['blacklist'][name] = False
                 self.config['botname'][name] = __BOTNAME__
                 self.config['last'][name] = 'unknow'
                 if arg.admin:
                     ADMIN.append(name)

            if 'Cari pesan' == i.text:
                _ = True

    def get_last_images(self):
        x = 1
        for i in glob.glob(arg.dir_cache+'/image_*.jpeg'):
            num =  int(i.split('/')[-1].split('_')[1][:-5]) + 1
            if num >= x:
                x = num
        return x

    def get_file_from_instagram(self, code):
        try:
            r = requests.get('https://www.instagram.com/p/'+code, params={'__a': 1}).json()
            media = r['graphql']['shortcode_media']
            if media['is_video']:
                self.send('sorry, i can\'t download other than images')
            else:
                if media.get('edge_sidecar_to_children', None):
                    self.send('downloading multiple images of this post')
                    for child_node in media['edge_sidecar_to_children']['edges']:
                        self.send_image(get_file(child_node['node']['display_url']), 'zvBot.jpeg')
                else:
                    self.send('downloading single image')
                    self.send_image(get_file(media['display_url']), 'zvBot.jpeg')
            sprt()
        except (KeyError, ValueError):
            self.send('invalid code: %s' % code)

    # ----------- send command ------------- #

    def send(self, temp):
        n = True
        if arg.botname and temp.split()[0] != 'download' or 'wait a minute' not in temp:
            temp += ('\n\n- via {0} | limit {1}/{2}'.format(
                self.config['botname'][self.name],
                self.config['limit'][self.name], arg.limit))

        for message in temp.split('<br>'):
            logger('sending message: %s' % message)
            self.br.select_form(nr=1)
            self.br.form['body'] = message.capitalize()
            self.br.submit()

            logger('result: success')

            if 'download' in message.lower() or 'wait a minute' in message.lower():
                n = False
            if 'example' in message.lower():
                n = True
        if n:
            sprt()

    def send_image(self, image, x = 'zvBot.jpeg'):
        if '_quote' in self.bcom:
            self.br.open(self.burl)
        logger('send pictures to the recipient')

        if arg.cache:
            logger('picture name: image_%s.jpeg' % self.image_numbers)

        self.br.select_form(nr=1)
        self.br.open(self.br.click(type = 'submit', nr = 2))
        self.br.select_form(nr=0)
        self.br.form.add_file(open(x), 'text/plain', x, nr=0)
        self.br.submit()
        logger('result: success')

        if image:
            if arg.cache:
                os.rename(str(x), 'image_%s.jpeg' % self.image_numbers)
                if arg.up_file:
                    self.send('hd image: ' + self.upload_file('image_%s.jpeg' % self.image_numbers))
                os.system('mv image_%s.jpeg %s' % (self.image_numbers, arg.dir_cache))
            else:
                os.remove(x)
            self.image_numbers +=1

    # ----------- Useless function --------- #

    def search_(self):
        data = {}
        logger('search for the latest chat history\n', 'DEBUG')
        self.br.open(self.url + '/messages/read')
        xD = False
        num = 1

        for i in self.br.links():
            if 'Lihat Pesan Sebelumnya' == i.text:
                break
            if xD:
                 print ('%s) %s' % (num, i.text.lower().split(' (')[0]))
                 data[num] = {'url': i.url, 'name': i.text.lower().split(' (')[0]}
                 num += 1
            if 'Cari pesan' == i.text:
                xD = True

        return data

    def select_(self):
        data = self.search_()
        final_ = []

        n = []
        user_ = raw_input('\nenter numbers [1-%s] : ' % len(data))
        for x in user_.split(','):
            if int(x) in range(len(data) + 1) and x not in n:
                final_.append(data[int(x)])
                n.append(x)

        sprt()
        logger('total selected : %s' % len(final_), 'DEBUG')
        sprt()

        return final_

    def delete_(self):
        res = self.select_()

        for i in res:
            logger('delete messages from %s' % i['name'])

            self.br.open(self.url + i['url'])
            self.br.select_form(nr=2)
            self.br.open(self.br.click(type = 'submit', nr = 1))
            self.br.open(self.url + self.br.find_link('Hapus').url)

        logger('finished all')

    # ----------- Browser Options ---------- #

    def setup(self):
        self.__ = False
        xd = os.uname()
        logger('build a virtual server (%s %s)' % (xd[0], xd[-1]), 'DEBUG')
        br = mechanize.Browser()
        self.cookie = cookielib.LWPCookieJar()
        if arg.cookie and not arg.own_bot:
            logger('use external cookies', 'DEBUG')
            self.cookie.load(arg.cookie)
            self.__ = True
        br.set_handle_robots(False)
        br.set_handle_equiv(True)
        br.set_handle_referer(True)
        br.set_handle_redirect(True)
        br.set_cookiejar(self.cookie)
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 5)
        br.addheaders = [('user-agent', arg.ua)]
        br.open(self.url)

        return br

    def login(self):
        logger('make server configuration', 'DEBUG')
        if not self.__ and arg.own_bot:
            self.br.select_form(nr=0)
            self.br.form['email'] = self.username
            self.br.form['pass'] = self.password
            self.br.submit()
        self.br.select_form(nr = 0)
        self.br.submit()

        if 'login' not in self.br.geturl():
            for i in self.br.links():
                if 'Keluar' in i.text:
                    name = i.text.replace('Keluar (', '')[:-1]

            logger('server is running (%s)' % name, 'DEBUG')
            logger('Press Ctrl-C to quit.', 'DEBUG')
            sprt()

            if arg.info:
                logger('settings\n')
                for num,i in enumerate(arg.__dict__):
                    print ('arg.{0:<20} {1}'.format(i+':', arg.__dict__[i]))
                print ('') # new line
                sprt()

            if arg.save_cookie and not arg.cookie:
                res = name.replace(' ', '_') + '.cj'
                self.cookie.save(res)
                logger('save the cookie in %s' % res, 'DEBUG')
                sprt()

            if not os.path.isdir(arg.dir_cache):
                logger('create new cache directory', 'DEBUG')
                os.mkdir(arg.dir_cache)
                sprt()

            self.get_last_commands()

            if not arg.delete_chat:
                while True:
                    self.run_a_bot()
                    logger('refresh', 'DEBUG')
                    sprt()
            else:
                self.delete_()
                sprt()
                exit()
        else:
            logger('failed to build server', 'ERROR')
            sprt()

def logger(mess, level='INFO', ex=False, sprt=False):

    mess = mess.lower().encode('utf8')

    code = {'INFO' : '38;5;2',
            'DEBUG': '38;5;11',
            'ERROR': 31,
            'WARNING': 33,
            'CRITICAL':41}

    if arg.underline:
        mess = mess.replace(arg.underline, '\x1b[%sm%s\x1b[0m' % ('4;32' if arg.color else '4' , arg.underline))

    message = '{0:<9}{1}'.format(level + ' ' if not sprt else ('-'*9), mess[:-9] if sprt else mess)
    print ('\r{1}{0}'.format(message.replace(level, '\x1b[%sm%s\x1b[0m' % (code[level], level)) if arg.color else message, time.strftime('%H:%M:%S ') if arg.time and not sprt else ''))

    if arg.log:
        if not os.path.isfile(arg.log):
            open(arg.log, 'a').write('# create a daily report | %s v%s\n# %s\n' % (__BOTNAME__, __VERSION__, time.strftime('%c')))

        with open(arg.log, 'a') as f:

            if arg.underline:
                message = message.replace('\x1b[{0}m{1}\x1b[0m'.format(
                        '4;32' if arg.color else '4' , arg.underline
                    ),
                    arg.underline
                )

            f.write('\n{0}{1}{2}'.format(
                time.strftime('%H:%M:%S ') if not sprt else '',
                message.replace('-'*arg.long_separator, '-'*30),
                '' if not ex else '\n')
             )

    if ex:
        exit()

def main():
    global __BOTNAME__, __LICENSE__, cookie, arg, user, pwd

    parse = argparse.ArgumentParser(usage='python2 zvbot [--run] (--cookie PATH | --account USER:PASS) [options]', description='description:\n  create a virtual server for Bot Messenger Facebook with a personal account', formatter_class=argparse.RawTextHelpFormatter, epilog='author:\n  zevtyardt <xnver404@gmail.com>\n ')
    parse.add_argument('-r', '--run', dest='run', action='store_true', help='run the server')

    value = parse.add_argument_group('value arguments')
    value.add_argument('--account', metavar='USER:PASS', dest='own_bot', help='create your own bot account')
    value.add_argument('--botname', metavar='NAME', dest='default_botname', help='rename your own bot, default %s' % __BOTNAME__)
    value.add_argument('--blacklist', metavar='NAME', dest='add_blacklist_user', action='append', help='add a new blacklist user by name')
    value.add_argument('--cookie', metavar='PATH', dest='cookie', help='use our own cookie')
    value.add_argument('--dirname', metavar='DIRNAME', dest='dir_cache', action='append', help='name of directory is used to store images', default='cache_image')
    value.add_argument('--ignore-cmd', metavar='COMMAND', dest='ignore_command', help='adding a prohibited command', choices=COMMANDS)
    value.add_argument('--limit', metavar='INT', dest='limit', help='limit of request from the user, default 4', type=int, default=4)
    value.add_argument('--logfile', metavar='PATH', dest='log', help='save all logs into the file')
    value.add_argument('--long-sprt',metavar='INT',dest='long_separator', help='long separating each session, min 20 max 30', type=int, default=30, choices=range(20,31))
    value.add_argument('--new-admin', metavar='NAME', dest='add_admin', action='append', help='add new admin by name')
    value.add_argument('--paragraph', metavar='INT', dest='paragraph', help='paragraph number on wikipedia, max 6', type=int, default=2)
    value.add_argument('--refresh', metavar='INT', dest='refresh', help='how many times the program refreshes the page', type=int, default=8)
    value.add_argument('--underline', metavar='WORD', dest='underline', help='underline the specific word in all logs')
    value.add_argument('--user-agent', metavar='UA', dest='ua', help='specify a custom user agent', default='Mozilla/5.0 (Linux; Android 7.0; 5060 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.109 Mobile Safari/537.36')

    choice = parse.add_argument_group('choice arguments')
    choice.add_argument('--all-admin', dest='admin', action='store_true', help='everyone can use admin command')
    choice.add_argument('--clear-screen', dest='clear_screen', action='store_true', help='clean the screen before running the bot')
    choice.add_argument('--color', dest='color', action='store_true', help='show colors in all logs')
    choice.add_argument('--delete-chat', dest='delete_chat', action='store_true', help='delete the latest chat history')
    choice.add_argument('--delete-logfile', dest='delete_logfile', action='store_true', help='delete old logs and create new logs')
    choice.add_argument('--ignore-botname', dest='botname', action='store_false', help='don\'t add the bot name to the final result')
    choice.add_argument('--ignore-cache', dest='cache', action='store_false', help='does not store all images from the sender\'s request')
    choice.add_argument('--ignore-group', dest='group_chat', action='store_true', help='ignore existing chat groups')
    choice.add_argument('-i', '--info', dest='info', action='store_true', help='showing any information')
    choice.add_argument('-l', '--license', dest='license', action='store_true', help='print license and exit.')
    choice.add_argument('-m', '--more', dest='commands', action='store_true', help='print all the available commands and exit')
    choice.add_argument('--save-cookie', action='store_true', dest='save_cookie', help='save session cookies into the file')
    choice.add_argument('--show-time', dest='time', action='store_true', help='show time in all logs')
    choice.add_argument('-v', '--version', dest='version', action='store_true', help='print version information and exit')
    choice.add_argument('-u', '--upload', dest='up_file', action='store_true', help='enable file upload. program will send hd image links')

    arg = parse.parse_args()

    if arg.version:
        exit ('v%s' % __VERSION__)

    if arg.license:
        exit (__LICENSE__)

    if arg.commands:
        exit ('\n' + ('\n'.join(HELP_TEXT)).replace('<br>', '\n') + '\n')

    if arg.default_botname:
        __BOTNAME__ = arg.default_botname

    if arg.ignore_command:
        for i in arg.ignore_command:
            if i.lower() != 'help':
                cmd = '@'+ i.lower() if i[0] != '@' else i.lower()
                BLACKLIST_COMMAND.append(cmd)

    if arg.add_admin:
        for i in arg.add_admin:
            ADMIN.append(i.lower())

    if arg.add_blacklist_user:
        for i in arg.add_blacklist_user:
            BLACKLIST.append(i.lower())

    if arg.run and arg.cookie and not arg.own_bot or arg.run and not arg.cookie and arg.own_bot:

        if arg.delete_logfile and arg.log:
            if os.path.isfile(arg.log):
                os.remove(arg.log)

        if arg.clear_screen:
            print('\x1bc')

        try:
            logger('Facebook Messenger bot | created by zevtyardt', 'DEBUG')
            user, pwd = arg.own_bot.split(':') if arg.own_bot else ('', '')

            start_bot(user, pwd)

        except KeyboardInterrupt:
            logger('user interrupt: stopped bot\n'+'-'*arg.long_separator, 'ERROR', ex=True)
        except Exception as e:
            logger('%s\n%s' % (e, '-'*arg.long_separator), 'CRITICAL', ex=True)

    else:
        print ('\n' + ( __BOTNAME__ + '\x1b[0m v' + __VERSION__ + '\n').center(77) )
        parse.print_help()

if __name__ == '__main__':
    main()

