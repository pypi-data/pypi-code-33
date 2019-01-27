from typing import Dict
from bootstrap_navbar.navbars.base import NavItemBase, NavLinkBase, Href
from unittest.mock import patch

import pytest


@pytest.fixture
def navitem(base_attrs: Dict):
    NavItemBase.template_name = "testing"
    return NavItemBase(**base_attrs)


@pytest.fixture
def navlink(link_attrs: Dict):
    NavLinkBase.template_name = "testing"
    return NavLinkBase(**link_attrs)


class TestNavItemBase:
    def test_init_raises(self, base_attrs: Dict) -> None:
        with pytest.raises(ValueError):
            NavItemBase(**base_attrs)

    def test_init(self, navitem: NavItemBase, base_attrs: Dict) -> None:

        assert navitem._text == base_attrs["text"]
        assert navitem._active == base_attrs["active"]
        assert navitem._disabled == base_attrs["disabled"]
        assert navitem._active_class == base_attrs["active_class"]
        assert navitem._class_set == set(base_attrs["class_list"])
        assert navitem._attrs == base_attrs["attrs"]

    def test_text_property(self, navitem: NavItemBase, base_attrs: Dict) -> None:
        assert navitem.text == base_attrs["text"]

    def test_class_list_property(self, navitem: NavItemBase, base_attrs: Dict) -> None:
        class_list = base_attrs["class_list"]
        class_list.append("active")

        assert navitem.class_list == class_list

    def test_active_class_property(
        self, navitem: NavItemBase, base_attrs: Dict
    ) -> None:
        assert navitem.active_class == base_attrs["active_class"]

    def test_active_class_property_set(
        self, navitem: NavItemBase, base_attrs: Dict
    ) -> None:
        navitem.active_class = "is-active"
        assert navitem.active_class == "is-active"

    def test_active_property(self, navitem: NavItemBase, base_attrs: Dict) -> None:
        assert navitem.active == base_attrs["active"]

    def test_active_property_set(self, navitem: NavItemBase, base_attrs: Dict) -> None:
        navitem.active = False
        assert navitem.active is False

    def test_disabled_property(self, navitem: NavItemBase, base_attrs: Dict) -> None:
        assert navitem.disabled == base_attrs["disabled"]

    def test_attrs_property(self, navitem: NavItemBase, base_attrs: Dict) -> None:
        assert navitem.attrs == base_attrs["attrs"]

    def test_get_context_data(self, navitem: NavItemBase, base_attrs: Dict):
        base_attrs_copy = base_attrs.copy()
        base_attrs_copy["class_list"].append("active")
        assert navitem.get_context_data() == base_attrs_copy

    def test_render(self, navitem: NavItemBase, base_attrs: Dict):
        base_attrs_copy = base_attrs.copy()
        base_attrs_copy["class_list"].append("active")

        with patch("bootstrap_navbar.navbars.base.get_template") as mock:
            mock.return_value.render.return_value = base_attrs_copy
            assert navitem.render() == base_attrs_copy


class TestNavLinkBase:
    def test_init(self, navlink: NavLinkBase, link_attrs: Dict) -> None:
        assert navlink._href == link_attrs["href"]

    def test_href_property(self, navlink: NavLinkBase, link_attrs: Dict) -> None:
        assert navlink.href == link_attrs["href"]

    def test_get_context_data(self, navlink: NavLinkBase, link_attrs: Dict):
        link_attrs_copy = link_attrs.copy()
        link_attrs_copy["class_list"].append("active")
        assert navlink.get_context_data() == link_attrs_copy


class TestHref:
    def test_basic(self) -> None:
        href = Href(url="https://testing.com")
        assert str(href) == "https://testing.com"

    def test_query_params(self) -> None:
        href = Href(url="https://testing.com", query_params={"test": 123})
        assert str(href) == "https://testing.com?test=123"
