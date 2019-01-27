# -*- coding: utf-8 -*-

from app.api.bootstrap import api
from app.api.geokrety import (GeokretDetail, GeokretInACacheList, GeokretList,
                              GeokretRelationship)
from app.api.geokrety_types import (GeokretTypeDetail, GeokretTypeList,
                                    GeokretTypeRelationship)
from app.api.moves import MoveDetail, MoveRelationship, MovesList
from app.api.moves_comments import (MoveCommentDetail, MoveCommentList,
                                    MoveCommentRelationship)
from app.api.moves_types import MovesTypeDetail, MovesTypeList
from app.api.news import NewsDetail, NewsList, NewsRelationship
from app.api.news_comments import (NewsCommentDetail, NewsCommentList,
                                   NewsCommentRelationship)
from app.api.news_subscriptions import (NewsSubscriptionDetail,
                                        NewsSubscriptionList,
                                        NewsSubscriptionRelationship)
from app.api.users import UserDetail, UserList, UserRelationship
from app.api.badges import BadgeDetail, BadgeList, BadgeRelationship

api.route(UserList, 'users_list',
          '/users',
          )
api.route(UserDetail,
          'user_details',
          '/users/<int:id>',
          '/badges/<int:badge_author_id>/author',
          '/news/<int:news_id>/author',
          '/news-comments/<int:news_comment_id>/author',
          '/news-subscriptions/<int:news_subscription_id>/user',
          '/geokrety/<int:geokret_owned_id>/owner',
          '/geokrety/<int:geokret_held_id>/holder',
          '/moves/<int:move_id>/author',
          '/moves-comments/<int:move_comment_id>/author',
          )
api.route(UserRelationship, 'user_moves', '/users/<int:id>/relationships/moves')
api.route(UserRelationship, 'user_moves_comments', '/users/<int:id>/relationships/moves-comments')
api.route(UserRelationship, 'user_news', '/users/<int:id>/relationships/news')
api.route(UserRelationship, 'user_news_comments', '/users/<int:id>/relationships/news-comments')
api.route(UserRelationship, 'user_news_subscriptions', '/users/<int:id>/relationships/news-subscriptions')
api.route(UserRelationship, 'user_geokrety_owned', '/users/<int:id>/relationships/geokrety-owned')
api.route(UserRelationship, 'user_geokrety_held', '/users/<int:id>/relationships/geokrety-held')

api.route(NewsList, 'news_list',
          '/news',
          '/users/<int:author_id>/news',
          )
api.route(NewsDetail, 'news_details',
          '/news/<int:id>',
          '/news-comments/<int:news_comment_id>/news',
          '/news-subscriptions/<int:news_subscription_id>/news',
          )
api.route(NewsRelationship, 'news_comments', '/news/<int:id>/relationships/comments')
api.route(NewsRelationship, 'news_author', '/news/<int:id>/relationships/author')
api.route(NewsRelationship, 'news_news_subscription', '/news/<int:id>/relationships/subscriptions')

api.route(NewsCommentList, 'news_comments_list',
          '/news-comments',
          '/users/<int:author_id>/news-comments',
          '/news/<int:news_id>/comments',
          '/moves/<int:move_id>/comments',
          )
api.route(NewsCommentDetail, 'news_comment_details',
          '/news-comments/<int:id>',
          )
api.route(NewsCommentRelationship, 'news_comments_author', '/news-comments/<int:id>/relationships/author')
api.route(NewsCommentRelationship, 'news_comments_news', '/news-comments/<int:id>/relationships/news')

api.route(NewsSubscriptionList, 'news_subscriptions_list',
          '/news-subscriptions',
          '/users/<int:user_id>/news-subscriptions',
          '/news/<int:news_id>/subscriptions',
          )
api.route(NewsSubscriptionDetail, 'news_subscription_details',
          '/news-subscriptions/<int:id>',
          )
api.route(NewsSubscriptionRelationship, 'news_subscription_user', '/news-subscriptions/<int:id>/relationships/user')
api.route(NewsSubscriptionRelationship, 'news_subscription_news', '/news-subscriptions/<int:id>/relationships/news')

api.route(MovesTypeList, 'moves_type_list',
          '/moves-types',
          )
api.route(MovesTypeDetail, 'move_type_details',
          '/moves-types/<int:id>',
          '/moves/<int:move_id>/type',
          )

api.route(MoveCommentList, 'move_comment_list',
          '/moves-comments',
          '/users/<int:author_id>/moves-comments',
          '/moves/<int:news_id>/moves-comments',
          )
api.route(MoveCommentDetail, 'move_comment_details',
          '/moves-comments/<int:id>',
          )
api.route(MoveCommentRelationship, 'move_comment_author', '/moves-comments/<int:id>/relationships/author')
api.route(MoveCommentRelationship, 'move_comment_move', '/moves-comments/<int:id>/relationships/move')

api.route(GeokretTypeList, 'geokrety_type_list',
          '/geokrety-types',
          )
api.route(GeokretTypeDetail, 'geokrety_type_details',
          '/geokrety-types/<int:id>',
          '/geokrety/<int:geokret_id>/type',
          '/moves/<int:move_id>/geokret',
          )
api.route(GeokretTypeRelationship, 'geokrety_type_geokret', '/geokrety-types/<int:id>/relationships/geokrety')

api.route(GeokretList, 'geokrety_list', '/geokrety',
          '/users/<int:owner_id>/geokrety-owned',
          '/users/<int:holder_id>/geokrety-held',
          '/geokrety-types/<int:geokrety_type_id>/geokrety',
          )
api.route(GeokretInACacheList, 'geokrety_in_a_cache_list',
          '/geokrety/in-cache',
          )
api.route(GeokretDetail, 'geokret_details',
          '/geokrety/<int:id>',
          '/users/<int:user_id>/geokrety-owned',
          )
api.route(GeokretRelationship, 'geokret_owner', '/geokrety/<int:id>/relationships/owner')
api.route(GeokretRelationship, 'geokret_holder', '/geokrety/<int:id>/relationships/holder')
api.route(GeokretRelationship, 'geokret_type', '/geokrety/<int:id>/relationships/type')
api.route(GeokretRelationship, 'geokret_moves', '/geokrety/<int:id>/relationships/moves')
api.route(GeokretRelationship, 'geokret_last_position', '/geokrety/<int:id>/relationships/last-position')
api.route(GeokretRelationship, 'geokret_last_move', '/geokrety/<int:id>/relationships/last-move')

api.route(MovesList, 'moves_list',
          '/moves',
          '/geokrety/<int:geokret_id>/moves',
          '/users/<int:user_id>/moves',
          )
api.route(MoveDetail, 'move_details',
          '/moves/<int:id>',
          '/geokrety/<int:geokret_last_position_id>/last-position',
          '/geokrety/<int:geokret_last_move_id>/last-move',
          '/moves-comments/<int:move_comment_id>/move',
          )
api.route(MoveRelationship, 'move_geokret', '/moves/<int:id>/relationships/geokret')
api.route(MoveRelationship, 'move_author', '/moves/<int:id>/relationships/author')
api.route(MoveRelationship, 'move_type', '/moves/<int:id>/relationships/type')
api.route(MoveRelationship, 'move_comments', '/moves/<int:id>/relationships/comments')

api.route(BadgeList, 'badges_list',
          '/badges',
          '/users/<int:author_id>/created-badges',
          )
api.route(BadgeDetail, 'badge_details',
          '/badges/<int:id>',
          )
api.route(BadgeRelationship, 'badge_author', '/badges/<int:id>/relationships/author')
