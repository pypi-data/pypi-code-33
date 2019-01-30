from typing import List, Optional

import wpilib
from networktables.util import ChooserControl
from networktables import NetworkTables

import logging

logger = logging.getLogger("marsutils")


class ControlInterface:
    """
        ``ControlInterface`` is the base class that all interfaces must subclass to
        be used with :class:`.ControlManager`.

        You must define a ``_DISPLAY_NAME``. This value will be displayed in the
        dashboard chooser. Optionally, you can define a ``_SORT`` value. The larger
        the value, the higher priority it will be given in the chooser.
    """

    _DISPLAY_NAME: str
    _SORT = 0

    def teleopPeriodic(self):
        pass

    def enabled(self):
        pass

    def disabled(self):
        pass


class ControlManager:
    """
        This class manages creating a dashboard chooser and the periodic
        calling of a series of "control interface" components.

        Each control interface must subclass :class:`ControlInterface` and
        define ``_DISPLAY_NAME``.

        Once this has been initalized with the list of interfaces, you must manually
        call every event function you want your components to recive, like
        "teleopPeridic" and "teleopInit" and they will be forwarded to the active
        interface

        You can optionally define a ``_SORT`` value for your interfaces.
        The larger the value, the higher priority it will be given in the chooser.

        If ``dashboard_key`` is None, then the control chooser will not be added
        automatically, use this if you are using the Shuffleboard API or want a
        different root path. The control chooser can be accessed from
        ``control_chooser``
    """

    __slots__ = [
        "control_mode",
        "control_interfaces",
        "control_chooser",
        "control_chooser_control",
    ]

    def __init__(
        self,
        *interfaces: ControlInterface,
        dashboard_key: Optional[str] = "Control Mode",
    ):
        assert len(interfaces) > 0, "No control interfaces given"

        # Sort the interfaces by their _SORT values
        interfaces = tuple(sorted(interfaces, key=lambda x: x._SORT, reverse=True))

        self.control_mode = None
        self.control_interfaces: List[ControlInterface] = []

        self.control_chooser = wpilib.SendableChooser()

        for i, mode in enumerate(interfaces):
            if not hasattr(mode, "_DISPLAY_NAME"):
                logger.error(
                    f'Control interface {mode.__class__.__name__} has no "_DISPLAY_NAME" attr, \
                    skipping'
                )
                continue
            if not isinstance(mode._DISPLAY_NAME, str):
                logger.error(
                    f'Control interface {mode.__class__.__name__} has non-string "_DISPLAY_NAME" \
                    attr'
                )
                continue
            self.control_interfaces.append(mode)
            # Make the first entry the default
            # TODO: Configurable?
            if i == 0:
                self.control_chooser.setDefaultOption(mode._DISPLAY_NAME, i)
            else:
                self.control_chooser.addOption(mode._DISPLAY_NAME, i)

        if dashboard_key is not None:
            wpilib.SmartDashboard.putData(dashboard_key, self.control_chooser)

            self.control_chooser_control = ChooserControl(
                dashboard_key, on_selected=self._control_mode_changed
            )

    def teleopPeriodic(self):
        if self.control_mode is not None:
            self.control_mode.teleopPeriodic()

    def _control_mode_changed(self, *args):
        new_selected: int = self.control_chooser.getSelected()
        if new_selected is None:
            return
        if new_selected >= len(self.control_interfaces):
            logger.error(f"Invalid control mode: {new_selected}")
            return
        if self.control_mode != self.control_interfaces[new_selected]:
            if self.control_mode is not None:
                self.control_mode.disabled()
            self.control_mode = self.control_interfaces[new_selected]
            if self.control_mode is not None:
                self.control_mode.enabled()

    def setup_listener(self, dashboard_key):
        """
            If you construct the ControlManager with a None dashboard_key, you
            must call this function with the full networktables path to connect
            the callback for the mode to be properly updated
        """
        table = NetworkTables.getTable(dashboard_key)
        table.addEntryListener(self._control_mode_changed, True)
