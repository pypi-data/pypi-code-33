"""Interface for Cloud Adapter"""


class ICloudAdapter:
    """Interface for Cloud Adapter"""

    def create_runners(self, count):
        """Creates count number of runners

        Args:
            count: Number of runners to create

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error encountered.
        """
        pass

    def delete_runner(self, runner_id, force=False):
        """Deletes runner by id

        Args:
            runner_id: The id of the runner to delete
            force: force to delete (defaults to False)

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in DELETEing.
            NotFoundError: occurs if the url is not found.
        """
        pass

    def delete_runners(self, force=False):
        """Deletes all runners

        Args:
            force: force to delete (defaults to False)

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in DELETEing.
            NotFoundError: occurs if the url is not found.
        """
        pass

    def get_runner(self, runner_id):
        """Gets a runner by ID

        Args:
            url: runner id to get

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in GETing.
            NotFoundError: occurs if the url is not found.
        """
        pass

    def get_runners(self):
        """Gets all runners.

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in GETing.
            NotFoundError: occurs if the url is not found.
        """
        pass
