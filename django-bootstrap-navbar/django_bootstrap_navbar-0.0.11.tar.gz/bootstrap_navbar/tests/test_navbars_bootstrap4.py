from typing import Dict
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from bootstrap_navbar.navbars.base import NavLinkBase, NavItemBase
from bootstrap_navbar.navbars.bootstrap4 import (
    Image,
    Link,
    ListItem,
    DropDown,
    Brand,
    NavGroup,
    NavBar,
)
from unittest.mock import MagicMock

import pytest


User = get_user_model()


@pytest.fixture
def image_attrs() -> Dict:
    return {"src": "src", "class_list": [], "attrs": {}}


@pytest.fixture
def image(image_attrs: Dict) -> Image:
    return Image(**image_attrs)


@pytest.fixture
def list_item(link_attrs: Dict) -> ListItem:
    return ListItem(**link_attrs)


@pytest.fixture
def dropdown(dropdown_attrs: Dict) -> ListItem:
    return DropDown(**dropdown_attrs)


@pytest.fixture
def brand(link_attrs: Dict, image: Image) -> Brand:
    return Brand(image=image, **link_attrs)


class MockNavGroup(NavGroup):
    home = ListItem(text="Home", href="/", active=True)
    account = ListItem(text="Home", href="/account/", active=False)
    dropdown = DropDown(text="Home", children=[Link(text="docs", href="/docs/")])

    class Meta:
        navitems = ["home", "account", "dropdown"]
        class_list = ["mr-auto"]


class MockNavBar(NavBar):
    menu = MockNavGroup()

    class Meta:
        navgroups = ["menu"]
        class_list = ["mr-auto"]


@pytest.fixture
def navgroup_class():
    return MockNavGroup


@pytest.fixture
def navbar_class():
    return MockNavBar


class TestImage:
    def test_template_name(self) -> None:
        assert Image.template_name == "bootstrap_navbar/bootstrap4/image.html"

    def test_init(self, image: Image, image_attrs: Dict) -> None:
        assert image._src == image_attrs["src"]
        assert image._class_set == set(image_attrs["class_list"])
        assert image._attrs == image_attrs["attrs"]

    def test_src_property(self, image: Image, image_attrs: Dict) -> None:
        assert image.src == image_attrs["src"]

    def test_attrs_property(self, image: Image, image_attrs: Dict) -> None:
        assert image.attrs == image_attrs["attrs"]

    def test_class_list_property(self, image: Image, image_attrs: Dict) -> None:
        assert image.class_list == image_attrs["class_list"]

    def test_get_context_data(self, image: Image, image_attrs: Dict) -> None:
        assert image.get_context_data() == image_attrs


class TestLink:
    def test_template_name(self) -> None:
        assert Link.template_name == "bootstrap_navbar/bootstrap4/link.html"


class TestListItem:
    def test_template_name(self) -> None:
        assert ListItem.template_name == "bootstrap_navbar/bootstrap4/link.html"

    def test_bootstrap_class_set(self, list_item: ListItem, link_attrs: Dict):
        assert "nav-link" in list_item._class_set
        assert "nav-item" in list_item._class_set


class TestDropDown:
    def test_template_name(self) -> None:
        assert DropDown.template_name == "bootstrap_navbar/bootstrap4/dropdown.html"

    def test_init(self, dropdown: DropDown, dropdown_attrs: Dict) -> None:
        assert dropdown._children == dropdown_attrs["children"]

    def test_child_class_set(self, dropdown: DropDown, dropdown_attrs: Dict) -> None:
        for child in dropdown._children:
            assert "dropdown-item" in child._class_set

    def test_init_raises(self, base_attrs: Dict) -> None:
        base_attrs_copy = base_attrs.copy()
        base_attrs_copy["children"] = ["should raise"]

        with pytest.raises(TypeError):
            DropDown(**base_attrs_copy)

    def test_href_property_active(self, dropdown: DropDown) -> None:
        child = dropdown._children[0]
        child._active = True
        assert dropdown.href == child.href

    def test_href_property_inactive(self, dropdown: DropDown) -> None:
        child = dropdown._children[0]
        child._active = False
        assert dropdown.href == ""

    def test_children_property(self, dropdown: DropDown) -> None:
        assert dropdown.children == dropdown._children

    def test_get_context_data(self, dropdown: DropDown, dropdown_attrs: Dict) -> None:
        dropdown_attrs["class_list"].append("active")
        assert dropdown.get_context_data() == dropdown_attrs


class TestBrand:
    def test_init(self, brand: Brand, image: Image) -> None:
        assert brand._image == image

    def test_image_property(self, brand: Brand, image: Image) -> None:
        assert brand.image == image

    def test_get_context_data(
        self, brand: Brand, image: Image, link_attrs: Dict
    ) -> None:
        link_attrs_copy = link_attrs.copy()
        link_attrs_copy["image"] = image
        link_attrs_copy["class_list"].append("active")
        assert brand.get_context_data() == link_attrs_copy


class TestNavGroup:
    def test_new_class_list_raises(self) -> None:
        NavGroup.Meta = MagicMock()
        NavGroup.Meta.navitems = []

        with pytest.raises(AttributeError):
            navgroup = NavGroup()

        del NavGroup.Meta

    def test_new_navitems_raises(self) -> None:
        NavGroup.Meta = MagicMock()
        NavGroup.Meta.class_list = []

        with pytest.raises(AttributeError):
            navgroup = NavGroup()

        del NavGroup.Meta

    def test_init(self) -> None:
        NavGroup.Meta = MagicMock()
        NavGroup.Meta.class_list = ["mr-auto"]
        NavGroup.Meta.navitems = ["testing"]
        NavGroup.testing = ListItem(text="Home", href="/")

        navgroup = NavGroup()
        assert "mr-auto" in navgroup._class_set

        del NavGroup.Meta
        del NavGroup.testing

    def test_init_raises(self) -> None:
        NavGroup.Meta = MagicMock()
        NavGroup.Meta.class_list = []
        NavGroup.Meta.navitems = ["testing"]

        with pytest.raises(AttributeError):
            navgroup = NavGroup()

        del NavGroup.Meta

    def test_class_list_property(self, navgroup_class: NavGroup) -> None:
        navgroup = navgroup_class()
        assert "mr-auto" in navgroup.class_list

    def test_navitems_property(self, navgroup_class: NavGroup) -> None:
        navgroup = navgroup_class()
        for navitem in navgroup.navitems:
            assert isinstance(navitem, (NavItemBase, NavLinkBase))

    def test_get_context_data(self, navgroup_class: NavGroup) -> None:
        navgroup = navgroup_class()
        context = navgroup.get_context_data()

        assert len(context)
        assert "navitems" in context
        assert "class_list" in context


@pytest.mark.django_db
class TestNavBar:
    def test_active_navitem(self, navbar_class: NavBar) -> None:
        navbar = navbar_class()
        assert navbar.active_navitem == next(navbar.navitems)

    def test_active_navitem_none_active(self, navbar_class: NavBar) -> None:
        navbar = navbar_class()
        active_navitem = navbar.active_navitem
        active_navitem.active = False
        assert navbar.active_navitem is None

    def test_set_active_navitem(
        self, user: User, request_factory: RequestFactory, navbar_class: NavBar
    ) -> None:
        navbar = navbar_class()

        request = request_factory.get("/account/")
        request.user = user

        navbar.set_active_navitem(request)
        assert navbar.active_navitem == list(navbar.navitems)[1]

    def test_set_active_navitem_dropdown(
        self, user: User, request_factory: RequestFactory, navbar_class: NavBar
    ) -> None:
        navbar = navbar_class()

        request = request_factory.get("/docs/")
        request.user = user

        navbar.set_active_navitem(request)
        assert navbar.active_navitem == list(navbar.navitems)[2]

    def test_get_context_data(self, navbar_class: NavBar) -> None:
        navbar = navbar_class()
        context = navbar.get_context_data()

        assert len(context) == 4
        assert "brand" in context
        assert "navgroups" in context
        assert "attrs" in context
        assert "class_list" in context
