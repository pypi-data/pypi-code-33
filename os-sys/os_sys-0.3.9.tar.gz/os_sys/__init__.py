__all = ['os_sys', 'fail', 'modules', 'system', 'wifi', 'programs', 'test']
fail_ = ['warn_return', 'make_warn', 'print_warn', 'warn_msg', 'warning_msg', 'warn_file_no', 'msg', 'module_warn', 'text_warn']
__all_names__ = ['main_dir', 'get_import_list', 'get_user', 'cmd', 'info', 'win_version', 'cmd_filter_haak', 'filter_regel', 'cmd_out_list',
           'cmd_out', 'ColorPrint', 'info', 'is_connected', 'ping', 'connect_time', 'internet',
           'chek_speed', 'internet_and_speed', 'cmd_ping', 'cmd',
           'ping_data', 'replace', 'open_site', 'explorer_dict', 'explorer',
           'is_even', 'is_oneven', 'fahr_to_celsius', 'celsius_to_kelvin', 'fahr_to_kelvin', 'convert_c_to_f'
           ]
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



__all__ = __all
try:
    from . import fail, modules, system, wifi, programs, test, os_sys
except Exception:
    from os_sys import fail, modules, system, wifi, programs, test, os_sys
fail = fail
modules = modules
system = system
wifi = fifi
programs = programs
test = test
os_sys = os_sys
