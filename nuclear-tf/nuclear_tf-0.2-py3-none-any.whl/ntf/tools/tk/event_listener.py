
class EventListener:
    def __init__(self, widget):
        self.widget = widget

    def registerLeftClick(self, callback):
        self.widget.bind('<Button-1>', callback)

    def registerRightClick(self, callback):
        self.widget.bind('<Button-3>', callback)

    def registerScrollUp(self, callback):
        self.widget.bind('<Button-4>', callback)

    def registerScrollDown(self, callback):
        self.widget.bind('<Button-5>', callback)

    def registerLeftDrag(self, callback):
        self.widget.bind('<B1-Motion>', callback)

    def registerRightDrag(self, callback):
        self.widget.bind('<B3-Motion>', callback)

    def registerKeyPress(self, callback):
        self.widget.bind('<Key>', callback)
