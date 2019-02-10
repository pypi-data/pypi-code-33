import urllib

def download_menu(url):
    file_name = "menu.pdf"
    u = urllib.request.urlopen(url)
    f = open ("menus/" + file_name, 'wb')
    f.write(u.read())
    f.close()
    return file_name
