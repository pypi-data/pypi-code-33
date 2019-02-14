# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['specify']

package_data = \
{'': ['*']}

install_requires = \
['prophepy>=0.0.1']

setup_kwargs = {
    'name': 'specify',
    'version': '0.0.6',
    'description': 'A spec tool to describe your classes',
    'long_description': '# Specify\n\nA [PHPSpec](https://github.com/phpspec/phpspec)-like for Python. For fun only (for now). If you\'re looking for a real valid PHPSpec-like, you could check [flowp](http://pawelgalazka.github.io/flowp/testing.html) (but deprecated). [mamba](https://nestorsalceda.com/mamba/) could also interest you, even if it\'s not exactly what you are searching.\n\n## Install\n\n`pip install specify`\n\n## Usage\n\nYou can check the [examples](examples) folder.\n\n```python\nfrom specify import ObjectBehavior\nfrom examples.calculator import Calculator\n\nclass CalculatorSpec(ObjectBehavior):\n    def _let(self):\n        self._describe(Calculator)\n        self._be_constructed_with(\'lorem\', id=32)\n\n    def it_adds_the_numbers(self):\n        self.add(2, 3)._should_be(5)\n```\n\nThe command `python -m specify examples/spec/calculator_spec.py` will render a valid TAP output (hopefully).\n\n```\nTAP version 13\n1..1\n\nok 1 - CalculatorSpec: it adds the numbers\n```\n\nTo have a nice and pretty output, you can then use a TAP formatter like [faucet](https://www.npmjs.com/package/faucet).\n\n- **All specifications must start by `it_`.**\n\n- **All spec files must end by `_spec` for now.**\n\n## Builtin matchers\n\n| Matcher                     | Details                 | Alias                           |\n| --------------------------- | ----------------------- | ------------------------------- |\n| `_should_be`                | check with `is`         | `_should_return`                |\n| `_should_be_like`           | check with `==`         | `_should_return_like`           |\n| `_should_not_be`            | check with `is not`     | `_should_not_return`            |\n| `_should_not_be_like`       | check with `!=`         | `_should_not_return_like`       |\n| `_should_be_an_instance_of` | check with `isinstance` | `_should_return_an_instance_of` |\n| `_should_have_length`       | check with `len(x)`     |                                 |\n\n## Custom matchers\n\nYou can implement a `_matchers` function in your spec, to add custom matchers.\n\nThe key of the matcher is left trimmed by `_should_` and the first argument\npassed to your function is the value itself.\n\nIf you return false, the test will fail.\n\nHere is an example:\n\n```python\nclass CalculatorSpec(ObjectBehavior):\n    # ...\n\n    def it_adds_the_numbers(self):\n        self.add(2, 3)._should_be_a_number()\n        self.add(2, 3)._should_be_greater_than(10)\n\n    def _matchers(self):\n        def be_a_number(value, *args):\n            return isinstance(value, int)\n\n        def be_greater_than(value, expected_value):\n            return value > expected_value\n\n        return {\n            \'be_a_number\': be_a_number,\n            \'be_greater_than\': be_greater_than\n        }\n```\n\n## Fluent API\n\nAll matchers (builtin and custom) are chainable. Example:\n\n`self.add(2, 3)._should_be_a_number()._should_be(5)._should_be_greater_than(3)`\n\n## Mocks\n\nThanks to [prophepy](https://github.com/Einenlum/prophepy) (did you get the pun with `prophecy`? Hoho), you can\neasily mock things in a [Prophecy](https://github.com/phpspec/prophecy) way.\n\nGiven this `Displayer` class:\n\n```python\nfrom .calculator import Calculator\n\nclass Displayer:\n    def __init__(self, calculator: Calculator):\n        self.calculator = calculator\n\n    def display_addition(self, *args) -> str:\n        total = str(self.calculator.add(*args))\n        args = [str(arg) for arg in args]\n\n        return f"{\' + \'.join(args)} = {total}"\n```\n\nHere is the spec, mocking the `Calculator`:\n\n```python\nfrom specify import ObjectBehavior\nfrom examples.calculator import Calculator\nfrom examples.displayer import Displayer\nfrom prophepy import prophesize\n\nclass DisplayerSpec(ObjectBehavior):\n    def _let(self):\n        self._describe(Displayer)\n        self.__calculator = prophesize(Calculator)\n        self._be_constructed_with(self.__calculator._reveal())\n\n    def it_displays_addition(self):\n        self.__calculator.add(2, 3)._should_be_called()\n        self.__calculator.add(2, 3)._will_return(5)\n        self.display_addition(2, 3)._should_be_like(\'2 + 3 = 5\')\n```\n\n## TODO\n\n- Handle attributes and not only methods\n- Import easily prophepy mocks (decorator?)\n- Find a way to easily mock internal calls\n- Add more matchers\n- Make the tap output a stream as the spec say\n- Improve the shitty way specs are loaded for now\n',
    'author': 'Einenlum',
    'author_email': 'yann.rabiller@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
