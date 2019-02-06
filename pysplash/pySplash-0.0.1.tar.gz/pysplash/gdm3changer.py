import ntpath
import subprocess
import tempfile

configCssFile = "/etc/alternatives/gdm3.css"
backgroundFolder = "/usr/share/backgrounds/"


def changeLoginWallpaper(wallpaperFile):
    subprocess.run(["sudo", "/bin/cp", "-rf", wallpaperFile, backgroundFolder])

    targetFile = ntpath.join(backgroundFolder, ntpath.basename(wallpaperFile))
    cssData = open(configCssFile, 'r').read()
    found = False
    finalCssData = ""

    for line in cssData.split('\n'):
        if "#lockDialogGroup" in line:
            finalCssData += '#lockDialogGroup {\n'
            finalCssData += '  background: url(file://%s);\n' % targetFile
            finalCssData += "  background-repeat: no-repeat;\n"
            finalCssData += "  background-size: cover;\n"
            finalCssData += "  background-position: center;\n"
            finalCssData += "  }\n"
            found = True
        elif found and "}" in line:
            found = False
        elif not found:
            finalCssData += line + '\n'

    with tempfile.TemporaryDirectory() as dirpath:
        tempConf = dirpath + "/config.conf"
        file_handler = open(tempConf, 'w')
        file_handler.write(finalCssData)
        file_handler.close()

        subprocess.run(["sudo", "/bin/cp", "-rf", tempConf, configCssFile])

    print("You will need to restart the computer for the login screen background changes to become visible.")
