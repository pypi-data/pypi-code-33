#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_CCC
------------

Tests for `CCC` models module.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from mixer.backend.django import mixer

UserProfile = get_user_model()


pytestmark = pytest.mark.django_db


class TestAccountModel:
    def test_account_model_can_create(self):
        account = mixer.blend(UserProfile, name='Damilola')
        assert account.pk == 1
