#TODO on space, if current name is not a function
#TODO fix autocomplete issues: backspace shouldn't erase everything, it should be faster, should highlight callables a different color, should let me immediately search in the middle of a word,3 shouldn't be persistent when I hit the enter key and the cursor is no longer on the keyword,
#TODO add a way to add a space without any of my autocomplete nonsense

#RULES:
    #Should follow normal typing even (such as import import --> import)
    #Should not use memory outisde current text (a few exceptions but they're exceptions not the rule)
    #Should be activated on the fringes of useless or invalid syntax

#TODO: Autocomplete "is" and "in" and "is not" and "and" and "or" (and any other alphabetic operators):
    #When NOT in a string: (WE NEED STRING AREA DETECTION):
        #On press 'a': "x |" ---> "x and |"
        #(because in no other situation would you need that space)
    #How to handle conflict: "in" vs "is":
        #Branch prediction: figure out how to predict which one the user uses more often.
        #Let's say they use 'in' more often; more specifically, if the variable to the left has a __contains__ function:
            #On press i: "x |" ---> "x in |"
        #Let's say that the user actually wanted "is". Because of the rule that normal typing should be supported:
            #On press s: "x in |" ---> "x is |"
    #Shouldn't REALLY be limited to just spaces (should also allow ')',']','')

#Hold alt to make space act normal.


from __future__ import unicode_literals

from rp.prompt_toolkit.document import Document
from rp.prompt_toolkit.enums import DEFAULT_BUFFER
from rp.prompt_toolkit.filters import HasSelection, IsMultiline, Filter, HasFocus, Condition, ViInsertMode, EmacsInsertMode
from rp.prompt_toolkit.key_binding.vi_state import InputMode
from rp.prompt_toolkit.key_binding.registry import Registry
from rp.prompt_toolkit.keys import Keys,Key
from rp.prompt_toolkit.buffer import Buffer
_copied_string=""
def do_copy(string):
    import rp
    global _copied_string
    rp.string_to_clipboard(string)
    _copied_string=string
def do_paste(buffer):
    buffer.insert_text(_copied_string)
import rp.r_iterm_comm as ric
enable_space_autocompletions=ric.enable_space_autocompletions#This variable is a list that's mutated between being empty and being full, which toggles it's truth value. This feature isn't completely figured out yet...I suppose it's better to disable it for the time being...

from rp import *
__all__ = (
    'load_python_bindings',
    'load_siƒdebar_bindings',
    'load_confirm_exit_bindings',
)
from rp import *
def starts_with_any(string,*prefixes):
    for p in prefixes:
        if string.startswith(p):
            return True
    return False
_meta_pressed=[]
def meta_pressed():#This should only be called once per keystroke
    out=bool(_meta_pressed)
    _meta_pressed.clear()
    return out
def line_above(buffer):
    document=buffer.document
    before=document.text_before_cursor
    if not '\n' in before:
        return None
    before_lines=before.split("\n")
    return before_lines[-2]
def beginswithany(a,*b):
    for x in b:
        if a.startswith(x):
            return True
    return False
def indent_hiearchy(s:str):
    """
    Takes a str such as:
'''
def hiu(iub):
    ewq(ojhi)
    if h:
        apple
        hio
            iuy
              ioo'''
    And returns:
    ['              ioo',
     '            iuy',
     '        hio',
     '    if h:',
     'def hiu(iub):']
    """
    o=None
    for l in reversed(s.splitlines()):
        if o is None or not l.startswith(o):
            yield l
            o=get_indent(l)
            if not o:
                break
def find_header(code:str,*line_starts:str)->str:
    #(was originally just find_level, see it's purpose)
    #this function returns the entire line itself instead of just the number of indents
    #returns None if not in such a block
    for i,e in enumerate(indent_hiearchy(code)):
        if starts_with_any(e.lstrip(),*line_starts):
            return e
    return None
def find_level(code:str,*line_starts:str)->int:
    #return the unindents needed (assumed to be spaces) to reach block starting with any string from line_starts
    #returns None if not in such a block
    header=find_header(code,line_starts)
    if header is None:
        return None
    return len(get_indent(header))
def get_indent(line):
    #returns a string that just contains the line's indent
    return line[:len(line)-len(line.lstrip())]
def endswithany(a,*b):
    for x in b:
        if a.endswith(x):
            return True
    return False
def in_class_func_decl(buffer):#can be easily memoized but i wont bother unless its an issue; (prob got bigger probs tbh)
    document=buffer.document
    current_line=document.current_line
    before_line=document.current_line_before_cursor
    after_line=document.current_line_after_cursor
    before=document.text_before_cursor
    after= document.text_after_cursor
    lines=reversed(before.split('\n'))
    indent=get_indent(before_line)
    for line in lines:
        if not line.startswith(indent):
            return line.lstrip().startswith('class ')
    return False
class TabShouldInsertWhitespaceFilter(Filter):
    """
    When the 'tab' key is pressed with only whitespace character before the
    cursor, do autocompletion. Otherwise, insert indentation.

    Except for the first character at the first line. Then always do a
    completion. It doesn't make sense to start the first line with
    indentation.
    """
    def __call__(self, cli):
        b = cli.current_buffer
        before_cursor = b.document.current_line_before_cursor

        return bool(b.text and (not before_cursor or before_cursor.isspace()))

def has_selected_completion(buffer):# If we have a completion visibly selected on the menu
    return buffer.complete_state and buffer.complete_state.complete_index is not None

ans_dot_completion_string=None

def load_python_bindings(python_input):
    """
    Author: Ryan Burgert
    """
    registry = Registry()

    sidebar_visible = Condition(lambda cli: python_input.show_sidebar)
    handle = registry.add_binding
    has_selection = HasSelection()
    vi_mode_enabled = Condition(lambda cli: python_input.vi_mode)

    #region Ryan Burgert Stuff
    from rp.prompt_toolkit.key_binding.input_processor import KeyPressEvent
    from rp.prompt_toolkit.document import Document
    #region Template
    def _(event):# Parenthesis completion
        #
        assert isinstance(event,KeyPressEvent)
        #
        from rp.prompt_toolkit.buffer import Buffer
        buffer=event.cli.current_buffer
        assert isinstance(buffer,Buffer)
        #
        document=buffer.document
        assert isinstance(document,Document)
        document.insert_after()
        #
        text=document.text_after_cursor
        assert isinstance(text,str)
        #
    # buffer.insert_text("(")
    # if not text or text[0] in " \t\n":
    #     buffer.insert_text(")")
    #     buffer.cursor_left(count=1)
#endregion
    for char in '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?`1234567890-=qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./':# Normal keyboard inputs
        def go(c):
            @handle(c,filter=has_selection)
            def _(event):
                buffer=event.cli.current_buffer
                # buffer.on_text_changed+=lambda *x:buffer.save_to_undo_stack(clear_redo_stack=False)
                buffer.cut_selection()# Overwrite text if we have something selected
                buffer.insert_text(c)
        go(char)
    from rp import regex_match
    def self_dot_var_equals_var(buffer,char_to_insert=None):
        #(upon typing foo)
        #
        #class x:
        #   def __init__(foo):
        #       self.|=
        #
        #    --->
        #
        #class x:
        #   def __init__(foo):
        #       self.foo|=foo

        document=buffer.document
        current_line=document.current_line
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        #Are we donig this shenanagin right now? (Where we do self.foo=foo, and self.bar=bar...etc)
        if not '.' in before_line:return False
        self=before_line.lstrip()[:before_line.lstrip().find('.')]
        if not (before_line.lstrip().startswith(self+'.') and after_line.lstrip().startswith('=')):
            return False

        before_var_name=before_line.lstrip()[len(self+'.'):]#might be blank, but that's OK
        after_var_name=after_line[1:].strip()
        # print("\nbefore_var_name="+before_var_name+', after_var_name='+after_var_name)
        out=before_var_name==after_var_name
        var_name=before_var_name#or after_name, makes no difference

        if out and char_to_insert is not None:
            if char_to_insert =='\b':
                if var_name.strip():
                    assert buffer is not None#internal logic of how you use this function
                    buffer.delete_before_cursor()
                    buffer.cursor_right(len('='+var_name))
                    buffer.delete_before_cursor()
                    buffer.cursor_left(len('='+var_name)-1)
            else:
                assert buffer is not None#internal logic of how you use this function
                buffer.insert_text(char_to_insert)
                buffer.cursor_right(len('='+var_name))
                buffer.insert_text(char_to_insert)
                buffer.cursor_left(len(char_to_insert))
                buffer.cursor_left(len('='+var_name))
        return out
    def setting_index(buffer,char):
        document=buffer.document
        current_line=document.current_line
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        before=document.text_before_cursor
        after= document.text_after_cursor
        if regex_match(before_line,r'.*\[.*=') and after_line==']':
            #a[b=|]  --->  a[b]=|
            if before_line.endswith('=='):
                #But NOT this:
                #a[b==|]  --->  a[b=]=|
                return False
            buffer.delete_before_cursor()
            buffer.cursor_right()
            buffer.insert_text('='+char)
            return True
        return False
    for char in 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm_':#Letter inputs
            def go(char):
                @handle(char)
                def _(event):
                    buffer=event.cli.current_buffer
                    document=buffer.document
                    current_line=document.current_line
                    before_line=document.current_line_before_cursor
                    after_line=document.current_line_after_cursor
                    before=document.text_before_cursor
                    after= document.text_after_cursor
                    if self_dot_var_equals_var(buffer,char) or setting_index(buffer,char):
                        return
                    if char=='m' and meta_pressed() and not before:
                        # ⌥ + m ---> MORE
                        buffer.insert_text('MORE')
                        return
                    if True:#not '"' in after_line and not "'" in after_line:
                        #Jump cursor to headers with special commands following the '\' key
                        #(on press d)
                        #def f():
                        #   return\|
                        #   --->
                        #|def f():
                        #   return
                        def jump_cursor_to_beginning_of_header(command:str='\\de',header:str='def '):
                            if before_line.endswith(command):
                                blines=before.splitlines()[:-1]
                                if any(x.lstrip().startswith(header)for x in blines):
                                    cline=lambda:buffer.document.current_line
                                    buffer.cursor_up()
                                    while not cline().lstrip().startswith(header):
                                        buffer.cursor_up()
                                        buffer.cursor_left(99999)
                                    buffer.cursor_right(99999)
                                    buffer.cursor_right(len(get_indent(cline())))
                                    return
                        header_jump_commands={
                                         '\\de':'def ',
                                         '\\cl':'class ',
                                         '\\if':'if ',#go ...etc
                                         '\\wh':'while ',
                                         '\\fo':'for ',#go f
                                         '\\el':'el'}#go e
                        header_arg_commands={'\\re':'replace','\\py':'python'}
                        header_commands={'\\co':'copy','\\da':'delete all','\\pa':'paste'}
                        header_commands.update(header_jump_commands)
                        header_commands.update(header_arg_commands)

                        for command,header in header_commands.items():
                            key=command[-1]
                            chopped_command=command[:-1]
                            if before_line.endswith(chopped_command) and char==key:
                                buffer.delete_before_cursor(len(chopped_command))
                                if command in header_jump_commands:
                                    jump_cursor_to_beginning_of_header(chopped_command,header)
                                elif command in header_arg_commands:
                                    if header=='replace' and '`' in before_line:
                                        #DEMO: Type
                                        #`foo`bar\r
                                        #into the buffer (with a whole bunch of foo's which will be turned into bar's')
                                        if before_line.count('`')==2:#dumb assumption im makin
                                            arg1=before_line.split('`')[1]
                                            arg2=before_line.split('`')[2].split('\\')[0]
                                            buffer.delete_before_cursor(len(arg1+'`'+arg2+'`'))
                                            text=buffer.document.text.replace(arg1,arg2)
                                            buffer.document=Document(text,buffer.document.cursor_position,buffer.document.selection)
                                    if header=='python' and '`' in before_line:
                                         #DEMO: Type        
                                         #`lambda x:x.replace('foo','bar')\p
                                         #into the buffer (with a whole bunch of foo's which will be turned into bar's')
                                        if before_line.count('`')==1:#give a lambda that takes one argument
                                            arg=before_line.split('`')[1].split('\\')[0]
                                            buffer.delete_before_cursor(len(arg+'`'))
                                            text=buffer.document.text
                                            try:modifier=eval(arg,r_iterm_comm.globa);text=modifier(text);buffer.document=Document(text,buffer.document.cursor_position,buffer.document.selection)
                                            except BaseException as E:buffer.insert_text("\nERROR: "+str(E)+"\n(Undo to make me go away)\n")
                                if header=='copy':
                                    import rp
                                    do_copy(buffer.document.text)
                                if header=='paste':
                                    do_paste(buffer)
                                if header=='delete all':
                                    import rp
                                    buffer.document=Document('',0,buffer.document.selection)
                                            

                                return


                    if char in {'d','c'} and not before_line.strip():
                        above=line_above(buffer)#returns None if there are no above lines
                        if above is not None and get_indent(above)==get_indent(before_line):
                            if above.strip().startswith('@'):#we have a decorator on our hands...
                                #when we're below a decorator and we press d or c, the only valid syntax is to create a 'def' or a 'class' keyword 
                                if char=='d':
                                    if in_class_func_decl(buffer):
                                        #class c:
                                        #   @decorator
                                        #   |
                                        #
                                        #   --->
                                        # 
                                        #class c:
                                        #   @decorator
                                        #   def |(self):
                                        buffer.insert_text('def (self):')
                                        buffer.cursor_left(7)
                                        return
                                    else:
                                        #@decorator
                                        #|
                                        #
                                        #--->
                                        # 
                                        #@decorator
                                        #def |():
                                        buffer.insert_text('def ():')
                                        buffer.cursor_left(3)
                                        return
                                if char=='c':
                                        #@decorator
                                        #|
                                        #
                                        #--->
                                        # 
                                        #@decorator
                                        #class |:
                                        buffer.insert_text('class :')
                                        buffer.cursor_left(1)
                                        return
                    if char=='s':
                            # cl=find_level("class ")#class level
                            # dl=find_level("def ")#def level
                            # dh=find_header("def ")#def header
                            # if cl is not None and dl is not None and dl>cl:
                            #     if '(self' in dh:
                            if meta_pressed():
                                buffer.insert_text('self')
                                return 
                    if regex_match(before_line,r'\s*for _ in range\(\d+'):
                        #(let's say we press Y)
                        #for _ in range(123|):  --->  for _ in range(Y|):
                        buffer.delete_before_cursor(len(before_line.lstrip())-len('for _ in range('))
                        buffer.insert_text(char)
                        return
                    buffer.insert_text(char) 
            go(char)
            meta_pressed()#Reset: we don't want to keep the esc key pressed (this should go after every keystroke. Period. But it doesnt yet cause ima be a lazy...)
    for char in '1234567890':#Digit inputs
        def go(c):
            @handle(c)
            def _(event):
                buffer=event.cli.current_buffer
                if self_dot_var_equals_var(buffer,c) or setting_index(buffer,c):
                    return
                document=buffer.document
                current_line=document.current_line
                before_line=document.current_line_before_cursor
                after_line=document.current_line_after_cursor
                before=document.text_before_cursor
                after= document.text_after_cursor
                #
                if regex_match(before_line,r'\s*for\s+\w+\s+in\s+') and after_line.strip()==':':
                    #(let's say c=3...)
                    #for x in |: --> for x in range(3|):
                    buffer.insert_text('range('+c+')')
                    buffer.cursor_left()
                    return
                if before_line.lstrip()=='for ' and after_line.rstrip()==' in :':
                    #(let's say c=3...)
                    #for | in : --> for _ in range(3|):
                    buffer.insert_text('_')
                    buffer.cursor_right(len(' in '))
                    buffer.insert_text('range('+c+')')
                    buffer.cursor_left()
                    return
                if c=='8' and before_line.lstrip().startswith('def ') and after_line.endswith('):') and before_line.count('(')==1 and endswithany(before_line,'(',',','*'):
                    #Why use the shift key to make kwargs?
                    #(on pressing 8)
                    #def f(|)   --->   def f(*|)
                    #def f(a,b,*|)   --->   def f(a,b,**|)
                    buffer.insert_text('*')
                    return
                if before_line.lstrip()=='def 'and after_line in ['():',':']:
                    #8 is the key that makes the * chracter. We can't start function names with numbers, so let's make this the default...
                    #On press 8:
                    #def |:   --->   def _(*args,**kwargs):|
                    buffer.delete(len(before_line))
                    buffer.insert_text('_(*args,**kwargs):')
                    return
                if before=='ans.' and not after:
                    if ans_dot_completion_string:
                        # Let's say c=3...
                        # (middle 'ans.|' is current state)
                        #   ans(|)   -->   ans.|   -->   ans(.3|)
                        #                   AND
                        #   ans[|]   -->   ans.|   -->   ans[.3|]
                        buffer.delete_before_cursor()
                        buffer.insert_text(ans_dot_completion_string)
                        buffer.cursor_left()
                        buffer.insert_text('.')
                    else:
                        # Let's say c=3...
                        #   ans.|   -->  .3|
                        # This lets use the 'ans.' completion from just typing '.', without sacrificing the ability to type '.4'
                        buffer.delete_before_cursor(len(before))
                        buffer.insert_text('.')
                buffer.insert_text(c)
        go(char)


    # @handle('Ω')
    # def _(event):
    #     import rp.prompt_toolkit.key_binding.bindings.vi as vi 
    #     try:
    #         vi.ryan_go_to_vim_navigation_mode(event)
    #     except:pass
    #
    @handle(Keys.ShiftLeft)
    def _(event):
        """
        Select from the history.
        """
        buffer=event.cli.current_buffer
        before_line=buffer.document.current_line_before_cursor
        if before_line.lstrip():
            #····blah|   --->   ····|blah
            buffer.cursor_left(len(before_line.lstrip()))
        elif before_line:
            #····|blah   --->   |····blah
            buffer.cursor_left(1000000)
        elif buffer.cursor_position:
            buffer.cursor_up()
            move_line_down(buffer)
            buffer.cursor_up()
            buffer.cursor_left(1000000)

    @handle(Keys.ControlBackslash)
    def _(event):
        buffer=event.cli.current_buffer
        pseudo_terminal(merge_dicts(r_iterm_comm.globa,{ans:buffer.document.text}))

    @handle(Keys.ShiftRight)
    def _(event):
        buffer=event.cli.current_buffer
        after_line=buffer.document.current_line_after_cursor
        before_line=buffer.document.current_line_before_cursor    
        if after_line and before_line.strip() or after_line and after_line==after_line.lstrip():
            #····|blah   --->   ····blah|
            buffer.cursor_right(1000000)
        elif after_line:
            #|····blah   --->   ····|blah
            buffer.cursor_right(len(after_line)-len(after_line.lstrip()))
        else:
            move_line_down(buffer)
    def move_line_down(buffer,up=False):
        document=buffer.document
        current_line=document.current_line
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        buffer.cursor_left(1000000)
        if not buffer.cursor_position:
            buffer.delete(2)
        buffer.cursor_right(1000000)
        # print("Ima doing/ it!")
        delete_current_line(buffer)
        buffer.cursor_right(10000)
        buffer.cursor_down(1)
        buffer.cursor_left(10000)
        #region Adaptive indentation: Currently not implemented. Sticking to simplicity.
        if False:
            buffer.insert_line_above(copy_margin=not up)
            buffer.insert_text(current_line.lstrip() if not up else current_line)
            text=buffer.document.text
            lstrip=text.lstrip()
        else:
            buffer.insert_line_above(copy_margin=False)
            buffer.insert_text(current_line)
            lstrip=text=buffer.document.text

        # buffer.cursor_down(1)
        # buffer.cursor_right(1000000)
        buffer.document=Document(lstrip,buffer.document.cursor_position+(len(lstrip)-len(text)),buffer.document.selection)

    #These keys don't respond on the mac terminal
    # @handle(Keys.ShiftUp)
    # def _(event):
    #     print(324982308974078923)
    #     event.cli.current_buffer.cursor_right(1000000)
    #
    # @handle(Keys.ShiftDown)
    # def _(event):
    #     print(324982308974078923)
    #     buffer=event.cli.current_buffer
    #     document=buffer.document
    #     current_line=document.current_line

    @handle(Keys.ControlD)# Duplicate current line Only applies when there's text, else it will trigger the exit
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        buffer.cursor_right(10000)
        current_line=document.current_line
        # buffer.insert_line_below()
        buffer.insert_text("\n"+current_line)

    def delete_current_line(buffer):
        document=buffer.document
        current_line=document.current_line
        buffer.cursor_left(10000)
        firstline=buffer.cursor_position==0
        buffer.delete(len(current_line))
        buffer.delete_before_cursor()
        if firstline:
            buffer.delete()
        else:
            buffer.cursor_down()

    #region Bracket Match Writers
    function_comma_flag=False# Used to keep track of when we are writing arguments to fucntions that were initially parenthesized with the spacebar
    can_take_no_args=False# Doesn't practically matter right now if function_comma_flag is false


    @handle(Keys.ControlDelete)# Delete current line
    def _(event):
        buffer=event.cli.current_buffer
        delete_current_line(buffer)

    #region Bracket Match Writers
    function_comma_flag=False# Used to keep track of when we are writing arguments to fucntions that were initially parenthesized with the spacebar
    can_take_no_args=False# Doesn't practically matter right now if function_comma_flag is false

    @handle('.')
    def _(event):# period '.' event handler function thingy
        buffer=event.cli.current_buffer
        if self_dot_var_equals_var(buffer,'.'):
            #self.foo|=foo   --->   self.foo.|=self.foo.
            return
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        if before_line.endswith('=') and not before_line.endswith('=='):
            #self=|   --->   self.|=   (and then type foo to get self.foo=foo)
            buffer.cursor_left()
            buffer.insert_text('.')
            return
        if not before and not after:
            buffer.insert_text('ans.')
            return
        import rp.r_iterm_comm
        var=rp.r_iterm_comm.last_assignable_comm
        if before.endswith('=') and before[:-1]==var:
            #var=|  -->  var.|
            #You can use a sequence like:
            #  (What you type)   (What rp types)
            #   i numpy np          import numpy as np
            #   np=.array?          np.array?
            buffer.delete_before_cursor()
        if before+after in {'ans[]','ans()'} and after in {']',')'}:
            #ans[|]  -->  ans.|
            #       AND
            #ans(|)  -->  ans.|
            #
            #For space-completing 'ans' then wanting to use a '.', but can't 
            #
            #Edge case: when we want to write ans(.25) where ans is a float-function
            #   This is handled like so:
            #       ans(|)  -->  ans.|  -->  ans(.25)  
            #   Basically, the parenthesis are put back because the character following the '.' is a digit
            #   (This is handled in the digit handler, search for "ans_dot_completion_string")
            buffer.delete()
            buffer.delete_before_cursor()
            global ans_dot_completion_string
            ans_dot_completion_string=before[-1]+after[0]# is either () or []
        buffer.insert_text('.')


    @handle(Keys.Escape)
    def _(event):
        _meta_pressed.append(True)#This is meant to be flipped to false immediately after anything reads it, with meta_pressed(). We're using a list to easily keep track of this after this method is @'d outta this file somewhere else idk where

    @handle(' ')
    def _(event):# Spacebar event
        buffer=event.cli.current_buffer
        single_line = line_above(buffer) is None
        if meta_pressed():#No shenanagins -- just give me a space.
            buffer.insert_text(' ')
            return
        nonlocal function_comma_flag# ,can_take_no_args
        # from rp import mini_terminal
        # exec(mini_terminal)
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor

        if document.text=='':# What else would we possibly want the spacebar for on an empty input? Spacebar invokes functions, and the default variable is ans.
            import rp.r_iterm_comm as ric
            if callable(ric.ans):
                buffer.insert_text('ans()')
                buffer.cursor_left()
                function_comma_flag=True
            elif hasattr(ric.ans,'__getitem__'):#if we can do ans[0], ans[1] etc
                buffer.insert_text('ans[]')#we cant call it...might want to iterate through it though!
                buffer.cursor_left()
                function_comma_flag=True
            else:
                buffer.insert_text('ans')#Bleh it's boring
            return


        if before.startswith('!'):# Don't do anything special
            buffer.insert_text(' ')
            return

        before_line=before.split('\n')[-1]# all on same line, but before cursor
        after_line=after.split('\n')[0]# ditto but after cursor
        if before_line.lstrip().startswith('class ') and after_line.startswith(':'):
            #class c|:   --->   class c(|):
            buffer.insert_text('()')
            buffer.cursor_left()
            return
        if before_line.lstrip().startswith('class ') and after_line.startswith('):'):
            if before_line.endswith(','):
                #class c(x,|):   --->   class c(x):|
                buffer.delete_before_cursor()
                buffer.cursor_right(2)
                return
            if before_line.endswith('('):
                #class c(|):   --->   class c:|
                buffer.delete_before_cursor()
                buffer.delete()
                buffer.cursor_right()
                return
        if before_line.lstrip().startswith('def '): 
            if before_line.endswith('def __') and after_line.startswith('__(self):'):
                #class x:
                #   def __|__(self):
                # 
                #   --->
                # 
                #class x:
                #   def __init__(self|):
                buffer.insert_text('init')
                buffer.cursor_right(7)
                return
            if before_line.strip()=='def' and after_line.startswith('(self):'):
                #class x:
                #   def |(self):
                # 
                #   --->
                # 
                #class x:
                #   def __|__(self):
                buffer.insert_text('____')
                buffer.cursor_left(2)
                return
            if after_line.startswith('__(self):'):
                #class x:
                #   def __eq|__(self):
                # 
                #   --->
                # 
                #class x:
                #   def __eq__(self|):
                if before_line.endswith('__'):
                    #autocomplete might have messed things up, this is a sloppy hack to fix that...
                    #def __eq__|__(self):   --->   #def __eq__(self|): 
                    buffer.delete_before_cursor(2)
                buffer.cursor_right(7)
                return
            if after_line.startswith('(self):'):
                #def f|(self):   --->   def f(self,|):
                buffer.cursor_right(5)
                buffer.insert_text(',')
                return
            if before_line.endswith(':') and not after_line.strip():
                #def f(x):|   --->   def f(x):return |
                buffer.insert_text('return ')
                return
            if before_line.strip()=='def __' and after_line.startswith('__(self):'):
                #class x:
                #   def __|__(self):
                # 
                #   --->
                # 
                #class x:
                #   def __init__(self|):
                buffer.insert_text('init')
                buffer.cursor_right(7)
                return
            if before_line.strip()=='def' and after_line.startswith('():'):
                def on_first_line():
                    return '\n' not in (before+after)
                function_title='ans' if on_first_line() else '_'
                #def |():   --->   def _(|):   (sometimes, when using decorators, you want an anonymous function)
                #def |():   --->   def ans(|): (if we're defining a function on the first line, perhaps we want to use it as our answer? I haven't actually used this yet; it's just an idea, I'll see how much I like it...)
                buffer.insert_text(function_title)
                buffer.cursor_right(1)
                return
        if before_line.strip()=='def' and not after_line.strip().endswith(':'):
            buffer.insert_text(' :')
            buffer.cursor_left()
            return
        if before_line.strip().startswith('def ') and endswithany(before_line.strip(),',','(') and after_line.strip()=='):':
            if before_line.endswith(','):
                buffer.delete_before_cursor()
            buffer.cursor_right(2)#If we want a one-line function
            return
        if self_dot_var_equals_var(buffer):
            #self.|foo=foo   --->   self.foo=foo|
            buffer.cursor_right(999999)
        from rp import is_namespaceable,space_split
        if before_line.strip().startswith('def ') and len(space_split(before_line.strip()))==2:
            if after_line.strip()==':' and is_namespaceable(before_line.split(' ')[-1]):
                buffer.insert_text('()')
                buffer.cursor_left()
                return
        if after_line=='):' and before_line.endswith(','):
            buffer.delete_before_cursor()
            buffer.cursor_right(2)
            return
            #for x in range(5,|):   --->   for x in range(5):|
        if before_line.endswith(' imoprt') or before_line.startswith("imoprt"):# This is a really common typo for me
            buffer.delete_before_cursor(6)
            buffer.insert_text('import ')
            return
        from rp import regex_match
        if regex_match(before_line.lstrip(),r'for\s+\w+\s+in\s+len'):
                #(Also implemented upon pressing '(')
                #for x in len|   -->  for x in range(len(|))
                buffer.delete_before_cursor(3)
                buffer.insert_text('range(len())')
                buffer.cursor_left(2)
                return
        if before_line.lstrip()=='if ' and after_line.rstrip()==':':
            #if |:   --->   import |
            buffer.delete_before_cursor(3)
            buffer.insert_text('import ')
            buffer.delete()
            return
        if before_line.lstrip()=='import ' and not after_line.rstrip():
            #import |   --->   if |:
            buffer.delete_before_cursor(len('import '))
            buffer.insert_text('if :')
            buffer.cursor_left()
            return
        # if before_line.lstrip()=='for ' and after_line==' in :':
        #     #"for | in :"  --->  "for _ in |:"
        #     buffer.insert_text('ans')
        #     return
        if regex_match(before,r'\s*for\s+\w+\s+in\s+') and after.strip()==':':
            #"for x in |:"  --->  "for x in ans:"
            #(better alternative than "for x in |:" ---> "for x in:|", which is in the next block...)
            buffer.insert_text('ans')
            return
        elif starts_with_any(before_line.lstrip(),'if ','for ','while ') and before_line.endswith(' ') and after_line.rstrip()==':':# This is a really common typo for me
            #if x|:   --->   if x:|
            buffer.delete_before_cursor(1)
            buffer.cursor_right(2)
            return
        from rp import space_split,is_namespaceable
        import rp.r_iterm_comm as r_iterm_comm
        split=space_split(before_line)
        from rp import printed
        from_or_import_on_beginning_of_line=before_line.lstrip().startswith("import ") or before_line.lstrip().startswith("from ")
        def is_callable_token(token_name):
            try:
                return callable(eval(token_name,r_iterm_comm.globa))
            except:
                return False#be on the safe side with space-function completions
        try:
            function_comma_flag=function_comma_flag and( after_line.startswith(")") or after_line.startswith("'") or after_line.startswith('"') or after_line.startswith(']') or after_line.startswith(']') )
            token_of_interest=name_of_interest=None
            try:
                # fansi_print("\n\n"+split[-1]+"\n\n")

                string=''
                for char in reversed(before_line):
                    if not is_namespaceable(char) and char not in '.':
                        break
                    string=char+string
                name_of_interest=string
                token_of_interest=eval(string,r_iterm_comm.globa)  # ≣token_of_interest=r_iterm_comm.rp_evaluator(string,True)# Should be just a name so there should be no side effects

                #
                # for char in string:
                #     if not char.isalnum() and char not in '.' and not is_namespaceable(char):
                #         string=string.replace(char,' ')
                # name_of_interest=string
                # token_of_interest=eval(string,r_iterm_comm.globa)# ≣token_of_interest=r_iterm_comm.rp_evaluator(string,True)# Should be just a name so there should be no side effects
            except:pass
            from rp import regex_match
            def is_autocompletable_prefix(big,suffixes=[''],allow_single_liner=True,use_name_of_interest=False):
                #leave suffixes [] or None to allow any suffix
                if not allow_single_liner:
                    if '\n' not in before+after:
                        return False
                if use_name_of_interest:
                    name=name_of_interest
                else:
                    name=before_line.strip()
                return big.strip() != name and big.startswith(name) and before_line.strip() and (not suffixes or after_line in suffixes)#Shouldn't trigger when r is a function, because of where this is in the elif chain
            def autocomplete_prefix(big,left=1,remove_suffix=False):
                if remove_suffix:#used in 'except|:' --> 'except | as :', which is also 'except|' --> 'except | as :'
                    buffer.cursor_right(len(after_line))
                    buffer.delete_before_cursor(len(after_line))
                buffer.insert_text(big[len(name_of_interest):])
                buffer.cursor_left(left)
                try_to_autounindent(buffer)

            def try_autocompleting_functions(N,not_just_functions=False):
                from rp import ring_terminal_bell
                # if not_just_functions:
                    # ring_terminal_bell
                #TODO: right now not_just_functions doesn't do anything, it's supposed to let you space complete functions while importing
                nonlocal before_line,after_line,before,after

                #go through the top N current autocompletion results, and if one of them is callable, call it.
                # if before.count(' ')+before.count('\n')>1:
                    # return False #Don't autocomplete like this unless we are doing a one-liner
                bs=before_line.lstrip()#Before Strip  (bs)
                if not not_just_functions:
                    if not '\n' in before.strip() and before.strip().isupper() or beginswithany(bs,'import ','from ','def ') or 'lambda' in bs:#Basically, any place we're allowed to declare new variable names, we shouldn't be autocompleting them. lambda is bit tricky so I'm just sayig 'no space function completion on lines that contain lambda'.
                        return False#We might be typing something like 'UNDO ALL', in which case we do NOT want the 'UNDO' to be autocompleted
                import rp.r_iterm_comm as ric
                for candidate in ric.current_candidates:#Don't autocomplete if our current word to complete allready exists. For example, don't complete 'in' into 'inverse', etc.
                    try:
                        if hasattr(candidate,'text') and candidate.text==name_of_interest or candidate==name_of_interest:
                            return False
                    except:pass
                # ring_terminal_bell()
                # print(ric.current_candidates)
                if not_just_functions:
                    if not ric.current_candidates:
                        return False 
                    buffer.delete_before_cursor(len(name_of_interest))#erase the current line
                    #space completions: 
                    #import num|   --->   import numpy as |
                    #(etc)
                    space_completion=ric.current_candidates[0]
                    if before_line.endswith(space_completion):
                        return False#Problem avoided: Used to be 'import cv2|' ---> 'import cv2cv2 as |s'
                    #region Erase before and after so we don't do stupid things: Example, on autocompleting 'print', we want:
                    #   'pr|i'  --->  'print|'
                    #       and NOT
                    #   'pr|i'  --->  'prprint|i'
                    if is_namespaceable(space_completion):
                        #Allready taken care of in above line commented "erase the current line"
                        # while before_line and before_line[-1] in space_completion:
                        #     buffer.delete_before_cursor()
                        #     before_line=before_line[:-1]
                        #     before     =before     [:-1]
                        while after_line  and  after_line[ 0] in space_completion:
                            buffer.delete()
                            after_line =after_line [1: ]
                            after      =after      [1: ]
                    #endregion
                    buffer.insert_text(space_completion)
                    return True 
                for x in ric.current_candidates[:N]:
                    if is_callable_token(x) or not_just_functions and not (after_line.strip()=='():' and before_line.rstrip().startswith('def ')):
                        buffer.delete_before_cursor(len(name_of_interest))#erase the current line
                        buffer.insert_text(x+('' if  not_just_functions else '()'))
                        buffer.cursor_left()
                        nonlocal function_comma_flag
                        function_comma_flag=True
                        return True
            if before_line.lstrip().startswith('def ') and before_line.endswith("=lambda")and after_line.startswith(')'):#When passing a lambda as an argument in a function definition default value (a nichey case, but important nevertheless), add a space so the rest of the program knows its a lambda (which it uses spaces to see)
                buffer.cursor_left(6)
                buffer.insert_text(' ')
                buffer.cursor_right(6)

            if not from_or_import_on_beginning_of_line and not before_line.endswith(" ") and callable(token_of_interest)  and not (after_line.strip()=='():' and before_line.rstrip().startswith('def ')):
                function_comma_flag=True
                import inspect
                # try:
                #     can_take_no_args=len(inspect.getfullargspec(token_of_interest).args)==0
                # except:# Probably a builtin function
                #     can_take_no_args=0 or token_of_interest is print
                buffer.insert_text('()')
                buffer.cursor_left(count=1)
            # region Brackets....they work but conceptually they're annoying.
            # elif not from_or_import_on_beginning_of_line and not before_line.endswith(" ") and hasattr(token_of_interest,'__getitem__'):
            #     buffer.insert_text('[]')
            #     buffer.cursor_left(count=1)
            #endregion

            elif regex_match(before_line.lstrip(),r'(from .*)|(import \w*)') and try_autocompleting_functions(N=1,not_just_functions=True):
                if(before_line.lstrip().startswith('from ')):
                    buffer.cursor_right(len(' import'))
                    buffer.insert_text(' ')
                elif(before_line.lstrip().startswith('import ')):
                    buffer.insert_text(' as ')#Without this, space would be redundant with respect to tab
            elif regex_match(before_line.lstrip(),r'from \w* import '):
                #'from rp import |'  -->  'from rp import *'
                buffer.insert_text('*')
            elif regex_match(before_line.lstrip(),r'from \w* import \*'):
                #'from rp import *|'  -->  'from rp import '
                buffer.delete_before_cursor()



            elif name_of_interest in {'l','la','lam','lamb','lambd','lambda'} and not 'import 'in before_line and not before_line.lstrip() in {'for '+name_of_interest,'with '+name_of_interest}:
                #Make a lambda from l
                #Shouldn't trigger when l is a function, because of where this is in the elif chain
                noil=len(name_of_interest)#noil stands for ((name of interest) length)
                if before_line.strip()!=name_of_interest:#don't do this at the beginning of an empty line
                    buffer.cursor_left(noil)
                    if not buffer.document.text_before_cursor.endswith(' '):
                        buffer.insert_text(' ')
                    buffer.cursor_right(noil)
                buffer.insert_text('lambda :'[noil:])
                buffer.cursor_left()
            elif regex_match(before_line.strip(),r'(for .* in in)') and after_line.strip()==':':
                buffer.delete_before_cursor(2)
            elif regex_match(before_line.strip(),r'(from \w* import import)') and after_line.strip()=='':
                buffer.delete_before_cursor(len('import'))
            elif before_line.endswith('lambda:'):
                #The default, most boring kind of lambda...
                #"lambda:|"   --->  "lambda:None|"
                buffer.insert_text('None')

            #None of the 'is_autocompletable_prefix's ahead should trigger when the prefix is a function, so as not to interfere with normal autocompletion in most cases
            elif is_autocompletable_prefix('def ():'):
                if in_class_func_decl(buffer):  autocomplete_prefix('def (self):',left=7)
                else:           autocomplete_prefix('def ():',left=3)
            elif before_line.lstrip().startswith('def ') and after_line.rstrip().endswith('):') and after_line.startswith('('):buffer.cursor_right()


            elif before_line.lstrip()=='else:'and not after_line.strip():
                #else:|   --->   elif |:
                buffer.delete_before_cursor(len('else:'))
                buffer.insert_text('elif :')
                buffer.cursor_left()
            elif before_line.lstrip()=='elif 'and after_line.rstrip()==':':
                #elif:|   --->   else:
                buffer.delete_before_cursor(len('elif '))
                buffer.insert_text('else')
                buffer.cursor_right()
            elif before_line.lstrip()=='f' and not after_line.strip() and single_line:
                #f|   --->   from | import         ONLY ON ONE-LINERS
                buffer.insert_text('rom  import')
                buffer.cursor_left(len(' import'))
            #Note that this was created after some other things in this file, and might even be redundant sometimes. For example, 'if'-->'if |:' is allready covered elsewhere in key_bindings.py
            elif is_autocompletable_prefix('return ',allow_single_liner=False):autocomplete_prefix('return ',left=0)
            elif is_autocompletable_prefix('while :'):autocomplete_prefix('while :')
            elif is_autocompletable_prefix('class :'):autocomplete_prefix('class :')
            elif is_autocompletable_prefix('for  in :'):autocomplete_prefix('for  in :',left=5)
            elif not (before=='i' and not after) and is_autocompletable_prefix('if :'):autocomplete_prefix('if :',left=1)#'i|' ---> 'if |:' ONLY IF we've typed something else in this buffer allready (often, I dedicate an input line to nothing but importing something)
            elif is_autocompletable_prefix('import '):autocomplete_prefix('import ',left=0)
            elif is_autocompletable_prefix('from  import'):autocomplete_prefix('from  import',left=7)
            elif is_autocompletable_prefix('elif :',allow_single_liner=False):autocomplete_prefix('elif :',left=1)
            elif is_autocompletable_prefix('else:',allow_single_liner=False):autocomplete_prefix('else:',left=0)
            elif is_autocompletable_prefix('try:'):autocomplete_prefix('try:',left=0)
            # elif is_autocompletable_prefix('True ',suffixes=[' ']):autocomplete_prefix('True ',left=0)
            # elif is_autocompletable_prefix('False ',suffixes=[' ']):autocomplete_prefix('False ',left=0)
            elif is_autocompletable_prefix('break',allow_single_liner=False):autocomplete_prefix('break',left=0)
            elif is_autocompletable_prefix('continue',allow_single_liner=False):autocomplete_prefix('continue',left=0)
            elif is_autocompletable_prefix('yield ',allow_single_liner=False):autocomplete_prefix('yield ',left=0)
            elif before_line.lstrip()!='yield' and is_autocompletable_prefix('yield from ',allow_single_liner=False):autocomplete_prefix('from ',left=0)
            # elif is_autocompletable_prefix('print()'):autocomplete_prefix('print()',left=1)#not a keyword, but used so frequently...
            elif is_autocompletable_prefix('assert '):autocomplete_prefix('assert ',left=0)
            elif is_autocompletable_prefix('raise '):autocomplete_prefix('raise ',left=0)

            elif is_autocompletable_prefix('print()',allow_single_liner=True):autocomplete_prefix('print()',left=1)
            elif is_autocompletable_prefix('pass',allow_single_liner=False):autocomplete_prefix('pass',left=0)

            elif is_autocompletable_prefix('except :',allow_single_liner=False):autocomplete_prefix('except :',left=1)
            elif is_autocompletable_prefix('with :'):autocomplete_prefix('with :',left=1)
            elif enable_space_autocompletions and not regex_match(before_line.lstrip(),r'(def .*)|(for \w*)') and not name_of_interest.isdigit() and name_of_interest and try_autocompleting_functions(N=20):pass#"not name_of_interest.isdigit() and name_of_interest " because '5' --> 'display_color_255' without it, which is REALLY annoying
            # elif is_autocompletable_prefix('except :',[':','']):autocomplete_prefix('except :',left=1,remove_suffix=True)
            # elif is_autocompletable_prefix('except  as :',[':','']):autocomplete_prefix('except  as :',left=5,remove_suffix=True)
            elif before_line.lstrip()=='except ' and after_line.rstrip()==':':
                buffer.delete_before_cursor()
                buffer.cursor_right()
                return
            elif before_line.endswith(' is '):
                #"x is |" --> "x is not |"
                buffer.insert_text('not ')
                return
            elif before_line.endswith(' is not '):
                #"x is not |" --> "x is |"
                buffer.delete_before_cursor(4)
                return
            elif before_line.lstrip()=='yield from ':
                #"yield from |" --> "yield |"
                buffer.delete_before_cursor(len('from '))
                return
            elif before_line.lstrip().startswith('except') and before_line.strip().endswith(":") and not after_line.rstrip():
                buffer.insert_text('pass')
                return
            elif starts_with_any(before_line.lstrip(),'except ','with ') and before_line.endswith(' as ') and after_line.strip()==':':
                #except A as |:   --->   except A:|
                buffer.delete_before_cursor(len(' as '))
                buffer.cursor_right()
            elif before_line.lstrip().startswith('except ') and not '(' in before_line:#not '(' in before_line because it won't properly complete functions for some reason inside the 'except' lines
                if before_line.lstrip()=='except ' and after_line.rstrip()==' as :':
                    #'except | as :' --> 'except|:'
                    buffer.cursor_right(len(' as '))#leave the ':' alone
                    buffer.delete_before_cursor(len(' as '))
                    buffer.delete_before_cursor()
                else:
                    if after_line==' as :':
                        #'except stuff | as :' --> 'except stuff as |:'
                        buffer.cursor_right(4)
                    elif after_line==':' and not ' as ' in before_line and not before_line.endswith('as'):
                        if before_line.endswith(' '):
                            buffer.delete_before_cursor()#when we have two spaces because of a function '()' --> ' '
                        if before_line.lstrip()=='except ':
                            buffer.delete_before_cursor()
                        else:
                            buffer.insert_text(' as ')
                        # buffer.cursor_right(0)
                    else:
                        buffer.insert_text(' ')
            elif before_line.lstrip().startswith('except ') and before_line.endswith('(') and after_line.startswith(')'):
                #except Exception()|:   -->   except Exception as |:
                buffer.cursor_right()
                buffer.delete_before_cursor(2)
                buffer.insert_text(' as ')
            elif before_line.lstrip().startswith('for ') and after_line.rstrip()==' in :':
                if before_line.lstrip()=='for ':#if we haven't given any variable name to iterate yet, switch to the 'from' shortcut instead because from and for both start with f
                    #Switch between 'for' and 'from'
                    buffer.cursor_right(len(' in :'))
                    buffer.delete_before_cursor(len('for '+' in :'))
                    buffer.insert_text('from  import')
                    buffer.cursor_left(len('import '))
                    return
                #Shouldn't trigger when r is a function, because of where this is in the elif chain
                buffer.cursor_right(4)
            elif before_line.endswith('lambda ')and after_line.startswith(':'):
                buffer.delete_before_cursor()
                buffer.cursor_right()
            elif before_line and after_line and before_line[-1]+after_line[0] in ['()','[]','{}']:
                if document.text in ['ans()','ans[]']:
                    buffer.delete()
                    buffer.delete_before_cursor(count=40000)
                    buffer.insert_text(' ')
                    return
                if '\n' not in before and after==')':
                    #'print()|' --> 'print(ans,|)'
                    #NOTE that upon hitting the enter key, the extra comma dissapears ('print(a,b,c,ans,|)'   --->   'print(a,b,c,ans)')
                    buffer.insert_text('ans,')
                    return
                buffer.cursor_right(count=1)
                buffer.delete_before_cursor(count=2)
                # if can_take_no_args:
                #     if function_comma_flag:
                #             buffer.insert_text(',')
                #     else:
                #             buffer.insert_text('(),')
                # else:
                #     if function_comma_flag:
                #         buffer.insert_text(',')
                #     else:
                #         buffer.insert_text(' ')
                if function_comma_flag and after_line.startswith("))"):
                    buffer.insert_text(',')
                else:
                    buffer.insert_text(' ')
            elif function_comma_flag and after_line.startswith(')'):
                if before_line.endswith(","):
                    if '\n' not in before and after==')':#(meant for one-liners, not multiliners. I wanted a convenient way to write ans into functions like this.)
                        #print(a,b,c,|) --> print(a,b,c,ans,|)
                        buffer.insert_text('ans,')
                        #NOTE that upon hitting the enter key, the extra comma dissapears ('print(a,b,c,ans,|)'   --->   'print(a,b,c,ans)\n|')
                    else:
                        #print(|) --> print
                        buffer.delete_before_cursor()
                        buffer.cursor_right()
                        if after_line.startswith("))"):
                            #print(f(|)) --> print(f(),|)
                            buffer.insert_text(',')
                elif before_line.endswith("lambda"):#special case to detect and space-autocomplete lambda syntax inside functions (normally, space in a function would make a comma; but we want print(lambda|) to go to print(lambda |:), not print(lambda,|))

                    buffer.cursor_left(count=6)
                    rev=document.text_before_cursor[::-1]
                    buffer.insert_text(' ')#This space is just an easy patch to let lambdas be easily put inside function arguments (before it was kinda annoying and didnt work well but not it does. yay. )
                    buffer.cursor_right(count=6)
                    buffer.insert_text(' :')
                    buffer.cursor_left(count=1)
                else:
                    buffer.insert_text(',')
            elif not after_line and all(is_namespaceable(x) for x in split) and len(split)==2 and split[0]=='def':
                buffer.insert_text('():')
                buffer.cursor_left(count=2)
            elif (before_line.lstrip() in['if','while','for','with','try','except'] or split and  name_of_interest=='lambda') and not after_line.strip().startswith(":"):
                buffer.insert_text(' :')
                buffer.cursor_left(count=1)
            elif before_line and after_line and before_line[-1]==','and after_line[0]==':':# for after lambda x,a,b,c,cursor:
                buffer.delete_before_cursor(count=1)
                buffer.cursor_right(count=1)
                buffer.insert_text(' ')

            elif len(split)>=2 and split[-2]=='lambda' and ':'not in name_of_interest or after_line=='):' and not before_line.rstrip().endswith(','):# new argument in def
                buffer.insert_text(',')#Re-reading this later, suspicious that this block MIGHT never be reached in practice?
            elif before_line.lstrip()=='i':#Quick shortcut for importing. Type 'i' then press space. THis should only come after checking if i is a function, which should happen in some other if/else case above this line.
                #"i|" --> "import |"
                buffer.insert_text('mport ')
            elif before_line.lstrip()=='f':#Quick shortcut for 'from * import * style importing'. Type 'f' then press space.
                #"f|" --> "from | import"
                buffer.insert_text('rom  import')
                buffer.cursor_left(7)
            elif not after_line and (before_line.lstrip().startswith('import ') or before_line.lstrip().startswith('from ')):
                if before_line.endswith(' as'):
                    #for when the user doesn't know about or forgets about the 'as' autocompletion, so we don't end up with 'as as'
                    #'import x as as|'  -->  'import x as |'
                    buffer.delete_before_cursor(2)
                    buffer.insert_text('')#To trigger autocompletion
                    return
                if before_line.endswith(','):
                    #'import x,'  -->  'import x, |'
                    #Weird behavior if we don't do this an the user manually puts a comma without a space before this function would
                    buffer.insert_text(' ')
                    return
                #not after_line, so we're at the end of the line, which means we are done inputting the module name after 'from' or 'input'
                l=space_split(before_line)
                allready_end_with_an_as=len(l)>=2 and l[-2]=='as'
                if before_line.endswith(' as '):
                    #import x as | --> import x,|
                    buffer.delete_before_cursor(4)
                    buffer.insert_text(', ')
                elif before_line.rstrip().endswith(','):
                    #import x,| --> import x as |
                    buffer.delete_before_cursor(2)
                    # if allready_end_with_an_as:
                        # return
                    # buffer.insert_text(' as ')
                elif 'import ' in before_line:#to protect against "from x|" --> "from x as |" if we decide to type out the whole thing (naively)
                    #import x| --> import x as |
                    buffer.insert_text(', ' if allready_end_with_an_as else ' as ')#We default to the ' as ' instead of ',' because ' as ' starts with a space, which is the key we pressed. This is as opposed to functions, which default to using the comma on space by default.
                else:
                    buffer.insert_text(' ')
            elif before_line.lstrip().count(' ')==1 and before_line.lstrip().startswith('from ') and after_line==' import':#Quick shortcut for 'from * import * style importing'. Type 'f' then press space.
                # "from *| import" --> "from * import |"
                if before_line.lstrip()=='from ' and after_line.startswith(' import'):#we have no module name specified yet
                    #Switch between 'for' and 'from'
                    buffer.cursor_right(len(' import'))
                    buffer.delete_before_cursor(len('from '+' import'))
                    buffer.delete_before_cursor(13)
                    buffer.insert_text('for  in :')
                    buffer.cursor_left(len(' in :'))
                    return
                buffer.cursor_right(7)
                buffer.insert_text(' ')
            elif starts_with_any(before_line.lstrip(),'for ','except ') and after_line==':':#If we want a one-line if, elif, etc.
                if before_line.lstrip not in ['for ','except ']:#make sure it's not empty; we don't want to override completion etc
                    buffer.cursor_right(1)#Note that we exclude things we'd normally want to say, like "if x in y:"
                    buffer.insert_text('')#To trigger autocompletion
                    return
                
            else:
                buffer.insert_text(' ')
            buffer.insert_text('')#To trigger autocompletion

        except Exception as e:
            from rp import print_stack_trace
            print_stack_trace(e)

    @handle("?")
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before=document.text_before_cursor
        # after= document.text_after_cursor

        # before_line=before.split('\n')[-1]# all on same line, but before cursor
        # after_line=after.split('\n')[0]# ditto but after cursor
        if before.endswith('='):
            #x=| --> x?   (meant because I often want to use ? on something that I've just imported, and this is a small, stable way to do it)
            buffer.delete_before_cursor()
        buffer.insert_text('?')
    @handle("!")
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before=document.text_before_cursor
        if not before:
            buffer.insert_text('!')
            return

        # after= document.text_after_cursor

        before_line=before.split('\n')[-1]# all on same line, but before cursor
        # after_line=after.split('\n')[0]# ditto but after cursor
        if len(before)<3 and not (before_line.count("'")%2 or before_line.count('"')%2):#not in a string
            #if not in the beginning (for a ! or !! shell command) and not in string, the only time we'd want ! is for !=
            buffer.insert_text('!=')
            return
        buffer.insert_text('!')
    @handle(":")
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor

        before_line=before.split('\n')[-1]# all on same line, but before cursor
        after_line=after.split('\n')[0]# ditto but after cursor
        if after_line==':':
            buffer.cursor_right(count=1)
        else:
            buffer.insert_text(':')
    @handle('=')
    def _(event):
        import rp.r_iterm_comm as r_iterm_comm

        buffer=event.cli.current_buffer
        document=buffer.document
        #
        before=document.text_before_cursor
        after= document.text_after_cursor
        before_line=before.split('\n')[-1]# all on same line, but before cursor
        after_line=after.split('\n')[0]# ditto but after cursor

        for l,r in {'()','[]'}:
            if before_line.endswith(r) and before_line.count(l)<=before_line.count(r) and not after_line:
                #The ')=' operator
                #alpha)|   --->   alpha=|(alpha)
                #foo(bar)[0])|   --->   foo(bar[0])=|(foo(bar[0]))
                buffer.delete_before_cursor()
                arg='='+l+before_line.lstrip()
                buffer.insert_text(arg)
                buffer.cursor_left(len(arg))
                buffer.cursor_right()
                return

        if starts_with_any(before_line.lstrip(),'elif','if','while'):
            # if x==y:
            #     blah
            # elif |: —> elif x==|:
            #
            # AND a cooler use-case: (because it only copies the variable from the same indent layer)
            #   if x==5:
            #       if y==6:
            #           pass
            #   elif x==7:
            #       if y==7:
            start=None
            starts={'elif','if','while'}
            for x in starts:
                if before_line.strip()==x:
                    indent=before_line[:before_line.find(x)]
                    start=x
            if start is not None:
                assert before_line.startswith(indent)
                i=-2
                try:
                    while True:
                        match=before.split('\n')[i]
                        # if match[:len(indent)].strip():#If wrong indentation level. This check is kinda rigid, maybe it would be nice to not have it...
                            # break
                        for match_start in starts:
                            if match.startswith(indent+match_start) and '==' in match:
                                match=match[match.find(match_start)+len(match_start):]
                                match=match[:match.find('==')]
                                match=match.strip()
                                if before_line[-1].strip():
                                    buffer.insert_text(' :')
                                    buffer.cursor_left()
                                buffer.insert_text(match+'==')
                                return
                        i-=1
                    return
                except:pass
        if starts_with_any(before_line.lstrip(),'if ','elif ','while ','not ','assert ') and\
                not (before_line.count("'")%2 or before_line.count('"')%2):#not in a string
            #if x|:  -->  if x==|:
            #   and
            #if x==|:  -->  if x==|:
            if before_line.endswith('!'):
                buffer.insert_text('=')
                return
            if not before_line.endswith('==') or before_line.endswith('!='):
                buffer.insert_text('==')
            return




        char_operators=['','+','-','*','/','%','//','**','&','|','^','>>','<<','~']
        letter_operators=['and','or','not','==','!=','>=','<=']
        var=r_iterm_comm.last_assignable_comm
        if endswithany(before_line.lstrip(),'.','(','['):# the .=, (=, and [= operators
            if before_line.lstrip()=='ans.':
                #Prevent: '|' --> 'ans.|' --> 'ans=ans.'
                #Because last_assignable_comm is more useful in this case.
                buffer.delete_before_cursor(4)
                buffer.insert_text('.')
                document=buffer.document
                before_line=document.current_line_before_cursor
                before     =document.text_before_cursor
            #x.=y --> x=x.y
            #x.|  --> x=x.|
            #AND
            #x(|) --> x=x(|)
            #x[|] --> x=x[|]
            operator=before_line.lstrip()[-1]
            buffer.delete_before_cursor(count=1)
            assign_to=before_line.lstrip()
            if var and not assign_to[:-1]:
                #.|  -->  ans=ans.|
                buffer.insert_text(var+'='+var+operator)
                return
            buffer.insert_text("="+assign_to)
        elif before=='ans('and after==')':# Space + equals -> import torch;
            buffer.delete()
            buffer.delete_before_cursor(count=1000)
            buffer.insert_text("ans="+str(var))

        elif var and before==var+"=":
            buffer.delete_before_cursor(count=1000)
            buffer.insert_text("==")

        elif var and not after and before in letter_operators:# User hasn't typed anything in yet
            buffer.cursor_left(count=10000)
            buffer.insert_text(var)
            buffer.insert_text("=")
            buffer.insert_text(var)
            if before.isalpha():# and, or, not
                buffer.insert_text(" ")# We need a space
            buffer.cursor_right(count=10000)
        elif var and not after and before in char_operators:# User hasn't typed anything in yet
            buffer.cursor_left(count=10000)
            buffer.insert_text(var)
            buffer.cursor_right(count=10000)
            buffer.insert_text('=')
        else:
            buffer.insert_text('=')

    import os
    if os.name != 'nt':#If we are NOT running windows, which screws EVERYTHING up...
        # @handle(Keys.ControlC)
        # def _(event):
        #     buffer=event.cli.current_buffer
        #     # document=buffer.document
        #     # before=document.text_before_cursor
        #     # after= document.text_after_cursor
        #     buffer.insert_text('RETURN')
        @handle(Keys.ControlH)
        def _(event):
            buffer=event.cli.current_buffer
            buffer.insert_text('HISTORY')
        @handle(Keys.ControlU)
        def _(event):
            buffer=event.cli.current_buffer
            buffer.insert_text('UNDO')
        @handle(Keys.ControlP)
        def _(event):
            buffer=event.cli.current_buffer
            buffer.insert_text('PREV')

    def move_arg(buffer,delta_positions:int):
        assert delta_positions in {1,-1}
        document=buffer.document
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor

        def chop_at_parenthesis_level(s:str,l:int):
            n=0
            for i,c in enumerate(s):
                if c in '([{':n+=1
                if c in '])}':n-=1
                if n==l:return s[:i]
            return s

        after_line=chop_at_parenthesis_level(after_line,-1)#Count and match parenthesis (we want 'A(B)(C)D)E' --> 'A(B)(C)D') (when we're dealing with after_line)
        before_line=before_line[::-1]
        before_line=chop_at_parenthesis_level(before_line,1)
        before_line=before_line[::-1]


        bargs=before_line.split(',')
        aargs=after_line.split(',')
        aarg=aargs[0]
        barg=bargs[-1]
        laarg=len(aarg)
        lbarg=len(barg)
        arg=barg+aarg
        larg=len(arg)

        def erase_arg():
            buffer.delete_before_cursor(lbarg)
            buffer.delete              (laarg)

        if delta_positions==1:
            if not ',' in after_line:return#Otherwise we glitch and delete the rest of it
            if len(aargs)==1:return
            erase_arg()
            buffer.delete()
            buffer.cursor_right(len(aargs[1]))#Shouldn't get index error if called properly (where cursor is AFTER a comma)
            buffer.insert_text(','+arg)
            buffer.cursor_left(larg)
        if delta_positions==-1:
            # if not ',' in after_line:return#Otherwise we glitch and delete the rest of it
            #     buffer.delete_before_cursor()
            #     buffer.delete(laarg)
            #     buffer.cursor_left(lbarg)
            #     buffer.insert_text(arg+',')
            erase_arg()
            buffer.delete_before_cursor()
            buffer.cursor_left(len(bargs[-2]))
            buffer.insert_text(arg+',')
            if len(bargs)>2:
                buffer.cursor_left(larg+1)




    @handle('<')
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        if before_line.endswith(','):
            #Swap arguments around parenthesis! (Warning: Doesn't handle parenthesis inside strings as an edge case)
            #(apple,f(x),|['bananna'])   --->   (apple,|['bananna'],f(x))
            try:move_arg(buffer,-1)
            except:print("JAM")
            return
        buffer.insert_text('<')
    @handle('>')
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        if before_line.endswith(','):
            #Swap arguments around parenthesis! (Warning: Doesn't handle parenthesis inside strings as an edge case)
            #(apple,|f(x),['bananna'])   --->   (apple,['bananna'],f(x))
            try:move_arg(buffer,1)
            except:print("JAM")
            return
        buffer.insert_text('>')
    def do_backspace(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        if self_dot_var_equals_var(buffer,'\b') and after_line.strip()!='=':
            #self.foo|=foo   --->   self.fo|=fo
            return
        if before_line.endswith(' as '):
            #(I'm often trigger-happy with the space-bar on using imports, and try to correct it with backspace. This saves me some time...)
            #import osaidf as |   --->   import osaidf
            buffer.delete_before_cursor(len(' as '))
            return
        if before_line.endswith(', '):
            #import osaidf as c, |   --->   import osaidf as c|
            buffer.delete_before_cursor(len(', '))
            return
        selection_tuples=list(document.selection_ranges())
        if not selection_tuples:
            before=document.text_before_cursor
            after= document.text_after_cursor
            if not after and before =='ans.':
                buffer.delete_before_cursor(len(before))
                return
            if not before_line.strip():
                #(backspace entire indent when it's empty. example:)
                #def f(x):
                #····|return x
                #  --->
                #def f(x):return x
                buffer.delete_before_cursor(len(before_line))
            bl=before_line.lstrip()
            al=after_line.rstrip()
            if bl+'|'+al in {'from | import','for | in :','while |:','if |:','except |:','lambda :'}|\
                            {'import |','return |','return|','pass|',''}:
                            #Delete from both sides of the cursor on constructs we tend to make automatically (to make it less annoying)
                buffer.cursor_right(len(al))
                buffer.delete_before_cursor(len(bl+al))
            if before and after:
                if after_line.strip()in {':','():'} and before_line.lstrip() in {'def ','while ','for ','class ','if ','elif ','else','except ','lambda ','with ','try'}:
                    #  '    def |:'   -->   '    |'
                    buffer.delete(len(after_line))
                    buffer.delete_before_cursor(len(before_line.lstrip()))
                    return
                pair=before[-1]+after[0]
                if pair in ['()','{}','[]',"''",'""']:
                    #  'f(|)'   -->   'f|'
                    buffer.cursor_right(count=1)
                    buffer.delete_before_cursor(count=2)
                    buffer.insert_text('')#trigger autocompletion
                    return
            buffer.delete_before_cursor(count=1)
        else:
            buffer.cut_selection()
        buffer.insert_text("")#Using this to trigger autocompletion on backspace
    def alt_backspace_char_class(event):
        #get char before cursor and distinguish between whitespace, alphanumerics, and other chars
        c=event.cli.current_buffer.document.text_before_cursor
        if not c:
            return None#no chars behind cursor
        c=c[-1]
        if c.isalnum():
            return 1
        elif not c.strip():
            return 2
        else:
            return 3

    @handle(Keys.Backspace,eager=True)
    def _(event):
        if meta_pressed():
            do_backspace(event)#We expect at least two characters to dissapear; so eat through one-char wide spaces (for example, "def |a()" --> "|a()", not "def|a()")
            c=alt_backspace_char_class(event)
            while c is not None and c==alt_backspace_char_class(event):
                do_backspace(event)
            return
        do_backspace(event)

    @handle(Keys.Right)
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        selection_tuples=list(document.selection_ranges())
        for t in selection_tuples:
            buffer._set_cursor_position(t[1])
            buffer.exit_selection()
        else:
            cpos=buffer.cursor_position
            buffer.cursor_right(1)
            if buffer.cursor_position==cpos:
                buffer=event.cli.current_buffer
                buffer._set_cursor_position(min(buffer.cursor_position + 1,len(buffer.document.text)))
            # buffer.cursor_right(0)# Gets stuck on ends of lines. Not as good as the new version

    @handle(Keys.Left)
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        selection_tuples=list(document.selection_ranges())
        for t in selection_tuples:# Handle arrow-keys on selection by putting the cursor on beginning or end of selection
            buffer._set_cursor_position(min(t[0]+1,len(buffer.document.text)))
            buffer.exit_selection()
        else:
            cpos=buffer.cursor_position
            buffer.cursor_left(1)
            if cpos==buffer.cursor_position:
                buffer=event.cli.current_buffer
                buffer._set_cursor_position(max(buffer.cursor_position - 1,0))

    @handle(Keys.Down)
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        assert isinstance(buffer,Buffer)
        if has_selected_completion(buffer) or not '\n' in buffer.document.text:
            buffer.auto_down()# Will select next completion
            try:
                if not has_selected_completion(buffer) or not '\n' in buffer.document.text3:#
                    buffer.auto_down()# So we don't get stuck when we come back around again
            except:pass
        else:
            temp=buffer.complete_state
            try:
                buffer.complete_state=False
                buffer.auto_down()# Will select next completion
            finally:
                buffer.complete_state=temp

    @handle(Keys.Up)
    def _(event):
        buffer=event.cli.current_buffer
        assert isinstance(buffer,Buffer)
        if has_selected_completion(buffer):#  Up is the only one that can initially select a history item
            buffer.auto_up()# Will select next completion
            if not has_selected_completion(buffer):
                buffer.auto_up()# So we don't get stuck when we come back around again
        else:
            temp=buffer.complete_state
            try:
                buffer.complete_state=False# So we don't select a completion
                buffer.auto_up()# Will select next completion
            finally:
                buffer.complete_state=temp





    @handle(Keys.ControlZ)# On mac this is alt+z
    def _(event):
        buffer=event.cli.current_buffer
        # print(buffer._redo_stack)
        buffer.undo()

    import rp.r_iterm_comm as r_iterm_comm
    @handle(Keys.ControlV)# On mac this is alt+z
    def _(event):
        buffer=event.cli.current_buffer
        from rp import string_from_clipboard
        clip=r_iterm_comm.clipboard_text
        try:
            clip=string_from_clipboard()
        except:
            pass# Paste failed
        buffer.cut_selection()
        buffer.insert_text(clip)


    @handle(Keys.ControlC)# ,filter=has_selection)# On mac this is alt+z
    def _(event):
        buffer=event.cli.current_buffer
        selection_tuples=list(buffer.document.selection_ranges())

        #region
        if not selection_tuples:
            selection_tuples=[]
            line=buffer.document.current_line
            to_copy="\n" + line# ' ' * (len(line)-len(line.lstrip()))
            buffer.cursor_right(12323213)
        else:
            to_copy=""
            for t in selection_tuples:
                to_copy+=buffer.document.text[t[0]:t[1]+1]
        r_iterm_comm.clipboard_text=to_copy
        from rp import string_to_clipboard
        try:
            string_to_clipboard(to_copy)
        except:
            pass# Copy failed


    def inc_dec(inc_or_dec:str):# ++ ⟶ +=1
        #increment or decrement
        @handle(inc_or_dec)
        def _(event):
            buffer=event.cli.current_buffer
            document=buffer.document
            before=document.text_before_cursor
            before_line=document.current_line_before_cursor
            after_line=document.current_line_after_cursor
            after= document.text_after_cursor
            current_line= document.current_line
            # import r_iterm_comm
            # if not after and r_iterm_comm.last_assignable_comm and before[-1]==inc_or_dec:# So you can do ++ -> assignable ++= (because +=1 -> assignable+=1)
            #     buffer.cursor_left(count=1000)
            #     buffer.insert_text(r_iterm_comm.last_assignable_comm)
            #     buffer.cursor_right(count=1000)
            #     return
            # print('GAGAGAGA')
            from rp import is_namespaceable
            if inc_or_dec == '-' and all(is_namespaceable(x) for x in before_line if x not in ' ') and before_line.lstrip().startswith('def '):# When writing the title of a function, you don't have to use _ you can type - and it will turn it into _
                #(on -)
                #def |(): ---> def _|():
                #     AND
                #def f|(): ---> def _f_|():
                buffer.insert_text('_')
                return
            if inc_or_dec=='+' and (after_line.startswith('"') or after_line.startswith("'")):
                #(on + followed by +) (for combining strings more easily)
                #"Hello"|"World"  --->  "Hello"|+"World"  --->  "Hello"+|+"World"
                #       AND
                #'Hello'|'World'  --->  'Hello'|+'World'  --->  'Hello'+|+'World'
                buffer.insert_text('+')
                buffer.cursor_left()
                return
                #"Hello"|"World"  --->  "Hello"|+"World"  --->  "Hello"+|+"World"
            if inc_or_dec=='-' and before_line.lstrip()=='for ' and after_line.rstrip()==' in :':
                #(on -)
                #for | in : --> for _ in |:
                buffer.insert_text('_')
                buffer.cursor_right(len(' in '))
                return
            if len(before_line.strip())>1 and before and before[-1]==inc_or_dec and is_namespaceable(before_line[:-1].lstrip()):
                #(on +) x+|  --->  x+=1
                #       AND
                #(on -) x-|  --->  x-=1
                if not after_line:
                    buffer.insert_text("=1")
                else:
                    buffer.insert_text(inc_or_dec)
                    buffer.cursor_left()
            elif inc_or_dec=='-' and before_line.endswith('-'):
                #becuase then we dont have to reach for the shify key (default blank vairable is _ in for loops)
                #print(-|) ---> print(_|)
                buffer.delete_before_cursor()
                buffer.insert_text('_')
            elif inc_or_dec=='-' and before_line.endswith('-=1'):
                #(when we wanted to make an underscore but got -=1, just press - again...)
                #x-=1| ---> x_| 
                buffer.delete_before_cursor(3)
                buffer.insert_text('_')
            else:
                buffer.insert_text(inc_or_dec)
            # if inc_or_dec=='+':
            #     print("ewfoijfdsijoijowfijofejio")
            #     if before.endswith('+') and after and after[0] in '\'"':
            #         buffer.cursor_left()
    inc_dec('+')
    inc_dec('-')

    # @handle("h")
    # def sploo(x):
    #     print("A")
    # @handle("h")
    # def sploo(x):
    #     print("B")


    bracket_pairs={"()","[]","{}"}
    def thing(begin,end):
        @handle(begin)
        def _(event):# Parenthesis completion
            buffer=event.cli.current_buffer
            if(begin=='('):
                document=buffer.document
                before_line=document.current_line_before_cursor
                after_line =document.current_line_after_cursor
                if regex_match(before_line.lstrip(),r'for\s+\w+\s+in\s+len'):
                    #for x in len|   -->  for x in range(len(|))
                    buffer.delete_before_cursor(3)
                    buffer.insert_text('range(len())')
                    buffer.cursor_left(2)
                    return
                if before_line.rstrip().startswith('def ') and after_line.strip()=='():':
                    #def f|() --> def f(|):
                    buffer.cursor_right()
                    return
            if not surround(buffer,begin,end):
                document=buffer.document
                before=document.text_before_cursor
                after= document.text_after_cursor
                buffer.insert_text(begin)
                if after.strip()==':' or not after or after[0].isspace() or before and before[-1]+after[0]in bracket_pairs or document.find_matching_bracket_position()!=0:
                    buffer.insert_text(end)
                    buffer.cursor_left(count=1)
        @handle(end)
        def _(event):# Parenthesis completion
            buffer=event.cli.current_buffer
            if not surround(buffer,begin,end):
                document=buffer.document
                before=document.text_before_cursor
                after= document.text_after_cursor
                if not after or after[0]!=end:#  or before.count(begin)>before.count(end):#Last part is checking for parenthesis matches. I know somewhere there's a way to do this already thats better and isnt confused by strings but idk where that is
                    buffer.insert_text(end)
                else:
                    buffer.cursor_right(count=1)
    for bracket_pair in bracket_pairs:
        thing(bracket_pair[0],bracket_pair[1])

    def surround(buffer,begin,end):
        from rp.prompt_toolkit.selection import SelectionState
        document=buffer.document
        text=document.text
        selection_tuples=list(document.selection_ranges())
        for range in selection_tuples:
            buffer.document=Document(text=text[:range[0]]+begin+text[range[0]:range[1]+1]+end +text[range[1]+1:],cursor_position=range[0]+1,selection=None)
            buffer.document._selection=SelectionState(original_cursor_position=range[1]+1,type=document.selection.type)
        # exec(mini_terminal)
        # from rp.rp_ptpython.utils import get_jedi_script_from_document
        # script=get_jedi_script_from_document(document,r_iterm_comm.globa,r_iterm_comm.globa)
        # script.call_signatures()
        return bool(selection_tuples)# Returns whether we have a selection
    def thing2(char):
        @handle(char)
        def _(event,filter=has_selection):# Parenthesis completion
            buffer=event.cli.current_buffer
            if not surround(buffer,char,char):
                document=buffer.document
                before=document.text_before_cursor
                after= document.text_after_cursor
                before_line=document.current_line_before_cursor
                after_line=document.current_line_after_cursor

                if after.startswith(char) and not before.endswith(char):
                    buffer.cursor_right()
                # else:
                #     buffer.insert_text(char)
                #     buffer.cursor_left()
                #     buffer.insert_text(char)

                elif (before and after and before[-1]+after[0] in {"[]","()","{}",",}",",)",",]",'+)','+,','+}','+]'}) or (not after_line or not before and not after or before and after and before[-1]in'(=!#%&*+,-./:;<>^|~' and after[0]in')=!#%&*+,-./ :;<>^|~' or before and after and before[-1]+after[0] in 2*char):
                    #| --> "|"
                    #| --> '|'
                    buffer.insert_text(char)
                    buffer.cursor_left()
                    buffer.insert_text(char)
                elif before.endswith(char):
                    #For splitting strings into two pieces
                    #(" pressed twice)
                    #"Hello|World!"  -->  "Hello"|World!"  -->  "Hello"|"World!"
                    buffer.insert_text(char)
                    buffer.cursor_left()
                else:
                    buffer.insert_text(char)

    for char in '"\'':
        thing2(char)
    @handle(',')  
    def _(event):
        #Comma event
        buffer=event.cli.current_buffer
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        if before_line.endswith(',') and after_line.startswith(','):
            #We prevent from accidently putting in more parenthesis than make sense
            #x,|,y  --->  x,|,y    (no change)...
            return
        if before_line.endswith(',') and \
            not before_line.endswith(',,'):#...however, we do allow ,,,,,,,:   x,,|y  --->  x,,,|y  
            #y,|x  -->  y,|,x
            buffer.insert_text(',')
            buffer.cursor_left()
            return
        if before_line.endswith('-'):
            #Turning the '-' into a '_' where a '-' would be syntactically invalid
            buffer.delete_before_cursor()
            buffer.insert_text('_')
            
        if after_line.startswith(','):
            #f(a,b,c|,)   --->   [a,b,c,|)
            #(don't waste commas)
            buffer.cursor_right()
            return
        if not (before_line.endswith(',') and after_line.startswith(']')):
            #[x,y|]  -->  [x,y,|]
            #       AND
            #[x,y,|]  -->  [x,y,|]
            #for when I spam the [12,3123,12,31,23,12,31,23,123,1,23,123,12,31,23] and don't want accidental ',,'s
            buffer.insert_text(',')
            return

    # @handle(',')
    # def thing3(char):
    #     @handle(char)
    #     def _(event,filter=~has_selection):# Parenthesis completion
    #         buffer=event.cli.current_buffer
    #         document=buffer.document
    #         before=document.text_before_cursor
    #         after= document.text_after_cursor
    #         if before.endswith('(') and after.startswith(')'):
    #             buffer.cursor_right()
    #         buffer.insert_text(char)
    # for char in '!#%&*,./:;<>^|~':# + and - allready taken
    #     thing3(char)

    @handle(Keys.ControlSpace)# For commenting
    def _(event):  # Parenthesis completion
        # def toggle_comment_on_line(x):
        #     y=x.lstrip()
        #     if y.startswith("#"):# Line is commented out
        #         i=x.find('#')
        #         return x[:i]+x[i+1:]
        #     l=len(x)-len(y)
        #     return l*' ' +'#' + y

        buffer=event.cli.current_buffer
        # buffer.transform_current_line(toggle_comment_on_line)
        # buffer.insert_text("ⵁ")
        # buffer.delete_before_cursor
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor
        current_line=document.current_line
        before_line=document.current_line_before_cursor
        after_line=document.current_line_after_cursor
        buffer.cursor_left(10000)
        lstrip=current_line.lstrip()
        w=len(current_line)-len(lstrip)
        buffer.cursor_right(w)
        if current_line.lstrip().startswith('#'):
            buffer.delete()
        else:
            buffer.insert_text('#')
        buffer.cursor_down()
    #endregion

    @handle(Keys.ControlT,eager=True)
    def _(event):
        """
        Cursor to top.
        """
        event.cli.current_buffer.history_backward()
    @handle(Keys.ControlB,eager=True)
    def _(event):
        """
        Cursor to top.
        """
        event.cli.current_buffer.history_forward()

    @handle(Keys.ControlL)
    def _(event):
        """
        Clear whole screen and render again -- also when the sidebar is visible.
        """
        event.cli.renderer.clear()
    @handle(Keys.F2)
    def _(event):
        """
        Show/hide sidebar.
        """
        python_input.show_sidebar = not python_input.show_sidebar

    @handle(Keys.F3)
    def _(event):
        """
        Select from the history.
        """
        python_input.enter_history(event.cli)

    @handle(Keys.F4)
    def _(event):
        """
        Toggle between Vi and Emacs mode.
        """
        python_input.vi_mode = not python_input.vi_mode

    @handle(Keys.F6)
    def _(event):
        """
        Enable/Disable paste mode.
        """
        python_input.paste_mode = not python_input.paste_mode

    @handle(Keys.F1)
    def _(event):
        """
        Enable/Disable mouse mode.
        """
        python_input.enable_mouse_support = not python_input.enable_mouse_support
    def number_of_leading_spaces(string):
        i=0
        for x in string:
            if x==' ':
                i+=1
            else:
                break
        return i
    @handle(Keys.Tab, filter= ~sidebar_visible & ~has_selection & TabShouldInsertWhitespaceFilter())
    def _(event):
        """
        When tab should insert whitespace, do that instead of completion.
        """
        buffer=event.cli.current_buffer
        buffer.insert_text('    ')
        after_line = buffer.document.current_line_after_cursor
        before_line = buffer.document.current_line_after_cursor
        # N=number_of_leading_spaces(before_line+after_line)
        # if not before_line.strip() and N%4:
            # buffer.insert_text(' '*(4-N%4))
            # return
        if after_line.lstrip():
            buffer.cursor_left(4)
    #region  Ryan Burgert Method
    @handle(Keys.BackTab,filter=IsMultiline())
    def _(event):
        """
        When tab should insert whitespace, do that instead of completion.
        """
        # from r import mini_terminal
        buffer=event.cli.current_buffer
        after_line = buffer.document.current_line_after_cursor
        before_line = buffer.document.current_line_before_cursor
        # flag=before_line.strip() and before_line#has some whitespace characters on it
        N=min(4,number_of_leading_spaces(before_line+after_line))
        # i=0
        if not after_line.strip() and not before_line.strip():
            for i in range(4):
                if buffer.document.current_line_before_cursor:
                    buffer.delete_before_cursor(1)

            return
        for _ in range(N):
            try:
                if buffer.document.current_line.startswith(' ') or not has_selected_completion(buffer):
                    flag=False
                    if not buffer.document.current_line_after_cursor:#Otherwise it might jump to another line if we dont do this first
                        buffer.cursor_left()
                        flag=True
                    buffer.transform_current_line(lambda x:x[1:])
                    if not flag and buffer.document.current_line_before_cursor.strip():
                        buffer.cursor_left()
                # buffer.transform_current_line(lambda x:(x[1:]if x.startswith(' '*4)else x.lstrip()))
                # buffer.transform_current_line(lambda x:(x[4:]if x.startswith(' '*4)else x.lstrip()))
            except:
                pass# Error migght happen if cursor is in bad place. Not sure what to do about that; but its an edge case so I'm just gonna squelch it.
        #endregion
        # if flag:
            # buffer.cursor_right(i)
    from rp import ring_terminal_bell ,text_to_speech
    def try_to_unindent(buffer,*matching_prefixes):
        b=buffer
        current_line = b.document.current_line
        after_line = b.document.current_line_after_cursor
        before_line = b.document.current_line_before_cursor
        before=b.document.text_before_cursor
        after= b.document.text_after_cursor
        l=find_level(before,*matching_prefixes)
        if l is None:
            # ring_terminal_bell()
            # text_to_speech('a')
            return#We're at a bit of a loss on what to do here...
        i=get_indent(current_line)
        d=len(i)-l
        L=len(before_line.lstrip())
        # ring_terminal_bell()
        buffer.cursor_left(L)
        buffer.delete_before_cursor(d)
        buffer.cursor_right(L)
        # text_to_speech('b')
    indent_block_matches={
            'except':{'try','finally'},#cant add except for buggy reasons (it sees itself when trying to unindent and thus doesnt unindent)
            'finally':{'try','except','else'},
            'else':{'if','elif','for','while','except'},
            'elif':{'if'},#cant add elif for buggy reasons (it sees itself when trying to unindent and thus doesnt unindent)
            }
    def try_to_autounindent(buffer):
        b=buffer
        current_line = b.document.current_line
        after_line = b.document.current_line_after_cursor
        before_line = b.document.current_line_before_cursor
        before=b.document.text_before_cursor
        after= b.document.text_after_cursor
        if current_line.rstrip().endswith(':'):
            
            for m in indent_block_matches:
                if current_line.lstrip().startswith(m):
                    try_to_unindent(buffer,*indent_block_matches[m])
                    # text_to_speech('c')
                    return
        # text_to_speech('d')
        return



    @handle(Keys.ControlJ, filter= ~sidebar_visible & ~has_selection &(ViInsertMode() | EmacsInsertMode()) &HasFocus(DEFAULT_BUFFER) )#& IsMultiline())
    def _(event):
        """
        Behaviour of the Enter key.

        Auto indent after newline/Enter.
        (When not in Vi navigaton mode, and when multiline is enabled.)
        """
        b = event.current_buffer
        buffer=b
        empty_lines_required = python_input.accept_input_on_enter or 10000
        text=current_line=after_line=before_line=before=after=above_line=None
        def refresh_strings_from_buffer():
            nonlocal text,current_line,after_line,before_line,before,after,above_line
            text =         b.document.text_after_cursor
            current_line = b.document.current_line
            after_line =   b.document.current_line_after_cursor
            before_line =  b.document.current_line_before_cursor
            before=        b.document.text_before_cursor
            after=         b.document.text_after_cursor
            above_line=    line_above(b)
        refresh_strings_from_buffer()

        single_line = above_line is None
        def auto_pass():#try automatically adding a 'pass' keyword if it helps to avoid a syntax error; return True if we add a 'pass'
            if not single_line and not current_line.strip() and above_line.rstrip().endswith(':'):
                #Implicitly add 'pass' when hitting enter below an if/for/def block (which would otherwise be a syntax error because of the autounindent)
                buffer.insert_text('pass')
                refresh_strings_from_buffer()
                return True
            return False
        auto_pass()
        for end in ')]}':
            if current_line.endswith(','+end) and before_line.endswith(',') and after_line==end:
                #print(ans,|)   --->   print(ans|)
                #[1,2,3,|]      --->   [1,2,3|]
                #{1,2,3,|}      --->   {1,2,3|}
                buffer.delete_before_cursor()
                refresh_strings_from_buffer()
        if endswithany(before_line,',-','(-','[-','{-'):
            #Completing the '-' dash to the underscore variable '_' in one of many instances where it makes sense
            #print(-|) ---> print(_)\n|
            buffer.delete_before_cursor()
            buffer.insert_text('_')
            refresh_strings_from_buffer()
        #a line with a sigle letter on it is useless, so let's make it useful.
        #TODO: Make it semantically aware: make 'e' write 'except' when in a try block, and 'else' when in an 'if' or after a 'for' block. Same logic SHOULD (but doesn't yet) apply to all of these (see below line)
        if before_line.lstrip()=='#':
            #'#|' ---> '|'  (so we can hit enter twice to break out of a comment)
            buffer.delete_before_cursor()
            return
        continue_comment=before_line.lstrip().startswith('#')
        if before_line=='from 'and after_line==' import':
            #With current completions, which come in the next few 'if' blocks, we get this:
            #from | import ---> for _ in ans:\n\t
            buffer.delete_before_cursor(len('from '))
            buffer.delete(len(' import'))
            buffer.insert_text('for  in :')
            buffer.cursor_left(len(' in :'))
            refresh_strings_from_buffer()

        if before_line.lstrip()=='for 'and after_line.rstrip()==' in :':
            #for | in :   --->   for _ in |:   (we don't stop here, it eventually goes to "for _ in ans": see the next 'if' block)
            buffer.insert_text('_')
            # buffer.insert_text('ans')
            # 
            refresh_strings_from_buffer()

        if after_line.rstrip()==' in :':
            buffer.cursor_right(len(' in '))
            # 
            refresh_strings_from_buffer()

        if after_line.rstrip()==':':
            #for spaoddsg in |:   --->   for spaoddsg in ans:
            spl=before_line.split()
            if len(spl)==3 and spl[0]=='for' and spl[2]=='in':
                buffer.insert_text('ans')
                # 
                refresh_strings_from_buffer()
        import rp.r_iterm_comm
        enter_completable_keywords=dict(fo='for _ in ans:',e='else:',t='try:',b='break',c='continue',f='finally:',p='pass',r='return',y='yield',d='def _():',w='while True:',i='if True:')#enter-completion of keywords that don't need to take arguments
        single_line_enabled_keywords={'fo','f','i','t','d','w'}-set(rp.r_iterm_comm.globa)
        keyword=current_line.lstrip()

        if (not single_line or keyword in single_line_enabled_keywords) and keyword in enter_completable_keywords:
            #Examples:
            #'e|' ---> 'else:\n    |'
            #'t|' ---> 'try:\n    |'
            #'r|' ---> 'return\n|'
            char=current_line.lstrip()
            replacement=enter_completable_keywords[char]
            level=lambda candidate:find_level(before,*indent_block_matches[candidate])
            if replacement=='else:':
                exl=level('except')
                ell=level('else')
                if ell is None and exl is not None or exl is not None and exl>ell:
                    text_to_speech('q')
                    replacement='except:'
            if '_' in replacement:
                if single_line:
                    replacement=replacement.replace('_','ans')
            if not 'try' in text and replacement=='finally:':
                replacement='for _ in ans:'
            buffer.delete_before_cursor(len(char))
            refresh_strings_from_buffer()
            indent=current_line
            assert not current_line.strip()
            # if auto_pass():buffer.insert_text('\n'+indent)
            buffer.insert_text(replacement)
            try_to_autounindent(buffer)   
            refresh_strings_from_buffer()

        if not after and before.startswith('import ') and before.endswith(', '):
            #Sometimes when using my import microcompletions I hit the space key by accident, which causes this:
            #import w as x,y as z, |
            #Which is a syntax error. Autocorrect it to:
            #import w as x,y as z
            buffer.delete_before_cursor(2)
        if before_line.lstrip() in ('def ','class ') and current_line.strip() in ('def ():','def (self):','class :'):
            #def |():  --->  'def ans():\n|'  or 'def _():\n|' 
            #class |:  --->  class _:\n|
            if single_line:
                buffer.insert_text('ans')
            else:
                buffer.insert_text('_')
        #we might have made some changes; refreshing:
        refresh_strings_from_buffer()

        # if  (after_line.startswith('"""') and before_line.endswith ('"""')) or\
        #     (after_line.startswith("'''") and before_line.endswith ("'''")):
        #     print("ASOID")
        #     b.insert_text('\n')
        #     return
        def at_the_end(b):
            """ we consider the cursor at the end when there is no text after
            the cursor, or only whitespace. """
            assert isinstance(b,Buffer)
            refresh_strings_from_buffer()
            #region RYAN BURGERT STUFF
            text=after
            assert isinstance(text,str)
            if self_dot_var_equals_var(buffer) or (before_line.lstrip() and not beginswithany(before_line[::-1],' ',',',':',';','{','[','"""',"'''") and not '"""' in before_line and not "'''" in before_line and '(' in before_line or beginswithany(before_line.lstrip(),'for ','def ','lambda ','while ','with ','if ','except ','try ') or not text or text.split('\n')[0] in ["):",']',')','}',':']):# Presumably at the end of def( a,b,c,d,e^): where ^ is cursor
                event.cli.current_buffer.cursor_right(1000000)# Move cursor to end of line then proceed as normal
                text = b.document.text_after_cursor
            #endregion
            return text == '' or (text.isspace() and not '\n' in text)
        if single_line:#single-line commands are entered immediately.
            if not current_line.rstrip().endswith(':') \
            and not   endswithany(current_line.lstrip(),'@',"'''",'"""') \
            and not starts_with_any(current_line.lstrip(),'@',"'''",'"""'):
                b.accept_action.validate_and_handle(event.cli, b)
        # if at_the_end(b):# TODO Stuff here
            # print("""def a b c d e (enter)
# ->
# def a(b,c,d,e):
# """)
        if python_input.paste_mode:
            # In paste mode, always insert text.
            b.insert_text('\n')

        elif at_the_end(b) and b.document.text.replace(' ', '').endswith('\n' * (empty_lines_required - 1)):
            if b.validate():
                # When the cursor is at the end, and we have an empty line:
                # drop the empty lines, but return the value.
                b.document = Document(
                    text=b.text.rstrip(),
                    cursor_position=len(b.text.rstrip()))

                b.accept_action.validate_and_handle(event.cli, b)
        else:
            auto_newline(b)
            if continue_comment:
                #'#Foo|'-->'#Foo\n#|'
                buffer.insert_text('#')


    @handle(Keys.ControlD, filter=~sidebar_visible & Condition(lambda cli:
            # Only when the `confirm_exit` flag is set.
            python_input.confirm_exit and
            # And the current buffer is empty.
            cli.current_buffer_name == DEFAULT_BUFFER and
            not cli.current_buffer.text))
    def _(event):
        """
        Override Control-D exit, to ask for confirmation.
        """
        python_input.show_exit_confirmation = True

    return registry


def load_sidebar_bindings(python_input):
    """
    Load bindings for the navigation in the sidebar.
    """
    registry = Registry()

    handle = registry.add_binding
    sidebar_visible = Condition(lambda cli: python_input.show_sidebar)

    @handle(Keys.Up, filter=sidebar_visible)
    @handle(Keys.ControlP, filter=sidebar_visible)
    @handle('k', filter=sidebar_visible)
    def _(event):
        " Go to previous option. "
        python_input.selected_option_index = (
            (python_input.selected_option_index - 1) % python_input.option_count)

    @handle(Keys.Down, filter=sidebar_visible)
    @handle(Keys.ControlN, filter=sidebar_visible)
    @handle('j', filter=sidebar_visible)
    def _(event):
        " Go to next option. "
        python_input.selected_option_index = (
            (python_input.selected_option_index + 1) % python_input.option_count)

    @handle(Keys.Right, filter=sidebar_visible)
    @handle('l', filter=sidebar_visible)
    @handle(' ', filter=sidebar_visible)
    def _(event):
        " Select next value for current option. "
        option = python_input.selected_option
        option.activate_next()

    @handle(Keys.Left, filter=sidebar_visible)
    @handle('h', filter=sidebar_visible)
    def _(event):
        " Select previous value for current option. "
        option = python_input.selected_option
        option.activate_previous()

    @handle(Keys.ControlC, filter=sidebar_visible)
    @handle(Keys.ControlG, filter=sidebar_visible)
    @handle(Keys.ControlD, filter=sidebar_visible)
    @handle(Keys.ControlJ, filter=sidebar_visible)
    @handle(Keys.Escape, filter=sidebar_visible)
    def _(event):
        " Hide sidebar. "
        python_input.show_sidebar = False

    return registry


def load_confirm_exit_bindings(python_input):
    """
    Handle yes/no key presses when the exit confirmation is shown.
    """
    registry = Registry()

    handle = registry.add_binding
    confirmation_visible = Condition(lambda cli: python_input.show_exit_confirmation)

    @handle('y', filter=confirmation_visible)
    @handle('Y', filter=confirmation_visible)
    @handle(Keys.ControlJ, filter=confirmation_visible)
    @handle(Keys.ControlD, filter=confirmation_visible)
    def _(event):
        """
        Really quit.
        """
        event.cli.exit()

    @handle(Keys.Any, filter=confirmation_visible)
    def _(event):
        """
        Cancel exit.
        """
        python_input.show_exit_confirmation = False

    return registry
diddly=0

def auto_newline(buffer):
    r"""
    Insert \n at the cursor position. Also add necessary padding.
    """
    insert_text = buffer.insert_text

    if buffer.document.current_line_after_cursor:
        # When we are in the middle of a line. Always insert a newline.
        insert_text('\n')
    else:
        # Go to new line, but also add indentation.
        current_line = buffer.document.current_line_before_cursor.rstrip()
        insert_text('\n')

        # Unident if the last line ends with 'pass', remove four spaces.
        unindent = current_line.rstrip().endswith(' pass') or current_line.lstrip().startswith('return ') or current_line.lstrip().startswith('raise ')  or current_line.strip()==('break') or  current_line.strip()==('continue') or  current_line.strip()==('raise') or  current_line.strip()==('pass')or  current_line.strip()==('return')

        # Copy whitespace from current line
        current_line2 = current_line[4:] if unindent else current_line

        for c in current_line2:
            if c.isspace():
                insert_text(c)
            else:
                break

        # If the last line ends with a colon, add four extra spaces.
        if current_line[-1:] == ':':
            for x in range(4):
                insert_text(' ')
