from . import CommandExecutor


class ChatCommands(CommandExecutor):

    def get_conversations(self, *args, **kwargs):
        try:
            if 'linkedin' in kwargs.keys():
                return {
                    'exId': kwargs['exId'],
                    'type': 'PARTIAL',
                    'params': kwargs['linkedin'].get_conversations()
                }
            else:
                return {
                    'exId': kwargs['exId'],
                    'type': 'ERROR',
                    'params': {
                        'status': False,
                        'message': 'Missing Linkedin API'
                    }
                }
        except Exception as ex:
            return {
                'exId': kwargs['exId'],
                'type': 'ERROR',
                'params': {
                    'status': False,
                    'message': str(ex)
                }
            }

    def get_profile(self, *args, **kwargs):
        try:
            if 'linkedin' in kwargs.keys():
                return {
                    'exId': kwargs['exId'],
                    'type': 'FINAL',
                    'params': kwargs['linkedin'].get_profile(kwargs['identifier'])
                }
            else:
                return {
                    'exId': kwargs['exId'],
                    'type': 'ERROR',
                    'params': {
                        'status': False,
                        'message': 'Missing Linkedin API'
                    }
                }
        except Exception as ex:
            return {
                'exId': kwargs['exId'],
                'type': 'ERROR',
                'params': {
                    'status': False,
                    'message': str(ex)
                }
            }

    def get_conversation_details(self, *args, **kwargs):
        try:
            if 'linkedin' in kwargs.keys():
                return {
                    'exId': kwargs['exId'],
                    'type': 'FINAL',
                    'params': kwargs['linkedin'].get_conversation_details(kwargs['profile_urn_id'])
                }
            else:
                return {
                    'exId': kwargs['exId'],
                    'type': 'ERROR',
                    'params': {
                        'status': False,
                        'message': 'Missing Linkedin API'
                    }
                }
        except Exception as ex:
            return {
                'exId': kwargs['exId'],
                'type': 'ERROR',
                'params': {
                    'status': False,
                    'message': str(ex)
                }
            }

    def get_conversation(self, *args, **kwargs):
        try:
            if 'linkedin' in kwargs.keys():
                return {
                    'exId': kwargs['exId'],
                    'type': 'FINAL',
                    'params': kwargs['linkedin'].get_conversation(kwargs['conversation_id'])
                }
            else:
                return {
                    'exId': kwargs['exId'],
                    'type': 'ERROR',
                    'params': {
                        'status': False,
                        'message': 'Missing Linkedin API'
                    }
                }
        except Exception as ex:
            return {
                'exId': kwargs['exId'],
                'type': 'ERROR',
                'params': {
                    'status': False,
                    'message': str(ex)
                }
            }

    def send_message(self, *args, **kwargs):
        try:
            if 'linkedin' in kwargs.keys():
                if not kwargs['linkedin'].send_message(
                        kwargs['id'],
                        kwargs['message']
                ):
                    return {
                        'exId': kwargs['exId'],
                        'type': 'FINAL',
                        'params': {'status': True}}
                else:
                    return {
                        'exId': kwargs['exId'],
                        'type': 'ERROR',
                        'params': {
                            'status': False,
                            'message': 'Error sending message'
                        }
                    }
            else:
                return {
                    'exId': kwargs['exId'],
                    'type': 'ERROR',
                    'params': {
                        'status': False,
                        'message': 'Missing Linkedin API'
                    }
                }
        except Exception as ex:
            return {
                'exId': kwargs['exId'],
                'type': 'ERROR',
                'params': {
                    'status': False,
                    'message': str(ex)
                }
            }

    def send_seen(self, *args, **kwargs):
        try:
            if 'linkedin' in kwargs.keys():
                err = kwargs['linkedin'].mark_conversation_as_seen(kwargs['id'])

                if not err:
                    return {
                        'exId': kwargs['exId'],
                        'type': 'FINAL',
                        'params': {'status': True}}
                else:
                    return {
                        'exId': kwargs['exId'],
                        'type': 'ERROR',
                        'params': {
                            'status': False,
                            'message': 'Error sending seen to chat'
                        }
                    }
            else:
                return {
                    'exId': kwargs['exId'],
                    'type': 'ERROR',
                    'params': {
                        'status': False,
                        'message': 'Missing Linkedin API'
                    }
                }
        except Exception as ex:
            return {
                'exId': kwargs['exId'],
                'type': 'ERROR',
                'params': {
                    'status': False,
                    'message': str(ex)
                }
            }
