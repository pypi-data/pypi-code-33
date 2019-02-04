
from __future__ import print_function

import time

from kabaret import flow

from .flow_objects import InGridConfig, ShowInGridDialogAction, ShowInGridAction

#
#----------------------------------TOOLS
#

class CreateMappedItem(flow.Action):

    _map = flow.Parent()
    item_name = flow.Param('')

    def needs_dialog(self):
        return True

    def get_buttons(self):
        return ['Create Item', 'Close']

    def run(self, button):
        if button == 'Close':
            return

        name = self.item_name.get()
        try:
            exec('{}=None'.format(name))
        except Exception, err:
            self.message.set('Invalid name "{}"\n({})'.format(name, err))
            return self.get_result(close=False)

        if name in self._map.mapped_names():
            self.message.set('An item "{}" already exists'.format(name))
            return self.get_result(close=False)

        item = self._map.add(name)
        self.message.set('Item created:\n{}'.format(item.oid()))
        self._map.touch()

        return self.get_result(close=False)


class MyInGridConfig(InGridConfig):
    '''
    This call defines the color_from_display() method
    and is used for all InGridConfig in the project.
    This ensure visual consistency a easy tuning.

    Note that a real implementation would probably delegate
    the status display and colors to the status value class...
    '''
    def colors_from_row(self, row):
        if row % 2:
            return ('#222222', None)
        return (None, None)

    def colors_from_display(self, display):
        return {
            True: ('#000022', '#004488'),
            False: (None, None),
            'INV': ('#002244', '#004488'),
            'WIP': ('#220044', None),
            'RTK': ('#440022', None),
            'DONE': ('#004400', '#008800'),
            'OOP': (None, '#444444'),
        }.get(display, (None, None))

#
#----------------------------- TASK
#

class EditTaskStatusAction(flow.ChoiceValueSelectAction):

    SHOW_IN_PARENT_INLINE = True

class TaskStatus(flow.values.ChoiceValue):

    CHOICES = ['INV', 'WIP', 'RTK', 'DONE', 'OOP']

    edit = flow.Child(EditTaskStatusAction)

    @classmethod
    def default(cls):
        return cls.CHOICES[0]

    def is_finished(self):
        return self.get() in ('DONE', 'OOP')

class SetTaskDoneAction(flow.Action):

    ICON = ('icons.status', 'DONE')

    _task = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._task.status.set('DONE')

class ToggleAssignedToMeAction(flow.Action):

    _v = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._v.set(not self._v.get())

class ClearMapAction(flow.Action):

    _map = flow.Parent()

    confirm = flow.Param('')

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.confirm.set('')
        self.message.set('Please enter "Confirm" in the confirm field.')
        return ['Cancel', 'Confirm']

    def run(self, button):
        if button != 'Confirm':
            return 
        if self.confirm.get() != 'Confirm':
            self.message.set('Please enter "Confirm" in the confirm field.\n(BETTER THAN THAT !!!)')
            return self.get_result(close=False)

        self._map.clear()
        self._map.on_clear()

class ValueHistoryRevertAction(flow.Action):

    _entry = flow.Parent()
    _map = flow.Parent(2)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Set value to %r ?'%(self._entry.value.get()))
        return ['Confirm']

    def run(self, button):
        if button != 'Confirm':
            return 
        self._map.on_revert(self._entry)

class ValueHistoryEntry(flow.Object):

    event = flow.Param().ui(editable=False)
    value = flow.Param().ui(editable=False)
    by = flow.Param().ui(editable=False)
    on = flow.Param().ui(editable=False)

    revert_to_this_value = flow.Child(ValueHistoryRevertAction)

class ValueHistory(flow.Map):

    _value = flow.Parent()

    clear_history = flow.Child(ClearMapAction)

    @classmethod
    def mapped_type(cls):
        return ValueHistoryEntry

    def mapped_names(self, page_num=0, page_size=None):
        return [i for i in reversed(super(ValueHistory, self).mapped_names(page_num, page_size))]

    def get_session_uid(self):
        return self.root().session().session_uid()

    def on_set(self, value):
        return self._add_entry('set', value)

    def on_clear(self):
        return self._add_entry('history cleared', self._value.get())

    def on_revert(self, entry):
        value = entry.value.get()
        self._add_entry('revert to %s'%(entry.name(),), value)
        self._value.set(value)

    def _add_entry(self, event, value):
        mtime = time.time()
        nb = len(self)
        name = 'E%s'%(nb,)
        entry = self.add(name)
        entry.event.set(event)
        entry.value.set(value)
        entry.by.set(self.get_session_uid())
        entry.on.set(mtime)
        self.touch()
        return entry

    def columns(self):
        return ['Event', 'Value', 'On', 'By']

    def _fill_row_cells(self, row, item):
        row.update(dict(
            Event=str(item.event.get()),
            Value=str(item.value.get()),
            On=str(time.ctime(item.on.get())),
            By=str(item.by.get()),
        ))

class TaskAssignedToMeValue(flow.values.BoolValue):

    toggle = flow.Child(ToggleAssignedToMeAction)

    history = flow.Child(ValueHistory)

    def set(self, value):
        if self.get() != value:
            self.history.on_set(value)
        super(TaskAssignedToMeValue, self).set(value)

class Task(flow.Object):

    status = flow.Param(TaskStatus.default(), TaskStatus)
    assigned_to_me = flow.BoolParam(True, TaskAssignedToMeValue)

    set_done = flow.Child(SetTaskDoneAction)

    def belongs_to_me(self):
        return self.assigned_to_me.get()

    def get_ingrid_row(self):
        return dict(
            display=self.name().title(),
            oid=self.oid(),
        )

#
#----------------------------- ASSET
#

class AssetTask(Task):

    asset = flow.Parent()

class SetAssetOOPAction(flow.Action):

    ICON = ('icons.status', 'OOP')

    _asset = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._asset.mod.status.set('OOP')
        self._asset.setup.status.set('OOP')
        self._asset.lookdev.status.set('OOP')

class Asset(flow.Object):

    mod = flow.Child(AssetTask)
    setup = flow.Child(AssetTask)
    lookdev = flow.Child(AssetTask)

    set_oop = flow.Child(SetAssetOOPAction)

    def count_assigned_to_me(self):
        return [
            self.mod.belongs_to_me(),
            self.setup.belongs_to_me(),
            self.lookdev.belongs_to_me(),
        ].count(True)

    def is_done(self):
        for t in (self.mod, self.setup, self.lookdev):
            if not t.status.is_finished():
                return False
        return True

class InGridAssetsReport(MyInGridConfig):

    _assets = flow.Parent(2)

    def get_related_config_oids(self):
        return self.root().project().get_ingrid_config_oids()

    def _get_assets(self):
        return self._assets.mapped_items()

    def _get_column_paths(self):
        return (
            'mod/status',
            'setup/status',
            'lookdev/status',
        )

    def get_rows(self):
        rows = []
        for asset in self._get_assets():
            rows.append(
                dict(
                    display=asset.name(),
                    oid=asset.oid(),
                    bg=None,
                    fg=None,
                    icon=None
                )
            )
        return rows

    def get_columns(self):
        return [
            dict(display=p.split('/')[0].title())
            for p in self._get_column_paths()
        ]

    def get_cell(self, row, column):
        asset = self._get_assets()[row]
        path = self._get_column_paths()[column]
        value = asset._mng.get_object(path)
        display = value.get()
        bg, fg = self.colors_from_display(display)
        return dict(
            display=display,
            oid=value.oid(),
            bg=bg,
            fg=fg,
            icon=None,
        )

    def get_actions(self, *row_column_pairs):
        return []

class InGridMyAssets(InGridAssetsReport):

    def _get_assets(self):
        return [
            a for a in self._assets.mapped_items()
            if (
                a.mod.belongs_to_me()
                or 
                a.setup.belongs_to_me()
                or 
                a.lookdev.belongs_to_me()
            )
        ]

class InGridAssetConfigs(flow.Object):

    assets_report = flow.Child(InGridAssetsReport)
    my_assets = flow.Child(InGridMyAssets)

    def get_ingrid_config_oids(self):
        return [
            self.assets_report.oid(),
            self.my_assets.oid(),
        ]

class Assets(flow.Map):

    create_asset = flow.Child(CreateMappedItem)

    _ingrid_configs = flow.Child(InGridAssetConfigs)

    @classmethod
    def mapped_type(cls):
        return Asset

    def count_assigned_to_me(self):
        assets = [
            asset.count_assigned_to_me()
            for asset in self.mapped_items()
        ]
        return sum(assets, 0)

    def count_done(self):
        done_assets = [
            asset
            for asset in self.mapped_items()
            if asset.is_done()
        ]
        return len(done_assets)

    def get_ingrid_config_oids(self):
        '''
        Must return a list of InGridConfig subclasses oids
        '''
        return self._ingrid_configs.get_ingrid_config_oids()

#
#----------------------------- SHOT
#

class ShotTask(Task):

    shot = flow.Parent()

class ShotInGridConfig(MyInGridConfig):

    _shot = flow.Parent()

    def get_config_name(self):
        return '{} Report'.format(self._shot.name())

    def get_related_config_oids(self):
        oids = self._shot.prev_shot().get_ingrid_config_oids()
        oids.extend(
            self.root().project().shots.get_ingrid_config_oids()
        )
        oids.extend(
            self._shot.next_shot().get_ingrid_config_oids()
        )
        return oids

    def get_rows(self):
        shot = self._shot
        return [
            shot.anim.get_ingrid_row(),
            shot.lighting.get_ingrid_row(),
            shot.render.get_ingrid_row(),
            shot.compo.get_ingrid_row(),
        ]
        return rows

    def get_columns(self):
        return [
            dict(display='Status', path='status'),
            dict(display='Assigned To Me', path='assigned_to_me'),
        ]

    def get_cell(self, row, column):
        shot = self._shot
        tasks = (shot.anim, shot.lighting, shot.render, shot.compo)
        task = tasks[row]
        path = self.get_columns()[column]['path']
        value = task._mng.get_object(path)
        ui = self.get_object_ui(value)
        display = value.get()
        bg, fg = self.colors_from_display(display)
        return dict(
            display=display,
            oid=value.oid(),
            bg=bg,
            fg=fg,
            ui=ui,
            icon=None,
        )

    def get_actions(self, *row_column_pairs):
        return []

class SetShotOOPAction(flow.Action):

    ICON = ('icons.status', 'OOP')

    _shot = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._shot.anim.status.set('OOP')
        self._shot.lighting.status.set('OOP')
        self._shot.render.status.set('OOP')
        self._shot.compo.status.set('OOP')

class Shot(flow.Object):

    _shots = flow.Parent()
    _ingrid_config = flow.Child(ShotInGridConfig)

    anim = flow.Child(ShotTask)
    lighting = flow.Child(ShotTask)
    render = flow.Child(ShotTask)
    compo = flow.Child(ShotTask)

    set_oop = flow.Child(SetShotOOPAction)
    open_ingrid = flow.Child(ShowInGridAction)
    load_ingrid = flow.Child(ShowInGridDialogAction)

    def prev_shot(self):
        return self._shots.get_prev_shot(self)

    def next_shot(self):
        return self._shots.get_next_shot(self)

    def count_assigned_to_me(self):
        return [
            self.anim.belongs_to_me(),
            self.lighting.belongs_to_me(),
            self.render.belongs_to_me(),
            self.compo.belongs_to_me(),
        ].count(True)

    def is_done(self):
        for t in (self.anim, self.lighting, self.render, self.compo):
            if not t.status.is_finished():
                return False
        return True

    def get_ingrid_config_oids(self):
        return [self._ingrid_config.oid()]

class InGridShotsReport(MyInGridConfig):

    _shots = flow.Parent(2)

    def get_related_config_oids(self):
        return self.root().project().get_ingrid_config_oids()
        
    def get_rows(self):
        rows = []
        for shot in self._shots.mapped_items():
            rows.append(
                dict(
                    display=shot.name(),
                    oid=shot.oid(),
                    bg=None,
                    fg=None,
                    icon=None
                )
            )
        return rows

    def get_columns(self):
        return [
            dict(
                display='Anim',
            ),
            dict(
                display='lighting',
            ),
            dict(
                display='Render',
            ),
            dict(
                display='Compo',
            ),
        ]

    def get_cell(self, row, column):
        shot = self._shots.mapped_items()[row]
        path = self.get_columns()[column]['display'].lower()+'/status'
        value = shot._mng.get_object(path)
        display = value.get()
        bg, fg = self.colors_from_display(display)
        return dict(
            display=display,
            oid=value.oid(),
            bg=bg,
            fg=fg,
            icon=None,
        )

    def get_actions(self, *row_column_pairs):
        return []

class InGridShotsConfigs(flow.Object):

    shots_report = flow.Child(InGridShotsReport)

    def get_ingrid_config_oids(self):
        return [
            self.shots_report.oid(),
        ]

class Shots(flow.Map):

    _ingrid_configs = flow.Child(InGridShotsConfigs)

    create_shot = flow.Child(CreateMappedItem)
    
    @classmethod
    def mapped_type(cls):
        return Shot

    def get_prev_shot(self, shot):
        shots = self.mapped_items()
        i = shots.index(shot)-1
        return shots[i]

    def get_next_shot(self, shot):
        shots = self.mapped_items()
        i = (shots.index(shot)+1) % len(shots)
        return shots[i]

    def count_assigned_to_me(self):
        shots = [
            shot.count_assigned_to_me()
            for shot in self.mapped_items()
        ]
        return sum(shots, 0)

    def count_done(self):
        done_shots = [
            shot
            for shot in self.mapped_items()
            if shot.is_done()
        ]
        return len(done_shots)

    def get_ingrid_config_oids(self):
        return self._ingrid_configs.get_ingrid_config_oids()


class ProjectReport(MyInGridConfig):

    _project = flow.Parent()

    def get_related_config_oids(self):
        return (
            self._project.assets._ingrid_configs.assets_report.oid(),
            self._project.shots._ingrid_configs.shots_report.oid(),
        )

    def get_rows(self):
        rows = [
            dict(display='Assets'),
            dict(display='Shots'),
            dict(display='Totals', fg='#000088'),
        ]
        return rows

    def get_columns(self):
        return [
            dict(display='Count'),
            dict(display='Assigned To Me'),
            dict(display='Done'),
        ]

    def _get_cell_value(self, row, column):
        project = self._project

        if column == 0:
            if row == 0:
                return len(project.assets)
            if row == 1:
                return len(project.shots)
            return len(project.assets) + len(project.shots)

        if column == 1:
            if row == 0:
                return project.assets.count_assigned_to_me()
            if row == 1:
                return project.shots.count_assigned_to_me()
            return (
                project.assets.count_assigned_to_me()
                +
                project.shots.count_assigned_to_me()
            )
                
        if column == 2:
            if row == 0:
                return project.assets.count_done()
            if row == 1:
                return project.shots.count_done()
            return (
                project.assets.count_done()
                +
                project.shots.count_done()
            )

    def get_cell(self, row, column):
        value = self._get_cell_value(row, column)
        bg, fg = self.colors_from_row(row)
        if row == 2:
            fg = '#000088'
        return dict(
            display=value,
            oid=None,
            bg=bg,
            fg=fg,
            icon=None,
        )

    def get_actions(self, *row_column_pairs):
        return []

help_text = '''<h1>
Create some Assets and Shots, open an InGrid view and drop some asset or shot into it.
</h1>'''
class InGridDemoFlow(flow.Object):
    '''
    This Project shows how to provide InGrid configuration in Objects.

    Try to drag'n'drop some Asset child to an InGrid view, and some Shot child.
    See how the view collects and show different content.
    '''
    help = flow.Label(help_text)
    assets = flow.Child(Assets)
    shots = flow.Child(Shots)

    _project_report = flow.Child(ProjectReport)

    def get_ingrid_config_oids(self):
        return [self._project_report.oid()]