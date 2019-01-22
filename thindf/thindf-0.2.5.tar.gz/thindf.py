import json

class Error(Exception):
    def __init__(self, message, pos):
        self.message = message
        self.pos = pos

def to_thindf(obj, indent = 4, level = 0, toplevel = True):
    def balance_pq_string(s): # [[[‘]]]на вход подаётся строка без кавычек, например: "Don’t", а на выходе строка уже в кавычках, так как... снаружи их так просто уже не добавишь
        min_nesting_level = 0
        nesting_level = 0
        for ch in s:
            if ch == "‘":
                nesting_level += 1
            elif ch == "’":
                nesting_level -= 1
                min_nesting_level = min(min_nesting_level, nesting_level)
        nesting_level -= min_nesting_level
        return "'"*-min_nesting_level + "‘"*-min_nesting_level + "‘" + s + "’" + "’"*nesting_level + "'"*nesting_level

    def to_str(v, additional_prohibited_character = None):
        if type(v) in (int, float):
            return str(v)
        if type(v) == bool:
            return {True:'1B', False:'0B'}[v]
        if v == None:
            return 'N'
        assert(type(v) == str)
        if len(v) < 100 and "\n" in v:
            return '"' + repr(v)[1:-1].replace('"', R'\"').replace(R"\'", "'") + '"'
        if v == '' or v[0] in " \t[{" or v[:2] == '. ' or v[-1] in " \t" or '‘' in v or '’' in v or "\n" in v or v in 'NН' \
                or (additional_prohibited_character and additional_prohibited_character in v) or v[0].isdigit() or (v[0] == '-' and v[1:2].isdigit()): # }]
            return balance_pq_string(v)
        return v

    r = ''
    if type(obj) == dict:
        if len(obj) == 0 and toplevel:
            return "{}\n"
        for index, (key, value) in enumerate(obj.items()):
            r += indent * level * ' ' \
              +  to_str(key, '=')
            if type(value) == dict:
                if len(value) == 0:
                    r += " = {}\n"
                else:
                    r += "\n" + to_thindf(value, indent, level+1, False)
                    if len(value) > 2 and index < len(obj)-1:
                        r += "\n"
            elif type(value) == list:
                if len(value) == 0:
                    r += " = []\n"
                else:
                    r += " = [\n" + to_thindf(value, indent, level, False) \
                      + indent * level * ' ' + "]\n"
            else: # this is value
                r += ' = ' + to_str(value) + "\n"

    elif type(obj) == list:
        if toplevel:
            if len(obj) == 0:
                return "[]\n"
            r += "[\n"
        for index, value in enumerate(obj):
            if type(value) == list:
                r += indent * (level+1) * ' ' + '['
                for index2, subvalue in enumerate(value):
                    if type(subvalue) in (dict, list):
                        raise Error('sorry, but this object can not be represented in thindf (element `' + str(subvalue) + '` of `' + str(value) + '`)', 0)
                    r += to_str(subvalue, ',')
                    if index2 < len(value)-1:
                        r += ', '
                r += "]\n"
            elif type(value) == dict:
                if len(value) == 0:
                    r += indent * level * ' ' + '.' + (indent-1) * ' ' + "{}\n"
                else:
                    r += indent * level * ' ' + '.' + to_thindf(value, indent, level+1, False)[indent * level + 1:]
                    if len(value) > 2 and index < len(obj)-1:
                        r += "\n"
            else:
                r += indent * (level+1) * ' ' + to_str(value, '=') + "\n"
        if toplevel:
            r += "]\n"

    return r

def parse(s):
    def find_ending_pair_quote(i): # ищет окончание ‘строки’
        assert(s[i] == "‘") # ’
        startqpos = i
        nesting_level = 0
        while True:
            if i == len(s):
                raise Error('unpaired left single quotation mark', startqpos)
            ch = s[i]
            if ch == "‘":
                nesting_level += 1
            elif ch == "’":
                nesting_level -= 1
                if nesting_level == 0:
                    return i
            i += 1

    def from_str(stop_characters = ''):
        nonlocal i
        start = i
        if s[i] == '"':
            i += 1
            while i < len(s):
                if s[i] == "\\":
                    i += 1
                elif s[i] == '"':
                    i += 1
                    break
                i += 1
            return json.loads(s[start:i])
        elif s[i] == '‘': # ’
            endqpos = find_ending_pair_quote(i)
            i = endqpos + 1
            while i < len(s):
                if s[i] != "'":
                    break
                i += 1
            eat_right = i - (endqpos + 1) # количество кавычек, которые нужно съесть справа # ‘

            if s[endqpos-eat_right:endqpos+1] != '’' * (eat_right+1):
                raise Error('wrong ending of the raw string', endqpos)

            return s[start+1:endqpos - eat_right]
        elif s[i] == "'":
            i += 1
            while i < len(s):
                if s[i] != "'":
                    break
                i += 1
            eat_left = i - start # количество кавычек, которые нужно съесть слева

            if s[i:i+eat_left+1] != '‘' * (eat_left+1):
                raise Error('wrong beginning of the raw string', start)

            startqpos = i
            endqpos = find_ending_pair_quote(i)
            i = endqpos + 1
            while i < len(s):
                if s[i] != "'":
                    break
                i += 1
            eat_right = i - (endqpos + 1) # количество кавычек, которые нужно съесть справа

            if s[endqpos-eat_right:endqpos+1] != '’' * (eat_right+1):
                raise Error('wrong ending of the raw string', endqpos)

            return s[startqpos + eat_left + 1:endqpos - eat_right]
        elif s[i].isdigit() or (s[i] == '-' and s[i+1:i+2].isdigit()):
            i += 1
            is_float = False
            while i < len(s):
                if not s[i].isdigit():
                    if s[i] in '.eE':
                        is_float = True
                        i += 1
                        if i < len(s) and s[i] in '-+':
                            i += 1
                        continue
                    elif s[i] in 'BВ':
                        if i - start != 1 or s[start] not in '01':
                            raise Error('wrong value', start)
                        i += 1
                        return {'0':False, '1':True}[s[start]]
                    break
                i += 1
            ss = s[start:i]
            return float(ss) if is_float else int(ss)

        stop_characters += "\r\n"
        while i < len(s):
            if s[i] in stop_characters:
                break
            i += 1
        t = i - 1
        while t > start and s[t] in " \t":
            t -= 1
        ss = s[start:t+1]
        if ss in ('N', 'Н'):
            return None
        return ss

    expected_an_indented_block = False
    indentation_levels = []
    obj_stack = []
    i = 0

    if len(s) == 0:
        raise Error('empty thindf is not allowed', 0)
    if s[0] == '[':
        assert(len(s) >= 2)
        if s[1] == ']':
            assert(len(s.rstrip()) == 2)
            return []
        obj_stack.append([])
        expected_an_indented_block = True
        i = 1
    else:
        if s[:2] == '{}':
            assert(len(s.rstrip()) == 2)
            return {}
        obj_stack.append({})

    while i < len(s):
        indentation_level = 0
        while i < len(s):
            if s[i] == ' ':
                indentation_level += 1
            else:
                break
            i += 1

        if i == len(s): # end of source
            break

        if s[i] in "\r\n": # lines with only whitespace do not affect the indentation
            i += 1
            while i < len(s) and s[i] in "\r\n":
                i += 1
            continue

        if s[i:i+2] == '. ':
            indentation_level += 1
            i += 1
            while i < len(s):
                if s[i] == ' ':
                    indentation_level += 1
                else:
                    break
                i += 1
            assert(type(obj_stack[-1]) == list or (type(obj_stack[-1]) == dict and type(obj_stack[-2]) == list))
            if type(obj_stack[-1]) == dict:
                obj_stack.pop()
            new_dict = {}
            obj_stack[-1].append(new_dict)
            obj_stack.append(new_dict)

        prev_indentation_level = indentation_levels[-1] if len(indentation_levels) else 0

        if expected_an_indented_block:
            if not indentation_level > prev_indentation_level:
                raise Error('expected an indented block', i)

        if indentation_level == prev_indentation_level:
            pass

        elif indentation_level > prev_indentation_level:
            if not expected_an_indented_block:
                raise Error('unexpected indent', i)
            expected_an_indented_block = False
            indentation_levels.append(indentation_level)
            #obj_stack.append(None)

        else: # [
            if s[i] == ']':
                assert(type(obj_stack[-1]) == list or (type(obj_stack[-1]) == dict and type(obj_stack[-2]) == list))
                i += 1
                indentation_levels.pop()
                if len(obj_stack) > 1:
                    if type(obj_stack[-1]) == list or (len(obj_stack) == 2 and type(obj_stack[0]) == list):
                        obj_stack.pop()
                    else:
                        obj_stack.pop()
                        obj_stack.pop()
                continue

            while True:
                indentation_levels.pop()
                obj_stack.pop()
                level = indentation_levels[-1] if len(indentation_levels) else 0
                if level == indentation_level:
                    break
                if level < indentation_level:
                    raise Error('unindent does not match any outer indentation level', i)

        if s[i] == '[': # nested inline list
            assert(type(obj_stack[-1]) == list)
            new_list = []
            obj_stack[-1].append(new_list)
            i += 1
            while True:
                if i == len(s):
                    raise Error('unexpected end of source', i)
                if s[i] == ']':
                    i += 1
                    break # [
                new_list.append(from_str(',]'))
                if i < len(s):
                    if s[i] == ',':
                        i += 1
                        while i < len(s) and s[i] in " \t": # skip spaces after `,`
                            i += 1 # [[
                    elif s[i] != ']':
                        raise Error('expected `]`', i)
            continue

        if s[i:i+2] == '{}':
            #assert(type(obj_stack[-1]) == list)
            #obj_stack[-1].append({})
            i += 2
            continue

        start = i
        key = from_str('=')
        while i < len(s) and s[i] in " \t": # skip spaces after key
            i += 1
        if i < len(s) and s[i] == '=':
            i += 1
            while i < len(s) and s[i] in " \t": # skip spaces after `=`
                i += 1
            if s[i:i+2] in ("[\r", "[\n"): # ]]
                i += 2
                expected_an_indented_block = True
                new_list = []
                obj_stack[-1][key] = new_list
                obj_stack.append(new_list)
            else:
                if s[i:i+2] == '[]':
                    i += 2
                    value = []
                elif s[i:i+2] == '{}':
                    i += 2
                    value = {}
                else:
                    value = from_str()
                if type(obj_stack[-1]) != dict:
                    raise Error('key/value pairs are allowed only inside dictionaries not lists', start)
                obj_stack[-1][key] = value
        else:
            if type(obj_stack[-1]) == list:
                obj_stack[-1].append(key)
            else:
                expected_an_indented_block = True
                new_dict = {}
                obj_stack[-1][key] = new_dict
                obj_stack.append(new_dict)

    if expected_an_indented_block:
        raise Error('expected an indented block', i)

    while len(indentation_levels):
        indentation_levels.pop()
        obj_stack.pop()

    assert(len(obj_stack) == 1)
    return obj_stack[0]
