from __future__ import print_function

from kabaret import flow


class NoDialogAction(flow.Action):

    def needs_dialog(self):
        return False

    def run(self, button):
        print('Well done Jolly Jumper !')

class SimpleDialogAction(flow.Action):

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is the action message: <3')
        return ['Ok', 'Maybe', 'Nope']

    def run(self, button):
        print('You chose {}'.format(button))

class DialogParamsAction(flow.Action):

    cut_down_trees = flow.BoolParam(True)
    skip_and_jump = flow.BoolParam(True)
    press_wild_flowers = flow.BoolParam(True)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Do you:')
        return ['Ok']

    def run(self, button):
        all_true = (
            self.cut_down_trees.get()
            and self.skip_and_jump.get()
            and self.press_wild_flowers.get()
        )
        if (
            self.cut_down_trees.get()
            and self.skip_and_jump.get()
            and self.press_wild_flowers.get()
        ):
            print('You hang around in bars')
        else:
            print('Do you ever party ?')

class DispatchParams(flow.Object):

    pool = flow.Param('Farm')
    priority = flow.Param(50)

    def get_flags(self):
        return [
            '-P', str(self.pool.get()),
            '-p', str(self.priority.get()),
        ]


class SequenceParam(flow.Object):

    first_frame = flow.Param(1)
    last_frame = flow.Param(100)

    def get_flags(self):
        return [
            '--first', str(self.first_frame.get()),
            '--last', str(self.last_frame.get()),
        ]

class ComplexDialogAction(flow.Action):

    dispatch = flow.Child(DispatchParams)
    sequence = flow.Child(SequenceParam)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Configure and Submit your job')
        return ['Submit']

    def run(self, button):
        cmd = ['spam_it']+self.dispatch.get_flags()+self.sequence.get_flags()
        print('#---> Cmd:', ' '.join(cmd))

class KeepOpenDialogAction(flow.Action):

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Click the Ok button !')
        return ['Ok', 'Close']

    def run(self, button):
        if button == 'Close':
            return

        self.message.set('Alrigth, now click the Close button :)')
        return self.get_result(close=False)

class GotoAction(flow.Action):

    _parent = flow.Parent()

    # def __init__(self, *args, **kwargs):
    #     super(GotoAction, self).__init__(*args, **kwargs)
    #     self._target_name = None

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self._target_name = None
        return ['Goto Project', 'Goto Parent', 'Create Page and use it for all Goto', 'Open new a page every time',]

    def run(self, button):
        if button == 'Goto Project':
            project_oid = self.root().project().oid()
            return self.get_result(goto=project_oid, close=False, goto_target=self._target_name)

        if button == 'Goto Parent':
            parent_oid = self._parent.oid()
            return self.get_result(goto=parent_oid, close=False, goto_target=self._target_name)

        if button == 'Create Page and use it for all Goto':
            project_oid = self.root().project().oid()
            import time
            self._target_name = str(time.time())
            return self.get_result(goto=project_oid, close=False, goto_target=self._target_name)

        if button == 'Open new a page every time':
            project_oid = self.root().project().oid()
            return self.get_result(goto=project_oid, close=False, goto_target='_NEW_')


class EditMyValueAction(flow.Action):

    _value = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Pick a color:')
        return ['Red', 'Pink', 'Blue', 'Violet']

    def run(self, button):
        self._value.set(button)

class MyValue(flow.values.Value):

    edit = flow.Child(EditMyValueAction)

class SubDialogAction(flow.Action):

    quote = flow.Param('', MyValue)

    def needs_dialog(self):
        return True

    def run(self, button):
        print('You selected: "{}"'.format(self.quote.get()))

class WizardDialogPage1(flow.Action):

    _parent = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is page <B>1/3</B> of a wizard style action')
        return ['Next']

    def run(self, button):
        return self.get_result(next_action=self._parent.wizard_page_2.oid())

class WizardDialogPage2(flow.Action):

    _parent = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is page <B>2/3</B> of a wizard style action')
        return ['Prev', 'Next']

    def run(self, button):
        if button == 'Next':
            return self.get_result(next_action=self._parent.wizard_page_3.oid())
        else:
            return self.get_result(next_action=self._parent.wizard_page_1.oid())

class WizardDialogPage3(flow.Action):

    _parent = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is page <B>3/3</B> of a wizard style action')
        return ['Prev', 'Finish']

    def run(self, button):
        if button == 'Prev':
            return self.get_result(next_action=self._parent.wizard_page_2.oid())
        print('#---> You are a Wizard now !!!')

class ActionsGroup(flow.Object):

    no_dialog_action = flow.Child(NoDialogAction)
    simple_dialog_action = flow.Child(SimpleDialogAction)
    keep_dialog_open_action = flow.Child(KeepOpenDialogAction)
    goto_action = flow.Child(GotoAction)
    dialog_params_action = flow.Child(DialogParamsAction)
    complex_dialog_action = flow.Child(ComplexDialogAction)

    sub_dialog_action = flow.Child(SubDialogAction)

    wizard_page_1 = flow.Child(WizardDialogPage1)
    wizard_page_2 = flow.Child(WizardDialogPage2).ui(hidden=True)
    wizard_page_3 = flow.Child(WizardDialogPage3).ui(hidden=True)
