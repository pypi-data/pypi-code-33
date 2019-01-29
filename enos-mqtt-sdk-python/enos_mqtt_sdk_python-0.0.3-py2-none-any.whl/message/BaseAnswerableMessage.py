from abc import ABCMeta
from message.AnswerableMessageBody import AnswerableMessageBody
from core.msg.IAnswerable import IAnswerable

class BaseAnswerableMessage(AnswerableMessageBody, IAnswerable):
    __metaclass__ = ABCMeta

    pass
    # def __init__(self):
    #     pass
