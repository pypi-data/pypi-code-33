
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.syned.widgets.gui.ow_optical_element import OWOpticalElementWithSurfaceShape

from syned.beamline.optical_elements.gratings.grating import Grating


class OWGrating(OWOpticalElementWithSurfaceShape):

    name = "Grating"
    description = "Syned: Grating"
    icon = "icons/grating.png"
    priority = 8

    ruling_at_center = Setting(800e3)

    def __init__(self):
        super().__init__()

    def draw_specific_box(self):

        self.tab_gra = oasysgui.createTabPage(self.tabs_setting, "Grating Setting")

        super().draw_specific_box(self.tab_gra)

        self.ruling_box = oasysgui.widgetBox(self.tab_gra, "Ruling", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.ruling_box, self, "ruling_at_center", "Ruling at Center [lines/m]", labelWidth=180, valueType=float, orientation="horizontal")


    def get_optical_element(self):
        return Grating(name=self.oe_name,
                       boundary_shape=self.get_boundary_shape(),
                       surface_shape=self.get_surface_shape(),
                       ruling=self.ruling_at_center)

    def check_data(self):
        super().check_data()

        congruence.checkStrictlyPositiveNumber(self.ruling_at_center, "Ruling at Center")
