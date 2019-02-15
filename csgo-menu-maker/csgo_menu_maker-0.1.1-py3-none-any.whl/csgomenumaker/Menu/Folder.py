from .. import Command
from .. import Component

from .Menu import Menu


@Component.ConfigType("folder")
class Folder(Command.NavState.VertFolder, Menu):
    defaultName = "Folder"
    defaultDesc = "A generic folder."

    def __init__(self, parent, options):
        Menu.__init__(self, parent, options)
        Command.NavState.VertFolder.__init__(self, parent)
        self.setSpecs()
        self.cls = "menu-folder"
        self.optTypeKey(options, "tree", list())
        self.optLenZero(options["tree"])
        for child in options["tree"]:
            if isinstance(child, dict):
                self.instantiate(child)
            elif isinstance(child, str):
                ch = {"type": child}
                self.instantiate(ch)
            else:
                self.optType(options, "type", dict())
        self.makeDialog()

    def instantiate(self, obj):
        self.optTypeKey(obj, "type", str())
        cl = None
        try:
            cl = self.root.getClass(obj["type"])
        except:
            self.error("Unknown type '%s' in object '%s'" % (obj["type"], obj))
        self.addSelection(cl(self, obj))

    def makeDialog(self):
        text0 = ""
        text1 = self.selections[0].getUIName()
        text2 = ""
        text3 = ""
        if len(self.selections) == 2:
            text0 = ""
            text1 = self.selections[0].getUIName()
            text2 = self.selections[1].getUIName()
            text3 = ""
        elif len(self.selections) == 3:
            text0 = ""
            text1 = self.selections[0].getUIName()
            text2 = self.selections[1].getUIName()
            text3 = self.selections[2].getUIName()
        elif len(self.selections) == 4:
            text0 = self.selections[0].getUIName()
            text1 = self.selections[1].getUIName()
            text2 = self.selections[2].getUIName()
            text3 = self.selections[3].getUIName()
        elif len(self.selections) > 4:
            text0 = self.selections[0].getUIName()
            text1 = self.selections[1].getUIName()
            text2 = self.selections[2].getUIName()
            text3 = "..."
        preNone = " "*15
        preContents = "     Contents: "
        preChildren = ("(%i children) " % len(self.selections)).rjust(15)
        self.dummy.setTextContent(0, preNone+text0)
        self.dummy.setTextContent(1, preContents+text1)
        self.dummy.setTextContent(2, preNone+text2)
        if len(self.selections) > 4:
            self.dummy.setTextContent(2, preChildren+text2)
        self.dummy.setTextContent(3, preNone+text3)
