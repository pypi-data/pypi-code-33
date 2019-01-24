from django.forms import widgets


class Selectr(widgets.Select):
    searchable = False
    multiple = False
    selectr_class = "selectr"
    searchable_class = "is-searchable"
    multiple_class = "is-multiple"

    def __init__(self, attrs=None):
        if attrs is not None:
            self.multiple = attrs.pop("multiple", self.multiple)
            self.searchable = attrs.pop("searchable", self.searchable)
        return super().__init__(attrs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        klass = self.selectr_class
        if self.multiple:
            klass = "{} {}".format(klass, self.multiple_class)
        if self.searchable:
            klass = "{} {}".format(klass, self.searchable_class)
        attrs["class"] = klass
        return attrs
