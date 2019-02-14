"""
A memory container for schemas and generated classes.
It also writes python classes to disk.
"""

from collections import OrderedDict
from pathlib import Path
from typing import Dict, Set, List, Any  # pylint: disable=W0611

from avro_preprocessor.avro_paths import AvroPaths
from avro_preprocessor.schemas_container import SchemasContainer

from pyavro_gen.codewriters.core import WritingMode, Writer, ClassWriter  # pylint: disable=W0611
from pyavro_gen.codewriters.namespace import ClassItem, NamespaceWriter, get_testing_base, \
    get_testing_class_list
from pyavro_gen.codewriters.utils import namespace_name


# pylint: disable=R0914
class SchemaAndClassesContainer(SchemasContainer):  # type: ignore
    """
    A memory container for schemas and generated classes.
    It also writes python classes to disk.
    """

    def __init__(self, paths: AvroPaths, verbose: bool = True) -> None:
        super(SchemaAndClassesContainer, self).__init__(paths, verbose)

        self.output_writers: 'OrderedDict[str, ClassWriter]' = OrderedDict()

        self.output_prefix = Path(self.paths.output_path).name

    def _store_schema(self, schema: 'OrderedDict[Any, Any]', namespace: str) -> None:
        self.original[namespace] = schema

    def write_classes(self, mode: WritingMode = WritingMode.GENERATION_INDEPENDENT) -> None:
        """
        Writes python classes to disk.
        """

        namespace_writers: Dict[str, NamespaceWriter] = {}
        for name, class_writer in self.output_writers.items():
            namespace = namespace_name(name)
            if namespace not in namespace_writers:
                namespace_writers[namespace] = NamespaceWriter(namespace)
            namespace_writers[namespace].class_writers.append(class_writer)

        all_modes = [mode, WritingMode.TEST]

        all_testing_classes: List[ClassItem] = []

        for current_mode in all_modes:

            if current_mode == WritingMode.TEST:
                path = Path(self.paths.output_path)
                test_name = str(path.name) + '_test'
                output_path = path.parent.joinpath(Path(test_name))
            else:
                output_path = Path(self.paths.output_path)

            print('############### OUTPUT PATH:', output_path)

            Writer.output_prefix = output_path.name.replace('/', '')

            # let's cleanup the output schema directory first
            AvroPaths.reset_directory(output_path)

            if current_mode != WritingMode.TEST:
                main_init = output_path.joinpath('__init__.py')
                from pyavro_gen import serde
                serde_text = Path(serde.__file__).read_text()
                main_init.parent.mkdir(parents=True, exist_ok=True)
                main_init.write_text(serde_text)

            parent_paths: Set[Path] = set()

            for namespace_writer in namespace_writers.values():
                print(namespace_writer.namespace, [w.name for w in namespace_writer.class_writers])

                fname = namespace_writer.namespace.replace('.', '/')
                init_file_path = output_path.joinpath(Path(fname))
                init_file_path.mkdir(parents=True, exist_ok=True)
                parent_paths = parent_paths.union(set(par for par in init_file_path.parents
                                                      if str(output_path) in str(par)))

                contents = namespace_writer.write(current_mode)
                self._write_to_disk(
                    {init_file_path.joinpath(fname): content for fname, content in contents.items()}
                )

                if current_mode == WritingMode.TEST:
                    all_testing_classes += namespace_writer.get_all_testing_classes()

            if current_mode == WritingMode.TEST:
                testing_base_content = get_testing_base()
                testing_base_path = output_path.joinpath(Path('__init__.py'))

                testing_class_list_content = get_testing_class_list(all_testing_classes)
                testing_class_list_path = output_path.joinpath(Path('testing_classes.py'))

                self._write_to_disk({
                    testing_base_path: testing_base_content,
                    testing_class_list_path: testing_class_list_content
                })

            for to_exclude in ['.', '..']:
                try:
                    parent_paths.remove(Path(to_exclude))
                except KeyError:
                    pass

            for path in sorted(parent_paths):
                self._init_python_module(Path(path))

    @staticmethod
    def _init_python_module(path: Path) -> None:
        path = path.joinpath('__init__.py')
        if not path.exists():
            path.write_text('')

    @staticmethod
    def _write_to_disk(contents: Dict[Path, str]) -> None:
        for fname, content in contents.items():
            fname.write_text(content)

    write_schemas = write_classes
