# -*- coding: utf-8 -*-

from geokrety_api_models import Move, User

from .base import BaseResponse
from .collections import BaseCollectionResponse


class MoveCommentResponse(BaseResponse):

    def assertHasComment(self, value):
        self.assertHasAttribute('comment', value)
        return self

    def assertHasType(self, value):
        self.assertHasAttribute('type', value)
        return self

    def assertHasRelationshipAuthor(self):
        self.assertHasRelationshipSelf('author', '/v1/moves-comments/%s/relationships/author' % self.id)
        self.assertHasRelationshipRelated('author', '/v1/moves-comments/%s/author' % self.id)
        return self

    def assertHasRelationshipMove(self):
        self.assertHasRelationshipSelf('move', '/v1/moves-comments/%s/relationships/move' % self.id)
        self.assertHasRelationshipRelated('move', '/v1/moves-comments/%s/move' % self.id)
        return self

    def assertHasRelationshipAuthorData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('author', user_id, 'user')
        return self

    def assertHasRelationshipMoveData(self, move):
        move_id = move.id if isinstance(move, Move) else move
        self.assertHasRelationshipData('move', move_id, 'move')
        return self

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('comment', obj.comment)
        self.assertHasAttribute('type', obj.type)
        self.assertCreationDateTime()
        self.assertUpdatedDateTime()
        self.assertHasRelationshipAuthor()
        self.assertHasRelationshipAuthorData(obj.author.id)
        self.assertHasRelationshipMove()
        self.assertHasRelationshipMoveData(obj.move.id)
        return self


class MoveCommentsCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(MoveCommentsCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(MoveCommentResponse(data_))
        self['data'] = datas
