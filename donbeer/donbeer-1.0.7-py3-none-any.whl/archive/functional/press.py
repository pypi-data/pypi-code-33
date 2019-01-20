import pygame
import sys
import random
from pygame.locals import *
from random import randint


FPS = 60
WINDOWWIDTH = 700
WINDOWHEIGHT = 600

CYAN = (0, 255, 255)


bier = pygame.image.load('images/beer2.png')
bierRect = bier.get_rect()
donut = pygame.image.load('images/donut2.png')
donutRect = donut.get_rect()

bierRect.center = (350, 300)
donutRect.center = (350, 300)
COUNTER = 0


def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)

    mouseX = 0
    mouseY = 0

    pygame.display.set_caption('PRESS!')

    DISPLAYSURF.fill(CYAN)

    while True:  # main game loop
        DISPLAYSURF.fill(CYAN)
        global COUNTER
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mpos = pygame.mouse.get_pos()
                DISPLAYSURF.fill(CYAN)
                DISPLAYSURF.blit(bier, bierRect)

                if bierRect.collidepoint(mpos):
                    COUNTER += 1
                    if test():

                        COUNTER = 0
                        DISPLAYSURF.blit(donut, donutRect)

                elif donutRect.collidepoint(mpos):
                    break

            else:

                if test():
                    DISPLAYSURF.blit(donut, donutRect)
                else:
                    DISPLAYSURF.blit(bier, bierRect)
                  #  print ("Hallo")

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def test():
    global COUNTER
    if COUNTER == randint(2, 20):
        return True
    #COUNTER += 1
    print(COUNTER)
    return False


if __name__ == '__main__':
    main()
