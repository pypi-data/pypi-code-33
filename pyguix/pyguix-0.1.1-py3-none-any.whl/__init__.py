import pygame, json, sys, copy
from .widgets import *
pygame.init()

class UI: #main UI
    def __init__(self, size, title='My GUI', skin_path='default'):
        if skin_path != 'default':
            with open(skin_path,'r') as f:
                sf = json.loads(f.read())
                self.skin_name = sf['name']
                self.skin_author = sf['author']
                self.skin = sf['skin']
        else:
            self.skin = {
                "background":[224, 224, 224],
                "borders":[25, 25, 25],
                "font-color":[0, 0, 0],
                "font-family":"arial",
                "active":[186, 186, 186],
                "text-background":[255,255,255]
            }
        self.screen = pygame.display.set_mode(size)
        self.widgets = []
        self.wdict = {}
        pygame.display.set_caption(title)
    def add_widget(self,widget):
        self.widgets.append(widget)
        self.wdict[widget.name] = len(self.widgets)-1
    def remove_widget(self,name):
        try:
            _index = self.wdict[name]
        except KeyError:
            raise KeyError(name + ' is not a registered widget. Your widgets are: ' + ', '.join(self.wdict.keys()) + '.')
        endict = copy.copy(self.wdict)
        for i in self.wdict.keys():
            if self.wdict[i] < _index:
                pass
            elif self.wdict[i] == _index:
                del self.widgets[self.wdict[i]]
                del endict[name]
            else:
                endict[i] -= 1
        self.wdict = copy.copy(endict)

    def add_widgets(self,widgets):
        for w in widgets:
            self.add_widget(w)
    def loop(self):
        self.screen.fill(self.skin['background'])
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        ret = {'None':{'None':None}}
        for wd in self.widgets[:]:
            r = {'click':False,'hover':False,'loop':False}
            if copy.copy(wd.rect).collidepoint(mouse_pos) and mouse_pressed and 'click' in wd.events:
                if not wd.hit:
                    r['click'] = wd.clicked(events)
                wd.hit = True
            else:
                wd.hit = False
            if copy.copy(wd.rect).collidepoint(mouse_pos) and 'hover' in wd.events:
                #print(i.rect)
                r['hover'] = wd.hover(events)
            if 'loop' in wd.events:
                r['loop'] = wd.loop(events)
            self.screen.blit(wd.surface,wd.pos)
            ret[wd.name] = r
        pygame.display.flip()
        return ret



'''ui = UI([200,400])
ui.add_widget(Menu([0,0],[200,20],ui.skin,'menu'))
#ui.add_widget(Label([0,0],[200,400],ui.skin,'label',tsize=12,text='You removed the widgey'))
while True:
    ret = ui.loop()
    if not ret:
        break
    try:
        if 'click' in ret['menu'].keys():
            if ret['menu']['click']:
                print(ret['menu']['click'])
                if ret['menu']['click'] == 'button3':
                    ui.remove_widget('menu')
                    ui.add_widget(Label([0,0],[200,400],ui.skin,'label',tsize=12,text='You removed the widgey'))
    except KeyError:
        pass
'''
