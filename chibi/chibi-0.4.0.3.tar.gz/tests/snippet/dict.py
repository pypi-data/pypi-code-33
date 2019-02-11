from unittest import TestCase
import tempfile, shutil
from faker import Factory as Faker_factory
from chibi.file.snippets import current_dir, cd, join, mkdir
from chibi.file import Chibi_file
from chibi.snippet.dict import keys_to_snake_case


faker = Faker_factory.create()


class Test_keys_to_snake_case( TestCase ):
    def setUp( self ):
        self.d = { 'camelCase': { 'snake_case': { 'PascalCase': '' } } }
        self.expected = {
            'camel_case': { 'snake_case': { 'pascal_case': '' } } }

    def test_should_transform_to_snake_case( self ):
        result = keys_to_snake_case( self.d )
        self.assertEqual( result, self.expected )
