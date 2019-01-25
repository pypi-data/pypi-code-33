from django.test import TestCase
from .create_data_users import create_users_role

from ..models import ProjectPermission


class ModelsTestCase(TestCase):
    def setUp(self):
        create_users_role()

    def test_owner_permission(self):
        perm = ProjectPermission.objects.get(name='owner')
        self.assertEqual(len(perm.role.all()), 1)
        for r in perm.role.all():
            self.assertEqual(r.name, 'owner')
