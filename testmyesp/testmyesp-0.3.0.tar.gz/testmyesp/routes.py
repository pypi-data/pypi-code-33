
from colibris.authorization import ANY_PERMISSION

from testmyesp import views
from testmyesp.constants import ROLE_ADMIN, ROLE_REGULAR


ROUTES = [
    ('GET',    '/clients/me', views.get_me,     ANY_PERMISSION),
    ('GET',    '/jobs',       views.list_jobs,   {ROLE_ADMIN, ROLE_REGULAR}),
    ('GET',    '/jobs/{id}',  views.get_job,    {ROLE_ADMIN, ROLE_REGULAR}),
    ('POST',   '/jobs',       views.add_job,    {ROLE_ADMIN, ROLE_REGULAR}),
    ('DELETE', '/jobs/{id}',  views.cancel_job, {ROLE_ADMIN, ROLE_REGULAR}),
    ('HEAD',   '/jobs/{id}/assets/{name}', views.get_asset, None),
    ('GET',    '/jobs/{id}/assets/{name}', views.get_asset, None),
]
