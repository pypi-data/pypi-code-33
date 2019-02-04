import logging
from contextlib import contextmanager

from requests import HTTPError
from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed, NotFound, PermissionDenied

from .models import KatkaProject


class BitbucketBaseAPIException(APIException):
    pass


class ProjectNotFoundAPIException(NotFound):
    default_detail = 'Project not found.'


class BadRequestAPIException(BitbucketBaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request.'
    default_code = 'bad_request'


@contextmanager
def bitbucket_service_exception_to_api():
    try:
        yield
    except KatkaProject.DoesNotExist:
        raise ProjectNotFoundAPIException()
    except HTTPError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise AuthenticationFailed()

        if ex.response.status_code == status.HTTP_403_FORBIDDEN:
            raise PermissionDenied()

        errors = ex.response.json().get('errors') if ex.response.content else None

        if errors and errors[0].get('exceptionName') == 'com.atlassian.bitbucket.project.NoSuchProjectException':
            logging.warning(errors[0].get('message'))
            raise ProjectNotFoundAPIException()

        if errors:
            logging.exception(f'Unexpected Bitbucket exception: {errors[0].get("message")}')
        else:
            logging.exception(f'Unexpected Bitbucket exception: {str(ex)}')

        if ex.response.status_code == status.HTTP_400_BAD_REQUEST:
            raise BadRequestAPIException()

        if ex.response.status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound()

        raise BitbucketBaseAPIException()
