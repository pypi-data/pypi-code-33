from . import BaseCollectionManager, BaseModelManager
from ..results import MonitorResult


class ChatManager(BaseModelManager):
    def __init__(self, driver, manager_path=''):
        super(ChatManager, self).__init__(driver, manager_path)


class ChatManagerCollection(BaseCollectionManager):

    def get_conversations(self, keep_polling=False, delay_sec=1):
        return self._execute_command(
            'get_conversations',
            result_class=MonitorResult,
            params={
                'keep_polling': keep_polling,
                'delay_sec': delay_sec
            }
        )

    async def send_seen(self, id):
        try:
            await self._execute_command(
                'send_seen',
                params={
                    'id': id
                }
            )
        except Exception as ex:
            self._logger.error('[-] Error sending seen to chat\n{}'.format(ex))

    async def send_message(self, packet, keep_polling=False, delay_sec=1):
        try:
            await self._execute_command(
                'send_message',
                params=packet
            )
        except Exception as ex:
            self._logger.error('[-] Error sending message\n{}'.format(ex))
            return False

    async def send_message_no_conversation_id(self, packet, keep_polling=False, delay_sec=1):
        try:
            profile = await self._execute_command(
                'get_profile', {'identifier': packet['id']}
            )
            profile_urn_id = profile['profile_id']

            conversation = await self._execute_command(
                'get_conversation_details', {'profile_urn_id': profile_urn_id}
            )
            conversation_id = conversation['id']

            await self._execute_command(
                'send_message',
                params={
                    'id': conversation_id,
                    'message': packet['message']
                }
            )

            return True
        except Exception as ex:
            self._logger.error('[-] Error sending message\n{}'.format(ex))
            return False

    async def get_conversation_id(self, mini_profile):
        try:
            profile = await self._execute_command(
                'get_profile', {'identifier': mini_profile['publicIdentifier']}
            )
            profile_urn_id = profile['profile_id']

            conversation = await self._execute_command(
                'get_conversation_details', {'profile_urn_id': profile_urn_id}
            )
            return conversation['id']
        except Exception as ex:
            self._logger.error('[-] Error getting conversation id\n{}'.format(ex))

    async def get_unread_messages(self, unread_count, conversation_id, keep_polling=False, delay_sec=1):

        try:
            full_conversation = await self._execute_command(
                'get_conversation', {'conversation_id': conversation_id}
            )

            messages = full_conversation['elements'][-unread_count:]
            text_messages = []

            for message in messages:
                [text_messages.append(message['eventContent'][key]['attachments']
                                      if 'attachments' in message['eventContent'][key].keys()
                                      else message['eventContent'][key]['body'])
                 for key in message['eventContent']
                 if key.endswith('MessageEvent')]

            return text_messages
        except Exception as ex:
            self._logger.error('[-] Error while getting unread messages\n{}'.format(ex))
            return []

    def get_mini_profile(self, conversation, keep_polling=False, delay_sec=1):

        try:
            participant = conversation['participants'][0]

            mini_profile = [participant[key]['miniProfile'] for key in participant.keys() if
                            key.endswith('MessagingMember')]

            return mini_profile[0]
        except Exception as ex:
            self._logger.error('[-] Error getting mini profile\n{}'.format(ex))
            return None
