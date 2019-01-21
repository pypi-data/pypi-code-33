"""
This module is for generating random, valid web navigator's User-Agent HTTP headers.

Functions:
* generate_user_agent: generates User-Agent HTTP header

"""


from itertools import product
from random import choice, randint

import six
from .exceptions import InvalidOption
from .constants import *


__all__ = ['generate_user_agent']


def get_firefox_build():
    return choice(FIREFOX_VERSION)


def get_chrome_build():
    build = choice(CHROME_BUILD)
    return '%d.0.%d.%d' % (
        build[0],
        randint(build[1], build[2]),
        randint(0, 99),
    )


def get_ie_build():
    return choice(IE_VERSION)


def get_edge_build():
    return choice(EDGE_VERSION)


def fix_chrome_mac_platform(platform):
    """
    Chrome on Mac OS adds minor version number and uses underscores instead
    of dots. E.g. platform for Firefox will be: 'Intel Mac OS X 10.11'
    but for Chrome it will be 'Intel Mac OS X 10_11_6'.

    :param platform: - string like "Macintosh; Intel Mac OS X 10.8"
    :return: platform with version number including minor number and formatted
    with underscores, e.g. "Macintosh; Intel Mac OS X 10_8_2"
    """
    ver = platform.split('OS X ')[1]
    build_range = range(*MACOSX_CHROME_BUILD_RANGE[ver])
    build = choice(build_range)
    mac_ver = ver.replace('.', '_') + '_' + str(build)
    return 'Macintosh; Intel Mac OS X %s' % mac_ver


def build_system_components(device_type, os_id, navigator_id):
    """
    For given os_id build random platform and oscpu components

    Returns dict {platform_version, platform, ua_platform, oscpu}

    platform_version is OS name used in different places
    ua_platform goes to navigator.platform
    platform is used in building navigator.userAgent
    oscpu goes to navigator.oscpu
    """

    if os_id == 'win':
        if navigator_id == 'edge':
            platform_version = 'Windows NT 10.0'
        else:
            platform_version = choice(OS_PLATFORM['win'])
        cpu = choice(OS_CPU['win'])
        if cpu:
            platform = '%s; %s' % (platform_version, cpu)
        else:
            platform = platform_version
        res = {
            'platform_version': platform_version,
            'platform': platform,
            'ua_platform': platform,
            'oscpu': platform,
        }
    elif os_id == 'linux':
        cpu = choice(OS_CPU['linux'])
        platform_version = choice(OS_PLATFORM['linux'])
        platform = '%s %s' % (platform_version, cpu)
        res = {
            'platform_version': platform_version,
            'platform': platform,
            'ua_platform': platform,
            'oscpu': 'Linux %s' % cpu,
        }
    elif os_id == 'mac':
        cpu = choice(OS_CPU['mac'])
        platform_version = choice(OS_PLATFORM['mac'])
        platform = platform_version
        if navigator_id == 'chrome':
            platform = fix_chrome_mac_platform(platform)
        res = {
            'platform_version': platform_version,
            'platform': 'MacIntel',
            'ua_platform': platform,
            'oscpu': 'Intel Mac OS X %s' % platform.split(' ')[-1],
        }
    elif os_id == 'android':
        platform_version = choice(OS_PLATFORM['android'])
        if navigator_id == 'firefox':
            ua_platform = '%s; Mobile' % platform_version
        elif navigator_id == 'chrome':
            dev_id = choice(SMARTPHONE_DEV)
            bulid_id = choice(SMARTPHONE_BUILD)
            device_id = '%s Build/%s' % (dev_id, bulid_id)
            ua_platform = 'Linux; %s; %s' % (platform_version, device_id)
        oscpu = 'Linux %s' % choice(OS_CPU['android'])
        res = {
            'platform_version': platform_version,
            'ua_platform': ua_platform,
            'platform': oscpu,
            'oscpu': oscpu,
        }
    return res


def build_app_components(os_id, navigator_id):
    """
    For given navigator_id build app features

    Returns dict
    """

    if navigator_id == 'firefox':
        build_version = get_firefox_build()
        if os_id in ('win', 'linux', 'mac'):
            geckotrail = '20100101'
        else:
            geckotrail = build_version
        res = {
            'build_version': build_version,
            'geckotrail': geckotrail,
        }
    elif navigator_id == 'chrome':
        res = {
            'build_version': get_chrome_build(),
        }
    elif navigator_id == 'ie':
        num_ver, build_version, trident_version = get_ie_build()
        res = {
            'build_version': build_version,
            'trident_version': trident_version,
        }
    elif navigator_id == 'edge':
        res = {
            'build_version': get_edge_build(),
        }
    return res
    
    
def get_option_choices(opt_name, opt_value, default_value, all_choices):
    """
    Generate possible choices for the option `opt_name`
    limited to `opt_value` value with default value
    as `default_value`
    """

    choices = []
    if isinstance(opt_value, six.string_types):
        choices = [opt_value]
    elif isinstance(opt_value, (list, tuple)):
        choices = list(opt_value)
    elif opt_value is None:
        choices = default_value
    else:
        raise InvalidOption('Option %s has invalid'
                            ' value: %s' % (opt_name, opt_value))
    if 'all' in choices:
        choices = all_choices
    for item in choices:
        if item not in all_choices:
            raise InvalidOption('Choices of option %s contains invalid'
                                ' item: %s' % (opt_name, item))
    return choices


def pick_config_ids(device_type, os, navigator):
    """
    Select one random pair (device_type, os_id, navigator_id) from
    all possible combinations matching the given os and
    navigator filters.

    :param os: allowed os(es)
    :type os: string or list/tuple or None
    :param navigator: allowed browser engine(s)
    :type navigator: string or list/tuple or None
    :param device_type: limit possible oses by device type
    :type device_type: list/tuple or None, possible values:
        "desktop", "smartphone", "all"
    """

    if os is None:
        default_dev_types = ['desktop']
    else:
        default_dev_types = list(DEVICE_TYPE_OS.keys())
    dev_type_choices = get_option_choices(
        'device_type', device_type, default_dev_types,
        list(DEVICE_TYPE_OS.keys())
    )
    os_choices = get_option_choices('os', os, list(OS_NAVIGATOR.keys()),
                                    list(OS_NAVIGATOR.keys()))
    nav_choices = get_option_choices('navigator', navigator,
                                     list(NAVIGATOR_OS.keys()),
                                     list(NAVIGATOR_OS.keys()))

    variants = []
    for dev, os, nav in product(dev_type_choices, os_choices,
                                nav_choices):

        if (os in DEVICE_TYPE_OS[dev]
                and nav in DEVICE_TYPE_NAVIGATOR[dev]
                and nav in OS_NAVIGATOR[os]):
            variants.append((dev, os, nav))
    if not variants:
        raise InvalidOption('Options device_type, os and navigator'
                            ' conflicts with each other')
    device_type, os_id, navigator_id = choice(variants)

    assert os_id in OS_PLATFORM
    assert navigator_id in NAVIGATOR_OS
    assert device_type in DEVICE_TYPE_OS

    return device_type, os_id, navigator_id


def choose_ua_template(device_type, navigator_id, app):
    tpl_name = navigator_id
    if navigator_id == 'ie':
        tpl_name = ('ie_11' if app['build_version'] == 'MSIE 11.0'
                    else 'ie_less_11')
    if navigator_id == 'chrome':
        if device_type == 'smartphone':
            tpl_name = 'chrome_smartphone'
    return USER_AGENT_TEMPLATE[tpl_name]


def build_navigator_app_version(os_id, navigator_id,
                                platform_version, user_agent):
    if navigator_id in ('chrome', 'ie', 'edge'):
        assert user_agent.startswith('Mozilla/')
        app_version = user_agent.split('Mozilla/', 1)[1]
    elif navigator_id == 'firefox':
        if os_id == 'android':
            app_version = '5.0 (%s)' % platform_version
        else:
            os_token = {
                'win': 'Windows',
                'mac': 'Macintosh',
                'linux': 'X11',
            }[os_id]
            app_version = '5.0 (%s)' % os_token
    return app_version


def generate_user_agent(os=None, navigator=None, device_type=None):
    """
    Generates HTTP User-Agent header

    :param os: limit list of os for generation, possible values:
        "win", "linux", "mac", "android", "all"
    :type os: string or list/tuple or None
    :param navigator: limit list of browser engines for generation, possible values:
        "chrome", "firefox", "ie", "edge", "all"
    :type navigator: string or list/tuple or None
    :param device_type: limit possible oses by device type
    :type device_type: list/tuple or None, possible values:
        "desktop", "smartphone", "all"
        
    :return: User-Agent string
    :rtype: string
    :raises InvalidOption: if could not generate user-agent for
        any combination of allowed oses and navigators
    :raise InvalidOption: if any of passed options is invalid
    """

    device_type, os_id, navigator_id = (
        pick_config_ids(device_type, os, navigator))
    system = build_system_components(device_type, os_id, navigator_id)
    app = build_app_components(os_id, navigator_id)
    ua_template = choose_ua_template(device_type, navigator_id, app)
    user_agent = ua_template.format(system=system, app=app)
    return user_agent
