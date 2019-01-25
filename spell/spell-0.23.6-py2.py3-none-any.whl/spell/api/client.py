from spell.api.runs_client import RunsClient
from spell.api.feedback_client import FeedbackClient
from spell.api.keys_client import KeysClient
from spell.api.resources_client import ResourcesClient
from spell.api.model_server_client import ModelServerClient
from spell.api.supported_options_client import SupportedOptionsClient
from spell.api.user_client import UserClient
from spell.api.user_datasets_client import UserDatasetsClient
from spell.api.workspaces_client import WorkspacesClient
from spell.api.workflows_client import WorkflowsClient


class APIClient(RunsClient,
                FeedbackClient,
                KeysClient,
                ResourcesClient,
                ModelServerClient,
                SupportedOptionsClient,
                UserClient,
                UserDatasetsClient,
                WorkspacesClient,
                WorkflowsClient):
    def __init__(self,  **kwargs):
        super(APIClient, self).__init__(**kwargs)
