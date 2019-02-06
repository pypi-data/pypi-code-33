import ntpath
import os
import sys
import urllib.request
import subprocess
import ctypes
import screeninfo
from pysplash import gdm3changer, lightdmchanger
import pathlib

name = "pySplash"
wallpaperFile = str(pathlib.Path.home()) + "/.pySplash/wallpaper.jpeg"


def downloadWallpaper(param):
    urllib.request.urlretrieve(param, wallpaperFile)


def detectDistro():
    output = subprocess.getoutput("lsb_release -a").lower()

    if "ubuntu" in output:
        return "ubuntu"
    elif "debian" in output:
        return "debian"
    elif "manjaro" in output:
        return "manjaro"


def detectDisplayManager(distro):
    dm = "unknown"

    if distro == "ubuntu" or distro == "debian":
        dm = open("/etc/X11/default-display-manager", 'r').read()
    elif distro == "redhat" or distro == "fedora":
        dm = open("/etc/sysconfig/desktop", 'r').read()
    elif distro == "redhat" or distro == "fedora":
        dm = open("/etc/sysconfig/displaymanager", 'r').read()
    elif distro == "manjaro":
        cout = subprocess.getoutput("cat /etc/systemd/system/display-manager.service | grep '/usr/bin'")
        dm = cout.split("/usr/bin/")[1]

    return dm.lower()


def changeLoginWallpaper():
    distro = detectDistro()
    dm = detectDisplayManager(distro)

    if "gdm3" in dm:
        gdm3changer.changeLoginWallpaper(wallpaperFile)
    elif "lightdm" in dm:
        lightdmchanger.changeLoginWallpaper(wallpaperFile)


def changeWallpaperLinux():
    desktop = str(os.environ['XDG_CURRENT_DESKTOP']).lower()
    if desktop == "gnome" or desktop == "x-cinnamon":
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://" + wallpaperFile])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-options", "wallpaper"])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.screensaver", "picture-uri", "file://" + wallpaperFile])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.screensaver", "picture-options", "wallpaper"])
    changeLoginWallpaper()


def changeWallpaperWindows():
    ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaperFile, 3)


dirname = ntpath.dirname(wallpaperFile)
os.makedirs(dirname, exist_ok=True)

wallpaperUrl = "https://source.unsplash.com/1920x1080/?wallpaper"


def buildWallpaperUrl(argv):
    reso = str(screeninfo.get_monitors()[0].width) + "x" + str(screeninfo.get_monitors()[0].height)
    return "https://source.unsplash.com/" + reso + "/?" + argv


if len(sys.argv) > 1:
    argv = str(sys.argv[1])
    if argv.startswith("http"):
        wallpaperUrl = argv
    else:
        wallpaperUrl = buildWallpaperUrl(argv)

downloadWallpaper(wallpaperUrl)

if os.name == "Linux" or os.name == "posix":
    changeWallpaperLinux()
elif os.name == "Windows":
    changeWallpaperWindows()
