from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.views.generic import TemplateView
from bootstrap_navbar.navbars.mixins import BootstrapNavBarViewMixin
from bootstrap_navbar.navbars.bootstrap4 import NavBar

import pytest


User = get_user_model()


class View(BootstrapNavBarViewMixin, TemplateView):
    def get_context_data(self, **kwargs):
        return super().get_context_data()


@pytest.fixture
def view(user: User, request_factory: RequestFactory):
    request = request_factory.get("/")
    request.user = user
    view = View()
    view.request = request
    return view


@pytest.mark.django_db
class TestBootstrapNavBarViewMixin:
    def test_get_navbar(self, view: View, navbar_class: NavBar):
        view.navbar_class = navbar_class
        navbar = view.get_navbar(view.request)
        assert isinstance(navbar, NavBar)

    def test_get_navbar_missing(self, view: View):
        assert view.get_navbar(view.request) is None

    def test_get_context_data(self, view: View, navbar_class: NavBar):
        view.navbar_class = navbar_class
        context = view.get_context_data()
        assert "navbar" in context

    def test_get_context_data_missing(self, view: View):
        context = view.get_context_data()
        assert "navbar" not in context
