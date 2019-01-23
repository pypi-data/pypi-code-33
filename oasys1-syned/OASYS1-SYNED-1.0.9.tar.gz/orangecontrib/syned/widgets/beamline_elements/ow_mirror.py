
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.util.oasys_util import ChemicalFormulaParser

from orangecontrib.syned.widgets.gui.ow_optical_element import OWOpticalElementWithSurfaceShape

from syned.beamline.optical_elements.mirrors.mirror import Mirror


class OWMirror(OWOpticalElementWithSurfaceShape):

    name = "Mirror"
    description = "Syned: Mirror"
    icon = "icons/mirror.png"
    priority = 6

    coating_material = Setting("Pt")
    coating_thickness = Setting(0.0)

    def __init__(self):
        super().__init__()

    def draw_specific_box(self):

        self.tab_mir = oasysgui.createTabPage(self.tabs_setting, "Mirror Setting")

        super().draw_specific_box(self.tab_mir)

        self.coating_box = oasysgui.widgetBox(self.tab_mir, "Coating", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.coating_box, self, "coating_material", "Material [Chemical Formula]", labelWidth=180, valueType=str, orientation="horizontal")
        oasysgui.lineEdit(self.coating_box, self, "coating_thickness", "Thickness [m]", labelWidth=260, valueType=float, orientation="horizontal")


    def get_optical_element(self):

        return Mirror(name=self.oe_name,
                      boundary_shape=self.get_boundary_shape(),
                      surface_shape=self.get_surface_shape(),
                      coating=self.coating_material,
                      coating_thickness=self.coating_thickness)

    def check_data(self):
        super().check_data()

        congruence.checkEmptyString(self.coating_material, "Coating Material")
        ChemicalFormulaParser.parse_formula(self.coating_material)
        congruence.checkStrictlyPositiveNumber(self.coating_thickness, "Coating Thickness")
