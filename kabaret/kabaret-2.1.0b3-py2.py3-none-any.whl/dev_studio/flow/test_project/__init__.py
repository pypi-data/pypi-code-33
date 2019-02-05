
from collections import OrderedDict

from kabaret.flow2 import (
    values,
    Object, Map, Action,
    Child, Parent, Computed,
    Param, IntParam, BoolParam, HashParam
)

#-------------------------------- ACTIONS


class ExploreAction(Action):

    SHOW_IN_PARENT_INLINE = False
    ICON = 'explorer'


class TextEditAction(Action):

    ICON = 'notepad'


class StatusValue(values.ChoiceValue):
    STRICT_CHOICES = True
    CHOICES = ['NYS', 'WAIT', 'WIP', 'RVW', 'RTK', 'DONE', 'OOP']


class Status(Param):

    def __init__(self, default_value='NYS'):
        super(Status, self).__init__(default_value, StatusValue)

#----------------------------------------- BANK


class Bank(Object):

    ICON = 'Bank'


class CreateBankAction(Action):

    _map = Parent()

    bank_name = Param('Bank')

    def get_buttons(self):
        return ['Create']

    def run(self, button):
        self._map.add(self.bank_name.get())
        self._map.touch()


class Banks(Map):

    ICON = 'Bank'

    # _items = HashParam(
    #     OrderedDict([
    #         ('Bank', ' my_studio.flow.test_project.Bank'),
    #     ])
    # )

    create_bank = Child(CreateBankAction)

    @classmethod
    def mapped_type(cls):
        return Bank

# --------------------------------------- SHOT


class Montage(Object):

    index = IntParam(0)
    first = IntParam(1)
    fade_in = IntParam(0)
    last = IntParam(100)
    fade_out = IntParam(0)
    nb_frames = Computed()

    def child_value_changed(self, child_value):
        if child_value in (self.first, self.last):
            self.nb_frames.touch()

    def compute_child_value(self, child_value):
        if child_value == self.nb_frames:
            self.nb_frames.set(
                self.last.get() - self.first.get() + 1
            )


class CastItem(Object):

    asset = Param('//ASSET//')
    index = IntParam(0)


class Casting(Map):

    @classmethod
    def mapped_type(cls):
        return CastItem


class ShotObject(Object):

    def summary(self):
        return '<font color=#440000><b>| File does not exists | Not Yet Reversionned |</b></font>'


class AddToReversionAction(Action):
    SHOW_IN_PARENT_INLINE = False


class ProtectedAction(Action):
    SHOW_IN_PARENT_INLINE = False


class FileHistoryMap(Map):
    pass


class PublishAction(Action):
    ICON = 'rvs_publish'


class InitAction(Action):
    pass


class ShotTask(ShotObject):

    filename = Computed()
    exists = Computed().editor('bool')
    explore = Child(ExploreAction)
    is_reversionned = BoolParam()
    add_to_reversion = Child(AddToReversionAction)
    locked_by = Computed()
    steal_work = Child(ProtectedAction)
    trash_work = Child(ProtectedAction)
    history = Child(FileHistoryMap)

    publish = Child(PublishAction)
    open = Child(TextEditAction)
    initialize = Child(InitAction)

    @classmethod
    def get_source_display(self, oid):
        shot_oid, task = oid.rsplit('/', 1)
        return (
            Shot.get_source_display(shot_oid)
            +
            ' -> ' + task
        )

    def compute_child_value(self, child_value):
        child_value.set({
            self.filename: 'path/to/filename.ext',
            self.exists: False,
            self.is_reversionned: False,
            self.locked_by: '-?-',
        }[child_value])


class Anim(ShotObject):

    ICON = 'maya'


class Lighting(ShotObject):

    ICON = 'alembic'


class Comp(ShotObject):

    ICON = 'natron'


class Shot(Object):

    ICON = 'shot'

    status = Status().watched()
    montage = Child(Montage)

    casting = Child(Casting)
    animatic = Child(ShotTask)
    sound = Child(ShotTask)
    anim = Child(ShotTask)
    lighting = Child(ShotTask)
    comp = Child(ShotTask)

    @classmethod
    def get_source_display(cls, oid):
        names = oid.split('/')
        return ' '.join(names[-3::2])

    def child_value_changed(self, child_value):
        if child_value is self.status:
            self.touch()

# --------------------------------------- FILM


class Add10ShotsAction(Action):

    ICON = 'sequence'

    _shots = Parent()

    def run(self, button):
        start = len(self._shots) + 1
        for i in range(10):
            self._shots.add('P%03i' % (i + start))

        self._shots.touch()


class Shots(Map):

    ICON = 'shot'

    add_10_shots = Child(Add10ShotsAction)

    @classmethod
    def mapped_type(cls):
        return Shot

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        '''
        Subclasses must override this to fill value for each column returned by columns()
        '''
        row['Name'] = item.name()
        row['Status'] = item.status.get()

    def _fill_row_style(self, style, item, row):
        style['Status_icon'] = 'status_' + row['Status']


class Film(Object):

    shots = Child(Shots)


class CreateFilmAction(Action):

    _map = Parent()

    film_name = Param('EP')

    def get_buttons(self):
        return ['Create']

    def run(self, button):
        i = len(self._map) + 1
        self._map.add('%s%03i' % (self.film_name.get(), i))
        self._map.touch()


class Films(Map):

    create_film = Child(CreateFilmAction)

    @classmethod
    def mapped_type(cls):
        return Film

# ------------------------------------------------- PROJECT


class Launcher(Object):
    pass


class Launchers(Object):

    maya = Child(Launcher)
    max = Child(Launcher)
    guerilla = Child(Launcher)

    nuke = Child(Launcher)
    natron = Child(Launcher)


class ImageSettings(Object):

    frame_rate = Param(25)
    width = Param(2840)
    height = Param(1188)
    padding = Param(4)
    par = Param(1.0)


class MayaSettings(Object):

    project_path = Param('path/to/maya_project')
    user_away_path = Param('path/to/AWAY/Users/me')


class Settings(Object):

    #project = Parent()

    image = Child(ImageSettings)
    Maya = Child(MayaSettings)


class CreateProjectFoldersAction(Action):

    def get_buttons(self):
        return ['Create']

    def run(self, button):
        pass


class ReversionAdmin(Object):

    repo_path = Param('path/to/rvs_repo')
    repo_exists = Param(True).ui(editor='bool')

    work_path = Param('path/to/work_dir')
    work_exists = Param(True).ui(editor='bool')

    mount_script = Param('\n\ntest...\n\n').ui(editor='textarea')


class ProjectMonkeyPatch(Object):

    filename = Param('path/to/project_monkey_patch.py')
    explore = Child(ExploreAction)
    edit = Child(TextEditAction)


class Admin(Object):

    create_folders = Child(CreateProjectFoldersAction)
    reversion = Child(ReversionAdmin)
    project_monkey_patch = Child(ProjectMonkeyPatch)


class EditChoicesAction(Action):
    pass


class MultiChoiceValueTest(values.MultiChoiceValue):
    CHOICES = ['WIP', 'RTK', 'DONE']

    edit = Child(EditChoicesAction)


class TestProject(Object):

    open = Child(Launchers)
    banks = Child(Banks)
    films = Child(Films)

    x = Param([], MultiChoiceValueTest).editor('multichoices')
    y = BoolParam(True)
    settings = Child(Settings)
    admin = Child(Admin)
