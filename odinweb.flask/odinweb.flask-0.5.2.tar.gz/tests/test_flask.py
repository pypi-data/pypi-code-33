import pytest

from flask import Flask, request

from odinweb import flask
from odinweb.constants import Method, Type
from odinweb.data_structures import PathParam


def test_request_proxy():
    test_app = Flask(__name__)
    test_app.testing = True
    app = test_app.test_client()

    @test_app.route('/')
    def test_method():
        target = flask.RequestProxy(request)
        assert target.method == Method.POST
        assert set(target.query.getlist('a')) == {'1', '3'}
        assert set(target.query.getlist('b')) == {'2'}
        assert target.body == "123"
        assert target.content_type == 'text/html'
        assert target.origin == "http://localhost"
        return 'OK'

    app.post('/?a=1&b=2&a=3', content_type='text/html', data="123", headers={"Origin": 'http://localhost'})


class TestApiBlueprint(object):
    @pytest.mark.parametrize('node, expected', (
        (PathParam('foo'), '<int:foo>'),
        (PathParam('bar', Type.String), '<string:bar>'),
        (PathParam('bar', None, None), '<bar>'),
    ))
    def test_node_formatter(self, node, expected):
        actual = flask.ApiBlueprint.node_formatter(node)
        assert actual == expected
