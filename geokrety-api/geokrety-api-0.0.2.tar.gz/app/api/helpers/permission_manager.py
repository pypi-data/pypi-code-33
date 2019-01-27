from flask import request
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permissions import (auth_required, has_touched_geokret,
                                         is_admin, is_anonymous,
                                         is_date_in_the_future,
                                         is_geokret_holder, is_geokret_owner,
                                         is_move_author,
                                         is_move_before_geokret_birth,
                                         is_move_comment_author,
                                         is_there_a_move_at_that_datetime,
                                         is_user_itself)

permissions = {
    'is_anonymous': is_anonymous,
    'is_admin': is_admin,
    'is_user_itself': is_user_itself,
    'auth_required': auth_required,
    'is_geokret_owner': is_geokret_owner,
    'is_geokret_holder': is_geokret_holder,
    'is_move_author': is_move_author,
    'is_move_comment_author': is_move_comment_author,
    'has_touched_geokret': has_touched_geokret,
    'is_there_a_move_at_that_datetime': is_there_a_move_at_that_datetime,
    'is_move_before_geokret_birth': is_move_before_geokret_birth,
    'is_date_in_the_future': is_date_in_the_future,
}


def is_multiple(data):  # pragma: no cover
    if isinstance(data, list):
        return True
    if isinstance(data, str):
        if data.find(",") > 0:
            return True
    return False


def permission_manager(view, view_args, view_kwargs, *args, **kwargs):  # pragma: no cover
    """The function use to check permissions

    :param callable view: the view
    :param list view_args: view args
    :param dict view_kwargs: view kwargs
    :param list args: decorator args
    :param dict kwargs: decorator kwargs
    """
    methods = 'GET,POST,DELETE,PATCH'
    if 'id' in kwargs:
        view_kwargs['id'] = kwargs['id']

    if 'methods' in kwargs:
        methods = kwargs['methods']

    if request.method not in methods:
        return

    # leave_if checks if we have to bypass this request on the basis of lambda function
    if 'leave_if' in kwargs:
        check = kwargs['leave_if']
        if check(view_kwargs):
            return

    # A check to ensure it is good to go ahead and check permissions
    if 'check' in kwargs:
        check = kwargs['check']
        if not check(view_kwargs):
            raise ForbiddenException('Access forbidden', {'source': ''})

    if 'fetch' in kwargs:
        fetched = None
        if is_multiple(kwargs['fetch']):
            kwargs['fetch'] = [f.strip() for f in kwargs['fetch'].split(",")]
            for f in kwargs['fetch']:
                if f in view_kwargs:
                    fetched = view_kwargs.get(f)
                    break
        elif kwargs['fetch'] in view_kwargs:
            fetched = view_kwargs[kwargs['fetch']]
        if not fetched:
            model = kwargs['model']
            fetch = kwargs['fetch']
            # fetch_as = kwargs['fetch_as']
            fetch_key_url = 'id'
            fetch_key_model = 'id'
            if 'fetch_key_url' in kwargs:
                fetch_key_url = kwargs['fetch_key_url']

            if 'fetch_key_model' in kwargs:
                fetch_key_model = kwargs['fetch_key_model']

            if not is_multiple(model):
                model = [model]

            if is_multiple(fetch_key_url):
                fetch_key_url = fetch_key_url.split(",")

            found = False
            for index, mod in enumerate(model):
                if is_multiple(fetch_key_url):
                    f_url = fetch_key_url[index].strip()
                else:
                    f_url = fetch_key_url
                if not view_kwargs.get(f_url):
                    continue
                try:
                    data = mod.query.filter(
                        getattr(mod, fetch_key_model) == view_kwargs[f_url]).one()
                except NoResultFound:
                    pass
                else:
                    found = True
                    break

            if not found:
                raise ObjectNotFound('Object not found.', {'source': ''})

            fetched = None
            if is_multiple(fetch):
                for f in fetch:
                    if hasattr(data, f):
                        fetched = getattr(data, f)
                        break
            else:
                fetched = getattr(data, fetch) if hasattr(
                    data, fetch) else None

        if fetched:
            kwargs[kwargs['fetch_as']] = fetched
        else:
            raise ObjectNotFound('Object not found.', {'source': ''})

    if args[0] in permissions:
        permissions[args[0]](view, view_args, view_kwargs, *args, **kwargs)
    else:
        raise ForbiddenException('Access forbidden', {'source': ''})


def has_access(access_level, **kwargs):
    """
    The method to check if the logged in user has specified access
    level or nor
    :param string access_level: name of access level
    :param dict kwargs: This is directly passed to permission manager
    :return: bool: True if passes the access else False
    """
    try:
        if access_level in permissions:
            permissions[access_level](lambda *a, **b: True, (), {}, (), **kwargs)
    except Exception:
        return False
    return True
