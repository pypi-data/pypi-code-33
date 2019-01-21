# Application version
ver = '0.2.65'

# Default paths to Mercurial and Git
hg_cmd = 'hg'
git_cmd = 'git'

ignores = [
    "make",
    "make.exe",
    "Makefile",
    "build",
    ".cproject",
    ".gdbinit",
    ".openocd_cfg",
    ".project",
    "aos",
    ".aos",
]

toolchains = {
    'arm-none-eabi':{
        'name': 'gcc-arm-none-eabi',
        'path': 'build/compiler/gcc-arm-none-eabi',
        'command': 'arm-none-eabi-gcc',
        'version': 'all',
        'use_global': True,
        'Win32_url':'https://gitee.com/alios-things/gcc-arm-none-eabi-win32.git',
        'Linux32_url': 'https://gitee.com/alios-things/gcc-arm-none-eabi-linux.git',
        'Linux64_url': 'https://gitee.com/alios-things/gcc-arm-none-eabi-linux.git',
        'OSX_url': 'https://gitee.com/alios-things/gcc-arm-none-eabi-osx.git',
        },
    'xtensa-esp32':{
        'name': 'gcc-xtensa-esp32',
        'path': 'build/compiler/gcc-xtensa-esp32',
        'command': 'xtensa-esp32-elf-gcc',
        'version': '5.2.0',
        'use_global': True,
        'Win32_url': 'https://gitee.com/alios-things/gcc-xtensa-esp32-win32.git',
        'Linux32_url': 'https://gitee.com/alios-things/gcc-xtensa-esp32-linux.git',
        'Linux64_url': 'https://gitee.com/alios-things/gcc-xtensa-esp32-linux.git',
        'OSX_url': 'https://gitee.com/alios-things/gcc-xtensa-esp32-osx.git',
        },
    'xtensa-lx106':{
        'name': 'gcc-xtensa-lx106',
        'path': 'build/compiler/gcc-xtensa-lx106',
        'command': 'xtensa-lx106-elf-gcc',
        'version': '4.8.2',
        'use_global': True,
        'Win32_url': 'https://gitee.com/alios-things/gcc-xtensa-lx106-win32.git',
        'Linux32_url': 'https://gitee.com/alios-things/gcc-xtensa-lx106-linux.git',
        'Linux64_url': 'https://gitee.com/alios-things/gcc-xtensa-lx106-linux.git',
        'OSX_url': 'https://gitee.com/alios-things/gcc-xtensa-lx106-osx.git',
        },
    'csky-abiv2': {
        'name': 'gcc-csky-abiv2',
        'path': 'build/compiler/gcc-csky-abiv2',
        'command': 'csky-abiv2-elf-gcc',
        'version': 'all',
        'use_global': True,
        'Win32_url': 'https://gitee.com/alios-things/gcc-csky-abiv2-win32.git',
        'Linux32_url': 'https://gitee.com/alios-things/gcc-csky-abiv2-linux.git',
        'Linux64_url': 'https://gitee.com/alios-things/gcc-csky-abiv2-linux.git',
        'OSX_url': '',
        },

    'arm-rockchip-linux-gnueabihf': {
        'name': 'gcc-arm-rockchip-linux-gnueabihf',
        'path': 'build/compiler/usr',
        'path_specific': True,
        'command': 'arm-rockchip-linux-gnueabihf-gcc',
        'version': 'all',
        'use_global': True,
        'Win32_url': '',
        'Linux32_url': 'https://gitee.com/alios-things/arm-rockchip-linux-gnueabihf-linux.git',
        'Linux64_url': 'https://gitee.com/alios-things/arm-rockchip-linux-gnueabihf-linux.git',
        'OSX_url': '',
        },

    'nds32le-elf-newlib-v3': {
        'name': 'nds32le-elf-newlib-v3',
        'path': 'build/compiler/nds32le-elf-newlib-v3',
        'path_specific': True,
        'command': 'nds32le-elf-gcc',
        'version': 'all',
        'use_global': True,
        'Win32_url': '',
        'Linux32_url': 'https://gitee.com/alios-things/gcc-nds32le-linux.git',
        'Linux64_url': 'https://gitee.com/alios-things/gcc-nds32le-linux.git',
        'OSX_url': '',
        },

    'openocd': {
        'name': 'OpenOCD',
        'path': 'build/OpenOCD',
        'command': 'openocd',
        'version': '0.10.0',
        'use_global': False,
        'Win32_url': 'https://gitee.com/alios-things/openocd-win32.git',
        'Linux32_url': '',
        'Linux64_url': 'https://gitee.com/alios-things/openocd-linux64.git',
        'OSX_url': 'https://gitee.com/alios-things/openocd-osx.git',
    }
}

boards = {
'amebaz_dev':[toolchains['arm-none-eabi']],
'atsame54-xpro':[toolchains['arm-none-eabi']],
'b_l475e':[toolchains['arm-none-eabi']],
'developerkit':[toolchains['arm-none-eabi']],
'eml3047':[toolchains['arm-none-eabi']],
'esp32devkitc':[toolchains['xtensa-esp32']],
'esp8266':[toolchains['xtensa-lx106']],
'frdmkl27z':[toolchains['arm-none-eabi']],
'hobbit1_evb':[toolchains['csky-abiv2']],
'dh5021a_evb':[toolchains['csky-abiv2']],
'cb2201':[toolchains['csky-abiv2']],
'lpcxpresso54102':[toolchains['arm-none-eabi']],
'mk1101':[toolchains['arm-none-eabi']],
'mk3060':[toolchains['arm-none-eabi'], toolchains['openocd']],
'mk3080':[toolchains['arm-none-eabi'], toolchains['openocd']],
'mk3165':[toolchains['arm-none-eabi']],
'mk3166':[toolchains['arm-none-eabi']],
'mk3239':[toolchains['arm-none-eabi']],
'pca10056':[toolchains['arm-none-eabi']],
'pca10040':[toolchains['arm-none-eabi']],
'starterkit':[toolchains['arm-none-eabi']],
'stm32f769i-discovery':[toolchains['arm-none-eabi']],
'stm32f412zg-nucleo':[toolchains['arm-none-eabi']],
'stm32l432kc-nucleo':[toolchains['arm-none-eabi']],
'stm32l433rc-nucleo':[toolchains['arm-none-eabi']],
'stm32l476rg-nucleo':[toolchains['arm-none-eabi']],
'stm32l496g-discovery':[toolchains['arm-none-eabi']],
'sv6266_evb':[toolchains['nds32le-elf-newlib-v3']],
'msp432p4111launchpad':[toolchains['arm-none-eabi']],
'xr871evb':[toolchains['arm-none-eabi']],
'rk1108':[toolchains['arm-rockchip-linux-gnueabihf']],
'uno-91h':[toolchains['arm-none-eabi']],
}

# reference to local (unpublished) repo - dir#rev
regex_local_ref = r'^([\w.+-][\w./+-]*?)/?(?:#(.*))?$'
# reference to repo - url#rev
regex_url_ref = r'^(.*/([\w.+-]+)(?:\.\w+)?)/?(?:#(.*?)?)?$'

# git url (no #rev)
regex_git_url = r'^(git\://|ssh\://|https?\://|)(([^/:@]+)(\:([^/:@]+))?@)?([^/:]+)[:/](.+?)(\.git|\/?)$'
# hg url (no #rev)
regex_hg_url = r'^(file|ssh|https?)://([^/:]+)/([^/]+)/?([^/]+?)?$'

# aos url is subset of hg. aos doesn't support ssh transport
regex_aos_url = r'^(https?)://([\w\-\.]*aos\.(co\.uk|org|com))/(users|teams)/([\w\-]{1,32})/(repos|code)/([\w\-]+)/?$'
# aos sdk builds url
regex_build_url = r'^(https?://([\w\-\.]*aos\.(co\.uk|org|com))/(users|teams)/([\w\-]{1,32})/(repos|code)/([\w\-]+))/builds/?([\w\-]{6,40}|tip)?/?$'

# default aos url
aos_os_url = 'https://github.com/alibaba/AliOS-Things.git'
# default aos component url
aos_lib_url = 'https://aos.org/users/aos_official/code/aos/builds/'
# aos SDK tools needed for programs based on aos SDK component
aos_sdk_tools_url = 'https://aos.org/users/aos_official/code/aos-sdk-tools'
# open_ocd_zip
open_ocd_url = 'https://files.alicdn.com/tpsservice/27ba2d597a43abfca94de351dae65dff.zip'

# verbose logging
verbose = False
very_verbose = False
install_requirements = True
cache_repositories = True

# stores current working directory for recursive operations
cwd_root = ""

eclispe_project_dir = 'aos/makefiles/eclipse_project'

APP_PATH = 'app_path'
PROGRAM_PATH = 'program_path'
AOS_SDK_PATH = 'AOS_SDK_PATH'
OS_PATH = 'os_path'
OS_NAME = 'AliOS-Things'
PATH_TYPE = 'path_type'
AOS_COMPONENT_BASE_URL = 'https://github.com/AliOS-Things'
CUBE_MAKEFILE = 'cube.mk'
CUBE_MODIFY = 'cube_modify'
REMOTE_PATH = 'remote'
