""" 
Name: pytrol
Description: easy to use Linux process managment in python
Version: 1.0
Author: daehruoydeef (Oskar)
License: MIT
Date: 9.2.2019
"""

import subprocess
import os


def start(process):
    """ Description
        this will not 
        :type process: String
        :param process: process to start
        :rtype: true or false
    """
    try:
        os.spawnlp(os.P_NOWAIT, process, "&")
    except:
        print("Could not start: ", process)
        return False


def startAndWait(process):
    """ Description
        :type process: String
        :param process: process to start and wait for it to finish
        :rtype: output or false
    """

    try:
        return subprocess.check_output([process])
    except:
        print("Could not start: ", process)
        return False


def restart(process):
    """ Description
        :type process: String
        :param process: Process to kill and then restart

        :rtype:
    """
    if (isRunning(process)):
        kill(process)
        start(process)
    else:
        print(process + " is not running and cannot be restarted")


def restartAndWait(process):
    """ Description
        :type process: String
        :param process: Process to kill and then restart and wait for it to finish

        :rtype:
    """
    kill(process)
    startAndWait(process)


def kill(process):
    """ Description
        :type process: String
        :param process: process to be killed
    """
    subprocess.run(["pkill", process])


def isRunning(process):
    """ Description
        :type process: String
        :param process: check if the process is running
        :rtype: True or False
    """
    try:
        p = subprocess.check_output(["pgrep", "-x",  process])
        result = p.decode("utf-8").rstrip()
        if (type(result) == str):
            return True
    except:
        return False


def playSound(sound):
    """ Description - only works with pulseaudio.
        :type sound: String (Path)
        :param sound: Sound path to be played audiofile from

        :rtype: I hope you will hear your Sound ;)
    """
    subprocess.run(["paplay", sound])


def getUser():
    """ Description
        Asks the System for the system user
        :rtype: User who called the script
    """
    return os.getlogin()


def getUserPath():
    """ Description
        Asks the System for the system user
        :rtype: path to current User
    """
    return "/home/"+os.getlogin()+"/"


def notify(message):
    """ Description
    :type message: String
    :param message: Message to by displayed as a native Systemnotification
    """
    subprocess.run(["notify-send", message])
