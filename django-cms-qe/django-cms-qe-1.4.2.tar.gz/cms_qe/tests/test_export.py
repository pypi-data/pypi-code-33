import csv
import io
import json

from django.contrib.auth import get_user_model
import pytest
from pytest_data import use_data

from ..export import export_data


class ModelAdmin:
    list_display = ('foo',)

    def foo(self, obj):
        return 'foo property'


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_csv'})
def test_export_data_as_csv(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('csv', ModelAdmin(), queryset)
    data = list(csv.reader(io.StringIO(data)))
    assert len(data) == 2
    assert 'test_export_data_as_csv' in data[1]
    assert 'foo property' in data[1]


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_tsv'})
def test_export_data_as_tsv(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('tsv', ModelAdmin(), queryset)
    data = list(csv.reader(io.StringIO(data), delimiter='\t'))
    assert len(data) == 2
    assert 'test_export_data_as_tsv' in data[1]
    assert 'foo property' in data[1]


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_json'})
def test_export_data_as_json(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('json', ModelAdmin(), queryset)
    data = json.loads(data)
    assert len(data) == 1
    assert data[0]['username'] == 'test_export_data_as_json'
    assert data[0]['foo'] == 'foo property'


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_yaml'})
def test_export_data_as_yaml(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('yaml', ModelAdmin(), queryset)
    assert 'test_export_data_as_yaml' in data
    assert 'foo property' in data


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_html'})
def test_export_data_as_html(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('html', ModelAdmin(), queryset)
    assert '<table>' in data
    assert 'test_export_data_as_html' in data
    assert 'foo property' in data
