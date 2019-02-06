import subprocess
import ntpath
import tempfile

backgroundFolder = "/usr/share/backgrounds/"
lightDmConfigFile = "/etc/lightdm/slick-greeter.conf"


def changeLoginWallpaper(wallpaperFile):
    subprocess.run(["sudo", "/bin/cp", "-rf", wallpaperFile, backgroundFolder])
    configFileData = open(lightDmConfigFile, 'r').read()

    targetFile = ntpath.join(backgroundFolder, ntpath.basename(wallpaperFile))

    outData = ""
    for line in configFileData.split('\n'):
        if "background=" in line:
            outData += "background=" + targetFile + "\n"
        else:
            outData += line + "\n"

    with tempfile.TemporaryDirectory() as dirpath:
        tempConf = dirpath + "/config.conf"
        file_handler = open(tempConf, 'w')
        file_handler.write(outData)
        file_handler.close()

        subprocess.run(["sudo", "/bin/cp", "-rf", tempConf, lightDmConfigFile])
