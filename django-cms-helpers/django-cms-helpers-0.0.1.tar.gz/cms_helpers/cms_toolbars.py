from cms.extensions.toolbar import ExtensionToolbar
from django.utils.encoding import force_text


class TitleExtensionToolbar(ExtensionToolbar):
    model = None
    insert_after = None

    def get_item_position(self, menu):
        position = None
        for items in menu._memo.values():
            for item in items:
                if force_text(getattr(item, 'name', None)) in (
                    force_text(self.insert_after),
                    '{0}...'.format(self.insert_after)
                ):
                    position = menu._item_position(item) + 1
                    break

        return position

    def populate(self):
        current_page_menu = self._setup_extension_toolbar()
        if not current_page_menu or not self.page:
            return

        position = self.get_item_position(current_page_menu)

        urls = self.get_title_extension_admin()
        for title_extension, url in urls:
            current_page_menu.add_modal_item(
                self.model._meta.verbose_name,
                url=url, position=position,
                disabled=not self.toolbar.edit_mode
            )
