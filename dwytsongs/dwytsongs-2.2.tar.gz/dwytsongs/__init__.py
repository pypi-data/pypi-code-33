#!/usr/bin/python3
import os
import pafy
import ffmpeg
import spotipy
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import spotipy.oauth2 as oauth2
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
from collections import OrderedDict
localdir = os.getcwd()
class TrackNotFound(Exception):
      def __init__(self, message):
          super().__init__(message)
class InvalidLink(Exception):
      def __init__(self, message):
          super().__init__(message)
class QuotaExceeded(Exception):
      def __init__(self, message):
          super().__init__(message)
def generate_token():
    return oauth2.SpotifyClientCredentials(client_id="4fe3fecfe5334023a1472516cc99d805", client_secret="0f02b7c483c04257984695007a4a8d5c").get_access_token()
spo = spotipy.Spotify(auth=generate_token())
def request(url, control=False):
    try:
       thing = requests.get(url)
    except:
       thing = requests.get(url)
    if control == True:
     try:
        if thing.json()['error']['message'] == "no data":
         raise TrackNotFound("Track not found :(")
     except KeyError:
        pass
     try:
        if thing.json()['error']['message'] == "Quota limit exceeded":
         raise QuotaExceeded("Too much requests limit yourself")
     except KeyError:
        pass
     try:
        if thing.json()['error']:
         raise InvalidLink("Invalid link ;)")
     except KeyError:
        pass
    return thing
def write_tags(song, data):
    tag = EasyID3(song)
    tag.delete()
    tag['artist'] = data['artist']
    tag['title'] = data['music']
    tag['date'] = data['year']
    tag['album'] = data['album']
    tag['tracknumber'] = data['tracknum']
    tag['discnumber'] = data['discnum']
    tag['albumartist'] = data['ar_album']
    tag['genre'] = data['genre']
    tag.save(v2_version=3)
    audio = ID3(song)
    audio['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u"Cover", data=data['image'])
    audio.save()
def download_trackdee(URL, output=localdir + "/Songs/", check=True):
    datas = {}
    array = []
    if "?utm" in URL:
     URL, a = URL.split("?utm")
    URL1 = "https://www.deezer.com/track/" + URL.split("/")[-1]
    URL2 = "https://api.deezer.com/track/" + URL.split("/")[-1]
    url = request(URL2, True).json()
    url1 = request("http://api.deezer.com/album/" + str(url['album']['id']), True).json()
    try:
       image = url['album']['cover_xl'].replace("1000x1000", "1200x1200")
    except AttributeError:
       image = request(URL1).text
       image = BeautifulSoup(image, "html.parser").find("img", class_="img_main").get("src").replace("120x120", "1200x1200")
    image = request(image).content
    if len(image) == 13:
     image = request("https://e-cdns-images.dzcdn.net/images/cover/1200x1200-000000-80-0-0.jpg").content
    datas['image'] = image
    datas['music'] = url['title']
    for a in url['contributors']:
        array.append(a['name'])
    if len(array) > 1:
     for a in array:
         for b in array:
             if a in b and a != b:
                array.remove(b)
     while len(", ".join(array)) + len(datas['music']) >= 240:
         del array[-1]
     if len(array) == 0:
      array.append("Unknown")
    datas['artist'] = ", ".join(OrderedDict.fromkeys(array))
    datas['album'] = url1['title']
    datas['tracknum'] = str(url['track_position'])
    datas['discnum'] = str(url['disk_number'])
    datas['year'] = url['release_date']
    song = datas['music'] + " - " + datas['artist']
    datas['genre'] = []
    try:
       for a in url1['genres']['data']:
           datas['genre'].append(a['name'])
    except KeyError:
       pass
    datas['ar_album'] = url1['artist']['name']
    dir = str(output) + "/" + datas['artist'].replace("/", "").replace("$", "S") + "/"
    try:
       os.makedirs(dir)
    except FileExistsError:
       pass
    name = datas['artist'].replace("/", "").replace("$", "S") + " " + datas['music'].replace("/", "").replace("$", "S") + ".mp3"
    url = request("https://www.youtube.com/results?search_query=" + datas['music'].replace("#", "") + "+" + datas['artist'].replace("#", "")).text
    bs = BeautifulSoup(url, "html.parser")
    for topicplus in bs.find_all("a"):
        if len(topicplus.get("href")) == 20:
         down = topicplus.get("href")
         break
    try:
       if pafy.new("https://www.youtube.com" + down).length > 700:
        raise TrackNotFound("Track not found: " + song)
    except OSError:
       raise TrackNotFound("Error cannot determine the length of the video")
    if os.path.isfile(dir + name):
     if check == False:
      return dir + name
     ans = input("Song already exist do you want to redownload it?(y or n):")
     if not ans == "y":
      return
    print("\nDownloading:" + song)
    file = URL.split("/")[-1]
    os.system('youtube-dl -q https://www.youtube.com' + down + ' -f best -o "' + dir + file + '"')
    try:
       ffmpeg.input(dir + file).output(dir + name).run(overwrite_output=True, quiet=True)
    except ffmpeg._run.Error as a:
       os.remove(dir + file)
       raise TrackNotFound("Error while downloading: " + song)
    os.remove(dir + file)
    write_tags(dir + name, datas)
    return dir + name
def download_albumdee(URL, output=localdir + "/Songs/", check=True):
    datas = {}
    array = []
    music = []
    artist = []
    tracknum = []
    discnum = []
    urls = []
    names = []
    if "?utm" in URL:
     URL, a = URL.split("?utm")
    URL1 = "https://www.deezer.com/album/" + URL.split("/")[-1]
    URL2 = "https://api.deezer.com/album/" + URL.split("/")[-1]
    url = request(URL2, True).json()
    try:
       image = url['cover_xl'].replace("1000x1000", "1200x1200")
    except AttributeError:
       image = request(URL1).text
       image = BeautifulSoup(image, "html.parser").find("img", class_="img_main").get("src").replace("120x120", "1200x1200")
    image = request(image).content
    if len(image) == 13:
     image = request("https://e-cdns-images.dzcdn.net/images/cover/1200x1200-000000-80-0-0.jpg").content
    datas['image'] = image
    for a in url['tracks']['data']:
        del array[:]
        music.append(a['title'])
        urls.append(a['link'])
        ur = request("https://api.deezer.com/track/" + str(a['id']), True).json()
        tracknum.append(str(ur['track_position']))
        discnum.append(str(ur['disk_number']))
        for a in ur['contributors']:
            array.append(a['name'])
        if len(array) > 1:
         for a in array:
             for b in array:
                 if a in b and a != b:
                  array.remove(b)
         while len(", ".join(array)) + len(max(music)) >= 240:
             del array[-1]
         if len(array) == 0:
          array.append("Unknown")
    artist.append(", ".join(OrderedDict.fromkeys(array)))
    datas['album'] = url['title']
    datas['year'] = url['release_date']
    datas['genre'] = []
    try:
       for a in url['genres']['data']:
           datas['genre'].append(a['name'])
    except KeyError:
       pass
    datas['ar_album'] = url['artist']['name']
    dir = str(output) + "/" + datas['album'].replace("/", "").replace("$", "S") + "/"
    try:
       os.makedirs(dir)
    except FileExistsError:
       pass
    for a in tqdm(range(len(music))):
        name = artist[a].replace("/", "").replace("$", "S") + " " + music[a].replace("/", "").replace("$", "S") + ".mp3"
        names.append(dir + name)
        url = request("https://www.youtube.com/results?search_query=" + music[a].replace("#", "") + "+" + artist[a].replace("#", "")).text
        bs = BeautifulSoup(url, "html.parser")
        for topicplus in bs.find_all("a"):
            if len(topicplus.get("href")) == 20:
             down = topicplus.get("href")
             break
        try:
           if pafy.new("https://www.youtube.com" + down).length > 700:
            print("Track not found: " + music[a] + "  " + artist[a])
            continue
        except OSError:
           print("Error cannot determine the length of the video")
           continue    
        if os.path.isfile(dir + name):
         if check == False:
          continue
         print(dir + name)
         ans = input("Song already exist do you want to redownload it?(y or n):")
         if not ans == "y":
          return
        file = urls[a].split("/")[-1]
        os.system('youtube-dl -q https://www.youtube.com' + down + ' -f best -o "' + dir + file + '"')
        try:
           ffmpeg.input(dir + file).output(dir + name).run(overwrite_output=True, quiet=True)
        except ffmpeg._run.Error:
           os.remove(dir + file)
           print("\nTrack not found: " + music[a] + " - " + artist[a])
           continue
        os.remove(dir + file)
        datas['artist'] = artist[a]
        datas['music'] = music[a]
        datas['tracknum'] = tracknum[a]
        datas['discnum'] = discnum[a]
        write_tags(names[a], datas)
    return names
def download_playlistdee(URL, output=localdir + "/Songs/", check=True):
    array = []
    if "?utm" in URL:
     URL, a = URL.split("?utm")
    url = request("https://api.deezer.com/playlist/" + URL.split("/")[-1], True).json()
    for a in url['tracks']['data']:
        try:
           array.append(download_trackdee(a['link'], output, check, quality, recursive))
        except TrackNotFound:
           print("\nTrack not found " + a['title'])
           array.append(output + a['title'] + "/" + a['title'])
    return array
def download_trackspo(URL, output=localdir + "/Songs/", check=True):
    global spo
    datas = {}
    array = []
    if "?" in URL:
     URL,a = URL.split("?")
    try:
       url = spo.track(URL)
    except Exception as a:
       if not "The access token expired" in str(a):
        raise InvalidLink("Invalid link ;)")
       spo = spotipy.Spotify(auth=generate_token())
       url = spo.track(URL)
    datas['music'] = url['name']
    for a in range(20):
        try:
           array.append(url['artists'][a]['name'])
        except IndexError:
           datas['artist'] = ", ".join(array)
           del array[:]
           break
    datas['album'] = url['album']['name']
    datas['image'] = url['album']['images'][0]['url']
    datas['tracknum'] = str(url['track_number'])
    datas['discnum'] = str(url['disc_number'])
    datas['year'] = url['album']['release_date']
    song = datas['music'] + " - " + datas['artist']
    datas['genre'] = []
    datas['ar_album'] = ""
    try:
       image = url['album']['images'][0]['url']
    except IndexError:
       image = "https://e-cdns-images.dzcdn.net/images/cover/1200x1200-000000-80-0-0.jpg"
    datas['image'] = request(image).content
    dir = str(output) + "/" + datas['artist'].replace("/", "").replace("$", "S") + "/"
    try:
       os.makedirs(dir)
    except FileExistsError:
       pass
    name = datas['artist'].replace("/", "").replace("$", "S") + " " + datas['music'].replace("/", "").replace("$", "S") + ".mp3"
    url = request("https://www.youtube.com/results?search_query=" + datas['music'].replace("#", "") + "+" + datas['artist'].replace("#", "")).text
    bs = BeautifulSoup(url, "html.parser")
    for topicplus in bs.find_all("a"):
        if len(topicplus.get("href")) == 20:
         down = topicplus.get("href")
         break
    try:
       if pafy.new("https://www.youtube.com" + down).length > 700:
        raise TrackNotFound("Track not found: " + song)
    except OSError:
       raise TrackNotFound("Error cannot determine the length of the video")
    if os.path.isfile(dir + name):
     if check == False:
      return dir + name
     ans = input("Song already exist do you want to redownload it?(y or n):")
     if not ans == "y":
      return
    print("\nDownloading:" + song)
    file = URL.split("/")[-1]
    os.system('youtube-dl -q https://www.youtube.com' + down + ' -f best -o "' + dir + file + '"')
    try:
       ffmpeg.input(dir + file).output(dir + name).run(overwrite_output=True, quiet=True)
    except ffmpeg._run.Error as a:
       os.remove(dir + file)
       raise TrackNotFound("Error while downloading: " + song)
    os.remove(dir + file)
    write_tags(dir + name, datas)
    return dir + name
def download_albumspo(URL, output=localdir + "/Songs/", check=True):
    global spo
    datas = {}
    array = []
    music = []
    artist = []
    tracknum = []
    discnum = []
    urls = []
    names = []
    if "?" in URL:
     URL,a = URL.split("?")
    try:
       tracks = spo.album(URL)
    except Exception as a:
       if not "The access token expired" in str(a):
        raise InvalidLink("Invalid link ;)")
       spo = spotipy.Spotify(auth=generate_token())
       tracks = spo.album(URL)
    datas['album'] = tracks['name']
    datas['ar_album'] = []
    datas['genre'] = []
    for track in tracks['tracks']['items']:
        music.append(track['name'])
        tracknum.append(str(track['track_number']))
        discnum.append(str(track['disc_number']))
        urls.append(track['external_urls']['spotify'])
    for artists in tracks['tracks']['items']:
        for a in range(20):
            try:
               array.append(artists['artists'][a]['name'])
            except IndexError:
               artist.append(", ".join(array))
               del array[:]
               break
    datas['year'] = tracks['release_date']
    try:
       image = tracks['images'][0]['url']
    except IndexError:
       image = "https://e-cdns-images.dzcdn.net/images/cover/1200x1200-000000-80-0-0.jpg"
    datas['image'] = request(image).content
    if tracks['total_tracks'] != 50:
     for a in range(tracks['total_tracks'] // 50):
         try:
            tracks = spo.next(tracks['tracks'])
         except:
            token = generate_token()
            spo = spotipy.Spotify(auth=token)
            tracks = spo.next(tracks)['items']
         for track in tracks['items']:
             music.append(track['name'])
             tracknum.append(str(track['track_number']))
             discnum.append(str(track['disc_number']))
             urls.append(track['external_urls']['spotify'])
         for artists in tracks['items']:
             for a in range(20):
                 try:
                    array.append(artists['artists'][a]['name'])
                 except IndexError:
                    artist.append(", ".join(array))
                    del array[:]
                    break
    dir = str(output) + "/" + datas['album'].replace("/", "").replace("$", "S") + "/"
    try:
       os.makedirs(dir)
    except FileExistsError:
       pass
    for a in tqdm(range(len(music))):
        name = artist[a].replace("/", "").replace("$", "S") + " " + music[a].replace("/", "").replace("$", "S") + ".mp3"
        names.append(dir + name)
        url = requests.get("https://www.youtube.com/results?search_query=" + music[a].replace("#", "") + "+" + artist[a].replace("#", ""))
        bs = BeautifulSoup(url.text, "html.parser")
        for topicplus in bs.find_all("a"):
            if len(topicplus.get("href")) == 20:
             down = topicplus.get("href") 
             break
        try:
           if pafy.new("https://www.youtube.com" + down).length > 700:
            print("Track not found: " + music[a] + "  " + artist[a])
            continue
        except OSError:
           print("Error cannot determine the length of the video")
           continue    
        if os.path.isfile(dir + name):
         if check == False:
          continue
         print(dir + name)
         ans = input("Song already exist do you want to redownload it?(y or n):")
         if not ans == "y":
          return
        file = urls[a].split("/")[-1]
        os.system('youtube-dl -q https://www.youtube.com' + down + ' -f best -o "' + dir + file + '"')
        try:
           ffmpeg.input(dir + file).output(dir + name).run(overwrite_output=True, quiet=True)
        except ffmpeg._run.Error:
           os.remove(dir + file)
           print("\nTrack not found: " + music[a] + " - " + artist[a])
           continue
        os.remove(dir + file)
        datas['artist'] = artist[a]
        datas['music'] = music[a]
        datas['tracknum'] = tracknum[a]
        datas['discnum'] = discnum[a]
        write_tags(names[a], datas)
    return names
def download_playlistspo(URL, output=localdir + "/Songs/", check=True):
    global spo
    array = []
    if "?" in URL:
     URL,a = URL.split("?")
    URL = URL.split("/")
    try:
       tracks = spo.user_playlist_tracks(URL[-3], playlist_id=URL[-1])
    except Exception as a:
       if not "The access token expired" in str(a):
        raise InvalidLink("Invalid link ;)")
       spo = spotipy.Spotify(auth=generate_token())
       tracks = spo.user_playlist_tracks(URL[-3], playlist_id=URL[-1])
    for a in tracks['items']:
        try:
           array.append(download_trackspo(a['track']['external_urls']['spotify'], output, check, quality, recursive))
        except TrackNotFound:
           print("\nTrack not found " + a['track']['name'])
           array.append(output + a['track']['name'] + "/" + a['track']['name'])
    if tracks['total'] != 100:
     for a in range(tracks['total'] // 100):
         try:
            tracks = spo.next(tracks)
         except:
            spo = spotipy.Spotify(auth=generate_token())
            tracks = spo.next(tracks)
         for a in tracks['items']:
             try:
                array.append(download_trackspo(a['track']['external_urls']['spotify'], output, check, quality, recursive))
             except:
                print("\nTrack not found " + a['track']['name'])
                array.append(output + a['track']['name'] + "/" + a['track']['name'])
    return array
def download_name(artist, song, output=localdir + "/Songs/", check=True):
    global spo
    try:
       search = spo.search(q="track:" + song + " artist:" + artist)
    except:
       token = generate_token()
       spo = spotipy.Spotify(auth=token)
       search = spo.search(q="track:" + song + " artist:" + artist)
    try:
       return download_trackspo(search['tracks']['items'][0]['external_urls']['spotify'], output, check)
    except:
       raise TrackNotFound("Track not found: " + song + " - " + artist)