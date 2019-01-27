{ SIZE | SIZE-CHARS | SIZE-PIXELS } width BY height


ignores = 'new,global,shared,private,protected,public,static,class'.split(',')
VIEW_AS 
  {    combo_box_phrase
     | editor_phrase
     | FILL_IN
          [ NATIVE ]
          [  size_phrase ]
          [ TOOLTIP tooltip ]
    | radio_set_phrase
    | selection_list_phrase
    | slider_phrase
    | TEXT
          [ size_phrase ]
          [ TOOLTIP tooltip ]
    | TOGGLE_BOX
          [ size_phrase ]
          [ TOOLTIP tooltip ]
  }
class phrase:
	starters = []
	@classmethod
	def check(cl,ar,kw=''):
		return kw in cl.starters

class view_as(phrase):
	starters = ['view-as']
	parts = [Part(ors=[combo_box,editor,fill_in,radio_set,selection_list,slider,text,toggle_box],req=1)]
	
class size(phrase):
	starters = ['size','size-chars','size-pixels']
	

DEFINE {[[ NEW [ GLOBAL ]] SHARED ]| 
            [ PRIVATE | PROTECTED | PUBLIC ]
            [ STATIC ][ SERIALIZABLE | NON_SERIALIZABLE ]}
  VARIABLE variable_name
  {{   AS primitive_type_name 
       | AS [ CLASS ]{object_type_name}
       | LIKE field       }[ EXTENT [constant]]} 
  [ SERIALIZE_NAME serialize_name ]
  [ BGCOLOR expression]
  [ COLUMN_LABEL label]
  [ CONTEXT_HELP_ID expression]
  [ DCOLOR expression]
  [ DECIMALS n]
  [ DROP_TARGET ]
  [ FONT expression]
  [ FGCOLOR expression]
  [ FORMAT string]
  [ INITIAL
      { constant |{[ constant[ , constant]...]}}]
  [ LABEL string[ , string]...]
  [ MOUSE_POINTER expression]
  [ NO_UNDO ]
  [[ NOT ] CASE_SENSITIVE ]
  [ PFCOLOR expression]
  {[ view_as_phrase ]}
  {[ trigger_phrase ]}
  
  
  
DEFINE {[[ NEW [ GLOBAL ]] SHARED ]| 
            [ PRIVATE | PROTECTED ][ STATIC ]
            [ SERIALIZABLE | NON_SERIALIZABLE ]}
  TEMP_TABLE temp_table_name[ NO_UNDO ] 
  [ NAMESPACE_URI namespace][ NAMESPACE_PREFIX prefix]
  [ XML_NODE_NAME node_name][ SERIALIZE_NAME serialize_name ] 
  [ REFERENCE_ONLY ]
  [ LIKE table_name
      [ VALIDATE ]
      [ USE_INDEX index_name[ AS PRIMARY ]]...]
  [ LIKE_SEQUENTIAL table_name
      [ VALIDATE ]
      [ USE_INDEX index_name[ AS PRIMARY ]]...]
  [ RCODE_INFORMATION ] 
  [ BEFORE_TABLE before_table_name] 
  [ FIELD field_name
      { AS data_type|  LIKE field[ VALIDATE ]}
  [field_options]
  ]...
  [ INDEX index_name
      [[ AS | IS ][ UNIQUE ][ PRIMARY ][ WORD_INDEX ]]
      {index_field[ ASCENDING | DESCENDING ]}...
  ]...
  
  
view_as = ['view_as',


class combo_box(phrase):
	
  
VIEW_AS COMBO_BOX
  [ LIST_ITEMS item_list | LIST_ITEM_PAIRS item_pair_list]
  [ INNER_LINES lines ] [size_phrase ] [ SORT ]
  [ TOOLTIP tooltip]
  [ SIMPLE | DROP_DOWN | DROP_DOWN_LIST ]
  [ MAX_CHARS characters ] 
  [ AUTO_COMPLETION [ UNIQUE_MATCH ] ]

COMBO_BOX
  [ LIST_ITEMS item_list | LIST_ITEM_PAIRS item_pair_list]
  [ INNER_LINES lines ] [ SORT ]
  [ DROP_DOWN | DROP_DOWN_LIST ]
  [ MAX_CHARS characters ] 
  [ AUTO_COMPLETION [ UNIQUE_MATCH ] ]
  
  
  
EDITOR
  {  size_phrase
      | INNER_CHARS characters INNER_LINES lines
  } 
  [ BUFFER_CHARS chars ]
  [ BUFFER_LINES lines ]
  [ LARGE ]
  [ MAX_CHARS characters ]
  [ NO_BOX ]
  [ NO_WORD_WRAP ]
  [ SCROLLBAR_HORIZONTAL ]
  [ SCROLLBAR_VERTICAL ]
  [ TOOLTIP tooltip ]
  
RADIO_SET
  [ HORIZONTAL [ EXPAND ] | VERTICAL ]
  [ size_phrase ]
  RADIO_BUTTONS label , value [ , label, value ... ] 
  [ TOOLTIP tooltip ]
  
SELECTION_LIST 
  [ SINGLE | MULTIPLE ]
  [ NO_DRAG ]
  [ LIST_ITEMS item_list ]
  [ SCROLLBAR_HORIZONTAL ]
  [ SCROLLBAR_VERTICAL ]
  { size_phrase | INNER_CHARS cols INNER_LINES rows }
  [ SORT ]
  [ TOOLTIP tooltip ]
  
SELECTION_LIST
  [ SINGLE | MULTIPLE ]
  [ NO_DRAG ]
  { LIST_ITEMS item_list| LIST_ITEM_PAIRS item_pair_list}
  [ SCROLLBAR_HORIZONTAL ][ SCROLLBAR_VERTICAL ]
  {size_phrase
    |{ INNER_CHARS cols INNER_LINES rows}
  }
  [ SORT ]
  [ TOOLTIP tooltip]
  

VIEW_AS SLIDER 
  MAX_VALUE max_value MIN_VALUE min_value 
  [ HORIZONTAL | VERTICAL ]
  [ NO_CURRENT_VALUE ]
  [ LARGE_TO_SMALL ]
  [ TIC_MARKS
      { NONE | TOP | BOTTOM | LEFT | RIGHT | BOTH }
      [ FREQUENCY n ]
  ]
  [ TOOLTIP tooltip ]
  [ size_phrase ]