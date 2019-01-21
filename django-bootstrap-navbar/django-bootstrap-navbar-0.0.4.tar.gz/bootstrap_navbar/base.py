from typing import List, Dict
from django.template.loader import get_template


class NavItemBase:
    """Provides base attributes for navigation items (anchor tags)."""

    template_name = None

    def __init__(
        self,
        *,
        text: str,
        active: bool = False,
        disabled: bool = False,
        active_class: str = "active",
        class_list: List[str] = None,
        attrs: Dict = None,
    ) -> None:
        """Instantiate the class instance."""

        self._text = text
        self._active = active
        self._disabled = disabled
        self._active_class = active_class
        self._class_set = class_list or []
        self._class_set = set(self._class_set)
        self._attrs = attrs

        if self.template_name is None:
            raise ValueError("'template_name' template name is a required property")

    @property
    def text(self):
        return self._text

    @property
    def class_list(self) -> List[str]:
        class_list = list(self._class_set)

        if self._active:
            class_list.append(self.active_class)

        return class_list

    @property
    def active_class(self) -> str:
        return self._active_class

    @active_class.setter
    def active_class(self, value: str) -> None:
        self._active_class = value

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        """Set the navitem as active."""

        self._active = value

    @property
    def disabled(self):
        return self._disabled

    @property
    def attrs(self):
        return self._attrs or {}

    def get_context_data(self) -> Dict:
        """Return the default context."""

        return {
            "text": self.text,
            "href": self.href,
            "active": self.active,
            "disabled": self.disabled,
            "active_class": self.active_class,
            "class_list": self.class_list,
            "attrs": self.attrs,
        }

    def render(self) -> str:
        """Render the nav item using the provided template."""

        context = self.get_context_data()
        return get_template(self.template_name).render(context=context)


class NavLinkBase(NavItemBase):
    """Provides base attributes for navigation items (anchor tags)."""

    template_name = None

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
            active=active,
            disabled=disabled,
            active_class=active_class,
            class_list=class_list,
            attrs=attrs,
        )

        self._href = href

    @property
    def href(self):
        return str(self._href)

    def get_context_data(self) -> Dict:
        """Return the default context."""

        return {**super().get_context_data(), **{"href": self.href}}
