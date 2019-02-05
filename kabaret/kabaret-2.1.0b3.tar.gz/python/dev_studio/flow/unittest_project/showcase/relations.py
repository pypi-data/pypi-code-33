
from kabaret.flow import (
    values, group,
    Object, Map, Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Param, IntParam, BoolParam, HashParam,
    Label, Separator,
)


class ParentExampleChild(Object):

    my_parent = Parent()
    relations = Parent(2)


class ParentExample(Object):

    relations = Parent()
    my_child = Child(ParentExampleChild)

    doc = Label(
        '<font color=#F88>/!\\ BEWARE:</font>'
        ' When your Objects need to access other objects, it is better to use a '
        'Connection or a method returning the object to use.<br>'
        'By doing so, you make your Object more reusable.'
        'The Parent() relation is usefull to add a button to the GUI, or when the relation '
        'is strong enough to not need an overrid in subclasses...'

    )


class MyChild(Object):

    doc = Label(
        'Some pretty dumb Object...'
    )

    def summary(self):
        return 'This is a child object. Double click its name to enter it, double click here to open it.'


class Option(Object):

    @classmethod
    def get_source_display(cls, oid):
        '''
        This is used by the GUI to display the source of a Connection.
        Default is to show the whole oid. Here we cut to the source label.
        '''
        return oid.split('/')[-1].replace('_', ' ').title()


class Option1(Option):

    ICON = 'maya'

    doc = Label('This is probably not a good option...')

class Option2(Option):

    ICON = '3dsmax'

    doc = Label('Is this even en option?')


class ConnectionExample(Object):

    option_maya = Child(Option1)
    option_3ds = Child(Option2)
    current = Connection(Option)


class RelationsGroup(Object):

    doc = Label(
        '<HR><H2>'
        'Relation is what binds objects together.<br>'
        'There are several relations types, all but the "Param" one are showcased here.<br>'
        '(See the Value page for examples of the Param relations)'
        '</H2>'
    )

    child_doc = Label(
        '<HR><H3>'
        'The <u>Child</u> relation let you add an Object under another one:'

    )
    my_child = Child(MyChild)

    parent_doc = Label(
        '<HR><H3>'
        'The <u>Parent</u> relation gives a reference to an Object\'s (grand)parent.<br>'
        'The GUI will show a "goto..." button for each Parent relation of the current '
        'page Object.'
        '</H3>'
        '(Open "Parent Example" and enter "My Child" to see the buttons)'
    )
    parent_example = Child(ParentExample)

    conn_doc = Label(
        '<HR><H3>'
        'The <u>Connection</u> relation lets the user specify the related Object.<br>'
        'In this example you can drag and drop one the the two options to the "Current" relation.'
    )
    connection_example = Child(ConnectionExample)

    label_doc = Label(
        '<HR><H3>'
        'Some relation are just GUI sugar, like this "Label" for example.<br>'
        'You can also add simple separators like this one:'
    )
    sep = Separator()

    group_doc = Label(
        '<HR><H3>'
        'You can group your relations with the group context by using "with kabaret.flow.group(&lt;name&gt;):".<br>'
        'Children are grouped together'
    )
    with group('foo'):

        bar = Child(MyChild)
        baz = Child(MyChild)

        with group('yolo'):
            wip = Label(
                '<HR><H3>'
                'Nested groups feature in progress...'
            )

    sep2 = Separator()
