"""
A generator for Python classes from Avro schemas.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from collections import OrderedDict
from typing import List

from avro_preprocessor.preprocessor import AvroPreprocessor
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

from pyavro_gen.codewriters.core import WritingMode
from pyavro_gen.schema_and_classes_container import SchemaAndClassesContainer
from pyavro_gen.modules.avsc_schema_dependency_checker import AvscSchemaDependenciesChecker
from pyavro_gen.modules.fields_collector import FieldsCollector


class AvroGenerator(AvroPreprocessor):  # type: ignore
    """
    A generator for Python classes from Avro schemas.
    """
    preprocessing_modules = [
        AvscSchemaDependenciesChecker,
        FieldsCollector
    ]

    #: OrderedDict of module_name -> module_class
    available_preprocessing_modules = OrderedDict((
        (m.__name__, m) for m in preprocessing_modules
    ))

    def _get_schemas_container(self) -> SchemasContainer:
        return SchemaAndClassesContainer(self.paths, self.verbose)

    def process_with_modules(
            self,
            requested_modules: List[PreprocessorModule],
            mode: WritingMode = WritingMode.GENERATION_INDEPENDENT
    ) -> None:
        """
        Process all the schemas using the modules pipeline.
        files in the output path.

        :param requested_modules: Instances of the modules to use.
        :param mode: WritingMode.GENERATION_INDEPENDENT to create independent class files,
        WritingMode.GENERATION to put all content in `__init__.py` files.
        """

        schemas: SchemaAndClassesContainer = self.schemas

        schemas.read_schemas()
        modules = OrderedDict(
            (module.__class__.__name__, module) for module in requested_modules
        )
        self._do_process(modules)
        schemas.write_schemas(mode)
