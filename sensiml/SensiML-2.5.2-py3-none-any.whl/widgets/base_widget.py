
class BaseWidget():
    def __init__(self, dsk):
        self._dsk = dsk
        self.setup()

    def setup(self):
        pass

    def on_button_clicked(self, b):
        pass

    def create_widget(self):
        pass
