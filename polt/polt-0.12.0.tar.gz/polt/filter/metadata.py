# system modules
import functools
import logging
from abc import ABC, abstractmethod

# internal modules
from polt.filter import Filter
from polt.utils import *

# external modules


class MetaDataFilter(Filter):
    """
    Filter for modifying metadata of a dataset
    """

    @property
    def when_quantity(self):
        """
        Only operate on this quantity

        .. note::

            Set this option from the command-line via
            ``polt add-filter -f metadata -o when-quantity=QUANTITY``

        :type: :class:`str` or ``None``
        """
        try:
            self._when_quantity
        except AttributeError:
            self._when_quantity = None
        return self._when_quantity

    @when_quantity.setter
    def when_quantity(self, new):
        self._when_quantity = str(new) if new else None

    @property
    def when_unit(self):
        """
        Only operate on this unit

        .. note::

            Set this option from the command-line via
            ``polt add-filter -f metadata -o when-unit=UNIT``

        :type: :class:`str` or ``None``
        """
        try:
            self._when_unit
        except AttributeError:
            self._when_unit = None
        return self._when_unit

    @when_unit.setter
    def when_unit(self, new):
        self._when_unit = str(new) if new else None

    @property
    def when_key(self):
        """
        Only operate on this key

        .. note::

            Set this option from the command-line via
            ``polt add-filter -f metadata -o when-key=KEY``

        :type: :class:`str` or ``None``
        """
        try:
            self._when_key
        except AttributeError:
            self._when_key = None
        return self._when_key

    @when_key.setter
    def when_key(self, new):
        self._when_key = str(new) if new else None

    @property
    def set_quantity(self):
        """
        Set the quantity to this value

        .. note::

            Set this option from the command-line via
            ``polt add-filter -f metadata -o set-quantity=QUANTITY``

        :type: :class:`str` or ``None``
        """
        try:
            self._set_quantity
        except AttributeError:
            self._set_quantity = None
        return self._set_quantity

    @set_quantity.setter
    def set_quantity(self, new):
        self._set_quantity = str(new) if new else None

    @property
    def set_unit(self):
        """
        Set the unit to this value

        .. note::

            Set this option from the command-line via
            ``polt add-filter -f metadata -o set-unit=UNIT``

        :type: :class:`str` or ``None``
        """
        try:
            self._set_unit
        except AttributeError:
            self._set_unit = None
        return self._set_unit

    @set_unit.setter
    def set_unit(self, new):
        self._set_unit = str(new) if new else None

    @property
    def set_key(self):
        """
        Set the key to this value

        .. note::

            Set this option from the command-line via
            ``polt add-filter -f metadata -o set-key=KEY``

        :type: :class:`str` or ``None``
        """
        try:
            self._set_key
        except AttributeError:
            self._set_key = None
        return self._set_key

    @set_key.setter
    def set_key(self, new):
        self._set_key = str(new) if new else None

    def update_dataset(self, dataset):
        """
        Modify parts of a dataset that match the conditions
        :any:`when_quantity`, :any:`when_unit` and :any:`when_key` and set
        their metadata according to the specified settings :any:`set_quantity`,
        :any:`set_unit` and :any:`set_key`.

        Args:
            dataset (dict): the dataset to modify

        Returns:
            dict or None: the modified dataset

        """
        data = dataset.get("data", {})
        rename = {}
        for key, val in data.items():
            keyiter = iter(to_tuple(key))
            props = {
                p: next(keyiter, None) for p in ("quantity", "unit", "key")
            }
            conditions = {
                p: getattr(self, "when_{}".format(p), None)
                for p in ("quantity", "unit", "key")
                if getattr(self, "when_{}".format(p), None) is not None
            }
            # skip this part if any conditions is not met
            if any(props[p] != v for p, v in conditions.items()):
                continue
            # determine new properties
            setprops = {
                p: getattr(self, "set_{}".format(p), None)
                for p in ("quantity", "unit", "key")
                if getattr(self, "set_{}".format(p), None) is not None
            }
            newprops = props.copy()
            newprops.update(setprops)
            if props == newprops:
                continue
            # make sure the new properties are not yet in the data
            propstuple = tuple(
                newprops[p] for p in ("quantity", "unit", "key")
            )
            while propstuple in data or propstuple in rename.values():
                propstuple += (None,)
            # record the new properties for later renaming
            rename[key] = propstuple
        # do the actual renaming
        for old, new in rename.items():
            data[new] = data.pop(old)

        return dataset
