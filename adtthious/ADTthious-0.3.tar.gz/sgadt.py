# encoding: utf-8

"""
TODO:
    * OK dériver de windows et finir pour tous les types de base pour un seul objet
      et avec les Class HBDS
    * OK faire les att composés
    * OK contrôle des types après saisie
        pas de contôle de type par widget à la volée car il faut des widgets
        spécifique qui ne sont pas faciles à ajouter.
        Donc on fait ça en signalant les erreurs. Pour l'instant le message de l'exception
        est remonté.
    * OK les unités. Reste encore a faire que l'on puisse la changer
    * choix du positionnement vertical ou horizontal des att
    * ajouter plusieurs objets
    * ajouter la modification en mode MVC des objets
    * faire les querytree
    * les traductions + locales
    * doc et tooltips
    * undo/redo
            
"""
from ADT import basictypes, fonctors, hbds, units

import PySimpleGUI as sg


def create_widget(valtype, val, key):
    if val is None: val = ''
    if valtype:
        for t in valtype.__mro__:
                    
            if t is bool:
                return [
                    sg.Check('', default=val, key=key, change_submits=True),
                    ]
            elif t is int:
                return [
                    sg.In(val, key=key, change_submits=True, do_not_clear=True, size=(20,1)),
                    ]
            elif t is float: 
                return [
                    sg.In(val, key=key, change_submits=True, do_not_clear=True, size=(20,1)),
                    ]
            elif t is str: 
                return [
                    sg.In(val, key=key, change_submits=True, do_not_clear=True, size=(20,1)),
                    ]
            elif t is basictypes.Enum:
                V = list(type(val).__members__.keys())
                # ajoute 2 à la longueur car si non la flêche de la combo cache la fin du text
                S = (max([len(v) for v in V])+2, sg.DEFAULT_ELEMENT_SIZE[1])
                return [
                    sg.Combo(values=V, size=S,
                             default_value=val.name, key=key, change_submits=True),
                    ]
            elif t is basictypes.date: 
                return [
                    sg.In(val, size=(20,1), key=key, change_submits=True, do_not_clear=True),
                    sg.CalendarButton("", target=key,
                                      default_date_m_d_y=(val.month, val.day, val.year),
                                      image_filename="./calendar.png",
                                      image_size=(25, 25),
                                      image_subsample=1,
                                      border_width=0),
                                    
                    ]
            elif t is basictypes.time: 
                return [
                    sg.In(val, size=(20,1), key=key, change_submits=True, do_not_clear=True),
                    ]
            elif t is basictypes.datetime: 
                return [
                    sg.In(val, size=(20,1), key=key, change_submits=True, do_not_clear=True),
                    sg.CalendarButton("", target=key,
                                      default_date_m_d_y=(val.month, val.day, val.year),
                                      image_filename="./calendar.png",
                                      image_size=(30, 30),
                                      image_subsample=1,
                                      border_width=0),
                    ]
            elif t is basictypes.Color:
                return [
                    sg.In(val, size=(8,1), key=key, change_submits=True, do_not_clear=True),
                    sg.ColorChooserButton('', key='__'+key, size=(2,1),
                                          target=key, button_color=(val,val)),
                    ]
            
    return [sg.T("Unknown widget for %s" % valtype)]

def _make_keys(rootkey, name):
    attr_key = "%s.%s" %(rootkey, name)
    attrname_key = "_%s.%s" %(rootkey, name)
    return attrname_key, attr_key

def _id_attr_from_keys(key):
    idx = key.find('.')
    if idx == -1: return None, None
    return int(key[:idx]), key[idx+1:]


class ADTWindow(sg.Window):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.objects = {}
        self.errors = {}
        
    def Layout(self, obj, attrs=None):
        layout = self._layout_attrs(obj, attrs)
        layout.append( [sg.RButton('Read')] )
        return super().Layout(layout)
    
    def _layout_attrs(self, obj, attrs=None):
        if attrs is None:
            attrs = [[a,] for a in fonctors.getattrs(obj)]
        self.objects[id(obj)] = obj
        label_size = (max([len(a) for row in attrs for a in row]), sg.DEFAULT_ELEMENT_SIZE[1])

        layout = []
        unit_widget = None
        for row in attrs:
            row_layout = []
            for attr in row:
                if isinstance(attr, sg.Element):
                    row_layout.append(attr)
                    continue
                val = getattr(obj, attr)
                nkey, key = _make_keys(id(obj), attr)
                if isinstance(type(obj), hbds.Class):
                    typeattr = getattr(type(obj), attr)
                    if type(typeattr).__name__.find('ComposedAtt_') != -1:
                        l = self._layout_attrs(val)
                        row_layout.append(sg.Frame(attr, l))
                        continue
                    valtype = getattr(type(obj), attr).type

                    if typeattr.unit:
    ##                    V = list(type(typeattr.unit).__members__.keys())
    ##                    S = (max([len(v) for v in V]), sg.DEFAULT_ELEMENT_SIZE[1])
    ##                    # bug dans PySimpleGUI ligne 5097: feild non unique!
    ##                    unit_widget = sg.Combo(values=V, size=S,
    ##                                           default_value=typeattr.unit.name,
    ##                                           key="u_"+key, change_submits=True)
                        # Ou juste le symbol
                        unit_widget = sg.T(typeattr.unit.symbol, tooltip=typeattr.unit.name)
                        
                else: # No hbds.Class
                    valtype = type(getattr(obj, attr))

                row_layout += \
                    [sg.T(attr, size=label_size, key=nkey),
                     sg.Button("?", visible=False, key="?"+nkey),
                     ] \
                    + create_widget(valtype, val, key)
                
                if unit_widget:
                    row_layout.append(unit_widget)

                print(row_layout)
            layout.append(row_layout)
        return layout
    
    def Read(self, timeout=None, timeout_key=sg.TIMEOUT_KEY):
        event, values = super().Read(timeout, timeout_key)
        print(event)
        if event is None: return event, values
        if event == 'Read':
            print(event, values)
            return event, values

        if event[0:2] == "?_":
            sg.PopupError(self.errors[event[2:]])
            return event, values
        
        i, attr = _id_attr_from_keys(event)
        obj = self.objects[i]
        try:
            setattr(obj, attr, values[event])
        except TypeError as e:
            self.FindElement('_'+event).Update(text_color='red')
            self.FindElement('?_'+event).Update(visible=True)
            #self.FindElement(event).Update(getattr(obj, attr))
            self.errors[event] = str(e)
            return event, values

        val = getattr(obj, attr)
        if isinstance(val, basictypes.Color):
            self.FindElement('__'+event).Update(button_color=(None,val))
            
        self.FindElement('_'+event).Update(text_color=sg.DEFAULT_TEXT_COLOR)
        self.FindElement('?_'+event).Update(visible=False)
        del self.errors[event]
        return event, values

def show_py_object():
    class X: pass
    Genre = basictypes.Enum('Genre', "Homme Femme XXY YYX XYX")

    x = X()
    x.nom = "xx"
    x.age = 12
    x.taille = 1.8
    x.marie = True
    x.date_de_naissance = basictypes.date("19/08/1963")
    x.heure_de_naissance = basictypes.time(10)
    x.genre = Genre.Homme
    x.X = []
    x.now = basictypes.datetime.now()
        
    window = ADTWindow('py object', resizable=True).Layout(x)

    while True:
      event, values = window.Read()
      if event is None: return

def show_hbds_object():

    class Equipement(metaclass=hbds.Class):
        nom = str
        blindage = str
        volume = float, units.CubicMeter.cubic_meter
        masse = float, units.Kilogram.tonne
        filtration_d_air = bool
        dimmensions = hbds.ComposedAtt(
            longueur = (float, units.Meter.metre),
            largeur = (float, units.Meter.metre),
            )
        pente = hbds.ComposedAtt(
            pente_max = float, # degré
            renlitissement = float, # pourcent
            )
        
        
    e = Equipement()
    window = ADTWindow('ADT: UrbanObject', resizable=True).Layout(e,
##    [
##        ["nom", "dimmensions",],
##        ["blindage", "pente",],
##        ["volume"],
##        ["masse"],
##        ["filtration_d_air"],
##        ]
    )

    while True:
      event, values = window.Read()
      if event is None: return

                        
    
def main():
    import random
    # PB avec COLOR_SYSTEM_DEFAULT qui apparait trop souvent
    index = random.choice(sg.ListOfLookAndFeelValues())
    ##    index = 'Kayak'
    colors = sg.LOOK_AND_FEEL_TABLE[index]
    ##    print(index, colors)

    sg.ChangeLookAndFeel(index)
    ##    print(sg.DEFAULT_TEXT_COLOR)
    sg.SetOptions(
        font=('Times', 10),
    ##        element_padding=(0,2),
    ##        margins = (2,5),
    ##        element_size = (20,1)
        )
    sg.DEFAULT_TEXT_COLOR = 'black'

    #show_py_object()
    show_hbds_object()

##    window = sg.Window('Tests')
##    L = [
##        [sg.T("1.1"), sg.T("1.2")],
##        [sg.T("2.1"), sg.T("2.2"), sg.T("2.3"), ],
##        [sg.T("3.1"), sg.T("3.2")],
##    ]
##    window.Layout(L)
##    while True:
##        event, values = window.Read()
##        if event is None: return


    
if __name__ == '__main__':
    main()

