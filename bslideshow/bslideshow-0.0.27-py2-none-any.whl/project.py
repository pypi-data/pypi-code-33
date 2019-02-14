#!/usr/bin/env python2.7
#coding:utf-8


#import bpy
import os
import math
import random
from PIL import Image
import time

import codecs
import hjson

from bslideshow.director import Director
from bslideshow.slideshow import Slideshow
from bslideshow.tools import BlenderTools

class Project(object):

  def __init__ (self, path):
    self.path = path
    self.parents = []

  def generateMainSection (self, section):
    print("generate Main Section " + section['title'])
    self.generateTitleSection(section)
    for simpleSection in section['sections']:
      self.parents.append([simpleSection, section])
      self.generateSection(simpleSection)
    self.mergeWithTransitions(section)
    pass

  def generateTitleSection (self, section):
    print("generate Title Section " + section['title'])

  def mergeWithTransitions (self, section):
    print("mergeWithTransitions " + section['title'])

  def generateSection (self, section):
    print("generate Section " + section['title'])
    director = Director()
    director.runMode = 'LOW'
    pathSection = os.path.join(os.path.dirname(self.path), section['path'])
    print("path section = " + pathSection)
    out = director.animScene(str(pathSection))
    print("out section = " + out)

    foregroundPath = 'overlay22.mp4'
    tools = BlenderTools()
    #tools.maxDebugFrames = 24
    out2 = tools.addForeground(out, foregroundPath)
    print("out2 section = " + out2)

    #tools.maxDebugFrames = 24
    banner = tools.generateBanner(title = str(section['title']), subtitle = str(section['subtitle']))
    print("banner section = " + banner)

    bannerOffset = tools.addOffset(banner, framesOffset = 48)
    #bannerOffset = '/tmp/.movieRWAuLJ.mp4'
    print("bannerOffset section = " + bannerOffset)

    result = tools.doAddBanner(out2, bannerOffset)
    print("result section = " + result)

    quit()
    
    pass

  def __saveObj__ (self, path, obj):
    fp = codecs.open(path, mode='w', encoding='utf-8')
    hjson.dump(obj, fp)

  def __loadObj__ (self, path):
    result = None
    fp = codecs.open(path, mode='r', encoding='utf-8')
    result = hjson.load(fp)
    return result

  def __get_parent__ (self, data):
    result = None
    for item in self.parents:
      if data == item[0]:
        result = item[1]
        break
    return result

  def generate (self):
    data = self.__loadObj__(self.path)
    self.parents.append([data, None])
    self.generateTitleSection(data)
    for mainSection in data['sections']:
      self.parents.append([mainSection, data])
      self.generateMainSection(mainSection)
    self.mergeWithTransitions(data)
 
    


if __name__ == '__main__':
  p = Project("/home/jmramoss/hd/res_slideshow/project/myproject.hjson")
  p.generate()

