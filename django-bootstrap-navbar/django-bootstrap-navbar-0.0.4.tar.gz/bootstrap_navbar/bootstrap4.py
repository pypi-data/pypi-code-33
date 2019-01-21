from typing import Dict, List
from django.http import HttpRequest
from django.template.loader import get_template
from bootstrap_navbar.base import NavItemBase, NavLinkBase


class Image:
    template_name = "bootstrap_navbar/image.html"

    def __init__(self, *, src: str, attrs: Dict = None) -> None:
        """Instantiate the class instance."""

        self._src = src
        self._attrs = attrs or {}

    @property
    def src(self) -> str:
        return self._src

    @property
    def attrs(self) -> Dict:
        return self._attrs

    def render(self) -> str:
        """Render the image."""

        return get_template(self.template_name).render(
            context={"src": self.src, "attrs": self.attrs}
        )


class Link(NavLinkBase):
    """Anchor tag used for navigation purposes."""

    template_name = "bootstrap_navbar/bootstrap4_link.html"


class ListItem(Link):
    """Anchor tag used for navigation purposes. Note this class is identical to
    Link class except for an additional class which is added in the initialize.
    """

    template_name = "bootstrap_navbar/bootstrap4_link.html"

    def __init__(
        self,
        *,
        text: str,
        href: str,
        active: bool = False,
        disabled: bool = False,
        active_class: str = "active",
        class_list: List[str] = None,
        attrs: Dict = None,
    ) -> None:
        """Instantiate the class instance."""

        super().__init__(
            text=text,
            href=href,
            active=active,
            disabled=disabled,
            active_class=active_class,
            class_list=class_list,
            attrs=attrs,
        )

        # Insert the appropriate bootstrap classes
        self._class_set.add("nav-item")
        self._class_set.add("nav-link")


class DropDown(NavItemBase):
    """Dropdown navigation menu."""

    template_name = "bootstrap_navbar/bootstrap4_dropdown.html"

    def __init__(
        self,
        *,
        text: str,
        children: List[NavLinkBase],
        active: bool = False,
        disabled: bool = False,
        active_class: str = "active",
        class_list: List[str] = None,
        attrs: Dict = None,
    ) -> None:
        """Instantiate the class instance."""

        super().__init__(
            text=text,
            active=active,
            disabled=disabled,
            active_class=active_class,
            class_list=class_list,
            attrs=attrs,
        )

        # Validate the children are of type NavLinkBase and add the appropriate bootstrap classes
        for child in children:
            if not isinstance(child, NavLinkBase):
                raise ValueError(
                    f"unsupported type for child attribute - '{type(child)}'"
                )

            child._class_set.add("dropdown-item")

        self._children = children

    @property
    def href(self) -> str:
        """Return the href of the active link."""

        for child in self.children:
            if child.active is True:
                return child.href

        return ""

    @property
    def children(self):
        return self._children

    def get_context_data(self) -> Dict:
        """Add the dropdown children to the context."""

        return {**super().get_context_data(), **{"children": self.children}}


class Brand(NavLinkBase):
    """Bootstrap 4 navbar brand."""

    template_name = "bootstrap_navbar/bootstrap4_brand.html"

    def __init__(
        self,
        *,
        text: str,
        href: str,
        active: bool = False,
        disabled: bool = False,
        active_class: str = "active",
        class_list: List[str] = None,
        attrs: Dict = None,
        image: Image = None,
    ) -> None:
        """Instantiate the class instance."""

        super().__init__(
            text=text,
            href=href,
            active=active,
            disabled=disabled,
            active_class=active_class,
            class_list=class_list,
            attrs=attrs,
        )

        self.image = image

    def get_context_data(self) -> Dict:
        """Add the brand image to the context."""

        return {**super().get_context_data(), **{"image": self.image}}


class NavGroup:
    template_name = "bootstrap_navbar/bootstrap4_list.html"

    def __new__(cls):
        """Validate the Meta class."""

        cls._meta = getattr(cls, "Meta", type("Meta", (), {}))

        if "class_list" not in cls._meta.__dict__:
            raise AttributeError("'class_list' is a required Meta class property")

        if "navitems" not in cls._meta.__dict__:
            raise AttributeError("'navitems' is a required Meta class property")

        return super().__new__(cls)

    def __init__(self) -> None:
        """Instantiate the class instance."""

        self._navitems = []
        for _navitem in self._meta.navitems:
            navitem = getattr(self, _navitem, None)

            if navitem is None:
                raise ValueError(
                    f"'{_navitem}' is declared in the Meta class but does not exist on the '{self.__class__}'"
                )

            self._navitems.append(navitem)

        self._class_set = set(self._meta.class_list)

    @property
    def class_list(self) -> List[str]:
        return list(self._class_set)

    @property
    def navitems(self):
        return [navitem for navitem in self._navitems]

    def get_context_data(self) -> Dict:
        """Generate the navbar context data."""

        return {"navitems": self.navitems, "class_list": self.class_list}

    def render(self) -> str:
        """Render the navigation list."""

        return get_template(self.template_name).render(context=self.get_context_data())


class Layout:
    def __new__(cls):
        """Validate the Meta class."""

        cls._meta = getattr(cls, "Meta", type("Meta", (), {}))

        if "brand" not in cls._meta.__dict__:
            cls._meta.brand = None

        if "navlists" not in cls._meta.__dict__:
            cls._meta.navlists = []

        return super().__new__(cls)

    def __init__(self) -> None:
        """Instantiate the class instance."""

        self._navlists = []

        for _navlist in self._meta.navlists:
            navlist = getattr(self, _navlist, None)

            if navlist is None:
                raise ValueError(
                    f"'{_navlist}' is declared in the Meta class but does not exist on the '{self.__class__}'"
                )

            self._navlists.append(navlist)

        self._brand = getattr(self._meta, "brand", None)

    @property
    def brand(self):
        return self._brand

    @property
    def navlists(self):
        return self._navlists


class NavBar:
    template_name = "bootstrap_navbar/bootstrap4_nav.html"

    def __new__(cls):
        """Validate the Meta class."""

        cls._meta = getattr(cls, "Meta", type("Meta", (), {}))

        if "layout_class" not in cls._meta.__dict__:
            raise AttributeError("'layout_class' is a required attribute")

        if "class_list" not in cls._meta.__dict__:
            cls._meta.class_list = []

        if "attrs" not in cls._meta.__dict__:
            cls._meta.attrs = {}

        return super().__new__(cls)

    def __init__(self):
        """Instantiate the class instance."""

        self._class_set = set(self._meta.class_list)
        self._attrs = self._meta.attrs
        self._layout_class = self._meta.layout_class
        self.layout = self._layout_class()

    @property
    def class_list(self) -> List[str]:
        return list(self._class_set)

    @property
    def attrs(self):
        return self._attrs

    @property
    def active_navitem(self) -> NavLinkBase:
        """Return the active navitem."""

        try:
            for navitem in self.navitems:
                print(navitem, navitem.active)

            return next(filter(lambda x: x.active is True, self.navitems))
        except StopIteration:
            return

    @property
    def navitems(self) -> List[NavLinkBase]:
        """Return a list of all the navitems."""

        navitems = []
        for navlist in self.layout.navlists:
            navitems.extend(navlist.navitems)

        return navitems

    def _set_active_navitem_dispatch(self, navitem: NavLinkBase, path: str) -> bool:
        """Dispatch to the appropriate function based on the navitem type."""

        if isinstance(navitem, DropDown):
            return self._set_active_navitem_dropdown(navitem, path)
        else:
            return self._set_active_navitem_link(navitem, path)

    def _set_active_navitem_link(self, navitem: ListItem, path: str):
        """Set the navitem to active if the current path matches the href."""

        navitem.active = navitem.href == path
        return navitem.active

    def _set_active_navitem_dropdown(self, dropdown: DropDown, path: str):
        """Set the dropdown to active if the current path matches one of the navitems href."""

        for navitem in dropdown.children:
            navitem.active = navitem.href == path

            if navitem.active:
                dropdown.active = True
                return True

        return False

    def set_active_navitem(self, request: HttpRequest) -> None:
        """Set the active flag of the active navitem."""

        for navitem in self.navitems:
            navitem.active = False

            if isinstance(navitem, DropDown):
                for child in navitem.children:
                    child.active = False

        for navitem in self.navitems:
            if self._set_active_navitem_dispatch(navitem, request.path) is True:
                return

    def get_context_data(self) -> Dict:
        """Generate the navbar context data."""

        return {
            "brand": self.layout.brand,
            "navlists": self.layout.navlists,
            "attrs": self.attrs,
            "class_list": self.class_list,
        }

    def render(self) -> str:
        """Render the navbar."""

        return get_template(self.template_name).render(context=self.get_context_data())
