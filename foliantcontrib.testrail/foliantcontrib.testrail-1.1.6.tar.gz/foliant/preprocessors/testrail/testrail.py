'''
Preprocessor for Foliant documentation authoring tool.
Collects test cases from TestRail project to markdown file.
'''


from foliant.preprocessors.base import BasePreprocessor
from .testrailapi import *

from jinja2 import Environment, FileSystemLoader
from pkg_resources import resource_filename
import os
from pathlib import Path
from pprint import pprint
from shutil import copytree, copyfile
import re


class Preprocessor(BasePreprocessor):
    defaults = {
        'filename': 'test_cases.md',
        'rewrite_src_file': False,
        'template_folder': 'case_templates',
        'section_header': 'Программа испытаний',
        'std_table_header': 'Таблица прохождения испытаний',
        'std_table_column_headers': '№; Приоритет; Платформа; ID; Название; Успешно; Комментарий',
        'suite_ids': set(),
        'section_ids': set(),
        'exclude_suite_ids': set(),
        'exclude_section_ids': set(),
        'exclude_case_ids': set(),
        'add_suite_headers': True,
        'add_section_headers': True,
        'add_case_id_to_case_header': False,
        'add_case_id_to_std_table': False,
        'add_std_table': True,
        'resolve_urls': False,
        'screenshots_url': '',
        'screenshots_ext': '.png',
        'print_case_structure': False,
        'multi_param_name': '',
        'multi_param_select': '',
        'multi_param_select_type': 'any',
        'add_cases_without_multi_param': True,
        'add_multi_param_to_case_header': False,
        'add_multi_param_to_std_table': False,
        'checkbox_param_name': '',
        'checkbox_param_select_type': 'checked',
        'choose_priorities': '',
        'add_priority_to_case_header': False,
        'add_priority_to_std_table': False,
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('testrail')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

        self._filename = self.options['filename']
        self._rewrite_src_file = self.options['rewrite_src_file']
        self._template_folder = self.options['template_folder']
        self._section_header = self.options['section_header']

        self._std_table_header = self.options['std_table_header']
        self._std_table_column_headers = list(map(str.strip, list(self.options['std_table_column_headers'].split(';'))))

        self._testrail_url = self.options['testrail_url']
        self._testrail_login = self.options['testrail_login']
        self._testrail_pass = self.options['testrail_pass']

        self._client = testrailapi.APIClient(self._testrail_url)
        self._client.user = self._testrail_login
        self._client.password = self._testrail_pass

        self._project_id = self.options['project_id']

        self._suite_ids = set()
        self._suite_ids = self._parse_ids_options(self._suite_ids, self.options['suite_ids'])
        self._exclude_suite_ids = set()
        self._exclude_suite_ids = self._parse_ids_options(self._exclude_suite_ids, self.options['exclude_suite_ids'])

        self._section_ids = set()
        self._section_ids = self._parse_ids_options(self._section_ids, self.options['section_ids'])
        self._exclude_section_ids = set()
        self._exclude_section_ids = self._parse_ids_options(self._exclude_section_ids, self.options['exclude_section_ids'])

        self._exclude_case_ids = set()
        self._exclude_case_ids = self._parse_ids_options(self._exclude_case_ids, self.options['exclude_case_ids'])

        self._params = {
            'multi_param_name': self.options['multi_param_name'],
            'multi_param_sys_name': 'custom_' + self.options['multi_param_name'],
            'multi_param_select': list(map(str.lower, map(str.strip, list(self.options['multi_param_select'].split(','))))),
            'multi_param_select_type': self.options['multi_param_select_type'],
            'add_cases_without_multi_param': self.options['add_cases_without_multi_param'],
            'checkbox_param_name': self.options['checkbox_param_name'],
            'checkbox_param_sys_name': 'custom_' + self.options['checkbox_param_name'],
            'checkbox_param_select_type': self.options['checkbox_param_select_type'],
            'choose_priorities': list(map(str.lower, map(str.strip, list(self.options['choose_priorities'].split(','))))),
            'add_multi_param_to_case_header': self.options['add_multi_param_to_case_header'],
            'add_multi_param_to_std_table': self.options['add_multi_param_to_std_table'],
            'add_priority_to_case_header': self.options['add_priority_to_case_header'],
            'add_priority_to_std_table': self.options['add_priority_to_std_table'],
            'add_case_id_to_case_header': self.options['add_case_id_to_case_header'],
            'add_case_id_to_std_table': self.options['add_case_id_to_std_table']
        }

        self._add_suite_headers = self.options['add_suite_headers']
        self._add_section_headers = self.options['add_section_headers']
        self._add_std_table = self.options['add_std_table']

        self._resolve_urls = self.options['resolve_urls']
        if self._params['multi_param_select'][0] != '':
            self._screenshots_url = '/'.join((self.options['screenshots_url'], 'raw/master/images', self._params['multi_param_select'][0], ''))
        else:
            self._screenshots_url = '/'.join((self.options['screenshots_url'], 'raw/master/images/'))
        self._screenshots_ext = self.options['screenshots_ext']

        self._print_case_structure = self.options['print_case_structure']

        self._case_counter = 0
        self._test_cases = ['# ' + self._section_header + '\n\n']
        self._std_table = []

        self._env = Environment(loader=FileSystemLoader(str(self.project_path)))

        self._template_folder = self.options['template_folder']
        if self._template_folder == self.defaults['template_folder'] and not os.path.exists(self.project_path / self.defaults['template_folder']):
            copytree(resource_filename(__name__, 'case_templates'), self.project_path / self.defaults['template_folder'])


    def _parse_ids_options(self, variable, option):
        if option:
            for item in str(option).replace(' ', '').split(','):
                variable.add(int(item))
        else:
            variable = option
        return variable


    def _collect_suites_and_sections_ids(self, project_suites):

        if not self._suite_ids:
            if not self._section_ids:
                for suite in project_suites:
                    self._suite_ids.add(suite['id'])
            else:
                for suite in project_suites:
                    suite_sections = self._client.send_get('get_sections/%s&suite_id=%s' % (self._project_id, suite['id']))
                    for section in suite_sections:
                        if section['id'] in self._section_ids:
                            self._suite_ids.add(suite['id'])
                            continue
        self._suite_ids -= self._exclude_suite_ids

        if not self._section_ids:
            for suite in project_suites:
                if suite['id'] in self._suite_ids:
                    suite_sections = self._client.send_get('get_sections/%s&suite_id=%s' % (self._project_id, suite['id']))
                    for section in suite_sections:    
                        self._section_ids.add(section['id'])
        next_iteration = True  # collect all child subsections for sections specified
        while next_iteration:
            next_iteration = False
            for suite in project_suites:
                if suite['id'] in self._suite_ids:
                    suite_sections = self._client.send_get('get_sections/%s&suite_id=%s' % (self._project_id, suite['id']))
                    for section in suite_sections:
                        if section['id'] not in self._section_ids and section['parent_id'] in self._section_ids:    
                            self._section_ids.add(section['id'])
                            next_iteration = True
        self._section_ids -= self._exclude_section_ids


    def _collect_cases(self, project_suites):
        for suite in project_suites:

            if suite['id'] in self._suite_ids:

                if self._add_suite_headers and not suite['is_master']:  # Add suite names if present and raise next chapters title level
                    self._test_cases.append('## %s\n\n' % suite['name'])
                    suite['name'] = ''.join(('**', suite['name'].upper(), '**'))

                    table_row = '|   | '
                    if self._params['add_priority_to_std_table']:
                        table_row += '  | '
                    if self._params['add_multi_param_to_std_table']:
                        table_row += '  | '
                    if self._params['add_case_id_to_std_table']:
                        table_row += '  | '
                    table_row += suite['name'] + ' |   |   |'

                    self._std_table.append(table_row)

                    if suite['description']:
                        self._test_cases.append('%s\n\n' % suite['description'])
                    suite_title_level_up = '#'
                else:
                    suite_title_level_up = ''

                self._collect_sections(suite['id'], suite_title_level_up)


    def _collect_sections(self, suite_id, suite_title_level_up):
        suite_sections = self._client.send_get('get_sections/%s&suite_id=%s' % (self._project_id, suite_id))

        for section in suite_sections:

            title_level_up = suite_title_level_up

            if self._add_section_headers:
                for i in range(section['depth']):
                    title_level_up += '#'

                section_name = re.sub("[0-9].*\.", "", section['name']).strip()  # Remove numbers in section headers

                if section_name.isupper():  # Remove headers capitalization
                    section_name = section_name.lower()
                    section_name = section_name[0].upper() + section_name[1:]

                self._test_cases.append('##%s %s\n\n' % (title_level_up,
                                section_name))

                section_name = ''.join(('**', section_name, '**'))

                table_row = '|   | '
                if self._params['add_priority_to_std_table']:
                    table_row += '  | '
                if self._params['add_multi_param_to_std_table']:
                    table_row += '  | '
                if self._params['add_case_id_to_std_table']:
                    table_row += '  | '
                table_row += section_name + ' |   |   |'

                self._std_table.append(table_row)

            if section['id'] in self._section_ids:  # This condition is checked not earlier to save parent chapter headers

                if self._add_section_headers and section['description']:
                    self._test_cases.append('%s\n\n' % section['description'])

                if self._add_section_headers:
                    title_level_up += '#'

                self._collect_case_data(suite_id, section['id'], title_level_up)


    def _if_take_case(self, case):

        multi_param_cond = True
        checkbox_param_cond = True
        priority_cond = True
        exclude_cond = True

        if self._params['multi_param_sys_name'] in case.keys():
            if type(case[self._params['multi_param_sys_name']]) == int:
                case[self._params['multi_param_sys_name']] = [case[self._params['multi_param_sys_name']]]

            if self._params['multi_param_sys_name'] not in case.keys() and not self._params['add_cases_without_multi_param']:
                    multi_param_cond = False
            elif self._params['multi_param_select_type'] == 'any' and not (set(case[self._params['multi_param_sys_name']]) & self._params['multi_param_matches']):
                multi_param_cond = False
            elif self._params['multi_param_select_type'] == 'only' and not (set(case[self._params['multi_param_sys_name']]) <= self._params['multi_param_matches']):
                multi_param_cond = False
            elif self._params['multi_param_select_type'] == 'all' and not (self._params['multi_param_matches'] <= set(case[self._params['multi_param_sys_name']])):
                multi_param_cond = False
            elif self._params['multi_param_select_type'] == 'match' and not (set(case[self._params['multi_param_sys_name']]) == self._params['multi_param_matches']):
                multi_param_cond = False

        if self._params['checkbox_param_sys_name'] in case.keys():
            if self._params['checkbox_param_select_type'] == 'checked' and not case[self._params['checkbox_param_sys_name']]:
                checkbox_param_cond = False
            if self._params['checkbox_param_select_type'] == 'unchecked' and case[self._params['checkbox_param_sys_name']]:
                checkbox_param_cond = False

        if self._params['choose_priorities'][0] != '' and case['priority_id'] not in self._params['priority_matches']:
            priority_cond = False

        if case['id'] in self._exclude_case_ids:
            exclude_cond = False

        take_case = multi_param_cond and checkbox_param_cond and priority_cond and exclude_cond

        return take_case


    def _collect_case_data(self, suite_id, section_id, title_level_up):
        section_cases = self._client.send_get(
            'get_cases/%s&suite_id=%s&section_id=%s' %
            (self._project_id, suite_id, section_id))

        for case in section_cases:
            take_case = self._if_take_case(case)

            if take_case:
                self._case_counter += 1

                table_row = '| ' + str(self._case_counter) + ' | '
                header_ending = ''
                header_ending_list = []

                if self._params['add_priority_to_std_table']:
                    table_row += self._priorities[case['priority_id']] + ' | '
                if self._params['add_priority_to_case_header']:
                    header_ending_list.append(self._priorities[case['priority_id']])
                text = ''
                if self._params['multi_param_name'] and self._params['multi_param_sys_name'] in case.keys():
                    for item in case[self._params['multi_param_sys_name']]:
                        text += self._params['multi_param_values'][item] + ', '
                if self._params['add_multi_param_to_std_table']:
                    table_row += text[:-2] + '  | '
                if self._params['add_multi_param_to_case_header']:
                    header_ending_list.append(text[:-2])
                if self._params['add_case_id_to_std_table']:
                    table_row += str(case['id']) + '  | '
                if self._params['add_case_id_to_case_header']:
                    header_ending_list.append('ID ' + str(case['id']))
                table_row += case['title'] + ' |   |   |'
                header_ending_list.reverse()
                for item in header_ending_list:
                    header_ending += item + '; '
                header_ending = header_ending[:-2]
                if header_ending:
                    header_ending = ' \[' + header_ending + '\]'

                self._std_table.append(table_row)
                self._test_cases.append('##%s %s%s\n\n' % (title_level_up, case['title'], header_ending))

# Test-case processing differs depending on the template id. All processors are in case_processing module.
                case_template = '/'.join((str(self.project_path), self._template_folder, ''.join((str(case['template_id']), '.j2'))))

                if not os.path.isfile(case_template):
                    print(f"\n\nThere is no jinja template for test case template_id {case['template_id']} (case_id {case['id']}) in folder {self._template_folder}")
                    if self._print_case_structure:
                        print('\nCase structure:')
                        pprint(case)
                else:
                    try:
                        template = self._env.get_template(case_template)
                        result = template.render(case=case, params=self._params).split('\r\n')
                    except Exception as exception:
                        print(f"\nThere is a problem with jinja template for test case template_id {case['template_id']} (case_id {case['id']}) in folder {self._template_folder}:\n{exception}")
                        if self._print_case_structure:
                            print('\nCase structure:')
                            pprint(case)
                        result = None

                    if result:
                        for string in result:
                            self._test_cases.append(string)
                            self._test_cases.append('\n')


    def _remove_empty_chapters(self):
        next_iteration = True

        while next_iteration:
            next_iteration = False
            empty_chapter = True
            empty_chapter_title_level = 1
            string_counter = 0
            remove_from_case_list = 0

            for index in range(len(self._test_cases)-1, -1, -1):

                string_counter += 1

                if self._test_cases[index] and not self._test_cases[index].startswith('#'):
                    empty_chapter = False

                elif self._test_cases[index].startswith('#'):
                    remove_from_case_list += 1
                    title_level = len(self._test_cases[index].split(' ')[0])

                    if empty_chapter and title_level >= empty_chapter_title_level:

                        for string in range(string_counter):
                            self._test_cases.pop(index)
                        if len(self._test_cases) > 0:
                            renumber_strings = False
                            if self._std_table[len(self._std_table)-remove_from_case_list].split('|')[1].strip():
                                renumber_strings = True
                            self._std_table.pop(len(self._std_table)-remove_from_case_list)
                            if renumber_strings:
                                self._renumber_strings(remove_from_case_list-1)
                        remove_from_case_list -= 1

                        next_iteration = True

                    empty_chapter_title_level = title_level
                    empty_chapter = True
                    string_counter = 0


    def _renumber_strings(self, shift):
        for string_number in range(len(self._std_table)-shift, len(self._std_table)):
            case_number = self._std_table[string_number].split('|')[1].strip()
            if case_number:
                new_number = str(int(case_number) - 1)
                if len(new_number)<len(case_number):
                    new_number += ' '
                self._std_table[string_number] = self._std_table[string_number].replace(case_number, new_number, 1)


    def _make_std_table_first_row(self, add_column_headers):
        first_row = '| '
        for i, header in enumerate(self._std_table_column_headers):
            if add_column_headers[i]:
                first_row += self._std_table_column_headers[i] + ' | '
        first_row = first_row.strip()
        return first_row


    def _std_table_aligning(self):
        add_column_headers = [True, self._params['add_priority_to_std_table'], self._params['add_multi_param_to_std_table'], self._params['add_case_id_to_std_table'], True, True, True]

        self._std_table_column_headers = self._make_std_table_first_row(add_column_headers)

        self._std_table = [self._std_table_column_headers] + self._std_table

        column_widths = [0 for i in range(self._std_table[0].count('|') - 1)]
        strings = []
        max_width = 60

        for i, line in enumerate(self._std_table):
            line = line.split('|')
            line.pop(0)
            line.pop(len(line) - 1)
            strings.append(line)

            for j in range(len(strings[i])):
                strings[i][j] = strings[i][j].strip(' ')
                if len(strings[i][j]) > column_widths[j]:
                    column_widths[j] = len(strings[i][j])

        for column in range(len(column_widths)):
            if column_widths[column] > max_width:
                column_widths[column] = max_width

        self._std_table = []

        for line in strings:
            new_string = '|'
            for i, item in enumerate(line):
                new_string = ''.join((new_string, ' ', item, ' ' * (column_widths[i] - len(item)), ' ', '|'))
            self._std_table.append(new_string)

        header_separator = '|'
        for i in range(len(strings[0])):
            header_separator = ''.join((header_separator, '-' * (column_widths[i] + 2), '|'))
        self._std_table.insert(1, header_separator)

        self._std_table = ['\n# %s\n' % self._std_table_header] + self._std_table


    def _resolve_url(self):
        for i, string in enumerate(self._test_cases):
            if '![' in string:
                if self._params['multi_param_select'][0] != '':
                    self._test_cases[i] = re.sub("(?<=[\]][\(])(\w*)", self._screenshots_url + "\g<1>" + '_' + self._params['multi_param_select'][0] + self._screenshots_ext, string)
                else:
                    self._test_cases[i] = re.sub("(?<=[\]][\(])(\w*)", self._screenshots_url + "\g<1>" + self._screenshots_ext, string)


    def _get_multi_param_matches(self):
        multi_param_matches = set()
        self._params.update({'multi_param_values': {}})
        values = []
        testrail_params = self._client.send_get('get_case_fields')

        for param in testrail_params:
            if param['system_name'] == self._params['multi_param_sys_name']:
                for item in param['configs']:
                    if self._project_id in item['context']['project_ids']:
                        values = item['options']['items'].split('\n')
        for value in values:
            if value.split(',')[1].strip().lower() in self._params['multi_param_select'] or self._params['multi_param_select'] == ['']:
                multi_param_matches.add(int(value.split(',')[0].strip()))
            self._params['multi_param_values'].update({int(value.split(',')[0].strip()): value.split(',')[1].strip()})

        self._params.update({'multi_param_matches': multi_param_matches})


    def _get_priority_matches(self):
        priority_matches = set()
        priorities = self._client.send_get('get_priorities')
        self._priorities = {}

        for priority in priorities:
            if priority['name'].lower() in self._params['choose_priorities']:
                priority_matches.add(priority['id'])
            self._priorities.update({priority['id']: priority['name']})

        self._params.update({'priority_matches': priority_matches})


    def apply(self):
        self.logger.info('Applying preprocessor')

        project_name = self._client.send_get('get_project/%s' % self._project_id)['name']

        self.logger.debug(f'Collect data from {self._testrail_url}, project {project_name}')

        self._get_multi_param_matches()
        self._get_priority_matches()

        project_suites = self._client.send_get('get_suites/%s' % self._project_id)

        self._collect_suites_and_sections_ids(project_suites)

        self._collect_cases(project_suites)

        self._remove_empty_chapters()

        if self._resolve_urls:
            self._resolve_url()

        self._std_table_aligning()

        if self._add_std_table and len(self._std_table) > 3:
            for line in self._std_table:
                self._test_cases.append('\n' + line)
            self._test_cases.append('\n')

        markdown_file_path = '/'.join((str(self.working_dir), self._filename))

        self.logger.debug(f'Processing Markdown file: {markdown_file_path}')

        with open(markdown_file_path, 'w', encoding="utf-8") as file_to_write:
            for string in self._test_cases:
                file_to_write.write(string)

        src_file_path = '/'.join((str(self.config['src_dir']), self._filename))
        if self._rewrite_src_file:
            copyfile(markdown_file_path, src_file_path)

        self.logger.info('Preprocessor applied')
