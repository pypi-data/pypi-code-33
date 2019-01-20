import pygame
import sys
import random
import datetime
from pygame.locals import *
from random import randint

FPS = 60

CYAN = (0, 255, 255)


def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()


class Lap:
    """
    create for every new lap/round object a randum number
    every round object should start with 1
    """

    def __init__(self):
        self.ranNum = randint(2, 20)
        self.index = 1


class Game:
    def __init__(self, symbols, conf):
        self.lap = Lap()
        self.points = 0
        self.symbols = symbols
        self.conf = conf
        self.startTimePause = None

    # new Round has new random Int and Local time of the pause(wait bcs of
    # Donut)
    def newRound(self, beer):
        self.lap.index += 1
        self.lap.ranNum = randint(2, 20)
        beer.clicks = 0
        self.randomTime = randint(2, 9)

    def getRanNum(self):
        return self.lap.ranNum

    """
    returns true if the pause is over
    """

    def wait(self, beer):
        #print (self.startTimePause)
        if (self.startTimePause is not None):
            # Adds seconds to the starttime and gets the end time
            endTimePause = addSecs(self.startTimePause, self.randomTime)
            localTime = datetime.datetime.now().time()
            print(self.startTimePause)
            print(endTimePause, datetime.datetime.now().time())
            if(localTime >= endTimePause):
                self.startTimePause = None
                return False
            else:
                return True

    def showObject(self, object):
        self.conf.window.fill(CYAN)
        self.conf.window.blit(object.get_image(), object.get_rect())
        #print (object.source)

    def isOverRect(self, object, mousePos):
        if (object.get_rect().collidepoint(mousePos)):
            return True
        return False

    """
    1 for Donut, 0 for Beer
    """

    def getStatus(self, beer, donut):
        #print (beer.clicks == self.getRanNum())
        if (beer.clicks == self.getRanNum()):
            self.startTimePause = datetime.datetime.now().time()
            print(self.startTimePause)
            self.newRound(beer)
            return 1
        if(self.wait(beer)):
            return 1
        else:
            return 0

    """
    Handles the clicks of the user to the beer and donut
    """

    def eventHandling(self, beer, donut):
        if (self.mousePos is not None):
            # if the user clicked onto beer or donut
            if (self.isOverRect(beer, self.mousePos)
                    or self.isOverRect(donut, self.mousePos)):
                # if he has clicked in the beer phase
                if(self.getStatus(beer, donut) == 0):
                    beer.clicks += 1
                    print(beer.clicks)
                    print(self.getRanNum())
                else:
                    print('hallo')
                    pygame.quit()
                    sys.exit()

    def input(self):
        self.mousePos = None
        for event in pygame.event.get():
            if (event.type == QUIT):
                pygame.quit()
                sys.exit()

            # If clicked
            elif (event.type == MOUSEBUTTONUP and event.button == 1):
                self.mousePos = pygame.mouse.get_pos()


class Beer:

    def __init__(self, source):
        self.clicks = 0
        self.source = source
        self.img = pygame.image.load(source)
        self.rect = self.img.get_rect()

    def getImage(self):
        return self.img

    def getRect(self):
        return self.rect


class Donut:

    def __init__(self, time, source):
        self.time = time
        self.source = source
        self.img = pygame.image.load(source)
        self.rect = self.img.get_rect()

    def getImage(self):
        return self.img

    def getRect(self):
        return self.rect


def tester(beer, beerRect):
    print(beer.get_rect().centerx)
    print(beer.get_rect().centery)


class Configuration:
    def __init__(self, width, height):
        self.windowWidth = width
        self.windowHeight = height
        self.fpsClock = pygame.time.Clock()

    def setUp(self, color):
        pygame.init()
        self.window = pygame.display.set_mode(
            (self.windowWidth, self.windowHeight), 0, 32)
        self.window.fill(CYAN)


def main():

    # Hauptelemente erstellen und konfigurieren
    conf = Configuration(700, 600)

    print(datetime.datetime.now().time())
    beer = Beer('../images/beer2.png')
    beerimg = beer.getImage()
    beerRect = beerimg.get_rect()

    donut = Donut(0, '../images/donut2.png')
    symbols = [beer, donut]
    game = Game(symbols, conf)

    beer.getRect().center = (350, 300)
    donut.getRect().center = (350, 300)

    conf.setUp(CYAN)
    #conf.window.blit(beer.getImage(), beer.getRect())
    print(game.lap)

    game.newRound(beer)
    while True:  # main game loop
        game.input()
        game.eventHandling(beer, donut)

        game.conf.window.fill(CYAN)
        if(game.getStatus(beer, donut) == 1):
            #print ('fuchs')
            game.showObject(donut)
        else:
            game.showObject(beer)

        pygame.display.update()
        game.conf.fpsClock.tick(FPS)


if __name__ == '__main__':
    main()
