from datetime import datetime, timedelta
from functools import wraps

from flask import current_app as app
from flask_jwt import _jwt_required, current_identity
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.data_layers import MOVE_TYPE_COMMENT
from app.api.helpers.exceptions import (AuthenticationRequired,
                                        ForbiddenException,
                                        UnprocessableEntity)
from geokrety_api_models import Geokret, Move, MoveComment


def jwt_required(fn, realm=None):
    """
    Modified from original jwt_required to comply with `flask-rest-jsonapi` decorator conventions
    View decorator that requires a valid JWT token to be present in the request
    :param fn: function to be decorated
    :param realm: an optional realm
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            _jwt_required(realm or app.config['JWT_DEFAULT_REALM'])
        except Exception:  # JWTError
            raise AuthenticationRequired('Authentication is required', {'source': ''})
        return fn(*args, **kwargs)
    return decorator


def is_anonymous(view, view_args, view_kwargs, *args, **kwargs):
    if current_identity._get_current_object() is not None:
        raise ForbiddenException('Anonymous access is required', {'source': 'id'})


@jwt_required
def auth_required(view, view_args, view_kwargs, *args, **kwargs):
    return True


@jwt_required
def is_admin(view, view_args, view_kwargs, *args, **kwargs):
    if not current_identity.is_admin:
        raise ForbiddenException('Admin access is required', {'source': 'id'})
    return True


@jwt_required
def is_user_itself(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    """
    user = current_identity
    if not user.is_admin and str(user.id) != str(kwargs['user_id']):
        raise ForbiddenException('Access Forbidden', {'source': 'user_id'})
    return True


@jwt_required
def is_move_author(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows Move author to fully manage move.
    """
    user = current_identity
    if user.is_admin:
        return True

    try:
        move = Move.query.filter(Move.id == kwargs['move_id']).one()
    except NoResultFound:  # pragma: no cover
        raise ObjectNotFound('Move not found.', {'source': 'move_id'})

    if move.author_id == user.id:
        return True

    if app.config['ALLOW_GEOKRET_OWNER_TO_MODERATE_MOVES']:
        # Allow GeoKret owner to moderate moves if necessary
        geokret = Geokret.query.filter(Geokret.id == move.geokret_id).one()
        if geokret.owner_id == user.id:
            return True

    raise ForbiddenException('Access denied.', {'source': 'move_id'})


@jwt_required
def is_move_comment_author(view, view_args, view_kwargs, *args, **kwargs):
    user = current_identity
    if user.is_admin:
        return True

    try:
        move_comment = MoveComment.query.filter(MoveComment.id == kwargs['move_comment_id']).one()
    except NoResultFound:  # pragma: no cover
        raise ObjectNotFound(
            'MoveComment %s not found.' % kwargs['move_comment_id'],
            {'source': 'move_comment_id'})

    if move_comment.author_id == user.id:
        return True

    if app.config['ALLOW_GEOKRET_OWNER_TO_MODERATE_MOVE_COMMENTS']:
        # Allow GeoKret owner to moderate move comments if necessary
        if move_comment.move.geokret.owner_id == user.id:
            return True

    if app.config['ALLOW_MOVE_AUTHOR_TO_MODERATE_MOVE_COMMENTS']:
        # Allow Move author to moderate move comments if necessary
        if move_comment.move.author_id == user.id:
            return True

    raise ForbiddenException('Access denied.', {'source': 'move_comment_id'})


@jwt_required
def is_geokret_owner(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows GeoKret owner access to private resources of owned GeoKrety.
    Otherwise the user can only access public resource.
    """
    user = current_identity
    if user.is_admin:
        return True

    try:
        geokret = Geokret.query.filter(Geokret.id == kwargs['geokret_id']).one()
    except NoResultFound:  # pragma: no cover
        raise ObjectNotFound('Geokret not found.', {'source': 'geokret_id'})

    if geokret.owner_id == user.id:
        return True

    raise ForbiddenException('Access denied.', {'source': 'geokret_id'})


@jwt_required
def is_geokret_holder(view, view_args, view_kwargs, *args, **kwargs):
    user = current_identity
    if user.is_admin:
        return True

    try:
        geokret = Geokret.query.filter(Geokret.id == kwargs['geokret_id']).one()
    except NoResultFound:  # pragma: no cover
        raise ObjectNotFound('Geokret not found.', {'source': 'geokret_id'})

    if geokret.holder_id == current_identity.id:
        return True

    raise ForbiddenException('Not the GeoKret holder.', {'source': 'geokret_id'})


@jwt_required
def has_touched_geokret(view, view_args, view_kwargs, *args, **kwargs):
    user = current_identity
    if user.is_admin:  # pragma: no cover
        return True

    try:
        geokret = Geokret.query.filter(Geokret.id == kwargs['geokret_id']).one()
    except NoResultFound:  # pragma: no cover
        raise ObjectNotFound('Geokret not found.', {'source': 'geokret_id'})

    if Move.query \
            .filter(Move.geokret_id == geokret.id) \
            .filter(Move.author_id == user.id) \
            .filter(Move.type != MOVE_TYPE_COMMENT).count() > 0:
        return True

    raise ForbiddenException('Has never touched the GeoKret.',
                             {'source': 'geokret_id'})


def is_there_a_move_at_that_datetime(view, view_args, view_kwargs, *args, **kwargs):
    if kwargs.get('type') == MOVE_TYPE_COMMENT:
        raise UnprocessableEntity('Date from comments are not necessarily unique.')

    geokret_id = kwargs.get('geokret')
    if geokret_id is None:
        geokret_id = Move.query.get(kwargs['id']).geokret_id
    if Move.query \
        .filter(Move.geokret_id == geokret_id) \
        .filter(Move.moved_on_datetime == kwargs['moved_on_datetime']) \
        .filter(Move.type != MOVE_TYPE_COMMENT) \
        .filter(Move.id != kwargs.get('id')) \
            .count() == 0:
        raise UnprocessableEntity('There is no move at that datetime.')


def is_move_before_geokret_birth(view, view_args, view_kwargs, *args, **kwargs):
    geokret_id = kwargs.get('geokret_id')
    moved_on_datetime = kwargs.get('moved_on_datetime')
    if kwargs.get('id') is not None \
            and moved_on_datetime is None:
        moved_on_datetime = Move.query.get(kwargs.get('id')).moved_on_datetime
    if geokret_id is None:
        geokret_id = Move.query.get(kwargs['id']).geokret_id
    geokret = Geokret.query.get(geokret_id)
    if moved_on_datetime < geokret.created_on_datetime:
        return
    raise UnprocessableEntity('Move date not prior to GeoKret birth.')


def is_date_in_the_future(view, view_args, view_kwargs, *args, **kwargs):
    if kwargs.get('date_time') > datetime.utcnow().replace(microsecond=0) + timedelta(seconds=1):
        return
    raise UnprocessableEntity('Date time is not in the future.')
