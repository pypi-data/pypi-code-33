import sys
from webbrowser import open
import requests
from time import sleep


def stalker(url, music, sleep_seconds=2):
    first = requests.get(url).content
    while 1:
        current = requests.get(url).content
        if current != first:
            break
        sleep(sleep_seconds)

    open(music)
    print("RESULTS")


if __name__ == "__main__":
    music = "https://youtu.be/9bZkp7q19f0?t=68"
    url = sys.argv[1]
    print(sys.argv)
    if len(sys.argv) > 2:
        music = sys.argv[2]

    stalker(url, music)
