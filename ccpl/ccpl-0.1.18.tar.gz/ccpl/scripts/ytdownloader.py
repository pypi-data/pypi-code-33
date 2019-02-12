#!/usr/bin/env python
# coding: utf-8

# In[7]:


from ccpl.console import printc, clear
from bs4 import BeautifulSoup
import requests
from pytube import YouTube


# In[12]:


def getPlaylistLinks(url):
    sourceCode = requests.get(url).text
    soup = BeautifulSoup(sourceCode, 'html.parser')
    domain = 'https://www.youtube.com'
    linklist = []
    for link in soup .find_all("a", {"dir": "ltr"}):
        href = link.get("href")
        if href.startswith('/watch?'):
            linklist.append(domain + href)
    return linklist


# In[ ]:


printc("Please input playlist link:")
playlink = input(">> ")
clear()

# In[ ]:

while True:
    printc("Download as video, or as sound? (v/s)")
    downloadtype = input(">> ")
    if downloadtype == 's' or downloadtype == "S":
        downloadtype = 's'
        break
    elif downloadtype == 'v' or downloadtype == 'V':
        downloadtype = 'v'
        break
    else:
        printc("Not a vaild option!")
        continue

# In[14]:


urllist = getPlaylistLinks(playlink)


# In[15]:

croplist = [item[:43] for item in urllist]

videolist = []

[videolist.append(YouTube(i)) for i in urllist]    #Metoda bez autyzmu

print('Video setup done...')

for c, v in enumerate(videolist):
    if downloadtype == 'v':
        v.streams.first().download()
    else:
        v.streams.filter(only_audio=True).first().download()
    print("Video {0} downloaded!".format(c))

print('All videos downloaded!')

