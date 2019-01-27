# -*- coding: utf-8 -*-

from mixer.backend.flask import mixer

from app.api.helpers.data_layers import MOVE_COMMENT_TYPE_COMMENT
from geokrety_api_models import Move, User

from .base import BasePayload


class MoveCommentPayload(BasePayload):
    _url = "/v1/moves-comments/{}"
    _url_collection = "/v1/moves-comments"
    _response_type = 'MoveCommentResponse'
    _response_type_collection = 'MoveCommentsCollectionResponse'

    def __init__(self, *args, **kwargs):
        super(MoveCommentPayload, self).__init__('move-comment', *args, **kwargs)

    def set_type(self, comment_type):
        self._set_attribute('type', comment_type)
        return self

    def set_comment(self, comment):
        self._set_attribute('comment', comment)
        return self

    def set_author(self, user):
        user_id = user.id if isinstance(user, User) else user
        self._set_relationships('author', 'user', user_id)
        return self

    def set_move(self, move):
        move_id = move.id if isinstance(move, Move) else move
        self._set_relationships('move', 'move', move_id)
        return self

    def set_obj(self, obj):
        self.set_type(obj.type)
        self.set_comment(obj.comment)
        self.set_move(obj.move.id)
        return self

    def blend(self, *args, **kwargs):
        move = kwargs.get('move')
        if move is None:
            with mixer.ctx():
                move = mixer.blend('geokrety_api_models.Move')
        with mixer.ctx(commit=False):
            move_comment = mixer.blend('geokrety_api_models.MoveComment',
                                       type=MOVE_COMMENT_TYPE_COMMENT,
                                       move=move)
            self.set_obj(move_comment)
            return self
