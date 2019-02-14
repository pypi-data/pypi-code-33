import pygame
pygame.init()

class Widget:#base widget
    def init(self,args=[],kwargs={}):
        self.events = []
    def __init__(self,pos,size,skin,name,*args,**kwargs):
        self.pos = pos
        self.name = name
        self.hit = False
        self.surface = pygame.Surface(size)
        self.size = size
        self.rect = pygame.Rect(pos,size)
        self.surface.fill(skin['background'])
        self.skin = skin
        if args == []:
            if kwargs == {}:
                self.init()
            else:
                self.init(kwargs=kwargs)
        else:
            if kwargs == {}:
                self.init(args=args)
            else:
                self.init(args=args,kwargs=kwargs)
#Click button
class Button(Widget):
    def init(self,args=[],kwargs={}):
        self.events = ['click', 'loop']
        self.text = kwargs['text']
        self.font = pygame.font.SysFont(self.skin['font-family'],15)
        self.surface.fill(self.skin['borders'])
        self.surface.fill(self.skin['background'],rect=pygame.Rect(1,1,self.rect.w-2,self.rect.h-2))
        self.surface.blit(self.font.render(self.text,True,self.skin['font-color']),[2,2])
    def clicked(self,events):
        #print('clicked!')
        return True
    def loop(self,events):
        pass
#switch
class ToggleButton(Button):
    def clicked(self,events):
        try:
            if self.on:
                self.on = False
                self.surface.fill(self.skin['background'],rect=pygame.Rect(1,1,self.rect.w-2,self.rect.h-2))
            else:
                self.on = True
                self.surface.fill(self.skin['active'],rect=pygame.Rect(1,1,self.rect.w-2,self.rect.h-2))
        except AttributeError:
            self.on = True
            self.surface.fill(self.skin['active'],rect=pygame.Rect(1,1,self.rect.w-2,self.rect.h-2))
        #print(self.on)
        self.surface.blit(self.font.render(self.text,True,self.skin['font-color']),[2,2])
        return self.on
    def loop(self,events):
        try:
            return self.on
        except:
            pass
#pygame draw surface for games
class Canvas(Widget):
    def init(self, args=[], kwargs={}):
        self.events = ['loop']
        self.cloop = kwargs['cloop']
    def loop(self,events):
        self.cloop(self, events)
#user input
class InputBox(Widget):
    def init(self,args=[],kwargs={'tsize':12,'start_text':''}):
        self.events = ['click','loop']
        self.text = list(kwargs['start_text'])
        self.fontsize = kwargs['tsize']
        self.font = pygame.font.SysFont(self.skin['font-family'],self.fontsize)
        self.active = False
        self.bp = False
        self.ep = False
    def loop(self,events):
        if self.active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                if not self.ep:
                    self.ep = True
                    return ''.join(self.text)
            else:
                self.ep = False
            if keys[pygame.K_BACKSPACE]:
                if not self.bp:
                    self.bp = True
                    try:
                        del self.text[len(self.text)-1]
                    except:
                        pass
            else:
                self.bp = False
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.unicode in 'qwertyuiopasdfghjklzxcvbnm1234567890-=[]\',./\\`!@#$%^&*()+ ':
                        if keys[pygame.KMOD_LSHIFT] or keys[pygame.KMOD_RSHIFT]:
                            self.text.append(e.unicode.upper())
                        else:
                            self.text.append(e.unicode)
        self.surface.fill(self.skin['text-background'])
        self.surface.blit(self.font.render(''.join(self.text),True,self.skin['font-color']),[2,2])
        return None
    def clicked(self,events):
        if self.active:
            self.active = False
        else:
            self.active = True
#label for text
class Label(Widget):
    def init(self,args=[],kwargs={'tsize':12,'text':'N/A'}):
        self.events = []
        self.font = pygame.font.SysFont(self.skin['font-family'],kwargs['tsize'])
        self.surface.blit(self.font.render(kwargs['text'],True,self.skin['font-color']),[2,2])
#Drop-down menu
class Menu(Widget):
    def init(self,args=[],kwargs={'title':'Menu','options':['button1','button2','button3']}):
        self.events = ['click','hover','loop']
        self.lopts = len(kwargs['options'])
        self.font = pygame.font.SysFont(self.skin['font-family'],12)
        self.unhover = pygame.Surface(self.size)
        self.unhover.fill(self.skin['background'])
        self.unhover.blit(self.font.render(kwargs['title'],True,self.skin['font-color']),[2,2])
        self.hovered = pygame.Surface([self.size[0],self.size[1]+(self.size[1]*self.lopts)])
        self.hovered.fill(self.skin['active'])
        self.hovered.blit(self.font.render(kwargs['title'],True,self.skin['font-color']),[2,2])
        self.ishovered = False
        self.colliders = {}
        c = 1
        for y in kwargs['options']:
            self.hovered.blit(self.font.render(y,True,self.skin['font-color']),[2,(c*20)])
            self.colliders[c*20] = y
            c += 1
    def hover(self,events):
        self.ishovered = True
    def clicked(self,events):
        if self.ishovered:
            for i in list(self.colliders.keys()):
                if pygame.Rect((0,i),(self.size[0],18)).collidepoint(pygame.mouse.get_pos()):
                    return self.colliders[i]
        return False
    def loop(self,events):
        if self.ishovered:
            self.surface = self.hovered.copy()
            self.rect = pygame.Rect(self.pos,[self.size[0],self.size[1]+(self.size[1]*self.lopts)])
            if not self.rect.collidepoint(pygame.mouse.get_pos()):
                self.ishovered = False
                self.surface = self.unhover.copy()
                self.rect = pygame.Rect(self.pos,self.size)
        else:
            self.surface = self.unhover.copy()
            self.rect = pygame.Rect(self.pos,self.size)
