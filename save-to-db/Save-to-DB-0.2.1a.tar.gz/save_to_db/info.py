import inspect
from save_to_db.adapters import ADAPTERS


name = 'Save-to-DB'
short_description = ('Make it easy to store data from any source into a '
                     'database.')
release = '0.2.1a'


def print_info():
    to_print = ['='*80, '{}, release: {}'.format(name, release)]
    to_print.append(short_description)
    to_print.append('='*80)
    to_print.append('Number of ORM adapters: {}'.format(len(ADAPTERS)))
    for i, adapter_cls in enumerate(ADAPTERS):
        to_print.append('-'*80)
        to_print.append('{}. {}:'.format(i+1, adapter_cls.__name__))
        to_print.append(inspect.getdoc(adapter_cls))
    to_print.append('='*80)
    
    print('\n'.join(to_print))


