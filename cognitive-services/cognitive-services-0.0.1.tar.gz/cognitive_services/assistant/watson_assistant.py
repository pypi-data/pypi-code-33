import json
from watson_developer_cloud import AssistantV1, watson_service
from .assistant import Assistant
from .assistant_exception import AssistantException


class WatsonAssistant(Assistant):

    def __init__(self, credentials):
        username = credentials.get('username')
        password = credentials.get('password')

        errors = []
        if not username:
            errors.append("username")
        if not password:
            errors.append("password")

        if len(errors) > 0:
            raise AssistantException(code=400, message='Missing parameters: {0}'.format(', '.join(errors)))

        self.conversation = AssistantV1(
            username=username,
            password=password,
            version='2018-07-10'
        )

    def message(self, parameters):

        workspace_id = parameters.get('workspace_id')
        body = parameters.get('body')

        errors = []
        if not workspace_id:
            errors.append("workspace_id")
        if not body:
            errors.append("body")

        if len(errors) > 0:
            raise AssistantException(code=400, message='Missing parameters: {0}'.format(', '.join(errors)))

        try:
            body = json.loads(body)
            input_text = body.get('input')
            context = body.get('context')

            response = self.conversation.message(
                workspace_id=workspace_id,
                input=input_text,
                context=context,
                alternate_intents=True
            )
            return response
        except watson_service.WatsonApiException as ex:
            raise AssistantException(code=ex.code, message=ex.message)
        except Exception as ex:
            raise AssistantException(code=500, message=ex.args[0])

    def information(self, parameters):

        workspace_id = parameters.get('workspace_id', None)

        if not workspace_id:
            raise AssistantException(code=400, message='Missing parameter: workspace_id')

        try:
            response = self.conversation.get_workspace(
                workspace_id=workspace_id,
                export=False
            )
            return response
        except watson_service.WatsonApiException as ex:
            raise AssistantException(code=ex.code, message=ex.message)
        except Exception as ex:
            raise AssistantException(code=500, message=ex.args[0])
