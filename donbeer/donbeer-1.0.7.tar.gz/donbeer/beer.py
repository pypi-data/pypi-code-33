import pygame


class Beer:

    def __init__(self, source):
        self.clicks = 0
        self.source = source
        self.img = pygame.image.load(source)
        self.rect = self.img.get_rect()
