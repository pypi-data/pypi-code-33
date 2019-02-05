import six
from qtpy import QtWidgets, QtCore

from kabaret.app import resources

from ..form_tree import FormField
from .ref_by import RefByWidget


class ObjectActionMenuManager(object):

    def __init__(self, session, action_callback):
        super(ObjectActionMenuManager, self).__init__()
        self.session = session
        self.action_callback = action_callback

    def _update_menu(self, menu, actions, action_callback):
        last_group = None
        menu.clear()
        for group, label, data, enabled, icon_ref in actions:
            if last_group != group:
                menu.addSeparator()
            last_group = group
            action_oid = data['oid']
            menu_callback = lambda oid=action_oid: action_callback(oid)  # noqa
            action = menu.addAction(label, menu_callback)
            if not enabled:
                action.setEnabled(False)
            if icon_ref and icon_ref[1]:
                try:
                    icon = resources.get_icon(icon_ref, self)
                except resources.NotFoundError as err:
                    self.session.log_debug("WARNING: RESOURCE NOT FOUND: %r" % (err,))
                else:
                    action.setIcon(icon)

    def update_oid_menu(self, oid, menu):
        actions_info = self.session.cmds.Flow.get_object_actions(oid)
        # =>  (
        #         relation.index,
        #         ui_group,
        #         relative_action_path,
        #         {
        #             'action_icon': relation_related_type.ICON,
        #             'ui': action_ui_config,
        #             'oid': action_oid,
        #         }
        #     )

        actions = []
        for index, group, path, data in actions_info:
            enabled = data.get('ui', {}).get('enabled', True)
            icon_name = data.get('action_icon') or 'action'
            if isinstance(icon_name, six.string_types):
                icon_ref = ('icons.flow', icon_name)
            else:
                icon_ref = icon_name
            label = data.get('ui', {}).get('label')
            if len(path) > 1 or label is None:
                label = ' > '.join(
                    name.strip('_').replace('_', ' ').title()
                    for name in path
                )
            actions.append((
                group,
                label,
                data,
                enabled,
                icon_ref
            ))

        self._update_menu(menu, actions, self.action_callback)

        # last_group = None
        # menu.clear()
        # for group, label, data, enabled, icon_ref in actions:
        #     if last_group != group:
        #         menu.addSeparator()
        #     last_group = group
        #     action_oid = data['oid']
        #     menu_callback = lambda oid=action_oid: self.action_callback(oid)  # noqa
        #     action = menu.addAction(label, menu_callback)
        #     if not enabled:
        #         action.setEnabled(False)
        #     if icon_ref and icon_ref[1]:
        #         try:
        #             icon = resources.get_icon(icon_ref, self)
        #         except resources.NotFoundError as err:
        #             print("WARNING: RESOURCE NOT FOUND: %r" % (err,))
        #         else:
        #             action.setIcon(icon)

        return bool(actions)

    def update_oids_menu(self, oids, menu):
        actions_info = self.session.cmds.Flow.get_objects_actions(oids)

        actions = []
        for index, group, path, data in actions_info:
            enabled = data.get('ui', {}).get('enabled', True)
            icon_name = data.get('action_icon') or 'action'
            if isinstance(icon_name, six.string_types):
                icon_ref = ('icons.flow', icon_name)
            else:
                icon_ref = icon_name
            label = data.get('ui', {}).get('label')
            if len(path) > 1 or label is None:
                label = ' > '.join(
                    name.strip('_').replace('_', ' ').title()
                    for name in path
                )
            actions.append((
                group, label, data, enabled, icon_ref
            ))

        self._update_menu(menu, actions, self._multiple_action_callback)
        return bool(actions)

    def _multiple_action_callback(self, oids):
        for oid in oids:
            self.action_callback(oid)


class ObjectActionsMenu(QtWidgets.QWidget):

    def __init__(self, session, parent, action_callback):
        super(ObjectActionsMenu, self).__init__(parent)
        self._menu_manager = ObjectActionMenuManager(
            session, action_callback
        )
        self.session = session

        # self._action_callback = action_callback

        # self.setStyleSheet('background-color: red;')
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        tb = QtWidgets.QToolButton(self)
        tb.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        tb.setArrowType(QtCore.Qt.NoArrow)
        tb.setProperty('hide_arrow', True)
        tb.setProperty('no_border', True)
        tb.setPopupMode(tb.InstantPopup)
        try:
            icon = resources.get_icon(('icons.gui', 'submenu'), self)
        except resources.NotFoundError as err:
            self.session.log_debug("WARNING: RESOURCE NOT FOUND: %r" % (err,))
        else:
            tb.setIcon(icon)

        self._menu = QtWidgets.QMenu(tb)
        tb.setMenu(self._menu)
        self.layout().addWidget(tb)

        self.hide()
        # self.set_actions(None)

    def load_actions(self, oid):
        got_actions = self._menu_manager.update_oid_menu(oid, self._menu)
        if not got_actions:
            self.hide()
        else:
            self.show()
        return

    #     actions_info = self.session.cmds.Flow.get_actions(oid)
    #     # =>  (
    #     #         relation.index,
    #     #         ui_group,
    #     #         relation.name,
    #     #         {
    #     #             'action_icon': relation_related_type.ICON,
    #     #             'ui': relation.get_ui(),
    #     #             #FIXME: should be handled by the relation!
    #     #             'oid': related_oid+'/'+relation.name,
    #     #         }
    #     #     )

    #     actions = []
    #     for index, group, name, data in actions_info:
    #         enabled = data.get('ui', {}).get('enabled', True)
    #         icon_name = data.get('action_icon') or 'action'
    #         icon_ref = ('icons.flow', icon_name)
    #         label = data.get('ui', {}).get('label')
    #         if label is None:
    #             label = name.strip('_').replace('_', ' ').title()
    #         actions.append((
    #             group,
    #             label,
    #             data,
    #             enabled,
    #             icon_ref
    #         ))
    #     self.set_actions(actions)

    # def set_actions(self, actions):
    #     if not actions:
    #         # self.setEnabled(False)
    #         self.hide()
    #         return
    #     # self.setEnabled(True)
    #     self.show()

    #     if self._action_callback is None:
    #         print(
    #             'WARNING, editor %r for %r requests action menu update '
    #             'but has no action_callable !!!' % (
    #                 self._editor, self._editor._field.field_id(),
    #             )
    #         )
    #         return

    #     last_group = None
    #     self._menu.clear()
    #     menu = self._menu
    #     for group, label, data, enabled, icon_ref in actions:
    #         if last_group != group:
    #             menu.addSeparator()
    #         last_group = group
    #         menu_callback = lambda data=data: self._on_action_menu(data)  # noqa
    #         action = menu.addAction(label, menu_callback)
    #         if not enabled:
    #             action.setEnabled(False)
    #         if icon_ref and icon_ref[1]:
    #             try:
    #                 icon = resources.get_icon(icon_ref, self)
    #             except resources.NotFoundError as err:
    #                 print("WARNING: RESOURCE NOT FOUND: %r" % (err,))
    #             else:
    #                 action.setIcon(icon)

    # def _on_action_menu(self, data):
    #     self._action_callback(data['oid'])


class ObjectSummary(QtWidgets.QWidget):

    def __init__(self, session, parent, icon_provider=None):
        super(ObjectSummary, self).__init__()
        self.session = session
        self.icon_provider = icon_provider

        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lo)

        self._tb = QtWidgets.QToolButton(self)
        self._tb.hide()
        self._lb = QtWidgets.QLabel(self)

        lo.addWidget(self._tb)
        lo.addWidget(self._lb)

    def load_summary(self, oid):
        summary = self.session.cmds.Flow.get_summary(oid)
        self._lb.setText(summary)
        if self.icon_provider is not None:
            icon = self.icon_provider(summary)
            self.set_icon(icon)

    def set_icon(self, icon):
        if icon is None:
            self._tb.hide()
            return
        self._tb.setIcon(icon)
        self._tb.show()


class FlowField(FormField):

    def __init__(self, parent, session, oid, ui_config=None):
        self.session = session
        self.oid = oid
        self.ui_config = ui_config or {}
        self._label = self.ui_config.get('label')
        if self._label is None:
            self._label = oid.rsplit('/', 1)[-1].replace('_', ' ').title()

        super(FlowField, self).__init__(parent)

    def _get_icon(self, icon_name, resource_folder='icons.flow'):
        if isinstance(icon_name, six.string_types):
            icon_ref = (resource_folder, icon_name)
        else:
            icon_ref = icon_name
        try:
            icon = resources.get_icon(icon_ref, self.treeWidget())
        except resources.NotFoundError as err:
            self.session.log_debug("WARNING: RESOURCE NOT FOUND: %r" % (err,))
            return None
        return icon

    def _get_config_icon(self):
        icon_name = self.ui_config.get('icon', 'object')
        if not icon_name:
            return None
        return self._get_icon(icon_name)

    def _get_icon_for(self, text, resource_folder='icons.status'):
        if text is None:
            return None
        first_word = text.split(' ', 1)[0]
        return self._get_icon(first_word.upper(), resource_folder)

    def activated(self, col):
        if QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier:
            self.treeWidget().open(self.oid)
            return True
        return None

    def build_children(self):
        tree = self.treeWidget()
        tree.build_children(self)

    def on_touch_event(self, oid):
        if self._inspect_touch_event(oid):
            return True
        return self._dispatch_touch_event(oid)

    def _inspect_touch_event(self, oid):
        if oid == self.oid:
            # print('  My OTE', self.oid)
            self.update_content()
            return True
        return False

    def _dispatch_touch_event(self, oid):
        if oid.startswith(self.oid + '/'):
            # print('  Child OTE', self.oid)
            for i in range(self.childCount()):
                c = self.child(i)
                try:
                    c.on_touch_event
                except AttributeError:
                    # This occurs over "_PRELOAD_CHILD_" :/ (who said ugly? :p)
                    pass
                else:
                    handled = c.on_touch_event(oid)
                    if handled:
                        return True
        return False

    def update_content(self):
        raise NotImplementedError(self.__class__.__name__)


class ReferencesField(FormField):

    _DEFAULT_EXPANDED_STATE = True

    def __init__(self, parent, oids, leaf_callback, group_callback):
        self.ref_by_widget = None
        self.oids = oids
        self._leaf_callback = leaf_callback
        self._group_callback = group_callback
        super(ReferencesField, self).__init__(parent)

    def activated(self, col):
        if not self.isExpanded():
            self.setExpanded(True)
        else:
            self.setExpanded(False)

    def build_children(self):
        return

    def build(self):
        tree = self.treeWidget()

        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

        self.setIcon(0, resources.get_icon(('icons.flow', 'ref')))
        self.setText(0, "References")
        self.ref_by_widget = RefByWidget(tree, self.oids,
                                         self._leaf_callback, self._group_callback,
                                         self.on_tree_hide)
        self.setItemWidget(1, self.ref_by_widget)

    def on_tree_hide(self, hidden):
        if self.ref_by_widget:
            self.update_height(self.ref_by_widget)

    def on_touch_event(self, oid):
        self.ref_by_widget.refresh()
        return True
