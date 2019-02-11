# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.typedefinitions import (AnonymousBlockData, ExportScriptFormat, SecretData,
                                        ExportScriptMessageArguments, ActivityReference,
                                        CreateAnonymousReferenceMessageArguments, PropertyOverride)
from .engineapi.api import EngineAPI
from importlib import import_module
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4
import atexit
import os
import shutil


class DataPrepImportError(Exception):
    pass


class SparkExecutor:
    def __init__(self, engine_api: EngineAPI):
        self._engine_api = engine_api

    # noinspection PyUnresolvedReferences
    def get_dataframe(self,
                      steps: List[AnonymousBlockData],
                      project_context: str,
                      use_sampling: bool=True,
                      overrides: Optional[List[PropertyOverride]]=None,
                      use_first_record_schema: bool=False) -> 'pyspark.sql.DataFrame':
        return self._execute(steps,
                             project_context,
                             ExportScriptFormat.PYSPARKDATAFRAMELOADER,
                             use_sampling,
                             overrides,
                             use_first_record_schema)

    def execute(self,
                steps: List[AnonymousBlockData],
                project_context: str,
                use_sampling: bool=True,
                overrides: Optional[List[PropertyOverride]]=None,
                use_first_record_schema: bool=False) -> None:
        return self._execute(steps,
                             project_context,
                             ExportScriptFormat.PYSPARKRUNFUNCTION,
                             use_sampling,
                             overrides,
                             use_first_record_schema)

    def _execute(self,
                 blocks: List[AnonymousBlockData],
                 project_context: str,
                 export_format: ExportScriptFormat,
                 use_sampling: bool=True,
                 overrides: Optional[List[PropertyOverride]]=None,
                 use_first_record_schema: bool=False) -> Any:
        activity = self._engine_api.create_anonymous_reference(
            CreateAnonymousReferenceMessageArguments(blocks, project_context))
        module, secrets = self._export_to_module(activity, export_format, use_sampling, overrides)
        try:
            if export_format == ExportScriptFormat.PYSPARKDATAFRAMELOADER:
                return module.LoadData(secrets=secrets, schemaFromFirstRecord=use_first_record_schema)
            else:
                module.run_dataflow(secrets=secrets)
        except Exception as e:
            lariat_version = e.args[1].get('lariat_version') if e.args and len(e.args) >= 2 and isinstance(e.args[1], dict) else None
            if lariat_version:
                raise DataPrepImportError('Unable to load the data preparation scale-out library for version '
                                          + lariat_version + '.')
            raise e

    def _export_to_module(self,
                          activity: ActivityReference,
                          export_format: ExportScriptFormat,
                          use_sampling: bool,
                          overrides: Optional[List[PropertyOverride]]=None) -> Tuple[Any, Dict[str, str]]:
        output, gathered_secrets = self._export_script(activity=activity,
                                                       export_format=export_format,
                                                       use_sampling=use_sampling,
                                                       overrides=overrides)
        secrets = {secret.key: secret.value for secret in gathered_secrets}
        # Python seems to be tolerant to deleting the modules immediately after import
        # but deferring their deletion until process exit is safer.
        SparkExecutor._register_directory_for_cleanup(output)

        # The generated module is always loader.py but we need a unique one to avoid module name clashes.
        loader_module_name = "loader" + uuid4().hex
        loader_module_file = os.path.join(output, loader_module_name + ".py")
        os.rename(
            os.path.join(output, "loader.py"),
            loader_module_file)

        self._add_spark_files(output, loader_module_file)
        module = import_module(loader_module_name)
        return module, secrets

    @staticmethod
    def _add_spark_files(directory: str, main_file: str):
        import pyspark
        from pyspark.sql.utils import IllegalArgumentException
        sc = pyspark.SparkContext.getOrCreate()
        SparkExecutor._add_lariat_spark_jar(sc)
        for item in os.listdir(directory):
            filename = os.path.join(directory, item)
            try:
                if filename[-3:].lower() == ".py" or filename[-4:].lower() == ".zip":
                    sc.addPyFile(filename)
                else:
                    sc.addFile(filename, recursive=True)
            except IllegalArgumentException as e:
                # IllegalArgumentException will be thrown if same file name but different path are being added to the
                # spark context. The reason we are catching is because there are files that are common but also files
                # that are unique to each execution. e.g. <guid>.scala - file with expressions
                pass
        # we are assuming the main file will have a unique file name each time
        sc.addPyFile(main_file)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _add_lariat_spark_jar(sc: 'pyspark.SparkContext'):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        lariat_spark_path = os.path.join(current_dir, 'engineapi', 'lariatSpark', 'dprep.jar')
        loader = SparkExecutor._get_mutable_class_loader(sc)
        if loader is not None:
            # noinspection PyBroadException
            try:
                # noinspection PyProtectedMember
                sc._jsc.addJar(lariat_spark_path)
                # noinspection PyProtectedMember
                file = sc._jvm.java.io.File(lariat_spark_path).toURI().toURL()
                loader.addURL(file)
            except Exception:
                pass

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _get_mutable_class_loader(sc: 'pyspark.SparkContext'):
        databricks_loader_class = 'com.databricks.backend.daemon.driver.DriverLocal$DriverLocalClassLoader'

        # noinspection PyBroadException
        try:
            # noinspection PyProtectedMember
            loader = sc._jvm.org.apache.spark.util.Utils.getContextOrSparkClassLoader()
            while loader is not None:
                if loader.getClass().getName() == databricks_loader_class:
                    loader = loader.getParent().getParent()
                    continue
                elif hasattr(loader, 'addURL'):
                    break
                loader = loader.getParent()

            return loader
        except Exception:
            return None

    def _export_script(self,
                       activity: ActivityReference,
                       export_format: ExportScriptFormat,
                       use_sampling: bool,
                       overrides: Optional[List[PropertyOverride]]=None,
                       project_session: Optional[UUID]=None):
        output = SparkExecutor._get_temp_file_path()
        args = ExportScriptMessageArguments(activity_reference=activity,
                                            format=export_format,
                                            overrides=overrides,
                                            path=output,
                                            use_sampling=use_sampling)
        gathered_secrets = self._engine_api.export_script(args)
        return output, gathered_secrets

    @staticmethod
    def _register_directory_for_cleanup(directory_path):
        def remove_directory(directory):
            shutil.rmtree(directory, ignore_errors=True)
        atexit.register(remove_directory, directory_path)

    @staticmethod
    def _get_temp_file_path():
        file = NamedTemporaryFile()
        name = file.name
        file.close()
        return name
