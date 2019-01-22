import re
from requests import get
name = "loopers"

def link_opener(link):
    print("Opening link: {}".format(link))
    try:
        header = get(link)
    except:
        try:
            link2 = 'http://www.' + link
            header = get(link2)
        except:
            try:
                link3 = 'https://www.' + link
                header = get(link3)
            except:
                pass

    return header.content

def converter(header):
    from bs4 import BeautifulSoup
    try:
        parsed_html = BeautifulSoup(header,
                                    features= 'html.parser')
        return parsed_html
    except Exception as err:
        print(err)

def link_generator(parsed_html):
    list_link = []
    link1 = []
    for links in parsed_html.findAll('a'):
        if 'href' in links.attrs:
            list_link.append(links.attrs['href'])
    list_link = set(list_link)
    for a in list_link:
        if a.startswith('https://') or a.startswith('http://'):
            link1.append(a)
        elif a.startswith('/'):
            link1.append(a)
    return set(link1)


def Regex(parsed_html):
    email_Regex = re.compile(r'''(
                [a-zA-Z0-9._%+-]+
                @
                [a-zA-Z0-9.-]+
                (\.[a-zA-Z]{2,4})
                )''',re.VERBOSE)
    try:
        text = str(parsed_html)
    except Exception as err:
        print(" {} \nFailed to read page!".format(err))
    matches = []
    for groups in email_Regex.findall(text):
        matches.append(groups[0])
    matches = set(matches)
    for emails in matches:
        print(emails)
    if len(matches) < 1:
        print("No email address found!!")


    return matches



def loop(link, iter):
    try:
        html = link_opener(link)
        if iter == True:
            all_emails = Regex(html)
            print('[**] Generating links...')
            try:
                parsed_html = converter(html)
                links = link_generator(parsed_html)
                print('[+] Links generated \n {}'.format(links))
            except:
                print('[-] Beautiful soup not installed')
            return all_emails
        else:
            all_emails = Regex(html)
            print('[-] Not generating links, Set iter to True to generate links')
            return all_emails
            pass

    except:
        print("[-] Error 404")
