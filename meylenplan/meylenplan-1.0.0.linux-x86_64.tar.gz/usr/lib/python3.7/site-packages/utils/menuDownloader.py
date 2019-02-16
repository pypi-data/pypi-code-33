import urllib

def download_menu(url):
    menu_pdf = "/tmp/menu.pdf"
    u = urllib.request.urlopen(url)
    f = open (menu_pdf, 'wb')
    f.write(u.read())
    f.close()
    return menu_pdf
