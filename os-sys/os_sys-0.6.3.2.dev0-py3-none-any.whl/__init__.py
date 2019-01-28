__all__ = ['os_sys', 'fail', 'modules', 'system', 'wifi', 'programs', 'test', 'code', 'decode', 'discription', '_code', 'more_input']
fail_ = ['warn_return', 'make_warn', 'print_warn', 'warn_msg', 'warning_msg', 'warn_file_no', 'msg', 'module_warn', 'text_warn']
__all_names__ = ['main_dir', 'get_import_list', 'get_user', 'cmd', 'info', 'win_version', 'cmd_filter_haak', 'filter_regel', 'cmd_out_list',
           'cmd_out', 'ColorPrint', 'info', 'is_connected', 'ping', 'connect_time', 'internet',
           'chek_speed', 'internet_and_speed', 'cmd_ping', 'cmd',
           'ping_data', 'replace', 'open_site', 'explorer_dict', 'explorer',
           'is_even', 'is_oneven', 'fahr_to_celsius', 'celsius_to_kelvin', 'fahr_to_kelvin', 'convert_c_to_f'
           ]
__all = []
os_sys_ = __all_names__
index = 0
os_all = []
while index < len(os_sys_):
    __all.append(''.join('os_sys.' + os_sys_[index]))
    index += 1
index = 0

index = 0
fail_all = []
while index < len(fail_):
    __all.append(''.join('fail.' + fail_[index]))
    index += 1

def _code(txt):
    b = txt
    d = {}
    for c in (65, 97):
        for i in range(26):
            d[chr(i+c)] = chr((i+13) % 26 + c)

    data = "".join([d.get(c, c) for c in b])
    
    return data
    
def more_input():
    init = input()
    mystr = str()
    while not init == 'None':
        mystr = mystr + (str(init)) + '\n'
        init = input()
    
    return mystr

def make_text(file):
    try:
        fh = open(str(file) + '.lib', mode='r', encoding='utf-8')
    except Exception:
        data = ''
        pass
    else:
        data = _code(fh.read())
        fh.close()
        print(data)
    fh = open(str(file) + '.lib', mode='w', encoding='utf-8')
    fh.write(str(_code(str(data + more_input()))))
    fh.close()

def all_dict(dictory, maps=True, files=False, print_data=False, exception=None):
    import os
    data = []
    string_data = ''
    print_ = True if print_data == 'print' or print or True else False
    for dirname, dirnames, filenames in os.walk(dicto):
        # print path to all subdirectories first.
        if maps:
            for subdirname in dirnames:
                dat = os.path.join(dirname, subdirname)
                data.append(dat)
                string_data = string_data + '\n' + dat
                if print_:
                    print(dat)

        # print path to all filenames.
        if files:
            for filename in filenames:
                dat = os.path.join(dirname, filename)
                data.append(dat)
                string_data = string_data + '\n' + dat
                if print_:
                    
                    print(dat)
        

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if exception in dirnames:
            # don't go into any .git directories.
            dirnames.remove(exception)
    
    return [data, string_data]

try:
    from . import fail, modules, system, wifi, programs, test, os_sys, errors, discription
except Exception:
    try:
        from os_sys import fail, modules, system, wifi, programs, test, os_sys, errors, discription
    except Exception:
        import fail, modules, system, wifi, programs, test, os_sys, errors, discription
fail = fail
modules = modules
system = system
wifi = wifi
programs = programs
test = test
os_sys = os_sys
errors = errors
discription = discription
decode = discription
code = discription
