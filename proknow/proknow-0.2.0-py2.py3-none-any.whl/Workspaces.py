__all__ = [
    'Workspaces',
]

import six
import re

from .Exceptions import WorkspaceLookupError


class Workspaces(object):
    """

    This class should be used to interact with the workspaces in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Workspaces class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor
        self._cache = None

    def create(self, slug, name, protected=True):
        """Creates a new workspace.

        Parameters:
            slug (str): The workspace slug.
            name (str): The workspace name.
            protected (bool, optional): Indicates whether the workspace should be protected from
                accidental deletion.

        Returns:
            :class:`proknow.Workspaces.WorkspaceItem`: A representation of the created workspace.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(slug, six.string_types), "`slug` is required as a string."
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(protected, bool), "`protected` is required as a bool."

        _, workspace = self._requestor.post('/workspaces', body={'slug': slug, 'name': name, 'protected': protected})
        self._cache = None
        return WorkspaceItem(self, workspace)

    def delete(self, workspace_id):
        """Deletes a workspace.

        Parameters:
            workspace_id (str): The id of the workspace to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(workspace_id, six.string_types), "`workspace_id` is required as a string."
        self._requestor.delete('/workspaces/' + workspace_id)
        self._cache = None

    def find(self, predicate=None, **props):
        """Finds the first workspace that matches the input paramters.

        Note:
            This method utilizes a cache of workspaces. Once it has a cache of workspaces, it will
            use that cache until the :meth:`proknow.Workspaces.Workspaces.query` method is called
            to refresh the cache. If you wish to make your code resilient to workspaces changes
            (i.e., new workspaces, renamed workspaces, deleted workspaces, etc.) while your script
            is running, you should call the :meth:`proknow.Workspaces.Workspaces.query` method
            before this method. In most use cases, this is not necessary.

        Parameters:
            predicate (func): A function that is passed a workspace as input and which should return
                a bool indicating whether the workspace is a match.
            **props: A dictionary of keyword arguments that may include any workspace attribute.
                These arguments are considered in turn to find matching workspaces.

        Returns:
            :class:`proknow.Workspaces.WorkspaceItem`: A representation of the matching workspace.
        """
        if self._cache is None:
            self.query()
        if predicate is None and len(props) == 0:
            return None

        for workspace in self._cache:
            match = True
            if predicate is not None and not predicate(workspace):
                match = False
            for key in props:
                if workspace._data[key] != props[key]:
                    match = False
            if match:
                return workspace

        return None

    def resolve(self, workspace):
        """Resolves a workspace by id or name.

        Parameters:
            workspace (str): The workspace id or name.

        Returns:
            :class:`proknow.Workspaces.WorkspaceItem`: A representation of the resolved workspace.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given name could not be found.
        """
        assert isinstance(workspace, six.string_types), "`workspace` is required as a string."

        pattern = re.compile(r"^[0-9a-f]{32}$")
        if pattern.match(workspace) is not None:
            return self.resolveById(workspace)
        else:
            return self.resolveByName(workspace)

    def resolveByName(self, name):
        """Resolves a workspace name to a workspace.

        Parameters:
            name (str): The workspace name.

        Returns:
            :class:`proknow.Workspaces.WorkspaceItem`: A representation of the resolved workspace.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given name could not be found.
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."

        workspace = self.find(name=name)
        if workspace is None:
            raise WorkspaceLookupError("Workspace with name `" + name + "` not found.")
        return workspace

    def resolveById(self, workspace_id):
        """Resolves a workspace id to a workspace.

        Parameters:
            workspace_id (str): The workspace id.

        Returns:
            :class:`proknow.Workspaces.WorkspaceItem`: A representation of the resolved workspace.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given name could not be found.
        """
        assert isinstance(workspace_id, six.string_types), "`workspace_id` is required as a string."

        workspace = self.find(workspace_id=workspace_id)
        if workspace is None:
            raise WorkspaceLookupError("Workspace with id `" + workspace_id + "` not found.")
        return workspace

    def query(self):
        """Queries for workspaces.

        Note:
            This method refreshes the workspaces cache.

        Returns:
            list: A list of :class:`proknow.Workspaces.WorkspaceItem` objects, each representing a
            workspace in the organization.
        """
        _, workspaces = self._requestor.get('/workspaces')
        self._cache = [WorkspaceItem(self, workspace) for workspace in workspaces]
        return self._cache

class WorkspaceItem(object):
    """

    This class represents a workspace. It's instantiated by the
    :class:`proknow.Workspaces.Workspaces` class to represent each of the workspaces in a query
    result and a created workspace.

    Attributes:
        id (str): The id of the workspace (readonly).
        data (dict): The complete representation of the workspace as returned from the API
            (readonly).
        slug (str): A string used in the URL that uniquely identifies the workspace.
        name (str): The name of the workspace.
        protected (bool): Indicates whether the workspace should be protected from accidental
            deletion.

    """

    def __init__(self, workspaces, workspace):
        """Initializes the WorkspaceItem class.

        Parameters:
            workspaces (proknow.Workspaces.Workspaces): The Workspaces instance that is
                instantiating the object.
            workspace (dict): A dictionary of workspace attributes.
        """
        self._workspaces = workspaces
        self._requestor = self._workspaces._requestor
        self._id = workspace["id"]
        self._data = workspace
        self.slug = workspace["slug"]
        self.name = workspace["name"]
        self.protected = workspace["protected"]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the workspace."""
        self._workspaces.delete(self._id)

    def save(self):
        """Saves the changes made to a workspace.

        Example:
            The following example illustrates how to find a workspace by its slug, modify the name,
            and save it::

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                clinical = pk.workspaces.find(slug='clinical')
                clinical.name = "Clinical Patients"
                clinical.save()
        """
        _, workspace = self._requestor.put('/workspaces/' + self._id, body={'slug': self.slug, 'name': self.name, 'protected': self.protected})
        self._data = workspace
        self.slug = workspace["slug"]
        self.name = workspace["name"]
        self.protected = workspace["protected"]
