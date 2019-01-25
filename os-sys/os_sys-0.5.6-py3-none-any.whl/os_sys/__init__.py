__all__ = ['os_sys', 'fail', 'modules', 'system', 'wifi', 'programs', 'test']
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

import os
def all_maps(d):
    lijst = [os.path.join(d, f) for f in os.listdir(d)]
    ret = []
    num = 0
    while num < len(lijst):
        if '.' in lijst[num]:
            pass
        else:
            ret.append(lijst[num])
        num += 1
    return ret


try:
    from . import fail, modules, system, wifi, programs, test, os_sys
except Exception:
    try:
        from os_sys import fail, modules, system, wifi, programs, test, os_sys
    except Exception:
        import fail, modules, system, wifi, programs, test, os_sys
fail = fail
modules = modules
system = system
wifi = wifi
programs = programs
test = test
os_sys = os_sys
