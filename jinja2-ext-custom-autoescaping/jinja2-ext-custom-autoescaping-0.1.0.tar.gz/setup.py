# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jinja2_ext_custom_autoescaping']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.10,<3.0']

setup_kwargs = {
    'name': 'jinja2-ext-custom-autoescaping',
    'version': '0.1.0',
    'description': 'Jinja2 extension to enable the use of any filter as a custom autescape filter.',
    'long_description': '# Overview\n\nJinja2 extension to enable the use of any filter as a custom autoscape filter.\n\nThis package allows you to define rules to determine when your custom autoescaping filter will be\nenabled using the same \'select_autoescape\' method you already use to determine\nwhen the built-in autoescaping filter is enabled.\n\n# Usage\n    from jinja2_ext_custom_autoescaping import CustomAutoescapeExtension, enable_custom_autoescaping\n    from jinja2 import Environment, select_autoescape, FileSystemLoader\n\n    # Your custom filter...        \n    def my_filter(val):\n        print(val)\n        if isinstance(val, str):\n            return val.replace(r"\\\\", r"\\\\\\\\")\n        return val\n    \n        \n    # Here you set the rules for when the built-in autoescaping will be enabled\n    built_in_select_autoescape = select_autoescape(enabled_extensions=[\'html\', \'htm\', \'xml\'],\n                                                   disabled_extensions=[\'txt\', \'tex\'],\n                                                   default_for_string=True,\n                                                   default=True)\n\n    # - select_autoescape is a closure\n    # - enabled_extensions takes precedence over disabled_extensions, so an extension in both lists will be enabled\n    # - You most likely do not want to have custom autoescaping on while built-in autoescaping is also on\n\n    # Here you set the rules for when your custom autoescaping will be enabled\n    custom_select_autoescape = select_autoescape(enabled_extensions=[\'tex\', \'txt\'],\n                                                 disabled_extensions=[],\n                                                 default_for_string=False,\n                                                 default=False)\n    \n    # Just focusing on the important parts of your Environment construction.\n    env = Environment(extensions=[CustomAutoescapeExtension],\n                      loader=FileSystemLoader([\'.\']),\n                      autoescape=built_in_select_autoescape)\n\n    opts = {\'custom_select_autoescape\': custom_select_autoescape,\n            \'custom_autoescape_filter_name\': \'my_filter\',\n            \'custom_autoescape_filter_func\': my_filter}\n\n    # Register the filter and enables autoescaping\n    enable_custom_autoescaping(env, **opts)\n    \n    # Now you are ready to go...\n    template = env.get_template(\'test_template.txt\')\n    print(template.render(var={\'entry 1\': \'value 1\', \'entry2\': r\'val\\\\ue 2\'}))\n',
    'author': 'mbello',
    'author_email': 'mbello@users.noreply.github.com',
    'url': 'https://github.com/mbello/jinja2-ext-custom-autoescaping',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
