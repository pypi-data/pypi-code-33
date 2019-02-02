import numpy

from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.util.oasys_util import ChemicalFormulaParser

from orangecontrib.syned.widgets.gui.ow_optical_element import OWOpticalElementWithSurfaceShape

from syned.beamline.optical_elements.crystals.crystal import Crystal


class OWCrystal(OWOpticalElementWithSurfaceShape):

    name = "Crystal"
    description = "Syned: Crystal"
    icon = "icons/crystal.png"
    priority = 7

    material = Setting("Si")
    miller_index_h = Setting(1)
    miller_index_k = Setting(1)
    miller_index_l = Setting(1)
    asymmetry_angle=0.0
    thickness = Setting(0.0)

    def __init__(self):
        super().__init__()

    def draw_specific_box(self):

        self.tab_cry = oasysgui.createTabPage(self.tabs_setting, "Crystal Setting")

        super().draw_specific_box(self.tab_cry)

        self.crystal_box = oasysgui.widgetBox(self.tab_cry, "Crystal", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.crystal_box, self, "material", "Material [Chemical Formula]", labelWidth=180, valueType=str, orientation="horizontal")
        oasysgui.lineEdit(self.crystal_box, self, "thickness", "Thickness [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.crystal_box, self, "miller_index_h", "Miller Index h", labelWidth=260, valueType=int, orientation="horizontal")
        oasysgui.lineEdit(self.crystal_box, self, "miller_index_k", "Miller Index j", labelWidth=260, valueType=int, orientation="horizontal")
        oasysgui.lineEdit(self.crystal_box, self, "miller_index_l", "Miller Index l", labelWidth=260, valueType=int, orientation="horizontal")

        oasysgui.lineEdit(self.crystal_box, self, "asymmetry_angle", "Asymmetry Angle [deg]", labelWidth=260, valueType=float, orientation="horizontal")


    def get_optical_element(self):
        return Crystal(name=self.oe_name,
                       boundary_shape=self.get_boundary_shape(),
                       surface_shape=self.get_surface_shape(),
                       material=self.material,
                       miller_index_h=self.miller_index_h,
                       miller_index_k=self.miller_index_k,
                       miller_index_l=self.miller_index_l,
                       asymmetry_angle=numpy.radians(self.asymmetry_angle),
                       thickness=self.thickness)

    def check_data(self):
        super().check_data()

        congruence.checkEmptyString(self.material, "Material")
        ChemicalFormulaParser.parse_formula(self.material)
        congruence.checkStrictlyPositiveNumber(self.thickness, "Thickness")

