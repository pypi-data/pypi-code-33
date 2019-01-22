import re


class RegexPatternPhp(object):

    FUNCTION = (
        (re.compile(r'(\w+[\.>-]+\w+)\.add\((\w+),\s*&(\w+)::(\w+)'), r'\1.add(\2, "\4"', ['.add(']),
        (re.compile(r'catch\((\w+)\s*(\w*)\)'), r'catch__\1__\2', ['catch']),
        (re.compile(r'DataStorage::shared\(\).get<(\w+)>'), r'DataStorage::shared()->get\1', ['DataStorage::shared']),
        (re.compile(r'Factory::(.+)<\w+>'), r'Factory::\1', ['Factory:']),
        (re.compile(r'\.str\(\)'), r'', ['str()']),
        (re.compile(r'for\s*\(\w+ (.+?)\s*:\s*(.+)\s*\)'), r'foreach($\2 as $\1)', ['for']),
        (re.compile(r'for\s*\(\w+& (.+?)\s*:\s*(.+)\s*\)'), r'foreach($\2 as $\1)', ['for']),
        (re.compile(r'for\s*\(\w+&&\s*\[(\w+),\s*(\w+)\]\s*:\s*(.+)\)'), r'foreach ($\3 as $\1 => $\2)', ['for']),
        (re.compile(r'auto (\w+)'), r'$\1', ['auto']),
        (re.compile(r'auto& (\w+)'), r'$\1', ['auto']),
        (re.compile(r'void (\w+)'), r'$\1', ['void']),
        (re.compile(r'int (\w+)'), r'$\1', ['int']),
        (re.compile(r'bool (\w+)'), r'$\1', ['bool']),
        (re.compile(r'\((\w+) (\w+)\)'), r'($\2)'),
        (re.compile(r'\(const (\w+)\& (\w+)\)'), r'($\2)', ['const']),
        (re.compile(r'\(const (\w+)\* (\w+)\)'), r'($\2)', ['const']),
        (re.compile(r'\((\w+)\* (\w+)\)'), r'($\2)'),
        (re.compile(r'(\w+)\ (\w+),'), r'$\2,'),
        (re.compile(r'(\w+)\& (\w+),'), r'$\2,', ['&']),
        (re.compile(r'(\w+)\* (\w+),'), r'$\2,', ['*']),
        (re.compile(r'const (\w+)\* (\w+)'), r'$\2', ['const ']),
        (re.compile(r'const (\w+)\& (\w+)'), r'$\2', ['const ']),
        (re.compile(r'float (\w+)'), r'$\1', ['float ']),
        (re.compile(r'std::string (\w+)'), r'$\1', ['std::string']),
        (re.compile(r'\bthis\b'), r'$this', ['this']),
        (re.compile(r':const'), r'', ['const']),
        (re.compile(r'(\w+)::(\w+)'), r'\1::$\2', ['::']),
        (re.compile(r'(\w+)::(\w+)\)'), r'\1::$\2)', ['::']),
        (re.compile(r'(\w+)::(\w+)\.'), r'\1::$\2.', ['::']),
        (re.compile(r'(\w+)::(\w+)->'), r'\1::$\2->', ['::']),
        (re.compile(r'(\w+)::(\w+)\]'), r'\1::$\2]', ['::']),
        (re.compile(r'(\w+)::\$(\w+)\('), r'\1::\2(', ['::']),
        (re.compile(r'(\w+)::\$(\w+)\((\w*)\)'), r'\1::\2(\3)', ['::']),
        (re.compile(r'function \$(\w+)'), r'function \1', ['function ']),
        (re.compile(r'\.at\((.*?)\)'), r'[\1]', ['.at']),
        (re.compile(r'(\w+)\.'), r'\1->'),
        (re.compile(r'(\w+)\(\)\.'), r'\1()->'),
        (re.compile(r'(\w+)\]\.'), r'\1]->'),
        (re.compile(r'&(\w+)'), r'\1', ['&']),
        (re.compile(r'\$if\('), r'if(', ['if']),
        (re.compile(r'delete \$(\w+);'), r'', ['delete']),
        (re.compile(r'([-0-9])->([-0-9])f\b'), r'\1.\2', ['']),
        (re.compile(r'assert\(.+\);'), r'', ['assert']),
        (re.compile(r'make_intrusive<(\w+)>\(\s*\)'), r'new \1()', ['make_intrusive']),
        (re.compile(r'dynamic_pointer_cast_intrusive<\w+>\((.+?)\)'), r'\1', ['dynamic_pointer_cast_intrusive']),
        (re.compile(r'new\s*(\w+)\s*\(\s*\)'), r'new \1()', ['']),
        (re.compile(r'(.+?)\->push_back\((.+)\);'), r'array_push(\1, \2);', ['push_back']),
        (re.compile(r'(\w+)\s+(\w+);'), r'$\2 = new \1();'),
        (re.compile(r'\$(\w+) = new return\(\);'), r'return \1;', ['new return']),
        (re.compile(r'std::\$vector<.+?>\s+(\w+)'), r'$\1 = array()', ['std::$vector']),
        (re.compile(r'\blist<.+>\s+(\w+)'), r'$\1 = array()', ['list<']),
        (re.compile(r'\bmap<([<:>\w\s\*&\$]+),\s*([<:>\w\s\*&\$]+)>\s*(\w+)'), r'$\3 = array()', ['map<']),
        (re.compile(r'\bstrTo<(\w+)>'), r'(\1)', ['strTo']),
        (re.compile(r'\btoStr\b'), r'(string)', ['toStr']),
        (re.compile(r'(@{__string_\d+__})\s*\+'), r'\1.', ['@{__string_']),
        (re.compile(r'\+\s*(@{__string_\d+__})'), r'.\1', ['@{__string_']),
    )

    FUNCTION_2 = (
        (re.compile(r'->\$(\w+)\('), r'->\1(', ['->']),
        (re.compile(r'([-0-9]*)->([-0-9]*)f\b'), r'\1.\2'),
        (re.compile(r'([-0-9]*)->f\\b'), r'\1.0'),
        (re.compile(r'\$return\s'), r'return', ['$return']),
        (re.compile(r',\s*std::\$*placeholders::\$*_\d'), r'', ['std::$placeholders']),
        (re.compile(r'list_remove\((\$.+?),\s*([\$.\w]+?)\);'), r'array_splice(\1, array_search(\2, \1), 1);',
         ['list_remove']),
        (re.compile(r'list_clear\((.+?)\);'), r'\1 = array();', ['list_clear']),
        (re.compile(r'string_empty\((.+?)\)'), r'empty(\1)', ['string_empty']),
        (re.compile(r'random_float\(\)'), r'(mt_rand() * 1.0 / mt_getrandmax())', ['random_float']),
        (re.compile(r'random_int\((.+?),\s*(.+)\)'), r'mt_rand(\1, \2-1)', ['random_int']),
        (re.compile(r'std::strcat\((.+?),\s*(.+?)\)'), r'((\1).(\2))', ['std::strcat']),

        # Exception with try/catch block (one catch)
        (re.compile(r'try\n\s*{([\s\S.]+?)}\n\s*catch__((\w+)__(\w*))\n\s+{([\s\S.]+?)}'),
         r'try\n{\1}\ncatch(\3 $\4)\n{\5}', ['try'])
    )

    VARIABLES = {
        re.compile(r'\$(\w+)'): {}
    }

    INITIALIZE = (re.compile(r'(\w+)::(\w+)'), r'\1::$\2')

    REPLACES = (
        ('$if(', 'if('),
        ('function $', 'function '),
        ('($int)', '(int)'),
        ('time(nullptr)', 'time()'),
        ('$$', '$'),
        ('std::max', 'max'),
        ('std::$max<int>', 'max'),
        ('std::$max<float>', 'max'),
        ('std::min', 'min'),
        ('std::$min<int>', 'min'),
        ('std::$min<float>', 'min'),
        ('std::round', 'round'),
        ('std::floor', 'floor'),
        ('std::fabs', 'abs'),
        ('std::ceil', 'ceil'),
        ('std::sqrt', 'sqrt'),
        ('in_list(', 'in_array('),
        ('in_map', 'array_key_exists'),
        ('list_push', 'array_push'),
        ('list_size', 'count'),
        ('map_size', 'count'),
    )
