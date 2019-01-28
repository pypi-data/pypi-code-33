# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Context manager that wraps an AutoML run context."""
from contextlib import contextmanager
import os
import pickle
import tempfile


class AutoMLRunContext:

    def __init__(self, run, is_adb_run: bool = False) -> None:
        """
        Create an AutoMLRunContext object that wraps a run context.

        :param run: the run context to use
        :param is_adb_run: whether we are running in Azure DataBricks or not
        """
        self._run = run
        self._is_adb_run = is_adb_run
        self._context_active = False

    @contextmanager
    def get_run(self):
        """
        Generator that retrieves a run context if needed and then yields it.

        Wrapped by contextlib to convert it to a context manager. Nested invocations will return the same run context.
        """
        # In case we use get_run in nested with statements, only get the run context once
        context_state = self._context_active
        if (self._is_adb_run and not context_state) or self._run is None:
            from azureml.core import Run
            self._run = Run.get_context(_batch_upload_metrics=False)
        self._context_active = True
        yield self._run
        self._context_active = context_state

    def save_model_output(self, fitted_pipeline: object, remote_path: str) -> None:
        """
        Save the given fitted model to the given path using this run context.

        :param fitted_pipeline: the fitted model to save
        :param remote_path: the path to save to
        """
        model_output = None
        try:
            model_output = tempfile.NamedTemporaryFile(mode='wb+', delete=False)

            with(open(model_output.name, 'wb')):
                pickle.dump(fitted_pipeline, model_output)
                model_output.flush()
            with(open(model_output.name, 'rb')):
                with self.get_run() as run_object:
                    run_object.upload_file(remote_path, model_output.name)
        finally:
            if model_output is not None:
                model_output.close()
                os.unlink(model_output.name)
