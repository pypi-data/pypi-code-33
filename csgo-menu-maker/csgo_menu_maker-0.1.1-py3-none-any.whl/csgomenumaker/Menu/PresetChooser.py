from .. import Command

from .Menu import Menu
from .Choice import Choice


class PresetChooser(Choice):
    def __init__(self, parent, options):
        Choice.__init__(self, parent, options)
        self.presetType = ""
        self.optTypeKey(self.options, "presets", list())
        for pre in self.options["presets"]:
            self.optType(pre, dict())
            cmds = self.getCommands(pre)
            self.optTypeKey(pre, "name", str())
            self.addPreset(pre["name"], cmds)
        self.makeChoices()

    def setPresetType(self, ptype):
        self.presetType = ptype

    def addPreset(self, name, commands):
        ocmd = Command.Compound(self)
        for cmd in commands:
            ocmd.addChild(cmd)
        self.addChoice(name, ocmd)
        self.menuRoot.addPreset(self.presetType, name, ocmd)
