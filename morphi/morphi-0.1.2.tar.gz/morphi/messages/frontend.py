import json
import os

import babel.messages.frontend
from babel.messages.pofile import read_po
from distutils.errors import DistutilsOptionError


class CompileJson(babel.messages.frontend.compile_catalog, object):
    """Provide a distutils `compile-json` command"""

    description = 'compile message catalogs to JSON files'
    user_options = babel.messages.frontend.compile_catalog.user_options + [
        ('output-dir=', 'u',
         'path to output directory'),
    ]

    def initialize_options(self):
        super(CompileJson, self).initialize_options()
        self.output_dir = None

    def finalize_options(self):
        super(CompileJson, self).finalize_options()
        if not self.output_dir:
            self.output_dir = self.directory

    def _run_domain(self, domain):  # noqa: C901
        # copied from `babel.messages.frontend.compile_catalog._run_domain`,
        #  * switched out 'mo' for 'json'
        #  * added `output_dir` option

        po_files = []
        json_files = []

        if not self.input_file:
            if self.locale:
                po_files.append((self.locale,
                                 os.path.join(self.directory, self.locale,
                                              'LC_MESSAGES',
                                              domain + '.po')))
                json_files.append(os.path.join(self.output_dir, self.locale,
                                               'LC_MESSAGES',
                                               domain + '.json'))
            else:
                for locale in os.listdir(self.directory):
                    po_file = os.path.join(self.directory, locale,
                                           'LC_MESSAGES', domain + '.po')
                    if os.path.exists(po_file):
                        po_files.append((locale, po_file))
                        json_files.append(os.path.join(self.output_dir, locale,
                                                       'LC_MESSAGES',
                                                       domain + '.json'))
        else:
            po_files.append((self.locale, self.input_file))
            if self.output_file:
                json_files.append(self.output_file)
            else:
                json_files.append(os.path.join(self.output_dir, self.locale,
                                               'LC_MESSAGES',
                                               domain + '.json'))

        if not po_files:
            raise DistutilsOptionError('no message catalogs found')

        for idx, (locale, po_file) in enumerate(po_files):
            json_file = json_files[idx]
            with open(po_file, 'rb') as infile:
                catalog = read_po(infile, locale)

            if self.statistics:
                translated = 0
                for message in list(catalog)[1:]:
                    if message.string:
                        translated += 1
                percentage = 0
                if len(catalog):
                    percentage = translated * 100 // len(catalog)
                self.log.info(
                    '%d of %d messages (%d%%) translated in %s',
                    translated, len(catalog), percentage, po_file
                )

            if catalog.fuzzy and not self.use_fuzzy:
                self.log.info('catalog %s is marked as fuzzy, skipping', po_file)
                continue

            for message, errors in catalog.check():
                for error in errors:
                    self.log.error(
                        'error: %s:%d: %s', po_file, message.lineno, error
                    )

            self.log.info('compiling catalog %s to %s', po_file, json_file)

            if not os.path.exists(os.path.dirname(json_file)):
                os.makedirs(os.path.dirname(json_file))

            with open(json_file, 'w') as outfile:
                self._write_json(outfile, catalog, use_fuzzy=self.use_fuzzy)

    @staticmethod
    def _write_json(outfile, catalog, use_fuzzy=False):
        """Write `catalog` as JSON text to the specified `outfile`"""
        messages = list(catalog)
        if not use_fuzzy:
            messages[1:] = [message for message in messages[1:] if not message.fuzzy]
        messages.sort()

        jscatalog = {}
        for message in messages:
            message_id = message.id
            if isinstance(message_id, (tuple, list)):
                message_id = message_id[0]

            jscatalog[message_id] = message.string

        jscatalog[""] = {
            'language': str(catalog.locale),
            'plural-forms': catalog.plural_forms
        }

        outfile.write(
            json.dumps(
                jscatalog,
                indent=4
            )
        )
