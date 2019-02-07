import os

from PyQt5.QtCore import *

translator = None


def changeLanguage(language: str = ""):
    global translator

    app = QCoreApplication.instance()
    if translator is not None:
        app.removeTranslator(translator)

    if language == "Deutsch":
        language = "de"

    if language != "":
        currentDir = os.path.dirname(__file__)
        translator = QTranslator()
        translator.load(language, os.path.join(currentDir, "translations"))
        translator.load(language, os.path.join(currentDir, "translations"))
        app.installTranslator(translator)
