
from kabaret import flow


class InGridConfig(flow.Object):

    @classmethod
    def _collect_ingrid_configs(cls, obj, collected, seen):
        oid = obj.oid()
        if oid in seen:
            return
        seen.add(oid)

        try:
            obj.get_ingrid_config_oids
        except AttributeError:
            pass
        else:
            collected.extend([
                obj._mng.get_object(oid)
                for oid in obj.get_ingrid_config_oids()
            ])

        parent = obj._mng.parent
        if parent.root() == parent:
            return
        cls._collect_ingrid_configs(parent, collected, seen)

    @classmethod
    def find_ingrid_configs(cls, obj):
        '''
        Returns a list of InGridConfig found between obj and its root.
        '''
        collected = []
        seen = set()
        cls._collect_ingrid_configs(obj, collected, seen)
        return collected

    @classmethod
    def get_object_ui(cls, obj):
        '''
        Returns the ui config of a flow Object, or None
        if it has no associated ui config.
        The return value is suitable as the value of
        the 'ui' key of get_rows() items, get_columns() 
        items, and get_cell() return value.

        This is provided as convenience as it is not so
        obvious how to get a ui config from the object
        itself.
        '''
        if obj._mng.parent is None:
            # Root object have no ui
            return None
        # Unless it's a mapped item, the relation creating
        # the object has the name of the object.
        # As mapped items dont have ui, we can just try:
        try:
            parent_relation = getattr(
                obj._mng.parent.__class__, obj.name()
            )
        except AttributeError:
            return None
        return parent_relation.get_ui()

    def get_config_name(self):
        return self.name().replace('_', ' ').title()
    
    def get_related_config_oids(self):
        '''
        Must return a list of oids pointing to other
        InGridConfig objects.
        '''
        return []

    def get_rows(self):
        '''
        Must return a list of dict with keys similar to 
        the get_cell() return value.
        '''
        return []

    def get_columns(self):
        '''
        Must return a list of dict with keys similar to 
        the get_cell() return value.
        '''
        return []

    def get_cell(self, row, column):
        '''
        Must return a dict with keys used in this default
        implementation.
        '''
        return dict(
            display='???',
            oid=None, # used to list available actions
            bg=None,
            fg=None,
            icon=None,
            ui=None,
            align='center', # one of ['left', 'right', 'center']
        )

    def get_actions(self, *row_column_pairs):
        '''
        Return a list of (label, action_oid) for the given list
        of (row, cols)
        '''
        return []


class SharedSessionValue(flow.values.SessionValue):
    '''
    This session value is shared for all ites instances.
    It is used to have a commun state for all 'new_ingrid' param
    of the ShowIngridDialogAction
    '''
    _VALUE = False

    def set(self, value):
        self.__class__._VALUE = value
        super(SharedSessionValue, self).set(value)

    def get(self):
        return self._VALUE

class ShowInGridDialogAction(flow.Action):
    '''
    This action will let the user select and load
    one of the InGridConfig found for its parent.
    '''
    _parent = flow.Parent()

    new_inGrid = flow.Param(False, SharedSessionValue).ui(editor='bool')

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self._configs_cache = [
            (c.get_config_name() , c)
            for c in InGridConfig.find_ingrid_configs(self._parent)
        ]
        return [ n for n, c in self._configs_cache ]

    def run(self, button):
        config = dict(self._configs_cache)[button]

        goto_target = None
        if self.new_inGrid.get():
            goto_target = '_NEW_'

        return self.get_result(
            goto=config.oid(),
            goto_target=goto_target,
            goto_target_type='InGrid'
        )

class ShowInGridAction(flow.Action):
    '''
    This action will open a new InGrid view for 
    the config specified by subclassing get_config_oid()

    This is usefull for mapped item where only dialog-less
    action can be used on a multi-selection
    '''

    def needs_dialog(self):
        return False

    def run(self, button):
        config_oid = self.get_config_oid()
        return self.get_result(
            goto=config_oid,
            goto_target='_NEW_',
            goto_target_type='InGrid'
        )

    def get_config_oid(self):
        '''
        Returns the oid of the InGridConfig to open.
        Default is to use the first discoverable one.
        Subclass may override this for arbitrary config.
        '''
        configs = InGridConfig.find_ingrid_configs(self._mng.parent)
        if not configs:
            raise Exception('No InGridConfig found under {}'.format(self._mng.parent.oid()))
        return configs[0].oid()
