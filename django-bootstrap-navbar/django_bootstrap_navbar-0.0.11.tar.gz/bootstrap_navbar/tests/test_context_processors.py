from django.contrib.auth import get_user_model
from django.test import RequestFactory
from bootstrap_navbar.navbars import context_processors
from unittest.mock import patch
from bootstrap_navbar.navbars.bootstrap4 import NavBar


import pytest

User = get_user_model()


@pytest.mark.django_db
class TestNavBarContextProcessor:
    def test_navbar(
        self, user: User, request_factory: RequestFactory, navbar_class: NavBar
    ):
        request = request_factory.get("/")
        request.user = user

        settings_patcher = patch("bootstrap_navbar.navbars.context_processors.settings")
        import_module_patcher = patch("importlib.import_module")
        settings = settings_patcher.start()
        import_module = import_module_patcher.start()

        settings.BOOTSTRAP_NAVBAR = "module:NavBar"
        import_module.return_value.NavBar = navbar_class

        context = context_processors.navbar(request)
        assert "navbar" in context
        assert isinstance(context["navbar"], NavBar)

        settings_patcher.stop()
        import_module_patcher.stop()

    def test_navbar_class_not_found(self, user: User, request_factory: RequestFactory):
        request = request_factory.get("/")
        request.user = user

        settings_patcher = patch("bootstrap_navbar.navbars.context_processors.settings")
        import_module_patcher = patch("importlib.import_module")
        settings = settings_patcher.start()
        import_module = import_module_patcher.start()

        settings.BOOTSTRAP_NAVBAR = "module:NavBar"
        import_module.return_value.NavBar = None

        context = context_processors.navbar(request)
        assert "navbar" in context
        assert context["navbar"] is None

        settings_patcher.stop()
        import_module_patcher.stop()

    def test_navbar_missing_settings(self, user: User, request_factory: RequestFactory):
        request = request_factory.get("/")
        request.user = user
        settings_patcher = patch("bootstrap_navbar.navbars.context_processors.settings")
        settings = settings_patcher.start()
        settings.BOOTSTRAP_NAVBAR = None
        assert context_processors.navbar(request) == {}
