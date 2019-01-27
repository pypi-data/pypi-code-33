from Com import Com

class Viewas:
	def __init__(self,ob):
		self.ob = ob
	
	
	
class Combobox(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class Fillin(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class Radioset(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class RadioButtons(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class Selectionlist(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class Slider(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class Text(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class Togglebox(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		
class Editor(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		

class Button(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		


class Browse(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		


"""
EFINE [ PRIVATE ] IMAGE image-name
  {image-phrase | LIKE image | size-phrase}
  [ BGCOLOR expression]
  [ FGCOLOR expression]
  [ CONVERT-3D-COLORS ]
  [ TOOLTIP tooltip]
  [ STRETCH-TO-FIT [ RETAIN-SHAPE ]] [ TRANSPARENT ]
  """
  
  
class Image(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		



class Frame(Viewas):
	def __init__(self,*a,**b):
		Viewas.__init__(self,*a,**b)
		



viewas_tab = {'button' : Button,'radio-buttons' : RadioButtons,'editor' : Editor,'combo-box' : Combobox,'fill-in' : Fillin,'radio-set' : Radioset,'selection-list' : Selectionlist,'slider' : Slider,'text' : Text,'toggle-box' : Togglebox}
def viewas(ob):
	if not ob.has.view_as: return
	if not ob.view_as: return
	va = [a for a in ob.view_as.replace("\n"," ").split(' ') if a]
	if not va: return
	if va[0].lower().strip() == 'view-as':
		va = va[1:]
	if not va: return
	type = va[0].lower().strip()
	va = va[1:]
	if not va: return
	
	
	
	
	if not type in viewas_tab:
		print(type)
		print('view_as_tab')
		return
	return view_as_tab[type](ob)


from jivi.fs import *
for k,v in viewas_tab.items():
	File.write("view_as\\%s.html" % v.__name__,"<div> </div>")
"""

VIEW-AS COMBO-BOX
  [LIST-ITEMS value [,value] ... |
   LIST-ITEM-PAIRS label,value [,label,value] ...]
  [{SIZE-PIXELS | SIZE-CHARS | SIZE} width BY height]
  [INNER-LINES height]
  [SORT] [SUBTYPE]
  [TOOLTIP <tooltip>]
  
  VIEW-AS EDITOR
  {{SIZE-PIXELS | SIZE-CHARS | SIZE} width BY height |
   INNER-CHARS num-chars INNER-LINES num-lines}
  [SCROLLBAR-HORIZONTAL] [SCROLLBAR-VERTICAL]
  [MAX-CHARS chars] [NO-WORD-WRAP] [LARGE]
  [BUFFER-CHARS chars] [BUFFER-LINES lines]
  [NO-BOX]
  [TOOLTIP <tooltip>]
  
  VIEW-AS FILL-IN [NATIVE]
  [{SIZE-PIXELS | SIZE-CHARS | SIZE} width BY height]
  TOOLTIP <tooltip>]
  
  VIEW-AS RADIO-SET
  RADIO-BUTTONS label, value [,label, value] ...
  [HORIZONTAL [EXPAND] | VERTICAL]
  [{SIZE-PIXELS | SIZE-CHARS | SIZE} width BY height]
  [TOOLTIP <tooltip>]
  
  
  VIEW-AS SELECTION-LIST
  {{SIZE-PIXELS | SIZE-CHARS | SIZE} width BY height |
   INNER-CHARS num-chars INNER-LINES num-lines}}
  [SINGLE | MULTIPLE] [NO-DRAG] [SORT]
  [SCROLLBAR-HORIZONTAL]
  [SCROLLBAR-VERTICAL]
  [LIST-ITEMS value [,value] ... |
  
  VIEW-AS TEXT
  [{SIZE-PIXELS | SIZE-CHARS | SIZE} width BY height]
  [TOOLTIP <tooltip>]
  
  
  DEFINE {[[ NEW [ GLOBAL ]] SHARED ]| 
            [ PRIVATE | PROTECTED | PUBLIC ]
            [ STATIC ][ SERIALIZABLE | NON-SERIALIZABLE ]}
  VARIABLE variable-name
  {{   AS primitive-type-name 
       | AS [ CLASS ]{object-type-name}
       | LIKE field       }[ EXTENT [constant]]} 
  [ SERIALIZE-NAME serialize-name ]
  [ BGCOLOR expression]
  [ COLUMN-LABEL label]
  [ CONTEXT-HELP-ID expression]
  [ DCOLOR expression]
  [ DECIMALS n]
  [ DROP-TARGET ]
  [ FONT expression]
  [ FGCOLOR expression]
  [ FORMAT string]
  [ INITIAL
      { constant |{[ constant[ , constant]...]}}]
  [ LABEL string[ , string]...]
  [ MOUSE-POINTER expression]
  [ NO-UNDO ]
  [[ NOT ] CASE-SENSITIVE ]
  [ PFCOLOR expression]
  {[ view-as-phrase ]}
  {[ trigger-phrase ]}
  
  
  
  DEFINE [ PRIVATE ] RECTANGLE rectangle[ LIKE rectangle2]
  [ NO-FILL ]
  [{ EDGE-CHARS width}|{ EDGE-PIXELS width}] 
  [ DCOLOR expression]
  [ BGCOLOR expression]
  [ FGCOLOR expression]
  [ GRAPHIC-EDGE ]
  [ PFCOLOR expression]
  [ ROUNDED ]
  [ GROUP-BOX ]
  [size-phrase]
  [ TOOLTIP tooltip]
  {[trigger-phrase]}
  
  DEFINE {[[ NEW ] SHARED ]|[ PRIVATE ]}
  BROWSE browse-name
  QUERY query-name  
    [ SHARE-LOCK | EXCLUSIVE-LOCK | NO-LOCK ][ NO-WAIT ] 
  DISPLAY
    {column-list|record[ EXCEPT field...]} 
    [browse-enable-phrase] 
    {browse-options-phrase}
    [ CONTEXT-HELP-ID expression]
    [ DROP-TARGET ]
    [ TOOLTIP tooltip]
  """