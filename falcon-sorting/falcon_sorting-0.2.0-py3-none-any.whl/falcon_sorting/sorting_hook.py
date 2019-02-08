import logging
from typing import Any, List

from falcon.request import Request
from falcon.response import Response


class SortingHook(object):
    """
    Falcon Hook to extract sorting information from request.

    It return a list of tuple for each fields that must be sorted.
    Each tuple contains:
        * The name of the field
        * The sorting order (ASC ord DESC)

    The extracted information are set in the request context dict
    under the context_key value.
    """

    def __init__(self, sort_query_key="sort"):
        self._sort_query_key = sort_query_key
        self._logger = logging.getLogger(__name__)

    def __call__(
        self,
        request: Request,
        response: Response = None,
        resource: Any = None,
        params: dict = None,
    ) -> None:
        """
        :param request: Falcon Request
        :param response: Falcon response
        :param resource: Reference to the resource class instance associated with the request
        :param params: dict of URI Template field names
        """
        if not self._resource_hasattr_not_empty(resource, "sorting_fields"):
            self._logger.debug("sorting_fields is not defined in resource, skipping")
            request.context["sort"] = []
            return

        sort_params = self._get_sort_params(request, resource)
        if not sort_params:
            request.context["sort"] = []
            return

        sort_list = [self._get_sql_sort(sort) for sort in sort_params]
        request.context["sort"] = sort_list
        self._logger.debug("Sorting set in request.context['sort']")

    def _get_sort_params(self, request: Request, resource: Any):
        try:
            sort_params = request.params[self._sort_query_key]
        except KeyError:
            self._logger.debug("Sorting key is not in query")
            if not self._resource_hasattr_not_empty(resource, "default_sorting"):
                self._logger.debug("No default order to apply")
                return
            sort_params = resource.default_sorting

        if not isinstance(sort_params, (list, tuple)):
            sort_params = [sort_params]
        return self._remove_invalid_fields(sort_params, resource.sorting_fields)

    @staticmethod
    def _resource_hasattr_not_empty(resource: Any, attribute_name: str):
        return bool(getattr(resource, attribute_name, False))

    @staticmethod
    def _remove_invalid_fields(sort_params: List, allowed_fields: List):
        return [f for f in sort_params if f.lstrip("-") in allowed_fields]

    @staticmethod
    def _get_sql_sort(sort):
        if sort[0:1] == "-":
            return sort[1:], "DESC"
        return sort, "ASC"
