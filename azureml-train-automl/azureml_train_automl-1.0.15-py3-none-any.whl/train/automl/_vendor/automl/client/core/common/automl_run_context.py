# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Context manager that wraps an AutoML run context."""
from abc import ABC, abstractmethod
from contextlib import contextmanager
import os
import pickle
import tempfile


class AutoMLAbstractRunContext(ABC):
    """Wrapper class for an AutoML run context."""

    @abstractmethod
    def _get_run_internal(self):
        """Retrieve the run context. Must be overridden by subclasses."""
        raise NotImplementedError

    @contextmanager
    def get_run(self):
        """
        Yield a run context.

        Wrapped by contextlib to convert it to a context manager. Nested invocations will return the same run context.
        """
        yield self._get_run_internal()

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
