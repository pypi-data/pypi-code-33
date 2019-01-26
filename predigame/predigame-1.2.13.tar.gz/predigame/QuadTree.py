import pygame, random, math, sys
# implementation from http://www.learnpygame.com/2015/03/implementing-quadtree-collision-system.html

class Quadtree(object):
    def __init__(self, level, rect, sprites=[]):
        '''Quadtree box at with a current level, rect, list of sprites'''
        self.MAX_LEVEL = 4#max number of subdivisions
        self.level = level#current level of subdivision
        self.MAX_SPRITES = 3#max number of sprites without subdivision
        self.rect = rect#pygame rect object
        self.sprites = sprites#list of sprites
        self.branches = []#empty list that is filled with four branches if subdivided

    def get_rect(self):
        '''Returns quadtree rect object'''
        return self.rect

    def subdivide(self):
        '''Subdivides quadtree into four branches'''
        for rect in rect_quad_split(self.rect):
            branch = Quadtree(self.level+1, rect, [])
            self.branches.append(branch)

    def add(self, sprite):
        '''Adds a sprite to the list of sprites inside quadtree box'''
        self.sprites.append(sprite)

    def subdivide_sprites(self):
        '''Subdivides list of sprites in current box to four branch boxes'''
        for sprite in self.sprites:
            for branch in self.branches:
                if branch.get_rect().colliderect(sprite.rect):
                    branch.add(sprite)

    def test_collisions(self):
        '''Tests for collisions between all sprites'''
        for i, sprite in enumerate(self.sprites):
            for sprite2 in self.sprites[i+1:]:
                collide(sprite, sprite2)

    def update(self):
        '''Updates the quadtree and begins recursive process of subdividing or collision testing'''
        if len(self.sprites) > self.MAX_SPRITES and self.level <= self.MAX_LEVEL:
            self.subdivide()
            self.subdivide_sprites()
            for branch in self.branches:
                branch.update()
        else:
            self.test_collisions()
